from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from feishu_push_runtime import maybe_push_feishu_bundle
from text_normalization import write_json_file, write_utf8_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a real TikTok capture-pack end-to-end into scene-report JSON, rendered outputs, and optional derived operator packs."
    )
    parser.add_argument("--scene", required=True, help="Scene id or slug. Supported by current importer: 01, 02, 03, 04, 05, 07, 08, 09, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, and auto.")
    parser.add_argument("--capture-root", required=True, help="Real TikTok capture-pack directory.")
    parser.add_argument("--name", required=True, help="Short run name.")
    parser.add_argument("--project", required=True, help="Project title.")
    parser.add_argument("--target-markets", default="", help="Optional comma-separated target markets for scene 13 localization blueprints.")
    parser.add_argument("--target-languages", default="", help="Optional comma-separated target languages for scene 15 image-translation blueprints.")
    parser.add_argument("--output-root", default="", help="Optional explicit run root.")
    parser.add_argument("--platform", default="TikTok", help="Platform label for derived packs.")
    parser.add_argument("--market", default="US", help="Market label for derived packs.")
    parser.add_argument(
        "--formats",
        default="md,docx,xlsx",
        help="Comma-separated rendered output formats: md, docx, xlsx.",
    )
    parser.add_argument(
        "--operator-packs",
        default="",
        help="Optional comma-separated operator packs: publish-prep, live-assist, creative-production-handoff, account-ops-assist.",
    )
    parser.add_argument("--push-feishu", action="store_true", help="After generating the run, also push the report to Feishu.")
    parser.add_argument("--feishu-app-id", default="", help="Optional explicit Feishu app ID.")
    parser.add_argument("--feishu-app-secret", default="", help="Optional explicit Feishu app secret.")
    parser.add_argument("--feishu-title", default="", help="Optional explicit Feishu Doc title.")
    parser.add_argument("--feishu-base-name", default="", help="Optional explicit Feishu Bitable app name.")
    return parser.parse_args()


def run_python(script: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        text=True,
        capture_output=True,
        check=True,
    )


def create_run_root(skill_root: Path, scene: str, name: str, output_root: str) -> Path:
    if output_root.strip():
        return Path(output_root).expanduser().resolve()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return skill_root / "tmp" / f"{timestamp}-capture-scene-{scene}-{name}"


def parse_operator_packs(raw: str) -> list[str]:
    allowed = {"publish-prep", "live-assist", "creative-production-handoff", "account-ops-assist"}
    values = [item.strip().lower() for item in raw.split(",") if item.strip()]
    invalid = [item for item in values if item not in allowed]
    if invalid:
        raise SystemExit(f"Unsupported operator pack(s): {', '.join(invalid)}")
    deduped: list[str] = []
    for item in values:
        if item not in deduped:
            deduped.append(item)
    return deduped


def default_operator_packs(scene_id: str) -> list[str]:
    if scene_id == "08":
        return ["live-assist"]
    if scene_id in {"09", "10", "11", "12", "13", "14", "15", "16"}:
        return ["publish-prep", "creative-production-handoff"]
    if scene_id == "17":
        return ["publish-prep"]
    return []


def write_readme(run_root: Path, scene: str, capture_root: Path, report_json: Path, outputs_dir: Path, operator_pack_results: list[dict]) -> None:
    content = f"""# Capture Pack 真实运行

## 输入信息

- 场景：{scene}
- 采集包：`{capture_root}`
- 报告 JSON：`{report_json.name}`
- 输出目录：`{outputs_dir.name}`
"""
    if operator_pack_results:
        content += "\n## 派生的 Operator 交付包\n\n"
        for item in operator_pack_results:
            content += f"- {item['type']}: `{Path(item['output_path']).name}`\n"
    content += """

## 运行流程

1. 先把采集包导入成结构化的 scene-report JSON。
2. 再把报告渲染成 `md/docx/xlsx` 成品。
3. 如有需要，再从已导入的场景报告继续生成 operator 交付包。
"""
    write_utf8_text(run_root / "README.md", content)


