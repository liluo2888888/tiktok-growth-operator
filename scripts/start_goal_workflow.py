from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

from generate_operator_pack import generate_pack_output
from generate_scene_report import build_report_payload, load_catalog, resolve_scene
from recommend_scene_chain import build_payload, match_goal_from_query
from render_scene_report import infer_base_name, render_markdown_from_payload, write_docx, write_xlsx


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a multi-scene goal workflow workspace from a goal slug or free-text goal."
    )
    parser.add_argument("--goal", help="Goal slug.")
    parser.add_argument("--query", help="Free-text business goal.")
    parser.add_argument("--name", required=True, help="Short workflow run name.")
    parser.add_argument("--project", default="", help="Optional project title. Defaults to run name.")
    parser.add_argument("--context-file", help="Optional UTF-8 brief file.")
    parser.add_argument("--output-root", default="", help="Optional explicit workflow root.")
    parser.add_argument("--formats", default="md", help="Comma-separated starter formats: md, docx, xlsx.")
    parser.add_argument("--platform", default="Douyin", help="Platform label for derived operator packs.")
    parser.add_argument("--market", default="China", help="Target market label for derived operator packs.")
    return parser.parse_args()


def make_goal_root(skill_root: Path, run_name: str, output_root: str) -> Path:
    if output_root.strip():
        return Path(output_root).expanduser().resolve()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return skill_root / "tmp" / f"{timestamp}-goal-{run_name}"


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip().lower())
    normalized = re.sub(r"-{2,}", "-", normalized).strip("-")
    return normalized or "workflow"


def truncate_slug(value: str, limit: int, fallback: str) -> str:
    text = slugify(value)
    if len(text) <= limit:
        return text
    trimmed = text[:limit].rstrip("-")
    return trimmed or fallback


def safe_run_name(name: str, query: str | None, goal: str | None) -> str:
    seed = name.strip() or (query or "").strip() or (goal or "").strip() or "goal-workflow"
    return truncate_slug(seed, 48, "goal-workflow")


def write_goal_readme(goal_root: Path, payload: dict, operator_pack_results: list[dict]) -> None:
    lines = [
        f"# Goal Workflow - {payload['label']}",
        "",
        payload["description"],
        "",
    ]
    if payload.get("matched_template") or payload.get("component_goals"):
        lines.extend(["## Workflow Routing", ""])
        if payload.get("matched_template"):
            lines.append(f"- Matched template: `{payload['matched_template']}`")
        if payload.get("component_goals"):
            lines.append(f"- Component goals: `{', '.join(payload['component_goals'])}`")
        lines.append("")
    lines.extend([
        "## Recommended Scenes",
        "",
    ])
    for index, scene in enumerate(payload["scenes"], start=1):
        lines.append(f"{index}. Scene {scene['id']} - {scene['title']} (`{scene['scenario_file']}`)")
    if payload.get("packs"):
        lines.extend(["", "## Suggested Operator Packs", ""])
        for item in payload["packs"]:
            lines.append(f"- {item}")
    if operator_pack_results:
        lines.extend(["", "## Generated Operator Packs", ""])
        for item in operator_pack_results:
            lines.append(f"- {item['type']}: `{Path(item['output_path']).name}`")
    if payload.get("matched_from_query"):
        lines.extend(["", "## Match Detail", ""])
        lines.append(f"- Query: {payload['matched_from_query']}")
        lines.append(f"- Chosen Goal: {payload['goal']}")
    (goal_root / "README.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8-sig")


def create_goal_workflow(
    goal: str | None = None,
    query: str | None = None,
    name: str = "",
    project: str = "",
    context_file: str | None = None,
    output_root: str = "",
    formats_raw: str = "md",
    platform: str = "Douyin",
    market: str = "China",
) -> dict:
    if bool(goal) == bool(query):
        raise SystemExit("Provide exactly one of goal or query.")

    skill_root = Path(__file__).resolve().parents[1]
    payload = build_payload(goal) if goal else match_goal_from_query(query)[1]
    normalized_name = safe_run_name(name, query, goal)
    resolved_project = project.strip() or normalized_name
    context = Path(context_file).read_text(encoding="utf-8") if context_file else ""
    goal_root = make_goal_root(skill_root, normalized_name, output_root)
    goal_root.mkdir(parents=True, exist_ok=True)
    scene_runs_root = goal_root / "scene-runs"
    scene_runs_root.mkdir(parents=True, exist_ok=True)
    packs_root = goal_root / "operator-packs"
    packs_root.mkdir(parents=True, exist_ok=True)

    catalog = load_catalog(skill_root)
    formats = [item.strip().lower() for item in formats_raw.split(",") if item.strip()]
    scene_runs = []
    operator_pack_results: list[dict] = []
    for scene_ref in payload["scenes"]:
        scene = resolve_scene(catalog, scene_ref["id"])
        scene_slug = truncate_slug(scene["slug"], 24, f"scene-{scene['id']}")
        scene_run_root = scene_runs_root / f"scene-{scene['id']}-{scene_slug}"
        for relative in ["inputs", "evidence", "outputs", "notes"]:
            (scene_run_root / relative).mkdir(parents=True, exist_ok=True)
        report = build_report_payload(scene, resolved_project, context)
        base_name = truncate_slug(infer_base_name(report, ""), 64, f"scene-{scene['id']}-report")
        report_json_path = scene_run_root / f"{base_name}.json"
        report_json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8-sig")
        if "md" in formats:
            (scene_run_root / "outputs" / f"{base_name}.md").write_text(
                render_markdown_from_payload(report), encoding="utf-8-sig"
            )
        if "docx" in formats:
            write_docx(report, scene_run_root / "outputs" / f"{base_name}.docx")
        if "xlsx" in formats:
            write_xlsx(report, scene_run_root / "outputs" / f"{base_name}.xlsx")
        scene_runs.append(
            {
                "scene_id": scene["id"],
                "scene_title": scene["title"],
                "run_root": str(scene_run_root),
                "report_json": str(report_json_path),
            }
        )

    for pack_type in payload.get("packs", []):
        operator_pack_results.append(
            generate_pack_output(
                pack_type=pack_type,
                output_dir=packs_root / pack_type,
                project=resolved_project,
                platform=platform,
                market=market,
                context=context,
                source_report_path=Path(scene_runs[-1]["report_json"]) if scene_runs else None,
            )
        )

    write_goal_readme(goal_root, payload, operator_pack_results)
    manifest = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "goal": payload["goal"],
        "label": payload["label"],
        "description": payload["description"],
        "matched_template": payload.get("matched_template"),
        "component_goals": payload.get("component_goals", []),
        "project": resolved_project,
        "scene_runs": scene_runs,
        "packs": payload.get("packs", []),
        "generated_operator_packs": operator_pack_results,
        "matched_from_query": payload.get("matched_from_query"),
    }
    (goal_root / "goal_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    return {
        "goal_root": str(goal_root),
        "run_name": normalized_name,
        "scene_runs": scene_runs,
        "operator_packs": operator_pack_results,
        "matched_template": payload.get("matched_template"),
        "component_goals": payload.get("component_goals", []),
    }


def main() -> None:
    args = parse_args()
    result = create_goal_workflow(
        goal=args.goal,
        query=args.query,
        name=args.name,
        project=args.project,
        context_file=args.context_file,
        output_root=args.output_root,
        formats_raw=args.formats,
        platform=args.platform,
        market=args.market,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
