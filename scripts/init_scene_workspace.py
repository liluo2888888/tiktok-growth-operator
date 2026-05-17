from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from text_normalization import read_json_file, write_json_file, write_utf8_text


def load_catalog(skill_root: Path) -> list[dict]:
    path = skill_root / "references" / "scene-catalog.json"
    loaded = read_json_file(path)
    if not isinstance(loaded, list):
        raise SystemExit(f"Scene catalog must be a JSON array: {path}")
    return loaded


def resolve_scene(catalog: list[dict], scene: str) -> dict:
    normalized = scene.strip().lower()
    for item in catalog:
        if normalized in {item["id"].lower(), item["slug"].lower()}:
            return item
        if normalized == f"scene-{item['id']}":
            return item
    raise SystemExit(f"Unknown scene: {scene}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a repeatable workspace scaffold for one TikTok Growth Operator scene."
    )
    parser.add_argument("--scene", required=True, help="Scene id or slug, e.g. 03 or batch-viral-search-plus-deep-teardown")
    parser.add_argument("--name", required=True, help="Short run name, e.g. lip-combo-us")
    parser.add_argument(
        "--output-root",
        default=None,
        help="Optional output root. Defaults to <skill>/tmp/<timestamp>-<scene>-<name>",
    )
    args = parser.parse_args()

    skill_root = Path(__file__).resolve().parents[1]
    catalog = load_catalog(skill_root)
    scene = resolve_scene(catalog, args.scene)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_root = skill_root / "tmp" / f"{timestamp}-scene-{scene['id']}-{args.name}"
    run_root = Path(args.output_root).resolve() if args.output_root else default_root

    for relative in [
        "inputs",
        "evidence",
        "outputs",
        "notes",
    ]:
        (run_root / relative).mkdir(parents=True, exist_ok=True)

    manifest = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "scene_id": scene["id"],
        "scene_slug": scene["slug"],
        "scene_title": scene["title"],
        "scene_summary": scene["summary"],
        "deliverable_type": scene["deliverable_type"],
        "scenario_file": scene["scenario_file"],
    }
    write_json_file(run_root / "run_manifest.json", manifest)

    prompt = f"""# Scene Workspace

## Scene

- id: {scene["id"]}
- slug: {scene["slug"]}
- title: {scene["title"]}

## What To Put Here

- `inputs/`: user brief, product info, keyword list, account list
- `evidence/`: links, screenshots, exports, transcripts, notes
- `outputs/`: generated reports or matrices
- `notes/`: reasoning notes or follow-up instructions

## Next Step

Open:
- `{scene["scenario_file"]}`
- `references/prompt-library.md`
- `references/deliverable-contracts.md`
"""
    write_utf8_text(run_root / "README.md", prompt)
    print(run_root)


if __name__ == "__main__":
    main()
