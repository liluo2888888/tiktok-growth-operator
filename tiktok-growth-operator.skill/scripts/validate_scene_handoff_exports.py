from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from production_spec_handoff import generator_branch_payload
from scene03_creation_matrix import build_creation_matrix_payload, write_scene03_creation_matrix
from text_normalization import read_json_file


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def fixture_capture_root(name: str) -> Path:
    return skill_root() / "testdata" / "validation" / "captures" / name


def load_ranked_videos(capture_root: Path) -> list[dict]:
    for name in ("aggregate_ranked_videos.json", "ranked_videos.json"):
        path = capture_root / name
        if path.exists():
            payload = read_json_file(path)
            if isinstance(payload, list):
                return payload
    raise FileNotFoundError(f"no ranked video list under {capture_root}")


def import_scene(capture_root: Path, scene_id: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        str(skill_root() / "scripts" / "import_tiktok_capture_pack.py"),
        "--capture-root",
        str(capture_root),
        "--scene",
        scene_id,
        "--project",
        "Scene Handoff Export Validation",
        "--output",
        str(output_dir / f"scene-{scene_id}.json"),
    ]
    completed = subprocess.run(command, text=True, capture_output=True, encoding="utf-8", check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr or completed.stdout or f"scene {scene_id} import failed")
    candidates = sorted(output_dir.glob(f"scene-{scene_id}*.json"), key=lambda item: item.stat().st_mtime, reverse=True)
    if not candidates:
        raise RuntimeError(f"scene {scene_id} report not found")
    return candidates[0]


def validate_scene01_board(capture_root: Path) -> dict:
    ranked = load_ranked_videos(capture_root)
    report = read_json_file(import_scene(capture_root, "01", skill_root() / "testdata" / "validation" / "reports" / "_handoff_validation" / "scene-01"))
    if not (capture_root / "collection_board.json").exists():
        raise RuntimeError("collection_board.json missing after scene 01 import")
    if not (capture_root / "collection_board.xlsx").exists():
        raise RuntimeError("collection_board.xlsx missing after scene 01 import")
    board = read_json_file(capture_root / "collection_board.json")
    if board.get("row_count", 0) < len(ranked):
        raise RuntimeError("collection board row_count smaller than ranked list")
    if not report.get("collection_board"):
        raise RuntimeError("scene 01 report missing collection_board payload")
    return {"rows": board.get("row_count"), "headers": len(board.get("headers") or [])}


def validate_scene03_matrix(capture_root: Path) -> dict:
    ranked = load_ranked_videos(capture_root)
    matrix_path = capture_root / "scene03_creation_matrix.json"
    if not matrix_path.exists():
        write_scene03_creation_matrix(capture_root, ranked[:3])
    payload = build_creation_matrix_payload(ranked[:3])
    if not payload.get("matrix_rows"):
        raise RuntimeError("scene03 creation matrix rows missing")
    report = read_json_file(import_scene(capture_root, "03", skill_root() / "testdata" / "validation" / "reports" / "_handoff_validation" / "scene-03"))
    matrix = report.get("creation_matrix") or {}
    if not matrix.get("matrix_rows"):
        raise RuntimeError("scene 03 report missing creation_matrix")
    reusable = next((section for section in report.get("sections", []) if section.get("heading") == "Reusable Formula"), {})
    if "创作就绪" not in json.dumps(reusable, ensure_ascii=False):
        raise RuntimeError("scene 03 reusable formula section missing creation-ready matrix title")
    return {"matrix_rows": len(matrix.get("matrix_rows") or []), "creation_ready": payload.get("creation_ready")}


def validate_production_handoff(capture_root: Path, scene_id: str) -> dict:
    handoff_path = capture_root / "production_spec_handoff.json"
    if not handoff_path.exists():
        import_scene(capture_root, scene_id, skill_root() / "testdata" / "validation" / "reports" / "_handoff_validation" / f"scene-{scene_id}")
    if not handoff_path.exists():
        raise RuntimeError(f"production_spec_handoff.json missing for scene {scene_id}")
    pack = read_json_file(handoff_path)
    branches = pack.get("generator_branches") or {}
    for branch in ("sora", "veo", "i2v"):
        if branch not in branches:
            raise RuntimeError(f"scene {scene_id} handoff missing generator branch: {branch}")
    if not pack.get("shot_list"):
        raise RuntimeError(f"scene {scene_id} handoff missing shot_list")
    report = read_json_file(import_scene(capture_root, scene_id, skill_root() / "testdata" / "validation" / "reports" / "_handoff_validation" / f"scene-{scene_id}-report"))
    if not report.get("production_handoff"):
        raise RuntimeError(f"scene {scene_id} report missing production_handoff payload")
    ranked = load_ranked_videos(capture_root)
    smoke = generator_branch_payload(ranked[0], scene_id=scene_id)
    if smoke.get("schema_version") != "production-spec-handoff-v1":
        raise RuntimeError("unexpected production handoff schema version")
    return {"branches": list(branches.keys()), "shots": len(pack.get("shot_list") or [])}


def main() -> None:
    capture_root = fixture_capture_root("scene01-strong-inputs-pass")
    results = {
        "scene01_board": validate_scene01_board(capture_root),
        "scene03_matrix": validate_scene03_matrix(capture_root),
        "scene04_handoff": validate_production_handoff(capture_root, "04"),
        "scene05_handoff": validate_production_handoff(capture_root, "05"),
    }
    print(json.dumps({"ok": True, "results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1) from exc
