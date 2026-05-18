from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from clipcat_client import (
    clipcat_configured,
    extract_artifact_links,
    extract_task_id,
    query_task,
    submit_generation_task,
)
from generation_jobs import artifact_manifest_path, load_jobs, save_jobs
from text_normalization import normalize_text, read_json_file, write_json_file


def renderer_http_url() -> str:
    return normalize_text(os.environ.get("GENERATION_RENDERER_URL")).rstrip("/")


def renderer_mode() -> str:
    return normalize_text(os.environ.get("GENERATION_RENDERER_MODE")).lower() or "auto"


def _http_json(method: str, url: str, payload: dict | None = None) -> dict:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    api_key = normalize_text(os.environ.get("GENERATION_RENDERER_API_KEY"))
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=120) as response:
        body = json.loads(response.read().decode("utf-8"))
    return body if isinstance(body, dict) else {"payload": body}


def load_handoff_pack(capture_root: Path, scene_id: str) -> dict:
    path = capture_root / "production_spec_handoff.json"
    if path.exists():
        payload = read_json_file(path)
        if isinstance(payload, dict):
            return payload
    return {}


def clipcat_task_type(backend: str, scene_id: str) -> str:
    if backend == "i2v" or scene_id in {"10", "14", "16"}:
        return "product_video"
    if backend in {"sora", "veo"}:
        return "replicate"
    return "product_video"


def build_renderer_prompt(job: dict, handoff_pack: dict) -> str:
    parts = [normalize_text(job.get("brief_summary"))]
    branches = handoff_pack.get("generator_branches") if isinstance(handoff_pack, dict) else {}
    if isinstance(branches, dict):
        for name, branch in branches.items():
            if isinstance(branch, dict):
                parts.append(f"[{name}] style={branch.get('style')} shots={len(branch.get('shots') or [])}")
    return " | ".join(part for part in parts if part)


def submit_via_http(capture_root: Path, job: dict, handoff_pack: dict) -> dict[str, Any]:
    base = renderer_http_url()
    if not base:
        return {"status": "skipped", "reason": "no-renderer-url"}
    payload = {
        "job_id": job["job_id"],
        "scene_id": job.get("scene_id"),
        "backend": job.get("backend_hint"),
        "brief_summary": job.get("brief_summary"),
        "handoff_pack": handoff_pack,
    }
    body = _http_json("POST", f"{base}/v1/generation/jobs", payload)
    external_job_id = normalize_text(body.get("external_job_id") or body.get("id") or body.get("job_id"))
    status = normalize_text(body.get("status")) or "submitted"
    job["external_job_id"] = external_job_id
    job["renderer_provider"] = "http"
    job["status"] = status if status in {"pending", "submitted", "running"} else "submitted"
    job["renderer_response"] = body
    registry = load_jobs(capture_root)
    registry.setdefault("jobs", {})[job["job_id"]] = job
    save_jobs(capture_root, registry)
    return {"status": job["status"], "provider": "http", "external_job_id": external_job_id, "response": body}


def submit_via_clipcat(capture_root: Path, job: dict, handoff_pack: dict) -> dict[str, Any]:
    if not clipcat_configured():
        return {"status": "skipped", "reason": "clipcat-not-configured"}
    backend = normalize_text(job.get("backend_hint")) or "sora"
    scene_id = normalize_text(job.get("scene_id"))
    task_type = clipcat_task_type(backend, scene_id)
    prompt = build_renderer_prompt(job, handoff_pack)
    model = backend if backend in {"sora", "veo"} else ""
    result = submit_generation_task(task_type=task_type, prompt=prompt, model=model, duration=20)
    if not result.get("ok"):
        return {"status": "error", "provider": "clipcat", "detail": result}
    stdout = result.get("stdout")
    external_job_id = extract_task_id(stdout)
    job["external_job_id"] = external_job_id
    job["renderer_provider"] = "clipcat"
    job["clipcat_task_type"] = task_type
    job["status"] = "submitted" if external_job_id else "pending"
    job["renderer_response"] = stdout
    registry = load_jobs(capture_root)
    registry.setdefault("jobs", {})[job["job_id"]] = job
    save_jobs(capture_root, registry)
    return {
        "status": job["status"],
        "provider": "clipcat",
        "external_job_id": external_job_id,
        "task_type": task_type,
    }


