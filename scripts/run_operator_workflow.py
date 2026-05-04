from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

from generate_operator_pack import generate_pack_output
from generate_scene_report import load_catalog
from recommend_entry_board import recommend_family, recommend_items
from recommend_scene_chain import match_goal_from_query
from run_scene_workflow import create_scene_workflow
from start_entry_board import create_entry_board_starter
from start_capture_pack_run import create_capture_pack_run
from start_goal_workflow import create_goal_workflow
from summarize_run_history import build_summary, discover_entries, render_markdown


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "create",
    "for",
    "from",
    "i",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "to",
    "want",
    "with",
}

PACK_KEYWORDS = {
    "publish-prep": [
        "publish-prep",
        "publish prep",
        "publish pack",
        "publish preparation",
        "title cover caption",
        "post handoff",
        "publish handoff",
        "发布包",
        "发布准备",
        "发布交付",
    ],
    "live-assist": [
        "live-assist",
        "live assist",
        "live pack",
        "moderator pack",
        "host prompt pack",
        "live session support",
        "直播包",
        "直播话术",
        "场控包",
    ],
}

MULTI_STAGE_MARKERS = [
    "workflow",
    "process",
    "flow",
    "from",
    "to",
    "then",
    "and then",
    "end to end",
    "full flow",
    "pipeline",
    "to launch",
    "to publish",
    "topic selection",
    "选题到",
    "从",
    "到",
    "工作流",
    "流程",
    "全流程",
]

CAPTURE_PACK_KEYWORDS = [
    "capture pack",
    "capture-pack",
    "capture root",
    "comment pack",
    "ranked_videos.json",
    "comments_sampled.json",
    "real tiktok project",
    "real tik tok project",
    "真实 tiktok 项目",
    "真实tik tok项目",
]


HISTORY_KEYWORDS = [
    "history",
    "run history",
    "recent runs",
    "dashboard",
    "manifest summary",
]


BOARD_PRIORITY_FAMILIES = {"launch-board", "manager-board", "cadence-board", "vertical", "combo"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Unified entrypoint for TikTok Growth Operator scene, goal, board, operator-pack, and auto-routed workflows."
    )
    parser.add_argument(
        "--mode",
        default="auto",
        choices=["auto", "scene", "goal", "board", "pack", "capture-pack", "history"],
        help="Run auto routing, one scene workflow, one goal workflow, one board starter workflow, one operator pack workflow, one TikTok capture-pack workflow, or one run-history dashboard workflow.",
    )

    parser.add_argument("--request", help="Natural-language request for auto mode.")
    parser.add_argument("--scene", help="Scene id or slug for scene mode.")
    parser.add_argument("--goal", help="Goal slug for goal mode.")
    parser.add_argument("--query", help="Free-text workflow description for goal mode or auto mode.")
    parser.add_argument("--bundle-root", default="", help="Optional preset bundle root for board mode or auto board routing.")
    parser.add_argument("--top-k", type=int, default=3, help="How many ranked board recommendations to keep in board mode.")
    parser.add_argument("--generate", action="store_true", help="In board mode, generate the local queue after scaffolding.")
    parser.add_argument("--dry-run", action="store_true", help="In board mode, preview the queue after generation.")
    parser.add_argument("--run", action="store_true", help="In board mode, execute the generated queue after generation.")
    parser.add_argument("--type", choices=["publish-prep", "live-assist"], help="Operator pack type for pack mode.")
    parser.add_argument("--capture-root", default="", help="Capture-pack root for capture-pack mode.")
    parser.add_argument("--target-markets", default="", help="Optional comma-separated target markets for scene 13 capture-pack localization blueprints.")
    parser.add_argument("--target-languages", default="", help="Optional comma-separated target languages for scene 15 capture-pack image-translation blueprints.")

    parser.add_argument("--name", default="", help="Run name for scene or goal mode.")
    parser.add_argument("--project", default="", help="Project or campaign name.")
    parser.add_argument("--context-file", help="Optional UTF-8 brief or context file.")
    parser.add_argument("--output-root", default="", help="Optional explicit run root for scene or goal mode.")
    parser.add_argument("--output-dir", default="", help="Optional explicit output directory for pack mode.")
    parser.add_argument("--formats", default="md", help="Starter formats for goal mode.")
    parser.add_argument("--platform", default="Douyin", help="Platform label.")
    parser.add_argument("--market", default="China", help="Target market label.")
    parser.add_argument("--source-report", help="Optional scene report JSON for pack mode.")
    parser.add_argument("--history-root", default="", help="Optional run-history scan root. Defaults to the skill tmp directory.")
    parser.add_argument("--history-output-json", default="", help="Optional JSON output path for history mode.")
    parser.add_argument("--history-output-md", default="", help="Optional Markdown output path for history mode.")
    parser.add_argument("--history-limit", type=int, default=50, help="Maximum number of history entries to keep.")
    return parser.parse_args()


