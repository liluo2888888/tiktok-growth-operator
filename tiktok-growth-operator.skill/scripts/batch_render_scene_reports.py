from __future__ import annotations

import argparse
import json
from pathlib import Path

from render_scene_report import infer_base_name, render_markdown_from_payload, resolve_payload, write_docx, write_xlsx
from text_normalization import write_utf8_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render multiple structured TikTok Growth Operator scene report JSON files."
    )
    parser.add_argument("--input-dir", required=True, help="Directory containing scene report JSON files.")
    parser.add_argument("--output-dir", required=True, help="Directory where rendered outputs will be written.")
    parser.add_argument(
        "--formats",
        default="md,docx,xlsx",
        help="Comma-separated output formats: md, docx, xlsx.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input_dir).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    formats = [item.strip().lower() for item in args.formats.split(",") if item.strip()]

    written: list[dict[str, str]] = []
    for path in sorted(input_dir.glob("*.json")):
        payload = resolve_payload(argparse.Namespace(input=str(path), scene=None, project=None, context_file=None))
        base_name = infer_base_name(payload, "")
        item: dict[str, str] = {"input": str(path)}
        if "md" in formats:
            md_path = output_dir / f"{base_name}.md"
            write_utf8_text(md_path, render_markdown_from_payload(payload))
            item["md"] = str(md_path)
        if "docx" in formats:
            docx_path = output_dir / f"{base_name}.docx"
            write_docx(payload, docx_path)
            item["docx"] = str(docx_path)
        if "xlsx" in formats:
            xlsx_path = output_dir / f"{base_name}.xlsx"
            write_xlsx(payload, xlsx_path)
            item["xlsx"] = str(xlsx_path)
        written.append(item)

    print(json.dumps(written, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
