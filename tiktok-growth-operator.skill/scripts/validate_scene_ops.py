from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from text_normalization import read_json_file


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def fixture_capture(name: str) -> Path:
    return skill_root() / "testdata" / "validation" / "captures" / name


def fixture_patrol_pack() -> Path:
    return skill_root() / "testdata" / "validation" / "capture-packs" / "scene02-patrol-capture-pack"


def load_ranked_videos(capture_root: Path) -> list[dict]:
    for name in ("aggregate_ranked_videos.json", "ranked_videos.json"):
        path = capture_root / name
        if path.exists():
            payload = read_json_file(path)
            if isinstance(payload, list):
                return [item for item in payload if isinstance(item, dict)]
    raise FileNotFoundError(f"no ranked videos under {capture_root}")


def import_scene_report(capture_root: Path, scene_id: str, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        str(skill_root() / "scripts" / "import_tiktok_capture_pack.py"),
        "--capture-root",
        str(capture_root),
        "--scene",
        scene_id,
        "--project",
        "Scene Ops Validation",
        "--output",
        str(output_dir / f"scene-{scene_id}.json"),
    ]
    completed = subprocess.run(command, text=True, capture_output=True, encoding="utf-8", check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr or completed.stdout or f"scene {scene_id} import failed")
    candidates = sorted(output_dir.glob(f"scene-{scene_id}*.json"), key=lambda item: item.stat().st_mtime, reverse=True)
    if not candidates:
        raise RuntimeError(f"scene {scene_id} report not found under {output_dir}")
    return read_json_file(candidates[0])


def assert_patrol_runtime(capture_root: Path) -> None:
    for name in ("patrol_snapshot.json", "patrol_delta.json", "patrol_alerts.json", "scene03_candidates.json"):
        if not (capture_root / name).exists():
            raise RuntimeError(f"Scene 02 ops: missing {name}")
    candidates = read_json_file(capture_root / "scene03_candidates.json")
    if not isinstance(candidates, list) or not candidates:
        raise RuntimeError("Scene 02 ops: scene03_candidates must be a non-empty list")


def assert_patrol_board(report: dict, capture_root: Path) -> None:
    board = report.get("patrol_board")
    if not isinstance(board, dict) or not board.get("rows"):
        raise RuntimeError("Scene 02 ops: patrol_board missing or empty")
    if board.get("schema_version") != "scene02-patrol-board-v1":
        raise RuntimeError("Scene 02 ops: patrol_board schema_version mismatch")
    path = capture_root / "patrol_board.json"
    if not path.exists():
        raise RuntimeError("Scene 02 ops: patrol_board.json not written to capture root")
    on_disk = read_json_file(path)
    if int(on_disk.get("row_count") or 0) < 1:
        raise RuntimeError("Scene 02 ops: patrol_board.json has no rows")


def assert_operator_schedule(report: dict, scene_id: str, *, capture_root: Path | None = None) -> None:
    schedule = report.get("operator_schedule") or {}
    if schedule.get("schema_version") != "operator-schedule-v1":
        raise RuntimeError(f"Scene {scene_id} P1: operator_schedule missing or wrong schema")
    if not schedule.get("dispatch"):
        raise RuntimeError(f"Scene {scene_id} P1: operator_schedule.dispatch is empty")
    if not schedule.get("next_runs"):
        raise RuntimeError(f"Scene {scene_id} P1: operator_schedule.next_runs is empty")
    feishu = (schedule.get("delivery") or {}).get("feishu") or {}
    if feishu.get("status") != "planned":
        raise RuntimeError(f"Scene {scene_id} P1: feishu delivery not planned")
    if capture_root is not None:
        artifact = capture_root / f"operator_schedule_scene_{scene_id.lstrip('0') or scene_id}.json"
        if not artifact.exists():
            raise RuntimeError(f"Scene {scene_id} P1: missing {artifact.name} under capture root")