def slugify(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in value.strip())
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-")


def make_default_pack_output_dir(pack_type: str, project: str) -> str:
    skill_root = Path(__file__).resolve().parents[1]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = slugify(project) or pack_type
    return str(skill_root / "tmp" / f"{timestamp}-pack-{pack_type}-{suffix}")


def first_non_empty(*values: str | None) -> str:
    for value in values:
        if value and value.strip():
            return value.strip()
    return ""


def build_default_name(seed: str, fallback: str) -> str:
    return slugify(seed) or fallback


def detect_board_intent(text: str) -> dict:
    lowered = text.lower()
    explicit_board_markers = [
        "board",
        "starter",
        "看板",
        "运营板",
        "入口板",
        "板",
    ]
    cadence_markers = [
        "daily",
        "weekly",
        "every day",
        "every week",
        "shift",
        "sprint",
        "日常",
        "日更",
        "每日",
        "每周",
        "周复盘",
        "班次",
        "节奏",
    ]
    role_markers = [
        "operator",
        "owner",
        "lead",
        "内容运营",
        "直播运营",
        "策略运营",
        "增长运营",
        "负责",
        "角色",
    ]
    matched = []
    for marker in explicit_board_markers + cadence_markers + role_markers:
        if marker in lowered or marker in text:
            matched.append(marker)
    return {
        "has_board_intent": bool(matched),
        "matched_markers": sorted(set(matched)),
    }


def tokenize(text: str) -> list[str]:
    tokens = [token for token in re.split(r"[^a-zA-Z0-9\u4e00-\u9fff]+", text.lower()) if token]
    return [token for token in tokens if token not in STOPWORDS and (len(token) > 1 or re.search(r"[\u4e00-\u9fff]", token))]


def score_pack_types(text: str) -> list[dict]:
    lowered = text.lower()
    scores = []
    for pack_type, keywords in PACK_KEYWORDS.items():
        score = 0
        matched_keywords: list[str] = []
        for keyword in keywords:
            key = keyword.lower()
            if key in lowered:
                score += max(2, len(key))
                matched_keywords.append(keyword)
        scores.append(
            {
                "type": pack_type,
                "score": score,
                "matched_keywords": matched_keywords,
            }
        )
    scores.sort(key=lambda item: item["score"], reverse=True)
    return scores


def classify_pack_type(text: str) -> tuple[str | None, list[dict]]:
    scores = score_pack_types(text)
    best = scores[0]
    return (best["type"] if best["score"] > 0 else None, scores)


def looks_like_capture_pack(text: str, capture_root: str = "") -> tuple[bool, list[str]]:
    matched: list[str] = []
    lowered = text.lower()
    for keyword in CAPTURE_PACK_KEYWORDS:
        if keyword.lower() in lowered:
            matched.append(keyword)
    if capture_root.strip():
        matched.append("explicit-capture-root")
    return bool(matched), matched


def looks_multi_stage(text: str) -> tuple[bool, list[str]]:
    lowered = text.lower()
    matched: list[str] = []
    for marker in MULTI_STAGE_MARKERS:
        if re.search(r"[a-z]", marker):
            if re.search(rf"\b{re.escape(marker.lower())}\b", lowered):
                matched.append(marker)
        elif marker in text:
            matched.append(marker)
    return bool(matched), matched


def explicit_scene_from_text(text: str) -> str | None:
    match = re.search(r"(?:scene|场景)\s*[-#:]*\s*(0?[1-9]|1[0-9])\b", text, flags=re.IGNORECASE)
    if not match:
        return None
    return f"{int(match.group(1)):02d}"


def score_scene_candidates(text: str, limit: int = 3) -> dict:
    explicit = explicit_scene_from_text(text)
    request_tokens = tokenize(text)
    catalog = load_catalog(Path(__file__).resolve().parents[1])
    lowered = text.lower()
    candidates = []
    for scene in catalog:
        haystack_parts = [scene["id"], scene["slug"], scene["title"], scene["summary"]]
        haystack = " ".join(haystack_parts).lower()
        haystack_tokens = tokenize(haystack)
        score = 0
        matched_terms: list[str] = []
        if scene["slug"] in lowered:
            score += 10
            matched_terms.append(scene["slug"])
        if scene["title"].lower() in lowered:
            score += 10
            matched_terms.append(scene["title"])
        for token in request_tokens:
            if token in haystack_tokens:
                score += 3
                matched_terms.append(token)
            elif any(token in item or item in token for item in haystack_tokens):
                score += 1
        candidates.append(
            {
                "scene_id": scene["id"],
                "scene_slug": scene["slug"],
                "scene_title": scene["title"],
                "score": score,
                "matched_terms": sorted(set(matched_terms)),
            }
        )
    candidates.sort(key=lambda item: item["score"], reverse=True)
    best = candidates[0] if candidates else None
    selected_scene = explicit or (best["scene_id"] if best and best["score"] >= 6 else None)
    return {
        "explicit_scene": explicit,
        "selected_scene": selected_scene,
        "candidates": candidates[:limit],
    }


