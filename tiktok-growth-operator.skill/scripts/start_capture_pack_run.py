from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a real TikTok capture-pack end-to-end into scene-report JSON, rendered outputs, and optional derived operator packs."
    )
    parser.add_argument("--scene", required=True, help="Scene id or slug. Supported by current importer: 01, 03, 07, 08, 09, 11, 12, 13, 14, 15, 16, 17, 18, 19, and auto.")
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
        help="Optional comma-separated operator packs: publish-prep, live-assist.",
    )
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
    allowed = {"publish-prep", "live-assist"}
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
    if scene_id in {"09", "10", "11", "12", "13", "14", "15", "16", "17"}:
        return ["publish-prep"]
    return []


def write_readme(run_root: Path, scene: str, capture_root: Path, report_json: Path, outputs_dir: Path, operator_pack_results: list[dict]) -> None:
    content = f"""# Capture Pack Run

## Inputs

- scene: {scene}
- capture pack: `{capture_root}`
- report json: `{report_json.name}`
- outputs dir: `{outputs_dir.name}`
"""
    if operator_pack_results:
        content += "\n## Derived Operator Packs\n\n"
        for item in operator_pack_results:
            content += f"- {item['type']}: `{Path(item['output_path']).name}`\n"
    content += """

## Flow

1. Import the capture pack into a structured scene-report JSON.
2. Render the report into md/docx/xlsx outputs.
3. Generate any requested operator packs from the imported scene report.
"""
    (run_root / "README.md").write_text(content, encoding="utf-8-sig")


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

    manifest = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "scene": scene,
        "name": name,
        "project": project,
        "capture_root": str(capture_root),
        "report_json": str(report_json),
        "render_outputs": json.loads(render_result.stdout),
        "operator_packs": operator_pack_results,
        "import_stdout": import_result.stdout.strip(),
    }
    (run_root / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    write_readme(run_root, scene, capture_root, report_json, outputs_dir, operator_pack_results)

    return {
        "run_root": str(run_root),
        "report_json": str(report_json),
        "outputs_dir": str(outputs_dir),
        "operator_packs": operator_pack_results,
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
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