def assert_scene03_report(report: dict, *, capture_root: Path | None = None) -> None:
    executive = next((sec for sec in report.get("sections", []) if sec.get("heading") == "Executive Conclusion"), {})
    joined = "\n".join(executive.get("paragraphs", []))
    if "短名单规则：" not in joined:
        raise RuntimeError("Scene 03 ops: missing shortlist-rule paragraph")
    matrix = report.get("creation_matrix") or {}
    if not matrix.get("matrix_rows"):
        raise RuntimeError("Scene 03 ops: report missing creation_matrix.matrix_rows")
    reusable = next((sec for sec in report.get("sections", []) if sec.get("heading") == "Reusable Formula"), {})
    blob = json.dumps(reusable, ensure_ascii=False)
    if "创作就绪" not in blob and "共性规律" not in blob:
        raise RuntimeError("Scene 03 ops: reusable formula section missing matrix guidance")
    next_action = next((sec for sec in report.get("sections", []) if sec.get("heading") == "Next Action"), {})
    handoff_blob = json.dumps(next_action, ensure_ascii=False)
    if "Scene 09" not in handoff_blob and "下游交接" not in handoff_blob:
        raise RuntimeError("Scene 03 P1: missing downstream handoff rows")
    assert_operator_schedule(report, "03", capture_root=capture_root)


def assert_structured_board(
    report: dict,
    capture_root: Path,
    *,
    board_key: str,
    json_name: str,
    table_key: str,
    schema_version: str,
) -> None:
    board = report.get(board_key)
    if not isinstance(board, dict) or not board.get("rows"):
        raise RuntimeError(f"Scene ops: {board_key} missing or empty")
    if board.get("schema_version") != schema_version:
        raise RuntimeError(f"Scene ops: {board_key} schema_version mismatch")
    path = capture_root / json_name
    if not path.exists():
        raise RuntimeError(f"Scene ops: {json_name} not written to capture root")
    feishu_table = ((report.get("operator_schedule") or {}).get("delivery") or {}).get("feishu") or {}
    if feishu_table.get("table_key") != table_key:
        raise RuntimeError(f"Scene ops: expected {table_key}, got {feishu_table.get('table_key')!r}")


def assert_competitor_weekly_board(report: dict, capture_root: Path) -> None:
    assert_structured_board(
        report,
        capture_root,
        board_key="competitor_weekly_board",
        json_name="competitor_weekly_board.json",
        table_key="scene18_competitor_weekly",
        schema_version="scene18-competitor-weekly-board-v1",
    )


def assert_scene18_report(report: dict, *, matrix_expected: bool, capture_root: Path | None = None) -> None:
    executive = next((sec for sec in report.get("sections", []) if sec.get("heading") == "Executive Conclusion"), {})
    joined = "\n".join(executive.get("paragraphs", [])) + "\n".join(executive.get("bullets", []))
    if "证据等级" not in joined:
        raise RuntimeError("Scene 18 ops: missing evidence grade in executive section")
    if matrix_expected and "竞品矩阵" not in joined and "矩阵" not in joined:
        raise RuntimeError("Scene 18 ops: matrix fixture should mention competitor matrix framing")
    next_action = next((sec for sec in report.get("sections", []) if sec.get("heading") == "Next Action"), {})
    rows = (next_action.get("table") or {}).get("rows") or []
    if not rows:
        raise RuntimeError("Scene 18 ops: Next Action dispatch rows missing")
    assert_operator_schedule(report, "18", capture_root=capture_root)


def assert_scene19_report(report: dict, *, capture_root: Path | None = None) -> None:
    executive = next((sec for sec in report.get("sections", []) if sec.get("heading") == "Executive Conclusion"), {})
    joined = "\n".join(executive.get("paragraphs", [])) + "\n".join(executive.get("bullets", []))
    if "证据等级" not in joined:
        raise RuntimeError("Scene 19 ops: missing evidence grade in executive section")
    action_section = next(
        (
            sec
            for sec in report.get("sections", [])
            if sec.get("heading") in {"Next Action", "Recommended Action"}
        ),
        {},
    )
    rows = (action_section.get("table") or {}).get("rows") or []
    if not rows:
        raise RuntimeError("Scene 19 ops: Recommended Action / Next Action rows missing")
    blob = json.dumps(report, ensure_ascii=False)
    if "多做" not in blob and "do-more" not in blob.lower():
        raise RuntimeError("Scene 19 ops: missing do-more / 多做 guidance")
    assert_operator_schedule(report, "19", capture_root=capture_root)