def preview_goal_route(text: str) -> dict:
    selected_goal, payload = match_goal_from_query(text)
    return {
        "selected_goal": selected_goal,
        "matched_template": payload.get("matched_template"),
        "component_goals": payload.get("component_goals", []),
        "match_score": payload.get("match_score", 0),
        "candidate_templates": payload.get("candidate_templates", []),
        "candidate_goals": payload.get("candidate_goals", []),
    }


def preview_board_route(text: str) -> dict:
    family_pick, family_scores = recommend_family(text)
    recommended_boards = recommend_items(text, family_pick["family"], limit=3)
    return {
        "recommended_family": family_pick["family"],
        "family_description": family_pick["description"],
        "matched_signals": family_pick["matched_signals"],
        "family_scoreboard": family_scores,
        "recommended_boards": recommended_boards,
    }


def infer_mode_from_request(args: argparse.Namespace) -> tuple[str, dict]:
    if args.history_root.strip() or args.history_output_json.strip() or args.history_output_md.strip():
        return "history", {
            "reason": "explicit-history-argument",
            "explanation": {
                "decision": "history",
                "reasons": ["Used explicit history arguments."],
            },
        }
    if args.capture_root:
        if args.scene:
            return "capture-pack", {
                "reason": "explicit-capture-root-and-scene-argument",
                "capture_root": args.capture_root,
                "scene": args.scene,
                "explanation": {
                    "decision": "capture-pack",
                    "reasons": ["Used explicit --capture-root and --scene arguments."],
                },
            }
        return "capture-pack", {
            "reason": "explicit-capture-root-argument",
            "capture_root": args.capture_root,
            "scene": args.scene,
            "explanation": {
                "decision": "capture-pack",
                "reasons": ["Used explicit --capture-root argument."],
            },
        }
    if args.scene:
        return "scene", {
            "reason": "explicit-scene-argument",
            "scene": args.scene,
            "explanation": {
                "decision": "scene",
                "reasons": ["Used explicit --scene argument."],
            },
        }
    if args.type or args.source_report:
        return "pack", {
            "reason": "explicit-pack-argument",
            "type": args.type,
            "explanation": {
                "decision": "pack",
                "reasons": ["Used explicit --type or --source-report argument."],
            },
        }
    if args.goal:
        return "goal", {
            "reason": "explicit-goal-argument",
            "goal": args.goal,
            "explanation": {
                "decision": "goal",
                "reasons": ["Used explicit --goal argument."],
            },
        }
    request_text = first_non_empty(args.request, args.query, args.project, args.name)
    if not request_text:
        raise SystemExit("Auto mode requires --request, --query, --scene, --goal, or --type.")

    lowered = request_text.lower()
    matched_history_markers = [keyword for keyword in HISTORY_KEYWORDS if keyword in lowered]
    if matched_history_markers:
        return "history", {
            "request": request_text,
            "reason": "history-keyword-match",
            "explanation": {
                "decision": "history",
                "reasons": ["The request asked for run history or dashboard output."],
                "matched_history_markers": matched_history_markers,
            },
        }

    inferred_pack, pack_scores = classify_pack_type(request_text)
    is_capture_pack, matched_capture_markers = looks_like_capture_pack(request_text, args.capture_root)
    multi_stage, matched_stage_markers = looks_multi_stage(request_text)
    scene_preview = score_scene_candidates(request_text)
    goal_preview = preview_goal_route(request_text)
    board_preview = preview_board_route(request_text)
    board_intent = detect_board_intent(request_text)
    reasons: list[str] = []

    if is_capture_pack and scene_preview["selected_scene"]:
        reasons.append("The request referenced a capture-pack style project and also matched a specific scene strongly.")
        return "capture-pack", {
            "scene": scene_preview["selected_scene"],
            "request": request_text,
            "capture_root": args.capture_root,
            "reason": "capture-pack-scene-match",
            "explanation": {
                "decision": "capture-pack",
                "reasons": reasons,
                "capture_markers": matched_capture_markers,
                "pack_scores": pack_scores,
                "scene_preview": scene_preview,
                "multi_stage": {
                    "value": multi_stage,
                    "matched_markers": matched_stage_markers,
                },
                "goal_preview": goal_preview,
            },
        }

    if inferred_pack and not multi_stage:
        reasons.append("Pack keywords were stronger than scene/goal signals and no multi-stage markers were present.")
        return "pack", {
            "type": inferred_pack,
            "request": request_text,
            "reason": "pack-keyword-match",
            "explanation": {
                "decision": "pack",
                "reasons": reasons,
                "pack_scores": pack_scores,
                "scene_preview": scene_preview,
                "multi_stage": {
                    "value": multi_stage,
                    "matched_markers": matched_stage_markers,
                },
                "goal_preview": goal_preview,
                "board_preview": board_preview,
            },
        }

    if (
        board_preview["recommended_family"] in BOARD_PRIORITY_FAMILIES
        and board_preview["recommended_boards"]
        and board_preview["family_scoreboard"]
        and (
            board_preview["family_scoreboard"][0]["score"] >= 4
            or board_intent["has_board_intent"]
        )
        and not (
            goal_preview.get("matched_template")
            and multi_stage
            and not board_intent["has_board_intent"]
        )
        and (
            not multi_stage
            or board_intent["has_board_intent"]
        )
        and (
            not scene_preview["selected_scene"]
            or board_intent["has_board_intent"]
        )
    ):
        reasons.append("The request is better framed as a reusable board starter than a single scene, pack, or multi-stage goal workflow.")
        return "board", {
            "query": request_text,
            "reason": "board-family-match",
            "explanation": {
                "decision": "board",
                "reasons": reasons,
                "board_intent": board_intent,
                "pack_scores": pack_scores,
                "scene_preview": scene_preview,
                "multi_stage": {
                    "value": multi_stage,
                    "matched_markers": matched_stage_markers,
                },
                "goal_preview": goal_preview,
                "board_preview": board_preview,
            },
        }

    if scene_preview["selected_scene"] and not multi_stage:
        reasons.append("A strong single-scene match was found and no multi-stage markers were present.")
        return "scene", {
            "scene": scene_preview["selected_scene"],
            "request": request_text,
            "reason": "scene-candidate-match",
            "explanation": {
                "decision": "scene",
                "reasons": reasons,
                "board_intent": board_intent,
                "pack_scores": pack_scores,
                "scene_preview": scene_preview,
                "multi_stage": {
                    "value": multi_stage,
                    "matched_markers": matched_stage_markers,
                },
                "goal_preview": goal_preview,
                "board_preview": board_preview,
            },
        }

    reasons.append("The request looked multi-stage or did not strongly map to one scene or pack, so it was routed to goal/template matching.")
    return "goal", {
        "query": request_text,
        "reason": "goal-template-or-goal-match",
        "explanation": {
            "decision": "goal",
            "reasons": reasons,
            "board_intent": board_intent,
            "pack_scores": pack_scores,
            "scene_preview": scene_preview,
            "multi_stage": {
                "value": multi_stage,
                "matched_markers": matched_stage_markers,
            },
            "goal_preview": goal_preview,
            "board_preview": board_preview,
        },
    }


