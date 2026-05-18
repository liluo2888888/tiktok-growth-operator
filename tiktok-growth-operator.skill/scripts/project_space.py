from __future__ import annotations

from datetime import datetime
from pathlib import Path

from text_normalization import read_json_file, write_json_file

PROJECT_SPACE_FILENAME = "project_space.json"

ROLE_PIPELINE = [
    {
        "id": "creative_director",
        "title": "创意总监",
        "goal": "锁定参考方向、证明策略与不可迁移的账号加成边界",
        "outputs": ["reference_selection", "proof_strategy", "adaptation_constraints"],
    },
    {
        "id": "writer_screenwriter",
        "title": "编剧",
        "goal": "把策略落成可拍脚本、钩子变体与字幕节拍",
        "outputs": ["script_draft", "hook_variants", "subtitle_beats"],
    },
    {
        "id": "director_execution",
        "title": "导演执行",
        "goal": "输出分镜、资产需求与生成任务交接",
        "outputs": ["shot_list", "asset_requirements", "generation_job"],
    },
]


def default_project_space(*, name: str, project: str, request: str = "", mode: str = "") -> dict:
    now = datetime.now().isoformat(timespec="seconds")
    steps = []
    for role in ROLE_PIPELINE:
        steps.append(
            {
                "role_id": role["id"],
                "title": role["title"],
                "status": "pending",
                "goal": role["goal"],
                "expected_outputs": list(role["outputs"]),
                "artifacts": [],
                "updated_at": now,
            }
        )
    return {
        "schema_version": "project-space-v1",
        "name": name,
        "project": project,
        "request": request,
        "resolved_mode": mode,
        "created_at": now,
        "updated_at": now,
        "branching": {
            "mode": "one_script",
            "variants": 1,
            "notes": "可切换到 four_variant 分支；当前默认单脚本主线",
        },
        "roles": ROLE_PIPELINE,
        "steps": steps,
        "current_role_id": "creative_director",
    }


def project_space_path(project_root: Path) -> Path:
    return project_root / PROJECT_SPACE_FILENAME


def load_project_space(project_root: Path) -> dict | None:
    path = project_space_path(project_root)
    if not path.exists():
        return None
    payload = read_json_file(path)
    return payload if isinstance(payload, dict) else None


def write_project_space(project_root: Path, manifest: dict) -> Path:
    manifest["updated_at"] = datetime.now().isoformat(timespec="seconds")
    path = project_space_path(project_root)
    write_json_file(path, manifest)
    return path


def init_project_space(project_root: Path, *, name: str, project: str, request: str = "", mode: str = "") -> dict:
    manifest = default_project_space(name=name, project=project, request=request, mode=mode)
    write_project_space(project_root, manifest)
    return manifest


def advance_step(project_root: Path, role_id: str, *, status: str, artifacts: list[dict] | None = None) -> dict:
    manifest = load_project_space(project_root) or default_project_space(name=project_root.name, project=project_root.name)
    now = datetime.now().isoformat(timespec="seconds")
    for step in manifest.get("steps", []):
        if step.get("role_id") == role_id:
            step["status"] = status
            step["updated_at"] = now
            if artifacts:
                step["artifacts"] = list(artifacts)
    manifest["current_role_id"] = role_id
    write_project_space(project_root, manifest)
    return manifest


def attach_project_space_to_payload(payload: dict, project_root: Path | None) -> None:
    if project_root is None:
        return
    manifest = load_project_space(project_root)
    if manifest:
        payload["project_space"] = manifest
