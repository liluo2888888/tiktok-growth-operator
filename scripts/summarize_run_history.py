from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize TikTok Growth Operator run history from tmp manifests."
    )
    parser.add_argument(
        "--root",
        default="",
        help="Optional root to scan. Defaults to the skill tmp directory.",
    )
    parser.add_argument(
        "--output-json",
        default="",
        help="Optional summary JSON output path.",
    )
    parser.add_argument(
        "--output-md",
        default="",
        help="Optional markdown dashboard output path.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum number of items to keep in the summary.",
    )
    return parser.parse_args()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def shorten(path: str) -> str:
    return path.replace("\\", "/")


def candidate_roots(path: Path) -> list[Path]:
    return [path.parent, path.parent.parent]


def extract_scene_from_path(path: Path) -> str:
    for candidate in [path.parent.name, path.name]:
        if candidate.startswith("scene-"):
            parts = candidate.split("-")
            if len(parts) >= 2 and parts[1].isdigit():
                return parts[1]
    return ""


def load_run_manifest(path: Path) -> dict:
    payload = read_json(path)
    run_root = path.parent
    packs = [item.get("type", "") for item in payload.get("operator_packs", []) if isinstance(item, dict)]
    report_json = payload.get("report_json", "")
    scene_value = str(payload.get("scene", ""))
    derived_scene = extract_scene_from_path(Path(report_json)) if report_json else ""
    return {
        "kind": "run",
        "manifest_path": str(path),
        "root": str(run_root),
        "created_at": payload.get("created_at", ""),
        "name": payload.get("name", ""),
        "project": payload.get("project", ""),
        "scene": derived_scene or (scene_value if scene_value != "auto" else ""),
        "resolved_mode": "capture-pack" if payload.get("capture_root") else "scene",
        "capture_root": payload.get("capture_root", ""),
        "report_json": report_json,
        "operator_packs": packs,
    }


def load_project_manifest(path: Path) -> dict:
    payload = read_json(path)
    result = payload.get("result", {})
    route = payload.get("route", {})
    report_json = result.get("report_json", "")
    return {
        "kind": "project",
        "manifest_path": str(path),
        "root": str(path.parent),
        "created_at": payload.get("created_at", ""),
        "name": payload.get("name", ""),
        "project": payload.get("project", ""),
        "scene": extract_scene_from_path(Path(report_json)) if report_json else "",
        "resolved_mode": payload.get("resolved_mode", route.get("resolved_mode", "")),
        "capture_root": route.get("capture_root", ""),
        "report_json": report_json,
        "operator_packs": [item.get("type", "") for item in result.get("operator_packs", []) if isinstance(item, dict)],
    }


def load_pack_manifest(path: Path) -> dict:
    payload = read_json(path)
    pack_type = payload.get("type", path.stem.replace("-manifest", ""))
    return {
        "kind": "operator-pack",
        "manifest_path": str(path),
        "root": str(path.parent),
        "created_at": payload.get("created_at", ""),
        "name": payload.get("project", ""),
        "project": payload.get("project", ""),
        "scene": "",
        "resolved_mode": pack_type,
        "capture_root": "",
        "report_json": payload.get("source_report", ""),
        "operator_packs": [pack_type],
    }


def discover_entries(root: Path) -> list[dict]:
    entries: list[dict] = []
    seen_manifests: set[str] = set()
    project_roots = {path.parent.resolve() for path in root.rglob("project_manifest.json")}
    for path in root.rglob("*manifest.json"):
        if path.name == "run_manifest.json" and path.parent.resolve() in project_roots:
            continue
        if path.name == "run_manifest.json":
            entry = load_run_manifest(path)
        elif path.name == "project_manifest.json":
            entry = load_project_manifest(path)
        elif path.name.endswith("-manifest.json"):
            entry = load_pack_manifest(path)
        else:
            continue
        key = entry["manifest_path"]
        if key not in seen_manifests:
            seen_manifests.add(key)
            entries.append(entry)
    entries.sort(key=lambda item: item.get("created_at", ""), reverse=True)
    return entries


def build_summary(entries: list[dict], root: Path, limit: int) -> dict:
    kept = entries[:limit]
    by_mode: dict[str, int] = {}
    by_scene: dict[str, int] = {}
    by_kind: dict[str, int] = {}
    for item in kept:
        mode = item.get("resolved_mode", "") or "unknown"
        kind = item.get("kind", "") or "unknown"
        scene = item.get("scene", "")
        by_mode[mode] = by_mode.get(mode, 0) + 1
        by_kind[kind] = by_kind.get(kind, 0) + 1
        if scene:
            by_scene[scene] = by_scene.get(scene, 0) + 1
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "root": str(root),
        "count": len(kept),
        "counts": {
            "by_mode": by_mode,
            "by_scene": by_scene,
            "by_kind": by_kind,
        },
        "entries": kept,
    }


def render_markdown(summary: dict) -> str:
    lines = [
        "# Run History Dashboard",
        "",
        f"- generated at: `{summary['generated_at']}`",
        f"- root: `{shorten(summary['root'])}`",
        f"- entries: `{summary['count']}`",
        "",
        "## Counts By Mode",
        "",
    ]
    for mode, count in sorted(summary["counts"]["by_mode"].items()):
        lines.append(f"- `{mode}`: `{count}`")
    lines.extend(["", "## Counts By Scene", ""])
    for scene, count in sorted(summary["counts"]["by_scene"].items()):
        lines.append(f"- `scene-{scene}`: `{count}`")
    lines.extend(["", "## Recent Entries", ""])
    for item in summary["entries"]:
        title = item.get("project") or item.get("name") or item.get("kind")
        lines.append(f"### {title}")
        lines.append("")
        lines.append(f"- kind: `{item.get('kind', '')}`")
        lines.append(f"- created at: `{item.get('created_at', '')}`")
        lines.append(f"- mode: `{item.get('resolved_mode', '')}`")
        if item.get("scene"):
            lines.append(f"- scene: `scene-{item['scene']}`")
        if item.get("capture_root"):
            lines.append(f"- capture root: `{shorten(item['capture_root'])}`")
        if item.get("report_json"):
            lines.append(f"- report json: `{shorten(item['report_json'])}`")
        if item.get("operator_packs"):
            lines.append(f"- operator packs: `{', '.join(item['operator_packs'])}`")
        lines.append(f"- manifest: `{shorten(item['manifest_path'])}`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    args = parse_args()
    skill_root = Path(__file__).resolve().parents[1]
    root = Path(args.root).expanduser().resolve() if args.root.strip() else (skill_root / "tmp")
    entries = discover_entries(root)
    summary = build_summary(entries, root, args.limit)

    if args.output_json:
        output_json = Path(args.output_json).expanduser().resolve()
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8-sig")
    if args.output_md:
        output_md = Path(args.output_md).expanduser().resolve()
        output_md.parent.mkdir(parents=True, exist_ok=True)
        output_md.write_text(render_markdown(summary), encoding="utf-8-sig")

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
