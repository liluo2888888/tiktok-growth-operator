from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from asset_library import library_path, load_library, sync_asset_library
from feishu_delivery_adapter import plan_board_append, plan_structured_board_append
from generation_jobs import artifact_manifest_path, create_generation_job, poll_generation_job
from project_space import init_project_space, load_project_space
from text_normalization import read_json_file, write_json_file


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def fixture_capture_root() -> Path:
    return skill_root() / "testdata" / "validation" / "captures" / "scene01-strong-inputs-pass"


def import_scene(scene_id: str, output_dir: Path, *, capture_root: Path | None = None) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        str(skill_root() / "scripts" / "import_tiktok_capture_pack.py"),
        "--capture-root",
        str(capture_root or fixture_capture_root()),
        "--scene",
        scene_id,
        "--project",
        "Platform P0 Validation",
        "--output",
        str(output_dir / f"scene-{scene_id}.json"),
    ]
    completed = subprocess.run(command, text=True, capture_output=True, encoding="utf-8", check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr or completed.stdout or f"scene {scene_id} import failed")
    candidates = sorted(output_dir.glob(f"scene-{scene_id}*.json"), key=lambda item: item.stat().st_mtime, reverse=True)
    if not candidates:
        raise RuntimeError(f"scene {scene_id} report missing")
    return candidates[0]


def validate_scene06() -> dict:
    capture_root = fixture_capture_root()
    report_path = import_scene("06", skill_root() / "testdata" / "validation" / "reports" / "_platform_p0" / "scene-06")
    report = read_json_file(report_path)
    board_path = capture_root / "competitor_product_board.json"
    if not board_path.exists():
        raise RuntimeError("competitor_product_board.json missing")
    board = read_json_file(board_path)
    if board.get("data_source_mode") != "tiktok_shop_structured":
        raise RuntimeError(f"unexpected scene06 data mode: {board.get('data_source_mode')}")
    if not report.get("competitor_product_board"):
        raise RuntimeError("scene 06 report missing competitor_product_board payload")
    return {"rows": board.get("row_count"), "mode": board.get("data_source_mode")}


def validate_generation_jobs() -> dict:
    capture_root = fixture_capture_root()
    report_path = import_scene("09", skill_root() / "testdata" / "validation" / "reports" / "_platform_p0" / "scene-09")
    report = read_json_file(report_path)
    handoff = report.get("generation_handoff") or {}
    if not handoff.get("job_id"):
        raise RuntimeError("scene 09 missing generation_handoff.job_id")
    job = poll_generation_job(capture_root, handoff["job_id"])
    manifest = artifact_manifest_path(capture_root, handoff["job_id"])
    manifest.parent.mkdir(parents=True, exist_ok=True)
    write_json_file(manifest, {"artifact_links": ["https://example.com/generated-preview.mp4"]})
    job = poll_generation_job(capture_root, handoff["job_id"])
    if job.get("status") != "succeeded":
        raise RuntimeError("generation job poll did not mark succeeded after artifacts manifest")
    return {"job_id": handoff["job_id"], "status": job.get("status")}


def validate_asset_library() -> dict:
    capture_root = fixture_capture_root()
    ranked = read_json_file(capture_root / "aggregate_ranked_videos.json")
    profile = read_json_file(capture_root / "profile_summary.json")
    library = sync_asset_library(capture_root, ranked_videos=ranked, profile_summary=profile, scene_id="01")
    if not library.get("assets"):
        raise RuntimeError("asset library has no assets")
    if not library_path(capture_root).exists():
        raise RuntimeError("asset_library.json missing")
    return {"asset_count": len(library.get("assets") or [])}


def validate_project_space() -> dict:
    import tempfile

    with tempfile.TemporaryDirectory(prefix="tgo-project-space-") as temp_dir:
        root = Path(temp_dir) / "demo-project"
        root.mkdir(parents=True, exist_ok=True)
        init_project_space(root, name="demo", project="Platform P0", request="测试项目空间", mode="scene")
        manifest = load_project_space(root)
        if not manifest or len(manifest.get("steps") or []) != 3:
            raise RuntimeError("project_space steps incomplete")
        roles = [step.get("role_id") for step in manifest.get("steps") or []]
        if roles != ["creative_director", "writer_screenwriter", "director_execution"]:
            raise RuntimeError(f"unexpected project_space roles: {roles}")
    return {"roles": 3}


def validate_feishu_append_plan() -> dict:
    capture_root = fixture_capture_root()
    report_path = import_scene("01", skill_root() / "testdata" / "validation" / "reports" / "_platform_p0" / "scene-01")
    report = read_json_file(report_path)
    plan = plan_board_append(report, run_date="2026-05-17", append_scope="validation-batch")
    if plan.get("status") != "planned":
        raise RuntimeError(f"feishu append plan failed: {plan}")
    if plan.get("record_count", 0) < 1:
        raise RuntimeError("feishu append plan has no records")
    if "采集日期" not in (plan.get("headers") or [""])[0]:
        raise RuntimeError("feishu append headers missing run date column")
    return {"record_count": plan.get("record_count"), "headers": len(plan.get("headers") or [])}


