from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path

from text_normalization import normalize_text, read_json_file, write_json_file

JOBS_FILENAME = "generation_jobs.json"
GENERATION_SCENES = {f"{index:02d}" for index in range(9, 17)}

BACKEND_HINTS = {
    "09": ["manual_edit", "sora", "veo"],
    "10": ["i2v", "sora", "manual_edit"],
    "11": ["sora", "veo", "manual_edit"],
    "12": ["manual_edit", "variant_matrix"],
    "13": ["manual_edit", "localization_pack"],
    "14": ["manual_edit", "asset_family"],
    "15": ["manual_edit", "image_translate"],
    "16": ["manual_edit", "benchmark_still"],
}


def jobs_path(capture_root: Path) -> Path:
    return capture_root / JOBS_FILENAME


def load_jobs(capture_root: Path) -> dict:
    path = jobs_path(capture_root)
    if path.exists():
        payload = read_json_file(path)
        if isinstance(payload, dict):
            return payload
    return {"schema_version": "generation-jobs-v1", "jobs": {}}


def save_jobs(capture_root: Path, registry: dict) -> Path:
    path = jobs_path(capture_root)
    write_json_file(path, registry)
    return path


def artifact_manifest_path(capture_root: Path, job_id: str) -> Path:
    return capture_root / "generation_jobs" / job_id / "artifacts.json"


def create_generation_job(
    capture_root: Path,
    *,
    scene_id: str,
    project: str,
    brief_summary: str,
    backend_hint: str = "",
) -> dict:
    scene = normalize_scene_id(scene_id)
    job_id = f"gen-{scene}-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"
    backends = BACKEND_HINTS.get(scene, ["manual_edit", "sora", "veo", "i2v"])
    job = {
        "job_id": job_id,
        "scene_id": scene,
        "project": project,
        "status": "pending",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "backend_hint": backend_hint or backends[0],
        "backend_options": backends,
        "brief_summary": brief_summary,
        "artifact_links": [],
        "poll": {"interval_s": 30, "max_attempts": 120, "strategy": "read_local_artifact_manifest"},
        "submission": {
            "required_fields": ["brief_summary", "shot_list", "asset_requirements"],
            "note": "Final renderer API is pluggable; job stays pending until artifacts.json is supplied or status is updated.",
        },
    }
    registry = load_jobs(capture_root)
    registry.setdefault("jobs", {})[job_id] = job
    save_jobs(capture_root, registry)
    artifact_manifest_path(capture_root, job_id).parent.mkdir(parents=True, exist_ok=True)
    return job


def normalize_scene_id(scene_id: str) -> str:
    text = str(scene_id).strip().lower().replace("scene-", "").replace("scene", "")
    return text.zfill(2) if text.isdigit() else text


def poll_generation_job(capture_root: Path, job_id: str) -> dict:
    from generation_renderer_backend import poll_generation_job_remote

    registry = load_jobs(capture_root)
    job = (registry.get("jobs") or {}).get(job_id)
    if not isinstance(job, dict):
        return {"status": "missing", "job_id": job_id}
    if normalize_text(job.get("external_job_id")) or normalize_text(job.get("renderer_provider")):
        job = poll_generation_job_remote(capture_root, job_id)
    manifest_path = artifact_manifest_path(capture_root, job_id)
    if manifest_path.exists():
        manifest = read_json_file(manifest_path)
        links = manifest.get("artifact_links") if isinstance(manifest, dict) else []
        if isinstance(links, list) and links:
            job["status"] = "succeeded"
            job["artifact_links"] = links
            job["updated_at"] = datetime.now().isoformat(timespec="seconds")
            registry = load_jobs(capture_root)
            registry["jobs"][job_id] = job
            save_jobs(capture_root, registry)
    return job


def maybe_auto_submit_generation_job(capture_root: Path, job_id: str) -> dict | None:
    import os

    flag = normalize_text(os.environ.get("GENERATION_AUTO_SUBMIT")).lower()
    if flag not in {"1", "true", "yes", "on"}:
        return None
    from generation_renderer_backend import submit_generation_job

    return submit_generation_job(capture_root, job_id)


def register_scene_generation_handoff(
    payload: dict,
    capture_root: Path | None,
    *,
    scene_id: str,
    brief_summary: str,
) -> dict | None:
    scene = normalize_scene_id(scene_id)
    if scene not in GENERATION_SCENES or capture_root is None:
        return None
    project = (payload.get("metadata") or {}).get("project") or "tiktok-capture-pack"
    job = create_generation_job(capture_root, scene_id=scene, project=project, brief_summary=brief_summary)
    submit_result = maybe_auto_submit_generation_job(capture_root, job["job_id"])
    if isinstance(submit_result, dict) and submit_result.get("status") not in {None, "skipped"}:
        job = load_jobs(capture_root).get("jobs", {}).get(job["job_id"], job)
    payload["generation_handoff"] = {
        "job_id": job["job_id"],
        "status": job["status"],
        "backend_hint": job["backend_hint"],
        "backend_options": job["backend_options"],
        "poll": job["poll"],
        "artifact_manifest": str(artifact_manifest_path(capture_root, job["job_id"])),
        "jobs_registry": str(jobs_path(capture_root)),
        "external_job_id": job.get("external_job_id", ""),
        "renderer_provider": job.get("renderer_provider", ""),
        "submit_result": submit_result,
    }
    payload["assets"] = payload.get("assets", [])
    payload["assets"].append(
        {
            "label": f"Scene {scene} generation job registry",
            "path": str(jobs_path(capture_root)),
            "note": "Async generation job semantics; drop artifacts.json under generation_jobs/<job_id>/ to mark succeeded.",
        }
    )
    return job