def assert_weekly_baseline_file(capture_root: Path) -> dict:
    path = capture_root / "weekly_baseline_delta.json"
    if not path.exists():
        raise RuntimeError(f"Scene weekly ops: missing {path.name}")
    payload = read_json_file(path)
    if not clean_mode(payload):
        raise RuntimeError("Scene weekly ops: weekly_baseline_delta missing mode")
    return payload


def clean_mode(payload: dict) -> bool:
    return bool(clean_text(payload.get("mode")))


def clean_text(value: object) -> str:
    return str(value or "").strip()


def run_capture_pack_chain(capture_root: Path, scene: str, output_dir: Path) -> dict:
    command = [
        sys.executable,
        str(skill_root() / "scripts" / "start_capture_pack_run.py"),
        "--scene",
        scene,
        "--capture-root",
        str(capture_root),
        "--name",
        f"validate-scene-ops-{scene}",
        "--project",
        "Scene Ops Validation",
        "--platform",
        "TikTok",
        "--market",
        "US",
        "--formats",
        "md",
        "--output-root",
        str(output_dir / f"run-scene-{scene}"),
    ]
    completed = subprocess.run(command, text=True, capture_output=True, encoding="utf-8", check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr or completed.stdout or f"start_capture_pack_run scene {scene} failed")
    run_root = output_dir / f"run-scene-{scene}"
    manifest_path = run_root / "run_manifest.json"
    if not manifest_path.exists():
        raise RuntimeError(f"Scene {scene} ops: missing run manifest at {manifest_path}")
    return read_json_file(manifest_path)