def run_scene_mode(args: argparse.Namespace, scene_override: str | None = None, request_text: str = "") -> dict:
    scene_ref = scene_override or args.scene
    if not scene_ref:
        raise SystemExit("Scene mode requires --scene.")
    project = first_non_empty(args.project, request_text, f"Scene {scene_ref} Workflow")
    run_name = args.name or build_default_name(project, f"scene-{scene_ref}")
    return create_scene_workflow(
        scene_ref=scene_ref,
        project=project,
        name=run_name,
        context_file=args.context_file,
        output_root=args.output_root or None,
    )


def run_goal_mode(args: argparse.Namespace, goal_override: str | None = None, query_override: str | None = None) -> dict:
    goal = goal_override or args.goal
    query = query_override or args.query
    if bool(goal) == bool(query):
        raise SystemExit("Goal mode requires exactly one of --goal or --query.")
    project_seed = first_non_empty(args.project, query, goal, "goal-workflow")
    run_name = args.name or build_default_name(project_seed, "goal-workflow")
    return create_goal_workflow(
        goal=goal,
        query=query,
        name=run_name,
        project=args.project,
        context_file=args.context_file,
        output_root=args.output_root,
        formats_raw=args.formats,
        platform=args.platform,
        market=args.market,
    )


def run_board_mode(args: argparse.Namespace, query_override: str | None = None) -> dict:
    query = query_override or args.query or args.request
    if not query:
        raise SystemExit("Board mode requires --query or --request.")
    return create_entry_board_starter(
        query=query,
        bundle_root=args.bundle_root,
        name=args.name,
        project=args.project,
        output_root=args.output_root,
        top_k=args.top_k,
        generate=args.generate,
        dry_run=args.dry_run,
        run=args.run,
    )