def validate_scene18_competitor_weekly_board_plan() -> dict:
    matrix_pack = skill_root() / "testdata" / "validation" / "captures" / "scene18-matrix-multi-account"
    out_dir = skill_root() / "testdata" / "validation" / "reports" / "_platform_p0" / "scene-18"
    report_path = import_scene("18", out_dir, capture_root=matrix_pack)
    report = read_json_file(report_path)
    if not (matrix_pack / "competitor_weekly_board.json").exists():
        raise RuntimeError("scene18 competitor_weekly_board.json missing after import")
    plan = plan_structured_board_append(
        report,
        table_key="scene18_competitor_weekly",
        run_date="2026-05-17",
        append_scope="validation-weekly",
    )
    if plan.get("status") != "planned":
        raise RuntimeError(f"scene18 feishu weekly board plan failed: {plan}")
    if plan.get("record_count", 0) < 1:
        raise RuntimeError("scene18 weekly board plan has no records")
    return {"record_count": plan.get("record_count"), "table_key": plan.get("table_key"), "matrix_mode": report.get("competitor_weekly_board", {}).get("matrix_mode")}


def _assert_board_plan(report: dict, *, table_key: str, min_records: int = 1) -> dict:
    plan = plan_structured_board_append(
        report,
        table_key=table_key,
        run_date="2026-05-17",
        append_scope="validation-board",
    )
    if plan.get("status") != "planned":
        raise RuntimeError(f"feishu board plan failed for {table_key}: {plan}")
    if plan.get("record_count", 0) < min_records:
        raise RuntimeError(f"feishu board plan for {table_key} has no records")
    return {"record_count": plan.get("record_count"), "table_key": table_key}


def validate_scene06_board_plan() -> dict:
    capture_root = fixture_capture_root()
    report_path = import_scene("06", skill_root() / "testdata" / "validation" / "reports" / "_platform_p0" / "scene-06-rerun")
    report = read_json_file(report_path)
    return _assert_board_plan(report, table_key="scene06_competitor_product_board", min_records=2)


def validate_scene07_board_plan() -> dict:
    pack = skill_root() / "testdata" / "validation" / "captures" / "tiktok-analysis-pack-smoke-20260423f"
    report_path = import_scene("07", skill_root() / "testdata" / "validation" / "reports" / "_platform_p0" / "scene-07", capture_root=pack)
    report = read_json_file(report_path)
    if not (pack / "category_entry_board.json").exists():
        raise RuntimeError("scene07 category_entry_board.json missing")
    return _assert_board_plan(report, table_key="scene07_category_entry")


def validate_scene08_board_plan() -> dict:
    pack = skill_root() / "testdata" / "validation" / "captures" / "scene08-multi-product-home-goods-comments"
    report_path = import_scene("08", skill_root() / "testdata" / "validation" / "reports" / "_platform_p0" / "scene-08", capture_root=pack)
    report = read_json_file(report_path)
    if not (pack / "comment_persona_board.json").exists():
        raise RuntimeError("scene08 comment_persona_board.json missing")
    return _assert_board_plan(report, table_key="scene08_comment_persona")


def validate_scene17_board_plan() -> dict:
    pack = skill_root() / "testdata" / "validation" / "captures" / "tiktok-analysis-pack-smoke-20260423f"
    report_path = import_scene("17", skill_root() / "testdata" / "validation" / "reports" / "_platform_p0" / "scene-17", capture_root=pack)
    report = read_json_file(report_path)
    if not (pack / "creator_formula_board.json").exists():
        raise RuntimeError("scene17 creator_formula_board.json missing")
    return _assert_board_plan(report, table_key="scene17_creator_formula")


def validate_scene19_board_plan() -> dict:
    pack = skill_root() / "testdata" / "validation" / "captures" / "scene19-roi-multiwindow-account"
    report_path = import_scene("19", skill_root() / "testdata" / "validation" / "reports" / "_platform_p0" / "scene-19", capture_root=pack)
    report = read_json_file(report_path)
    if not (pack / "account_retro_board.json").exists():
        raise RuntimeError("scene19 account_retro_board.json missing")
    return _assert_board_plan(report, table_key="scene19_account_retro")


def validate_scene02_patrol_board_plan() -> dict:
    patrol_pack = skill_root() / "testdata" / "validation" / "capture-packs" / "scene02-patrol-capture-pack"
    out_dir = skill_root() / "testdata" / "validation" / "reports" / "_platform_p0" / "scene-02"
    report_path = import_scene("02", out_dir, capture_root=patrol_pack)
    report = read_json_file(report_path)
    if not (patrol_pack / "patrol_board.json").exists():
        raise RuntimeError("scene02 patrol_board.json missing after import")
    plan = plan_structured_board_append(
        report,
        table_key="scene02_patrol_board",
        run_date="2026-05-17",
        append_scope="validation-patrol",
    )
    if plan.get("status") != "planned":
        raise RuntimeError(f"scene02 feishu patrol board plan failed: {plan}")
    if plan.get("record_count", 0) < 1:
        raise RuntimeError("scene02 patrol board plan has no records")
    return {"record_count": plan.get("record_count"), "table_key": plan.get("table_key")}


def main() -> None:
    results = {
        "scene06": validate_scene06(),
        "generation_jobs": validate_generation_jobs(),
        "asset_library": validate_asset_library(),
        "project_space": validate_project_space(),
        "feishu_append_plan": validate_feishu_append_plan(),
        "scene02_patrol_board_plan": validate_scene02_patrol_board_plan(),
        "scene18_competitor_weekly_board_plan": validate_scene18_competitor_weekly_board_plan(),
        "scene06_board_plan": validate_scene06_board_plan(),
        "scene07_board_plan": validate_scene07_board_plan(),
        "scene08_board_plan": validate_scene08_board_plan(),
        "scene17_board_plan": validate_scene17_board_plan(),
        "scene19_board_plan": validate_scene19_board_plan(),
    }
    print(json.dumps({"ok": True, "results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1) from exc
