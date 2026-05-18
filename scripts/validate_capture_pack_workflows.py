from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from validator_runtime import create_validator_runtime


def assert_history_dedup(summary_stdout: str, project_root: Path) -> None:
    payload = json.loads(summary_stdout)
    matching = [item for item in payload.get("entries", []) if item.get("root") == str(project_root)]
    if len(matching) != 1:
        raise RuntimeError(
            f"Run history dedup regression: expected exactly 1 entry for {project_root}, got {len(matching)}."
        )


def assert_scene02_to_scene03_handoff(scene02_run_root: Path) -> None:
    manifest_path = scene02_run_root / "run_manifest.json"
    if not manifest_path.exists():
        raise RuntimeError(f"Scene 02 handoff regression: missing run manifest at {manifest_path}.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    chained_runs = manifest.get("chained_runs") or []
    if not chained_runs:
        raise RuntimeError("Scene 02 handoff regression: expected chained Scene 03 run, got none.")
    first = chained_runs[0]
    if first.get("trigger") != "scene02_patrol_handoff":
        raise RuntimeError(f"Scene 02 handoff regression: unexpected trigger {first.get('trigger')!r}.")
    report_json = Path(first.get("report_json", ""))
    if not report_json.exists():
        raise RuntimeError(f"Scene 02 handoff regression: missing chained Scene 03 report {report_json}.")
    report = json.loads(report_json.read_text(encoding="utf-8"))
    executive = next((sec for sec in report.get("sections", []) if sec.get("heading") == "Executive Conclusion"), None)
    if not executive:
        raise RuntimeError("Scene 02 handoff regression: chained Scene 03 report missing Executive Conclusion section.")
    joined = "\n".join(executive.get("paragraphs", []))
    if "短名单规则：" not in joined:
        raise RuntimeError("Scene 02 handoff regression: chained Scene 03 report missing shortlist-rule paragraph.")


def assert_scene03_creation_matrix(capture_root: Path, scene03_report_json: Path | None = None) -> None:
    matrix_path = capture_root / "scene03_creation_matrix.json"
    if not matrix_path.exists():
        raise RuntimeError(f"Scene 03 regression: missing {matrix_path}")
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    if not matrix.get("matrix_rows"):
        raise RuntimeError("Scene 03 regression: creation matrix has no matrix_rows")
    if scene03_report_json and scene03_report_json.exists():
        report = json.loads(scene03_report_json.read_text(encoding="utf-8"))
        embedded = report.get("creation_matrix") or {}
        if not embedded.get("matrix_rows"):
            raise RuntimeError("Scene 03 regression: report missing creation_matrix.matrix_rows")


def assert_weekly_baseline_artifact(capture_root: Path) -> None:
    path = capture_root / "weekly_baseline_delta.json"
    if not path.exists():
        raise RuntimeError(f"Scene 18/19 regression: missing {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    mode = str(payload.get("mode") or "").strip()
    if mode not in {"baseline", "compare", "none"}:
        raise RuntimeError(f"Scene 18/19 regression: unexpected weekly baseline mode {mode!r}")


def assert_scene06_structured_board(scene06_report_json: Path) -> None:
    if not scene06_report_json.exists():
        raise RuntimeError(f"Scene 06 regression: missing report {scene06_report_json}.")
    report = json.loads(scene06_report_json.read_text(encoding="utf-8"))
    board = report.get("competitor_product_board") or {}
    mode = board.get("data_source_mode")
    if mode != "tiktok_shop_structured":
        raise RuntimeError(f"Scene 06 regression: expected tiktok_shop_structured, got {mode!r}.")
    rows = board.get("rows") or []
    if len(rows) < 2:
        raise RuntimeError(f"Scene 06 regression: expected at least 2 competitor rows, got {len(rows)}.")


def assert_operator_schedule(report_json: Path, scene_id: str, *, capture_root: Path) -> None:
    if not report_json.exists():
        raise RuntimeError(f"Scene {scene_id} P1: missing report {report_json}")
    report = json.loads(report_json.read_text(encoding="utf-8"))
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
    artifact = capture_root / f"operator_schedule_scene_{scene_id.lstrip('0') or scene_id}.json"
    if not artifact.exists():
        raise RuntimeError(f"Scene {scene_id} P1: missing {artifact.name} under {capture_root}")


def resolve_capture_pack_report(run_root: Path, scene_id: str) -> Path:
    manifest_path = run_root / "run_manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        report_json = Path(str(manifest.get("report_json") or ""))
        if report_json.exists():
            return report_json
    scene_dir = run_root / f"scene-{scene_id}"
    candidates = sorted(scene_dir.glob(f"scene-{scene_id}*.json"), key=lambda item: item.stat().st_mtime, reverse=True)
    if not candidates:
        raise RuntimeError(f"Scene {scene_id} regression: no report json under {run_root}")
    return candidates[0]


def assert_scene01_handoff_state(scene01_report_json: Path, *, should_allow: bool) -> None:
    if not scene01_report_json.exists():
        raise RuntimeError(f"Scene 01 gate regression: missing report {scene01_report_json}.")
    report = json.loads(scene01_report_json.read_text(encoding="utf-8"))
    sections = {sec.get("heading"): sec for sec in report.get("sections", [])}
    joined = []
    for heading in ("Executive Conclusion", "Why They Matter", "Next Action"):
        sec = sections.get(heading) or {}
        joined.extend(sec.get("paragraphs", []))
        joined.extend(sec.get("bullets", []))
    text = "\n".join(joined)
    if should_allow:
        if "可以直接交接 Scene 03" not in text:
            raise RuntimeError("Scene 01 gate regression: expected allow-handoff state, but allow text was missing.")
        if "暂不建议直接全量交接 Scene 03" in text:
            raise RuntimeError("Scene 01 gate regression: allow fixture still rendered blocking text.")
    else:
        if "暂不建议直接全量交接 Scene 03" not in text:
            raise RuntimeError("Scene 01 gate regression: expected blocking state, but blocking text was missing.")


SCRIPTS = [
    "import_tiktok_capture_pack.py",
    "start_capture_pack_run.py",
    "run_operator_workflow.py",
    "batch_run_operator_workflows.py",
    "start_project_workflow.py",
    "summarize_run_history.py",
    "run_scene02_patrol.py",
    "run_tikmatrix_single_video_scene.py",
    "seed_scene06_competitor_products.py",
    "run_scene06.py",
    "seed_scene02_patrol_pack.py",
    "run_scene0203.py",
    "run_scene1819.py",
    "validate_scene_ops.py",
    "tiktok_shop_official_client.py",
    "tiktok_shop_official_gateway.py",
    "run_shop_gateway.py",
    "tiktok_shop_partner_client.py",
]


def run(command: list[str]) -> dict:
    completed = subprocess.run(command, text=True, capture_output=True)
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validation_fixture_root(skill_root: Path) -> Path:
    return skill_root / "testdata" / "validation"


def resolve_fixture_path(*candidates: Path) -> Path:
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise SystemExit(f"Missing required validation fixture. Checked: {[str(candidate) for candidate in candidates]}")


def main() -> None:
    skill_root = Path(__file__).resolve().parents[1]
    scripts_root = skill_root / "scripts"
    fixture_root = validation_fixture_root(skill_root)
    runtime_root = create_validator_runtime(skill_root, "capture")
    tikmatrix_fixture_root = fixture_root / "tikmatrix"
    capture_comment = resolve_fixture_path(
        fixture_root / "captures" / "tiktok-download-validated-20260423",
        skill_root.parent / "captures" / "tiktok-download-validated-20260423",
    )
    capture_ranked = resolve_fixture_path(
        fixture_root / "captures" / "tiktok-analysis-pack-smoke-20260423f",
        skill_root.parent / "captures" / "tiktok-analysis-pack-smoke-20260423f",
    )
    capture_scene01_pass = resolve_fixture_path(
        fixture_root / "captures" / "scene01-strong-inputs-pass",
    )
    capture_multiweek = resolve_fixture_path(
        fixture_root / "captures" / "scene18-19-multi-week-account",
    )
    capture_scene18_matrix = resolve_fixture_path(
        fixture_root / "captures" / "scene18-matrix-multi-account",
    )
    capture_scene08_home_goods = resolve_fixture_path(
        fixture_root / "captures" / "scene08-multi-product-home-goods-comments",
    )
    capture_scene19_roi = resolve_fixture_path(
        fixture_root / "captures" / "scene19-roi-multiwindow-account",
    )
    patrol_capture_pack = resolve_fixture_path(
        fixture_root / "capture-packs" / "scene02-patrol-capture-pack",
        skill_root / "tmp" / "20260507_validation_capture_scene02" / "capture-pack",
    )
    patrol_query_root = resolve_fixture_path(
        tikmatrix_fixture_root / "search-live-orange-cat",
        Path(r"E:\tiktok\TikMatrix\tmp\search-live-orange-cat"),
    )
    patrol_topic_root = resolve_fixture_path(
        tikmatrix_fixture_root / "topic-live-orangecat",
        Path(r"E:\tiktok\TikMatrix\tmp\topic-live-orangecat"),
    )

    results = []
    for script_name in SCRIPTS:
        results.append(run([sys.executable, "-m", "py_compile", str(scripts_root / script_name)]))

    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "run_scene02_patrol.py"),
                "--name",
                "validation-scene02-patrol",
                "--project",
                "TikTok Validation Scene 02 Patrol",
                "--category",
                "Orange Cat",
                "--market",
                "US",
                "--mode",
                "mixed",
                "--queries",
                "orange cat",
                "--topics",
                "orangecat",
                "--query-root",
                str(patrol_query_root),
                "--topic-root",
                str(patrol_topic_root),
                "--skip-live",
                "--formats",
                "md",
                "--output-root",
                str(runtime_root / "scene02_patrol"),
            ]
        )
    )

    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "start_capture_pack_run.py"),
                "--scene",
                "02",
                "--capture-root",
                str(patrol_capture_pack),
                "--name",
                "validation-scene02-capture",
                "--project",
                "TikTok Validation Scene 02 Capture",
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--output-root",
                str(runtime_root / "scene02_capture"),
                "--formats",
                "md",
            ]
        )
    )
    scene02_capture_idx = len(results) - 1
    if results[scene02_capture_idx]["returncode"] == 0:
        scene02_capture_root = runtime_root / "scene02_capture"
        assert_scene02_to_scene03_handoff(scene02_capture_root)
        scene02_report = resolve_capture_pack_report(scene02_capture_root, "02")
        assert_operator_schedule(scene02_report, "02", capture_root=patrol_capture_pack)
        manifest = json.loads((scene02_capture_root / "run_manifest.json").read_text(encoding="utf-8"))
        chained = manifest.get("chained_runs") or []
        scene03_report = Path(chained[0].get("report_json", "")) if chained else None
        assert_scene03_creation_matrix(patrol_capture_pack, scene03_report)
        if scene03_report and scene03_report.exists():
            assert_operator_schedule(scene03_report, "03", capture_root=patrol_capture_pack)
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "start_capture_pack_run.py"),
                "--scene",
                "01",
                "--capture-root",
                str(capture_scene01_pass),
                "--name",
                "validation-scene01-allow-handoff",
                "--project",
                "TikTok Validation Scene 01 Allow Handoff",
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--output-root",
                str(runtime_root / "scene01_allow_handoff"),
                "--formats",
                "md",
            ]
        )
    )
    if results[-1]["returncode"] == 0:
        scene01_run = runtime_root / "scene01_allow_handoff"
        scene01_report = resolve_capture_pack_report(scene01_run, "01")
        assert_scene01_handoff_state(scene01_report, should_allow=True)
        assert_operator_schedule(scene01_report, "01", capture_root=capture_scene01_pass)
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "run_scene06.py"),
                "--capture-root",
                str(capture_scene01_pass),
                "--name",
                "validation-scene06-structured",
                "--project",
                "TikTok Validation Scene 06 Structured",
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--data-path",
                "structured",
                "--seed-mode",
                "fixture",
                "--force-seed",
                "--formats",
                "md",
                "--output-root",
                str(runtime_root / "scene06_structured"),
            ]
        )
    )
    if results[-1]["returncode"] == 0:
        scene06_run = runtime_root / "scene06_structured"
        scene06_report = resolve_capture_pack_report(scene06_run, "06")
        assert_scene06_structured_board(scene06_report)
        assert_operator_schedule(scene06_report, "06", capture_root=capture_scene01_pass)
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "run_scene0203.py"),
                "--source",
                "fixture",
                "--name",
                "validation-scene0203-bundle",
                "--project",
                "TikTok Validation Scene 02-03 Bundle",
                "--formats",
                "md",
                "--output-root",
                str(runtime_root / "scene0203_bundle"),
            ]
        )
    )
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "start_capture_pack_run.py"),
                "--scene",
                "19",
                "--capture-root",
                str(capture_scene19_roi),
                "--name",
                "validation-scene19-roi-multiwindow",
                "--project",
                "TikTok Validation Scene 19 ROI Multiwindow",
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--output-root",
                str(runtime_root / "scene19_roi_multiwindow"),
                "--formats",
                "md",
            ]
        )
    )
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "start_capture_pack_run.py"),
                "--scene",
                "08",
                "--capture-root",
                str(capture_scene08_home_goods),
                "--name",
                "validation-scene08-home-goods",
                "--project",
                "TikTok Validation Scene 08 Home Goods",
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--output-root",
                str(runtime_root / "scene08_home_goods"),
                "--formats",
                "md",
            ]
        )
    )
    if results[-1]["returncode"] == 0:
        scene08_report = resolve_capture_pack_report(runtime_root / "scene08_home_goods", "08")
        assert_operator_schedule(scene08_report, "08", capture_root=capture_scene08_home_goods)
        action_section = next(
            (sec for sec in json.loads(scene08_report.read_text(encoding="utf-8")).get("sections", []) if sec.get("heading") == "Recommended Action"),
            {},
        )
        action_blob = json.dumps(action_section, ensure_ascii=False)
        if "定位话术" not in action_blob and "异议处理" not in action_blob:
            raise RuntimeError("Scene 08 P1: missing positioning bridge rows")
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "start_capture_pack_run.py"),
                "--scene",
                "18",
                "--capture-root",
                str(capture_scene18_matrix),
                "--name",
                "validation-scene18-matrix",
                "--project",
                "TikTok Validation Scene 18 Matrix",
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--output-root",
                str(runtime_root / "scene18_matrix"),
                "--formats",
                "md",
            ]
        )
    )
    if results[-1]["returncode"] == 0:
        scene18_matrix_report = resolve_capture_pack_report(runtime_root / "scene18_matrix", "18")
        assert_operator_schedule(scene18_matrix_report, "18", capture_root=capture_scene18_matrix)
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "start_capture_pack_run.py"),
                "--scene",
                "18",
                "--capture-root",
                str(capture_multiweek),
                "--name",
                "validation-scene18-multiweek",
                "--project",
                "TikTok Validation Scene 18 Multiweek",
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--output-root",
                str(runtime_root / "scene18_multiweek"),
                "--formats",
                "md",
            ]
        )
    )
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "start_capture_pack_run.py"),
                "--scene",
                "19",
                "--capture-root",
                str(capture_multiweek),
                "--name",
                "validation-scene19-multiweek",
                "--project",
                "TikTok Validation Scene 19 Multiweek",
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--output-root",
                str(runtime_root / "scene19_multiweek"),
                "--formats",
                "md",
            ]
        )
    )
    scene19_multiweek_idx = len(results) - 1
    if results[scene19_multiweek_idx]["returncode"] == 0:
        assert_weekly_baseline_artifact(capture_multiweek)
        scene19_report = resolve_capture_pack_report(runtime_root / "scene19_multiweek", "19")
        assert_operator_schedule(scene19_report, "19", capture_root=capture_multiweek)
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "run_scene1819.py"),
                "--preset",
                "multiweek",
                "--name",
                "validation-scene1819-bundle",
                "--formats",
                "md",
                "--output-root",
                str(runtime_root / "scene1819_bundle"),
            ]
        )
    )
    if results[-1]["returncode"] == 0:
        assert_weekly_baseline_artifact(capture_multiweek)
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "run_tikmatrix_single_video_scene.py"),
                "--url",
                "https://www.tiktok.com/@honmaggie/video/7618153785013194014",
                "--collect-json",
                str(
                    resolve_fixture_path(
                        tikmatrix_fixture_root / "single-video-collect" / "7618153785013194014.json",
                        Path(r"E:\tiktok\TikMatrix\tmp\acceptance-skill-download\7618153785013194014.json"),
                    )
                ),
                "--scene",
                "04",
                "--name",
                "validation-scene04-single-video",
                "--project",
                "TikTok Validation Scene 04 Single Video",
                "--output-root",
                str(runtime_root / "scene04_single_video"),
            ]
        )
    )
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "start_capture_pack_run.py"),
                "--scene",
                "04",
                "--capture-root",
                str(capture_ranked),
                "--name",
                "validation-scene04-capture",
                "--project",
                "TikTok Validation Scene 04 Capture",
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--output-root",
                str(runtime_root / "scene04_capture"),
                "--formats",
                "md",
            ]
        )
    )
    scene04_capture_idx = len(results) - 1
    if results[scene04_capture_idx]["returncode"] == 0:
        scene04_report = resolve_capture_pack_report(runtime_root / "scene04_capture", "04")
        assert_operator_schedule(scene04_report, "04", capture_root=capture_ranked)
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "start_capture_pack_run.py"),
                "--scene",
                "05",
                "--capture-root",
                str(capture_ranked),
                "--name",
                "validation-scene05-capture",
                "--project",
                "TikTok Validation Scene 05 Capture",
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--output-root",
                str(runtime_root / "scene05_capture"),
                "--formats",
                "md",
            ]
        )
    )
    scene05_capture_idx = len(results) - 1
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "start_capture_pack_run.py"),
                "--scene",
                "auto",
                "--capture-root",
                str(capture_comment),
                "--name",
                "validation-auto-capture",
                "--project",
                "TikTok Validation Auto Capture",
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--output-root",
                str(runtime_root / "scene_auto_capture"),
            ]
        )
    )
    if results[scene05_capture_idx]["returncode"] == 0:
        scene05_report = resolve_capture_pack_report(runtime_root / "scene05_capture", "05")
        assert_operator_schedule(scene05_report, "05", capture_root=capture_ranked)
        blob = json.dumps(json.loads(scene05_report.read_text(encoding="utf-8")), ensure_ascii=False)
        if "Generator 分支" not in blob and "sora" not in blob.lower():
            raise RuntimeError("Scene 05 P1: missing generator branch rows in report")
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "run_operator_workflow.py"),
                "--mode",
                "capture-pack",
                "--scene",
                "17",
                "--capture-root",
                str(capture_ranked),
                "--name",
                "validation-routed-capture",
                "--project",
                "TikTok Validation Routed Capture",
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--output-root",
                str(runtime_root / "scene17_routed_capture"),
                "--formats",
                "md",
            ]
        )
    )
    scene17_capture_idx = len(results) - 1
    if results[scene17_capture_idx]["returncode"] == 0:
        scene17_report = resolve_capture_pack_report(runtime_root / "scene17_routed_capture", "17")
        assert_operator_schedule(scene17_report, "17", capture_root=capture_ranked)
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "generate_operator_pack.py"),
                "--type",
                "creative-production-handoff",
                "--source-report",
                str(
                    resolve_fixture_path(
                        fixture_root / "reports" / "scene-15-validation-scene15-capture.json",
                        skill_root / "tmp" / "20260504_validation_capture_scene15" / "scene-15" / "scene-15-validation-scene15-capture.json",
                    )
                ),
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--output-dir",
                str(runtime_root / "creative_handoff_pack"),
            ]
        )
    )
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "start_capture_pack_run.py"),
                "--scene",
                "07",
                "--capture-root",
                str(capture_ranked),
                "--name",
                "validation-scene07-capture",
                "--project",
                "TikTok Validation Scene 07 Capture",
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--output-root",
                str(runtime_root / "scene07_capture"),
                "--formats",
                "md",
            ]
        )
    )
    if results[-1]["returncode"] == 0:
        scene07_report = resolve_capture_pack_report(runtime_root / "scene07_capture", "07")
        assert_operator_schedule(scene07_report, "07", capture_root=capture_ranked)
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "start_capture_pack_run.py"),
                "--scene",
                "09",
                "--capture-root",
                str(capture_ranked),
                "--name",
                "validation-scene09-capture",
                "--project",
                "TikTok Validation Scene 09 Capture",
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--output-root",
                str(runtime_root / "scene09_capture"),
                "--formats",
                "md",
            ]
        )
    )
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "start_capture_pack_run.py"),
                "--scene",
                "10",
                "--capture-root",
                str(capture_ranked),
                "--name",
                "validation-scene10-capture",
                "--project",
                "TikTok Validation Scene 10 Capture",
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--output-root",
                str(runtime_root / "scene10_capture"),
                "--formats",
                "md",
            ]
        )
    )
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "start_capture_pack_run.py"),
                "--scene",
                "15",
                "--capture-root",
                str(capture_ranked),
                "--target-languages",
                "English,Japanese,German",
                "--name",
                "validation-scene15-capture",
                "--project",
                "TikTok Validation Scene 15 Capture",
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--output-root",
                str(runtime_root / "scene15_capture"),
                "--formats",
                "md",
            ]
        )
    )
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "start_capture_pack_run.py"),
                "--scene",
                "13",
                "--capture-root",
                str(capture_ranked),
                "--target-markets",
                "US,Japan,Germany",
                "--name",
                "validation-scene13-capture",
                "--project",
                "TikTok Validation Scene 13 Capture",
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--output-root",
                str(runtime_root / "scene13_capture"),
                "--formats",
                "md",
            ]
        )
    )
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "start_capture_pack_run.py"),
                "--scene",
                "16",
                "--capture-root",
                str(capture_ranked),
                "--name",
                "validation-scene16-capture",
                "--project",
                "TikTok Validation Scene 16 Capture",
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--output-root",
                str(runtime_root / "scene16_capture"),
                "--formats",
                "md",
            ]
        )
    )
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "start_capture_pack_run.py"),
                "--scene",
                "11",
                "--capture-root",
                str(capture_ranked),
                "--name",
                "validation-scene11-capture",
                "--project",
                "TikTok Validation Scene 11 Capture",
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--output-root",
                str(runtime_root / "scene11_capture"),
                "--formats",
                "md",
            ]
        )
    )
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "start_capture_pack_run.py"),
                "--scene",
                "12",
                "--capture-root",
                str(capture_ranked),
                "--name",
                "validation-scene12-capture",
                "--project",
                "TikTok Validation Scene 12 Capture",
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--output-root",
                str(runtime_root / "scene12_capture"),
                "--formats",
                "md",
            ]
        )
    )
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "start_capture_pack_run.py"),
                "--scene",
                "14",
                "--capture-root",
                str(capture_ranked),
                "--name",
                "validation-scene14-capture",
                "--project",
                "TikTok Validation Scene 14 Capture",
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--output-root",
                str(runtime_root / "scene14_capture"),
                "--formats",
                "md",
            ]
        )
    )
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "run_operator_workflow.py"),
                "--mode",
                "history",
                "--history-output-json",
                str(runtime_root / "validation_run_history_unified.json"),
                "--history-output-md",
                str(runtime_root / "validation_run_history_unified.md"),
                "--history-limit",
                "20",
                "--history-root",
                str(runtime_root),
            ]
        )
    )
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "summarize_run_history.py"),
                "--output-json",
                str(runtime_root / "validation_run_history.json"),
                "--output-md",
                str(runtime_root / "validation_run_history.md"),
                "--limit",
                "20",
                "--root",
                str(runtime_root),
            ]
        )
    )

    project_launcher_root = runtime_root / "project_launcher_dedup_fixture"
    project_launcher_root.mkdir(parents=True, exist_ok=True)
    write_json(
        project_launcher_root / "project_manifest.json",
        {
            "created_at": "2026-05-08T02:00:00",
            "name": "validate-project-dedup",
            "project": "Validate Project Dedup",
            "resolved_mode": "goal",
            "route": {"resolved_mode": "goal", "capture_root": ""},
            "result": {
                "report_json": "",
                "operator_packs": [],
            },
        },
    )
    write_json(
        project_launcher_root / "run_manifest.json",
        {
            "created_at": "2026-05-08T02:00:01",
            "name": "validate-project-dedup-run",
            "project": "Validate Project Dedup",
            "capture_root": "",
            "report_json": "",
            "operator_packs": [],
        },
    )
    dedup_check = run(
        [
            sys.executable,
            str(scripts_root / "summarize_run_history.py"),
            "--root",
            str(project_launcher_root),
            "--limit",
            "10",
        ]
    )
    try:
        assert_history_dedup(dedup_check["stdout"], project_launcher_root)
    except BaseException as exc:  # noqa: BLE001
        dedup_check["returncode"] = 1
        dedup_check["stderr"] = str(exc)
    results.append(dedup_check)

    py_compile_failures = [
        item
        for item in results
        if item["command"][1:3] == ["-m", "py_compile"] and item["returncode"] != 0 and "拒绝访问" not in item["stderr"]
    ]
    runtime_failures = [
        item
        for item in results
        if not (item["command"][1:3] == ["-m", "py_compile"]) and item["returncode"] != 0
    ]
    payload = {
        "success": not py_compile_failures and not runtime_failures,
        "results": results,
        "notes": [
            "Windows py_compile can hit transient __pycache__ file-lock races; those are reported but not treated as code failures if runtime checks pass."
        ],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
