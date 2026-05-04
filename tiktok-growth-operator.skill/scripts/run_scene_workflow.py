from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from generate_scene_report import build_report_payload, render_markdown_from_payload
from init_scene_workspace import load_catalog, resolve_scene


def slugify(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in value.strip())
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-")


def build_run_root(skill_root: Path, scene: dict, name: str, output_root: str | None) -> Path:
    if output_root:
        return Path(output_root).resolve()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return skill_root / "tmp" / f"{timestamp}-scene-{scene['id']}-{name}"


def write_workspace_readme(run_root: Path, scene: dict, report_json_path: Path, report_path: Path) -> None:
    readme = f"""# Direct Scene Run

## Scene

- id: {scene["id"]}
- slug: {scene["slug"]}
- title: {scene["title"]}

## Generated Files

- report json: `{report_json_path.name}`
- report: `{report_path.name}`
- manifest: `run_manifest.json`
- next step note: `notes/next-step.md`

## Suggested Next Files To Open

- `{scene["scenario_file"]}`
- `references/direct-use.md`
- `references/prompt-library.md`
- `references/deliverable-contracts.md`
- `references/scene-report-contract.md`
"""
    (run_root / "README.md").write_text(readme, encoding="utf-8-sig")


def create_scene_workflow(
    scene_ref: str,
    project: str,
    name: str | None = None,
    context_file: str | None = None,
    output_root: str | None = None,
) -> dict:
    skill_root = Path(__file__).resolve().parents[1]
    catalog = load_catalog(skill_root)
    scene = resolve_scene(catalog, scene_ref)
    run_name = name or slugify(project) or scene["slug"]
    run_root = build_run_root(skill_root, scene, run_name, output_root)

    for relative in ["inputs", "evidence", "outputs", "notes"]:
        (run_root / relative).mkdir(parents=True, exist_ok=True)

    context = ""
    context_source = None
    if context_file:
        context_path = Path(context_file).resolve()
        context = context_path.read_text(encoding="utf-8")
        (run_root / "inputs" / "context.txt").write_text(context, encoding="utf-8-sig")
        context_source = str(context_path)

    payload = build_report_payload(scene, project, context)
    report_json_path = run_root / "outputs" / f"scene-{scene['id']}-report.json"
    report_path = run_root / "outputs" / f"scene-{scene['id']}-report.md"
    report_json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8-sig")
    report_path.write_text(render_markdown_from_payload(payload), encoding="utf-8-sig")

    next_step = f"""# Next Step

Open the scene file:

- `{scene["scenario_file"]}`

Then decide whether this run is:

- live-analysis
- evidence-pack-analysis
- planning-only

Finally, continue from:

- report json: `outputs/{report_json_path.name}`
- report scaffold: `outputs/{report_path.name}`
- direct-use guide: `references/direct-use.md`
"""
    (run_root / "notes" / "next-step.md").write_text(next_step, encoding="utf-8-sig")

    manifest = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "scene_id": scene["id"],
        "scene_slug": scene["slug"],
        "scene_title": scene["title"],
        "project": project,
        "run_name": run_name,
        "deliverable_type": scene["deliverable_type"],
        "scenario_file": scene["scenario_file"],
        "context_source": context_source,
        "report_json_path": str(report_json_path),
        "report_path": str(report_path),
    }
    (run_root / "run_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8-sig",
    )
    write_workspace_readme(run_root, scene, report_json_path, report_path)

    return {
        "run_root": str(run_root),
        "report_json_path": str(report_json_path),
        "report_path": str(report_path),
        "scene_file": scene["scenario_file"],
        "scene_id": scene["id"],
        "scene_slug": scene["slug"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a direct-use Codex workspace and report scaffold for one TikTok Growth Operator scene."
    )
    parser.add_argument("--scene", required=True, help="Scene id or slug, e.g. 03 or batch-viral-search-plus-deep-teardown")
    parser.add_argument("--project", required=True, help="Human-readable project name.")
    parser.add_argument("--name", default=None, help="Optional short run name. Defaults to a slugified project name.")
    parser.add_argument("--context-file", default=None, help="Optional UTF-8 text file with user brief or evidence summary.")
    parser.add_argument("--output-root", default=None, help="Optional output directory.")
    args = parser.parse_args()

    result = create_scene_workflow(
        scene_ref=args.scene,
        project=args.project,
        name=args.name,
        context_file=args.context_file,
        output_root=args.output_root,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
