from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from fnmatch import fnmatch

from render_scene_report import infer_base_name, render_markdown_from_payload, resolve_payload, write_docx, write_xlsx
from text_normalization import normalize_text, write_json_file, write_utf8_text


DEFAULT_FORMATS = ("md", "docx", "xlsx")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Re-render historical scene report outputs from existing scene-*.json files."
    )
    parser.add_argument(
        "--root",
        required=True,
        help="Root directory to scan recursively for scene-*.json files.",
    )
    parser.add_argument(
        "--formats",
        default="md,docx,xlsx",
        help="Comma-separated formats to render: md, docx, xlsx.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview candidate scene JSON files without writing outputs.",
    )
    parser.add_argument(
        "--summary-path",
        default="",
        help="Optional explicit summary JSON path. Defaults to <root>/rerender-summary.json.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional maximum number of scene JSON files to process after filtering. Zero means no limit.",
    )
    parser.add_argument(
        "--match",
        default="",
        help="Optional case-insensitive wildcard filter applied to the full scene JSON path, e.g. '*20260504_capture_runner_scene15*'.",
    )
    parser.add_argument(
        "--since",
        default="",
        help="Optional inclusive folder-date filter in YYYYMMDD format, applied to dated path segments under the root.",
    )
    return parser.parse_args()


def parse_formats(raw: str) -> list[str]:
    allowed = set(DEFAULT_FORMATS)
    values = [item.strip().lower() for item in raw.split(",") if item.strip()]
    invalid = [item for item in values if item not in allowed]
    if invalid:
        raise SystemExit(f"Unsupported formats: {', '.join(invalid)}")
    deduped: list[str] = []
    for item in values:
        if item not in deduped:
            deduped.append(item)
    return deduped or list(DEFAULT_FORMATS)


def looks_like_scene_report(path: Path) -> bool:
    if path.suffix.lower() != ".json":
        return False
    if not path.name.lower().startswith("scene-"):
        return False
    return True


def discover_scene_reports(root: Path) -> list[Path]:
    candidates: list[Path] = []
    for path in root.rglob("scene-*.json"):
        if not looks_like_scene_report(path):
            continue
        if path.name.lower() == "scene-catalog.json":
            continue
        candidates.append(path)
    return sorted(candidates)


def validate_since(raw: str) -> str:
    value = raw.strip()
    if not value:
        return ""
    if len(value) != 8 or not value.isdigit():
        raise SystemExit("--since must use YYYYMMDD format, e.g. 20260504")
    return value


def path_matches(path: Path, pattern: str) -> bool:
    if not pattern.strip():
        return True
    normalized_pattern = pattern.strip().lower()
    normalized_path = str(path).lower().replace("\\", "/")
    return fnmatch(normalized_path, normalized_pattern)


def extract_path_date_token(path: Path, root: Path) -> str:
    try:
        relative = path.relative_to(root)
        segments = relative.parts
    except ValueError:
        segments = path.parts
    for segment in segments:
        prefix = segment[:8]
        if len(prefix) == 8 and prefix.isdigit():
            return prefix
    return ""


def apply_filters(scene_reports: list[Path], root: Path, match: str, since: str, limit: int) -> list[Path]:
    filtered: list[Path] = []
    for path in scene_reports:
        if not path_matches(path, match):
            continue
        if since:
            token = extract_path_date_token(path, root)
            if token and token < since:
                continue
        filtered.append(path)
        if limit > 0 and len(filtered) >= limit:
            break
    return filtered


def summarize_batches(results: list[dict], root: Path) -> list[dict]:
    counts: dict[str, int] = {}
    for result in results:
        path = Path(result["scene_json"])
        try:
            relative = path.relative_to(root)
            batch = relative.parts[0] if relative.parts else "."
        except ValueError:
            batch = path.parent.name or "."
        counts[batch] = counts.get(batch, 0) + 1
    return [
        {"batch": batch, "count": counts[batch]}
        for batch in sorted(counts)
    ]


def resolve_output_dir(scene_json: Path) -> Path:
    if scene_json.parent.name.lower() == "outputs":
        return scene_json.parent
    sibling_outputs = scene_json.parent / "outputs"
    if sibling_outputs.exists() or scene_json.parent.name.lower().startswith("scene-"):
        return sibling_outputs
    return scene_json.parent


def rerender_one(scene_json: Path, formats: list[str], dry_run: bool) -> dict:
    payload = resolve_payload(argparse.Namespace(input=str(scene_json), scene=None, project=None, context_file=None, output_dir=".", formats="md", base_name=""))
    metadata = payload.get("metadata", {}) if isinstance(payload, dict) else {}
    scene_id = normalize_text(metadata.get("scene", ""))
    project = normalize_text(metadata.get("project", ""))
    base_name = infer_base_name(payload, "")
    output_dir = resolve_output_dir(scene_json)
    written: dict[str, str] = {}

    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
        if "md" in formats:
            md_path = output_dir / f"{base_name}.md"
            write_utf8_text(md_path, render_markdown_from_payload(payload))
            written["md"] = str(md_path)
        if "docx" in formats:
            docx_path = output_dir / f"{base_name}.docx"
            write_docx(payload, docx_path)
            written["docx"] = str(docx_path)
        if "xlsx" in formats:
            xlsx_path = output_dir / f"{base_name}.xlsx"
            write_xlsx(payload, xlsx_path)
            written["xlsx"] = str(xlsx_path)

    return {
        "scene_json": str(scene_json),
        "scene_id": scene_id,
        "project": project,
        "base_name": base_name,
        "output_dir": str(output_dir),
        "written": written,
    }


def main() -> None:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    formats = parse_formats(args.formats)
    since = validate_since(args.since)
    summary_path = Path(args.summary_path).expanduser().resolve() if args.summary_path.strip() else (root / "rerender-summary.json")
    discovered = discover_scene_reports(root)
    scene_reports = apply_filters(discovered, root, args.match, since, args.limit)
    results = [rerender_one(path, formats, args.dry_run) for path in scene_reports]
    format_counts = {fmt: 0 for fmt in formats}
    for result in results:
        for fmt in result.get("written", {}):
            if fmt in format_counts:
                format_counts[fmt] += 1
    summary = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "root": str(root),
        "formats": formats,
        "dry_run": args.dry_run,
        "filters": {
            "match": args.match.strip(),
            "since": since,
            "limit": args.limit,
        },
        "discovered_count": len(discovered),
        "count": len(results),
        "format_counts": format_counts,
        "batch_counts": summarize_batches(results, root),
        "results": results,
    }
    if not args.dry_run:
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        write_json_file(summary_path, summary)
    print(json.dumps({"summary_path": str(summary_path), **summary}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