def scene02_follow_on_scene03(
    scripts_root: Path,
    run_root: Path,
    capture_root: Path,
    project: str,
    platform: str,
    market: str,
    formats: str,
) -> dict | None:
    scene03_candidates = capture_root / "scene03_candidates.json"
    if not scene03_candidates.exists():
        return None
    try:
        candidates = json.loads(scene03_candidates.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(candidates, list) or not candidates:
        return None

    scene03_run_root = run_root / "scene-03-from-patrol"
    scene03_name = "patrol-scene03-handoff"
    scene03_project = f"{project} - Scene 03 Patrol Handoff"
    scene03_result = run_python(
        scripts_root / "start_capture_pack_run.py",
        [
            "--scene",
            "03",
            "--capture-root",
            str(capture_root),
            "--name",
            scene03_name,
            "--project",
            scene03_project,
            "--platform",
            platform,
            "--market",
            market,
            "--output-root",
            str(scene03_run_root),
            "--formats",
            formats,
        ],
    )
    parsed = json.loads(scene03_result.stdout)
    parsed["trigger"] = "scene02_patrol_handoff"
    return parsed


def create_capture_pack_run(
    scene: str,
    capture_root_raw: str,
    name: str,
    project: str,
    target_markets: str = "",
    target_languages: str = "",
    output_root: str = "",
    platform: str = "TikTok",
    market: str = "US",
    formats: str = "md,docx,xlsx",
    operator_packs_raw: str = "",
) -> dict:
    skill_root = Path(__file__).resolve().parents[1]
    scripts_root = skill_root / "scripts"
    importer = scripts_root / "import_tiktok_capture_pack.py"
    renderer = scripts_root / "render_scene_report.py"
    packer = scripts_root / "generate_operator_pack.py"

    run_root = create_run_root(skill_root, scene, name.strip(), output_root)
    run_root.mkdir(parents=True, exist_ok=True)
    scene_dir = run_root / f"scene-{scene}"
    outputs_dir = scene_dir / "outputs"
    report_json = scene_dir / f"scene-{scene}-{name.strip()}.json"
    capture_root = Path(capture_root_raw).expanduser().resolve()

    import_result = run_python(
        importer,
        [
            "--scene",
            scene,
            "--capture-root",
            str(capture_root),
            "--project",
            project,
            "--target-markets",
            target_markets,
            "--target-languages",
            target_languages,
            "--output",
            str(report_json),
        ],
    )
    imported_report_path = Path(import_result.stdout.strip())
    if imported_report_path.exists():
        imported_scene_dir = imported_report_path.parent
        target_scene_dir_name = imported_scene_dir.name
        match = re.match(r"scene-(\d{2})-", imported_report_path.name)
        if match:
            target_scene_dir_name = f"scene-{match.group(1)}"
        if imported_scene_dir.name != target_scene_dir_name:
            target_scene_dir = run_root / target_scene_dir_name
            if target_scene_dir.exists():
                shutil.rmtree(target_scene_dir)
            shutil.move(str(imported_scene_dir), str(target_scene_dir))
            imported_report_path = target_scene_dir / imported_report_path.name
        report_json = imported_report_path
        scene_dir = report_json.parent
        outputs_dir = scene_dir / "outputs"

    render_result = run_python(
        renderer,
        [
            "--input",
            str(report_json),
            "--output-dir",
            str(outputs_dir),
            "--formats",
            formats,
        ],
    )

    requested_packs = parse_operator_packs(operator_packs_raw) if operator_packs_raw.strip() else default_operator_packs(scene)
    operator_pack_results: list[dict] = []
    for pack_type in requested_packs:
        pack_output_dir = run_root / "operator-packs" / pack_type
        pack_result = run_python(
            packer,
            [
                "--type",
                pack_type,
                "--source-report",
                str(report_json),
                "--platform",
                platform,
                "--market",
                market,
                "--output-dir",
                str(pack_output_dir),
            ],
        )
        parsed = json.loads(pack_result.stdout)
        parsed["type"] = pack_type
        operator_pack_results.append(parsed)

    chained_runs: list[dict] = []
    if scene == "02":
        chained = scene02_follow_on_scene03(
            scripts_root=scripts_root,
            run_root=run_root,
            capture_root=capture_root,
            project=project,
            platform=platform,
            market=market,
            formats=formats,
        )
        if chained:
            chained_runs.append(chained)

    manifest = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "scene": scene,
        "name": name,
        "project": project,
        "capture_root": str(capture_root),
        "report_json": str(report_json),
        "render_outputs": json.loads(render_result.stdout),
        "operator_packs": operator_pack_results,
        "chained_runs": chained_runs,
        "import_stdout": import_result.stdout.strip(),
    }
    write_json_file(run_root / "run_manifest.json", manifest)
    write_readme(run_root, scene, capture_root, report_json, outputs_dir, operator_pack_results)

    return {
        "run_root": str(run_root),
        "report_json": str(report_json),
        "outputs_dir": str(outputs_dir),
        "operator_packs": operator_pack_results,
        "chained_runs": chained_runs,
    }


def main() -> None:
    args = parse_args()
    result = create_capture_pack_run(
        scene=args.scene,
        capture_root_raw=args.capture_root,
        name=args.name,
        project=args.project,
        target_markets=args.target_markets,
        target_languages=args.target_languages,
        output_root=args.output_root,
        platform=args.platform,
        market=args.market,
        formats=args.formats,
        operator_packs_raw=args.operator_packs,
    )
    if args.push_feishu:
        result["feishu_push"] = maybe_push_feishu_bundle(
            result["report_json"],
            args.feishu_app_id,
            args.feishu_app_secret,
            title=args.feishu_title.strip() or args.project,
            base_name=args.feishu_base_name.strip() or args.project,
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
