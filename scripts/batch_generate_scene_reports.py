from __future__ import annotations

import argparse
import json
from pathlib import Path

from generate_scene_report import build_report_payload, load_catalog, render_markdown_from_payload, resolve_scene


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate multiple scene report scaffolds from a batch JSON file."
    )
    parser.add_argument(
        "--batch-file",
        required=True,
        help="JSON file containing a list of objects with scene, project, optional context.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where all scaffold files will be written.",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Scaffold output format.",
    )
    args = parser.parse_args()

    skill_root = Path(__file__).resolve().parents[1]
    catalog = load_catalog(skill_root)
    batch = json.loads(Path(args.batch_file).read_text(encoding="utf-8-sig"))
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    written = []
    for item in batch:
        scene = resolve_scene(catalog, str(item["scene"]))
        project = item["project"]
        context = item.get("context", "")
        slug = scene["slug"]
        project_slug = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in project.strip().lower()).strip("-")
        extension = "json" if args.format == "json" else "md"
        filename = f"scene-{scene['id']}-{project_slug or slug}.{extension}"
        payload = build_report_payload(scene, project, context)
        report = json.dumps(payload, ensure_ascii=False, indent=2) if args.format == "json" else render_markdown_from_payload(payload)
        path = output_dir / filename
        path.write_text(report + ("" if report.endswith("\n") else "\n"), encoding="utf-8")
        written.append(str(path))

    print(json.dumps(written, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