def run_pack_mode(args: argparse.Namespace, pack_type_override: str | None = None, request_text: str = "") -> dict:
    pack_type = pack_type_override or args.type
    if not pack_type:
        raise SystemExit("Pack mode requires --type.")
    project = first_non_empty(args.project, request_text)
    if not project and not args.source_report:
        raise SystemExit("Pack mode requires --project, --request, or --source-report.")
    output_dir = args.output_dir or make_default_pack_output_dir(pack_type, project or pack_type)
    context = Path(args.context_file).read_text(encoding="utf-8") if args.context_file else ""
    return generate_pack_output(
        pack_type=pack_type,
        output_dir=Path(output_dir).resolve(),
        project=project,
        platform=args.platform,
        market=args.market,
        context=context,
        source_report_path=Path(args.source_report).resolve() if args.source_report else None,
    )


def run_capture_pack_mode(args: argparse.Namespace, scene_override: str | None = None, request_text: str = "") -> dict:
    scene_ref = scene_override or args.scene
    if not scene_ref:
        raise SystemExit("Capture-pack mode requires --scene or a request that maps strongly to one scene.")
    if not args.capture_root.strip():
        raise SystemExit("Capture-pack mode requires --capture-root.")
    project = first_non_empty(args.project, request_text, f"Capture Pack Scene {scene_ref}")
    run_name = args.name or build_default_name(project, f"capture-scene-{scene_ref}")
    return create_capture_pack_run(
        scene=scene_ref,
        capture_root_raw=args.capture_root,
        name=run_name,
        project=project,
        target_markets=args.target_markets,
        target_languages=args.target_languages,
        output_root=args.output_root,
        platform=args.platform,
        market=args.market,
        formats=args.formats or "md,docx,xlsx",
        operator_packs_raw="",
    )


def run_history_mode(args: argparse.Namespace) -> dict:
    skill_root = Path(__file__).resolve().parents[1]
    root = Path(args.history_root).expanduser().resolve() if args.history_root.strip() else (skill_root / "tmp")
    entries = discover_entries(root)
    summary = build_summary(entries, root, args.history_limit)

    output_json = ""
    output_md = ""
    if args.history_output_json.strip():
        json_path = Path(args.history_output_json).expanduser().resolve()
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8-sig")
        output_json = str(json_path)
    if args.history_output_md.strip():
        md_path = Path(args.history_output_md).expanduser().resolve()
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(render_markdown(summary), encoding="utf-8-sig")
        output_md = str(md_path)

    return {
        "history_root": str(root),
        "history_limit": args.history_limit,
        "entry_count": summary["count"],
        "counts": summary["counts"],
        "output_json": output_json,
        "output_md": output_md,
        "summary": summary,
    }


def main() -> None:
    args = parse_args()
    route_meta: dict = {"requested_mode": args.mode}

    if args.mode == "auto":
        routed_mode, routed = infer_mode_from_request(args)
        route_meta["resolved_mode"] = routed_mode
        route_meta.update(routed)
        if routed_mode == "scene":
            result = run_scene_mode(args, scene_override=routed.get("scene"), request_text=routed.get("request", ""))
        elif routed_mode == "board":
            result = run_board_mode(args, query_override=routed.get("query"))
        elif routed_mode == "goal":
            result = run_goal_mode(args, goal_override=routed.get("goal"), query_override=routed.get("query"))
        elif routed_mode == "capture-pack":
            result = run_capture_pack_mode(args, scene_override=routed.get("scene"), request_text=routed.get("request", ""))
        elif routed_mode == "history":
            result = run_history_mode(args)
        else:
            result = run_pack_mode(args, pack_type_override=routed.get("type"), request_text=routed.get("request", ""))
    elif args.mode == "scene":
        result = run_scene_mode(args)
    elif args.mode == "board":
        result = run_board_mode(args)
    elif args.mode == "goal":
        result = run_goal_mode(args)
    elif args.mode == "capture-pack":
        result = run_capture_pack_mode(args)
    elif args.mode == "history":
        result = run_history_mode(args)
    else:
        result = run_pack_mode(args)

    if args.mode == "auto":
        result = {"route": route_meta, **result}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
