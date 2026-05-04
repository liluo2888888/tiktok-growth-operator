from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from generate_operator_pack import generate_pack_output
from generate_scene_report import build_report_payload, load_catalog, resolve_scene
from render_scene_report import infer_base_name, render_markdown_from_payload, write_docx, write_xlsx


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap one TikTok Growth Operator scene run with workspace folders, structured report scaffold, starter deliverables, and optional operator packs."
    )
    parser.add_argument("--scene", required=True, help="Scene id or slug.")
    parser.add_argument("--name", required=True, help="Short run name, e.g. lip-combo-us.")
    parser.add_argument("--project", default="", help="Optional project title. Defaults to the run name.")
    parser.add_argument("--context-file", help="Optional UTF-8 brief file.")
    parser.add_argument(
        "--output-root",
        default="",
        help="Optional explicit run root. Defaults to <skill>/tmp/<timestamp>-scene-<id>-<name>.",
    )
    parser.add_argument(
        "--formats",
        default="md,docx,xlsx",
        help="Comma-separated starter deliverable formats: md, docx, xlsx.",
    )
    parser.add_argument(
        "--operator-packs",
        default="",
        help="Optional comma-separated operator packs to generate: publish-prep, live-assist, creative-production-handoff.",
    )
    parser.add_argument("--platform", default="Douyin", help="Platform label for derived operator packs.")
    parser.add_argument("--market", default="China", help="Target market label for derived operator packs.")
    return parser.parse_args()


def create_run_root(skill_root: Path, scene: dict, run_name: str, output_root: str) -> Path:
    if output_root.strip():
        return Path(output_root).expanduser().resolve()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return skill_root / "tmp" / f"{timestamp}-scene-{scene['id']}-{run_name}"


def parse_operator_packs(raw: str) -> list[str]:
    allowed = {"publish-prep", "live-assist", "creative-production-handoff"}
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
    if scene_id in {"09", "10", "11", "12", "13", "14", "15", "16"}:
        return ["publish-prep", "creative-production-handoff"]
    if scene_id in {"08", "18", "19"}:
        return ["live-assist"]
    return []


def write_manifest(
    run_root: Path,
    scene: dict,
    report_path: Path,
    operator_pack_results: list[dict],
) -> None:
    manifest = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "scene_id": scene["id"],
        "scene_slug": scene["slug"],
        "scene_title": scene["title"],
        "scene_summary": scene["summary"],
        "deliverable_type": scene["deliverable_type"],
        "scenario_file": scene["scenario_file"],
        "report_json": str(report_path),
        "operator_packs": operator_pack_results,
    }
    (run_root / "run_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8-sig",
    )


def write_readme(run_root: Path, scene: dict, report_path: Path, operator_pack_results: list[dict]) -> None:
    content = f"""# Scene Run Workspace

## Scene

- id: {scene["id"]}
- slug: {scene["slug"]}
- title: {scene["title"]}
- deliverable type: {scene["deliverable_type"]}

## Folder Use

- `inputs/`: user brief, product info, keyword list, account list
- `evidence/`: links, screenshots, exports, transcripts, notes
- `outputs/`: rendered reports
- `notes/`: reasoning notes, open questions, reviewer comments
- `operator-packs/`: derived publish-prep, live-assist, or creative-production-handoff packs when generated

## Main Files

- report json: `{report_path.name}`
- scene playbook: `{scene["scenario_file"]}`
"""
    if operator_pack_results:
        content += "\n## Generated Operator Packs\n\n"
        for item in operator_pack_results:
            content += f"- {item['type']}: `{Path(item['output_path']).name}`\n"
    content += """

## Suggested Flow

1. Put brief and raw material into `inputs/` and `evidence/`.
2. Fill the report JSON with real conclusions and evidence.
3. Re-render outputs with `scripts/render_scene_report.py`.
4. If operator packs were generated, refine those handoff packs from the now-complete scene report.
"""
    (run_root / "README.md").write_text(content, encoding="utf-8-sig")


def main() -> None:
    args = parse_args()
    skill_root = Path(__file__).resolve().parents[1]
    catalog = load_catalog(skill_root)
    scene = resolve_scene(catalog, args.scene)
    run_name = args.name.strip()
    project = args.project.strip() or run_name
    context = Path(args.context_file).read_text(encoding="utf-8") if args.context_file else ""

    run_root = create_run_root(skill_root, scene, run_name, args.output_root)
    for relative in ["inputs", "evidence", "outputs", "notes", "operator-packs"]:
        (run_root / relative).mkdir(parents=True, exist_ok=True)

    payload = build_report_payload(scene, project, context)
    base_name = infer_base_name(payload, "")
    report_json_path = run_root / f"{base_name}.json"
    report_json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8-sig")

    formats = [item.strip().lower() for item in args.formats.split(",") if item.strip()]
    outputs_dir = run_root / "outputs"
    if "md" in formats:
        (outputs_dir / f"{base_name}.md").write_text(render_markdown_from_payload(payload), encoding="utf-8-sig")
    if "docx" in formats:
        write_docx(payload, outputs_dir / f"{base_name}.docx")
    if "xlsx" in formats:
        write_xlsx(payload, outputs_dir / f"{base_name}.xlsx")

    requested_packs = parse_operator_packs(args.operator_packs) if args.operator_packs.strip() else default_operator_packs(scene["id"])
    operator_pack_results: list[dict] = []
    for pack_type in requested_packs:
        pack_output_dir = run_root / "operator-packs" / pack_type
        operator_pack_results.append(
            generate_pack_output(
                pack_type=pack_type,
                output_dir=pack_output_dir,
                project=project,
                platform=args.platform,
                market=args.market,
                context=context,
                source_report_path=report_json_path,
            )
        )

    write_manifest(run_root, scene, report_json_path, operator_pack_results)
    write_readme(run_root, scene, report_json_path, operator_pack_results)

    print(
        json.dumps(
            {
                "run_root": str(run_root),
                "report_json": str(report_json_path),
                "outputs_dir": str(outputs_dir),
                "operator_packs": operator_pack_results,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
