from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from run_operator_workflow import infer_mode_from_request, run_board_mode, run_capture_pack_mode, run_goal_mode, run_pack_mode, run_scene_mode
from text_normalization import write_json_file, write_utf8_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Thin project launcher for TikTok Growth Operator scene, goal, board, pack, capture-pack, and history runs."
    )
    parser.add_argument("--request", default="", help="Natural-language request. Used by auto mode.")
    parser.add_argument("--mode", default="auto", choices=["auto", "scene", "goal", "board", "pack", "capture-pack", "history"])
    parser.add_argument("--scene", default="", help="Scene id or slug.")
    parser.add_argument("--goal", default="", help="Goal slug.")
    parser.add_argument("--query", default="", help="Goal query.")
    parser.add_argument("--bundle-root", default="", help="Optional preset bundle root for board mode or auto board routing.")
    parser.add_argument("--top-k", type=int, default=3, help="How many board recommendations to keep in board mode.")
    parser.add_argument("--generate", action="store_true", help="In board mode, generate the local queue after scaffolding.")
    parser.add_argument("--dry-run", action="store_true", help="In board mode, preview the queue after generation.")
    parser.add_argument("--run", action="store_true", help="In board mode, execute the generated queue after generation.")
    parser.add_argument("--type", default="", help="Pack type.")
    parser.add_argument("--capture-root", default="", help="TikTok capture-pack root.")
    parser.add_argument("--target-markets", default="", help="Optional comma-separated target markets for scene 13 capture-pack localization blueprints.")
    parser.add_argument("--target-languages", default="", help="Optional comma-separated target languages for scene 15 capture-pack image-translation blueprints.")
    parser.add_argument("--name", required=True, help="Run name.")
    parser.add_argument("--project", default="", help="Project title.")
    parser.add_argument("--context-file", default="", help="Optional UTF-8 context file.")
    parser.add_argument("--output-root", default="", help="Optional explicit project root.")
    parser.add_argument("--output-dir", default="", help="Optional pack output dir.")
    parser.add_argument("--formats", default="md,docx,xlsx", help="Requested formats.")
    parser.add_argument("--platform", default="TikTok", help="Platform label.")
    parser.add_argument("--market", default="US", help="Market label.")
    parser.add_argument("--source-report", default="", help="Optional scene report path for pack mode.")
    parser.add_argument("--history-root", default="", help="Optional run-history scan root.")
    parser.add_argument("--history-output-json", default="", help="Optional JSON output path for history mode.")
    parser.add_argument("--history-output-md", default="", help="Optional Markdown output path for history mode.")
    parser.add_argument("--history-limit", type=int, default=50, help="Maximum number of history entries to keep.")
    return parser.parse_args()


def write_project_readme(project_root: Path, payload: dict) -> None:
    lines = [
        f"# Project Workflow - {payload['name']}",
        "",
        f"- resolved mode: {payload['resolved_mode']}",
        f"- created at: {payload['created_at']}",
        f"- project: {payload['project']}",
        "",
        "## Result",
        "",
        f"`{json.dumps(payload['result'], ensure_ascii=False)}`",
        "",
    ]
    write_utf8_text(project_root / "README.md", "\n".join(lines))


def main() -> None:
    args = parse_args()
    if args.output_root.strip():
        project_root = Path(args.output_root).expanduser().resolve()
    else:
        skill_root = Path(__file__).resolve().parents[1]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_root = skill_root / "tmp" / f"{timestamp}-project-{args.name}"
    project_root.mkdir(parents=True, exist_ok=True)

    from project_space import init_project_space

    init_project_space(
        project_root,
        name=args.name,
        project=args.project or args.name,
        request=args.request,
        mode=args.mode,
    )

    route_meta: dict = {"requested_mode": args.mode}
    resolved_mode = args.mode
    routed: dict = {}
    if args.mode == "auto":
        resolved_mode, routed = infer_mode_from_request(args)
        route_meta["resolved_mode"] = resolved_mode
        route_meta.update(routed)

    if resolved_mode == "scene":
        result = run_scene_mode(args, scene_override=routed.get("scene"), request_text=routed.get("request", ""))
    elif resolved_mode == "board":
        result = run_board_mode(args, query_override=routed.get("query"))
    elif resolved_mode == "goal":
        result = run_goal_mode(args, goal_override=routed.get("goal"), query_override=routed.get("query"))
    elif resolved_mode == "pack":
        result = run_pack_mode(args, pack_type_override=routed.get("type"), request_text=routed.get("request", ""))
    elif resolved_mode == "capture-pack":
        result = run_capture_pack_mode(args, scene_override=routed.get("scene"), request_text=routed.get("request", ""))
    elif resolved_mode == "history":
        from run_operator_workflow import run_history_mode

        result = run_history_mode(args)
    else:
        raise SystemExit(f"Unsupported mode: {resolved_mode}")

    payload = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "name": args.name,
        "project": args.project,
        "requested_mode": args.mode,
        "resolved_mode": resolved_mode,
        "route": route_meta if args.mode == "auto" else {},
        "result": result,
    }
    from project_space import load_project_space

    write_json_file(project_root / "project_manifest.json", payload)
    write_project_readme(project_root, payload)
    space = load_project_space(project_root)
    print(
        json.dumps(
            {"project_root": str(project_root), "project_space": space, **payload},
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