def main() -> None:
    reports_dir = skill_root() / "tmp" / "validate_scene_ops_reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    patrol_pack = fixture_patrol_pack()
    assert_patrol_runtime(patrol_pack)
    load_ranked_videos(patrol_pack)

    scene02_manifest = run_capture_pack_chain(patrol_pack, "02", reports_dir)
    chained = scene02_manifest.get("chained_runs") or []
    if not chained:
        raise RuntimeError("Scene 02 ops: expected chained Scene 03 run")
    if chained[0].get("trigger") != "scene02_patrol_handoff":
        raise RuntimeError(f"Scene 02 ops: unexpected handoff trigger {chained[0].get('trigger')!r}")
    scene03_report_path = Path(chained[0].get("report_json", ""))
    scene03_chained_report = read_json_file(scene03_report_path)
    assert_scene03_report(scene03_chained_report, capture_root=patrol_pack)
    assert_operator_schedule(scene03_chained_report, "02", capture_root=patrol_pack)

    scene03_direct = import_scene_report(patrol_pack, "03", reports_dir / "direct")
    assert_scene03_report(scene03_direct, capture_root=patrol_pack)
    if not (patrol_pack / "scene03_creation_matrix.json").exists():
        raise RuntimeError("Scene 03 ops: scene03_creation_matrix.json not written on import")

    multiweek = fixture_capture("scene18-19-multi-week-account")
    matrix_pack = fixture_capture("scene18-matrix-multi-account")
    roi_pack = fixture_capture("scene19-roi-multiwindow-account")

    run_capture_pack_chain(multiweek, "18", reports_dir)
    run_capture_pack_chain(multiweek, "19", reports_dir)
    assert_weekly_baseline_file(multiweek)

    scene02_report = import_scene_report(patrol_pack, "02", reports_dir / "scene02")
    assert_patrol_board(scene02_report, patrol_pack)
    assert_operator_schedule(scene02_report, "02", capture_root=patrol_pack)
    feishu_table = ((scene02_report.get("operator_schedule") or {}).get("delivery") or {}).get("feishu") or {}
    if feishu_table.get("table_key") != "scene02_patrol_board":
        raise RuntimeError(f"Scene 02 ops: expected scene02_patrol_board, got {feishu_table.get('table_key')!r}")

    scene01_pack = fixture_capture("scene01-strong-inputs-pass")
    scene01_report = import_scene_report(scene01_pack, "01", reports_dir / "scene01")
    assert_operator_schedule(scene01_report, "01", capture_root=scene01_pack)
    assert_structured_board(
        scene01_report,
        scene01_pack,
        board_key="collection_board",
        json_name="collection_board.json",
        table_key="scene01_collection_board",
        schema_version="scene01-collection-board-v1",
    )

    scene06_report = import_scene_report(scene01_pack, "06", reports_dir / "scene06")
    assert_operator_schedule(scene06_report, "06", capture_root=scene01_pack)
    assert_structured_board(
        scene06_report,
        scene01_pack,
        board_key="competitor_product_board",
        json_name="competitor_product_board.json",
        table_key="scene06_competitor_product_board",
        schema_version="competitor-product-board-v1",
    )

    analysis_pack = fixture_capture("tiktok-analysis-pack-smoke-20260423f")
    scene07_report = import_scene_report(analysis_pack, "07", reports_dir / "scene07")
    assert_operator_schedule(scene07_report, "07", capture_root=analysis_pack)
    assert_structured_board(
        scene07_report,
        analysis_pack,
        board_key="category_entry_board",
        json_name="category_entry_board.json",
        table_key="scene07_category_entry",
        schema_version="scene07-category-entry-board-v1",
    )

    scene08_pack = fixture_capture("scene08-multi-product-home-goods-comments")
    scene08_report = import_scene_report(scene08_pack, "08", reports_dir / "scene08")
    assert_operator_schedule(scene08_report, "08", capture_root=scene08_pack)
    assert_structured_board(
        scene08_report,
        scene08_pack,
        board_key="comment_persona_board",
        json_name="comment_persona_board.json",
        table_key="scene08_comment_persona",
        schema_version="scene08-comment-persona-board-v1",
    )
    action_section = next(
        (sec for sec in scene08_report.get("sections", []) if sec.get("heading") == "Recommended Action"),
        {},
    )
    action_blob = json.dumps(action_section, ensure_ascii=False)
    if "定位话术" not in action_blob and "异议处理" not in action_blob:
        raise RuntimeError("Scene 08 P1: missing positioning bridge rows")

    scene18_matrix_report = import_scene_report(matrix_pack, "18", reports_dir / "matrix")
    assert_competitor_weekly_board(scene18_matrix_report, matrix_pack)
    assert_scene18_report(scene18_matrix_report, matrix_expected=True, capture_root=matrix_pack)
    assert_weekly_baseline_file(matrix_pack)

    scene17_report = import_scene_report(analysis_pack, "17", reports_dir / "scene17")
    assert_operator_schedule(scene17_report, "17", capture_root=analysis_pack)
    assert_structured_board(
        scene17_report,
        analysis_pack,
        board_key="creator_formula_board",
        json_name="creator_formula_board.json",
        table_key="scene17_creator_formula",
        schema_version="scene17-creator-formula-board-v1",
    )

    scene19_roi_report = import_scene_report(roi_pack, "19", reports_dir / "roi")
    assert_scene19_report(scene19_roi_report, capture_root=roi_pack)
    assert_structured_board(
        scene19_roi_report,
        roi_pack,
        board_key="account_retro_board",
        json_name="account_retro_board.json",
        table_key="scene19_account_retro",
        schema_version="scene19-account-retro-board-v1",
    )
    assert_weekly_baseline_file(roi_pack)

    print(
        json.dumps(
            {
                "ok": True,
                "patrol_pack": str(patrol_pack),
                "chained_scene03": str(scene03_report_path),
                "fixtures": {
                    "multiweek": str(multiweek),
                    "matrix": str(matrix_pack),
                    "roi": str(roi_pack),
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1) from exc