def poll_via_http(capture_root: Path, job: dict) -> dict[str, Any]:
    base = renderer_http_url()
    external_job_id = normalize_text(job.get("external_job_id"))
    if not base or not external_job_id:
        return job
    body = _http_json("GET", f"{base}/v1/generation/jobs/{external_job_id}")
    status = normalize_text(body.get("status")) or job.get("status")
    links = body.get("artifact_links") if isinstance(body.get("artifact_links"), list) else []
    job["status"] = status
    if links:
        job["artifact_links"] = [normalize_text(item) for item in links if normalize_text(item)]
        write_json_file(
            artifact_manifest_path(capture_root, job["job_id"]),
            {"artifact_links": job["artifact_links"], "provider": "http", "poll_response": body},
        )
    job["poll_response"] = body
    registry = load_jobs(capture_root)
    registry.setdefault("jobs", {})[job["job_id"]] = job
    save_jobs(capture_root, registry)
    return job


def poll_via_clipcat(capture_root: Path, job: dict) -> dict[str, Any]:
    external_job_id = normalize_text(job.get("external_job_id"))
    task_type = normalize_text(job.get("clipcat_task_type")) or "replicate"
    if not external_job_id or not clipcat_configured():
        return job
    result = query_task(task_id=external_job_id, task_type=task_type)
    stdout = result.get("stdout")
    status = "succeeded"
    if isinstance(stdout, dict):
        raw_status = normalize_text(stdout.get("status") or _dig_status(stdout)).lower()
        if raw_status in {"failed", "error"}:
            status = "failed"
        elif raw_status in {"pending", "running", "processing", "queued"}:
            status = "running"
    links = extract_artifact_links(stdout)
    if links:
        job["status"] = "succeeded"
        job["artifact_links"] = links
        write_json_file(
            artifact_manifest_path(capture_root, job["job_id"]),
            {"artifact_links": links, "provider": "clipcat", "poll_response": stdout},
        )
    else:
        job["status"] = status
    job["poll_response"] = stdout
    registry = load_jobs(capture_root)
    registry.setdefault("jobs", {})[job["job_id"]] = job
    save_jobs(capture_root, registry)
    return job


def _dig_status(payload: dict) -> str:
    for key in ("status", "task_status", "state"):
        value = normalize_text(payload.get(key))
        if value:
            return value
    data = payload.get("data")
    if isinstance(data, dict):
        return _dig_status(data)
    return ""


def submit_generation_job(capture_root: Path, job_id: str) -> dict[str, Any]:
    registry = load_jobs(capture_root)
    job = (registry.get("jobs") or {}).get(job_id)
    if not isinstance(job, dict):
        return {"status": "missing", "job_id": job_id}
    handoff_pack = load_handoff_pack(capture_root, normalize_text(job.get("scene_id")))
    mode = renderer_mode()
    if mode in {"http", "auto"} and renderer_http_url():
        result = submit_via_http(capture_root, job, handoff_pack)
        if result.get("status") not in {"skipped"}:
            return result
    if mode in {"clipcat", "auto"}:
        return submit_via_clipcat(capture_root, job, handoff_pack)
    return {"status": "skipped", "reason": "no-renderer-backend"}


def poll_generation_job_remote(capture_root: Path, job_id: str) -> dict[str, Any]:
    registry = load_jobs(capture_root)
    job = (registry.get("jobs") or {}).get(job_id)
    if not isinstance(job, dict):
        return {"status": "missing", "job_id": job_id}
    provider = normalize_text(job.get("renderer_provider"))
    if provider == "http":
        return poll_via_http(capture_root, job)
    if provider == "clipcat":
        return poll_via_clipcat(capture_root, job)
    if renderer_http_url():
        job = poll_via_http(capture_root, job)
        if normalize_text(job.get("external_job_id")):
            return job
    if clipcat_configured() and normalize_text(job.get("external_job_id")):
        return poll_via_clipcat(capture_root, job)
    return job
