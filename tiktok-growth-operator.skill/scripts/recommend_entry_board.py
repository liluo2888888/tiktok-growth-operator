from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from generate_batch_preset import (
    CADENCE_BOARDS,
    LAUNCH_BOARDS,
    MANAGER_BOARDS,
    PRESETS,
    TEMPLATE_BUNDLES,
    VERTICAL_STARTERS,
)


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "board",
    "build",
    "create",
    "for",
    "from",
    "i",
    "in",
    "into",
    "is",
    "it",
    "me",
    "my",
    "need",
    "of",
    "on",
    "or",
    "set",
    "the",
    "this",
    "to",
    "up",
    "want",
    "with",
    "帮我",
    "给我",
    "一个",
}


ENTRY_FAMILIES = [
    {
        "family": "single",
        "label": "Single Preset",
        "description": "One direct preset when the request is narrow and already maps to one workflow.",
        "keywords": [
            "single",
            "one workflow",
            "just one",
            "only one",
            "goal",
            "preset",
            "one preset",
            "direct preset",
            "topic to publish",
            "viral to testing",
            "competitor to publish",
            "audience to live",
            "weekly monitor",
            "单个",
            "单一",
            "单条",
            "一个工作流",
            "一个预设",
        ],
        "fallbacks": ["combo", "launch-board"],
    },
    {
        "family": "combo",
        "label": "Combo Board",
        "description": "Curated multi-preset board when you want several workflows bundled together but not seeded to a role or cadence.",
        "keywords": [
            "bundle",
            "combo",
            "combined",
            "multi workflow",
            "multi preset",
            "operating board",
            "multi scene",
            "组合",
            "组合板",
            "多工作流",
            "多预设",
            "整套",
        ],
        "fallbacks": ["launch-board", "manager-board"],
    },
    {
        "family": "vertical",
        "label": "Vertical Starter",
        "description": "Seeded starter board when the request is tied to a niche, market, or seeded business context.",
        "keywords": [
            "beauty",
            "skincare",
            "lip",
            "douyin beauty",
            "tiktok beauty",
            "vertical",
            "starter",
            "seeded",
            "category",
            "us market",
            "china market",
            "美妆",
            "护肤",
            "口红",
            "赛道",
            "垂类",
            "启动板",
            "tiktok",
            "douyin",
        ],
        "fallbacks": ["launch-board", "combo"],
    },
    {
        "family": "launch-board",
        "label": "Launch Board",
        "description": "Outcome-first board when the operator thinks in terms of this week's business deliverable.",
        "keywords": [
            "publish week",
            "publish plan",
            "this week",
            "launch",
            "localization sprint",
            "competitor review",
            "comment to live",
            "testing sprint",
            "outcome",
            "deliverable",
            "objective",
            "本周发布",
            "发布",
            "发布计划",
            "竞品复盘",
            "本地化冲刺",
            "目标",
            "结果",
            "周计划",
            "发布板",
        ],
        "fallbacks": ["cadence-board", "combo"],
    },
    {
        "family": "manager-board",
        "label": "Manager Board",
        "description": "Role-first board when the request is defined by the operator's responsibility.",
        "keywords": [
            "content operator",
            "live operator",
            "strategy operator",
            "growth operator",
            "operator",
            "manager",
            "role",
            "owner",
            "content lead",
            "live lead",
            "我是",
            "负责",
            "内容运营",
            "直播运营",
            "策略运营",
            "增长运营",
            "岗位",
            "角色",
            "运营板",
            "入口板",
            "看板",
        ],
        "fallbacks": ["cadence-board", "launch-board"],
    },
    {
        "family": "cadence-board",
        "label": "Cadence Board",
        "description": "Rhythm-first board when the request is defined by cadence such as daily, weekly, sprint, or shift.",
        "keywords": [
            "daily",
            "daily board",
            "weekly",
            "weekly review",
            "sprint",
            "shift",
            "cadence",
            "routine",
            "every day",
            "every week",
            "day plan",
            "week plan",
            "daily ops",
            "weekly ops",
            "每日",
            "每天",
            "每周",
            "周度",
            "冲刺",
            "班次",
            "节奏",
            "日常运营",
            "日更运营",
            "周复盘",
            "日常运营板",
            "日更运营板",
        ],
        "fallbacks": ["launch-board", "manager-board"],
    },
]

BOARD_INTENT_MARKERS = ["board", "starter", "运营板", "入口板", "看板", "板", "board for", "starter for"]
CADENCE_MARKERS = ["daily", "weekly", "every day", "every week", "shift", "sprint", "每日", "每周", "班次", "日常", "日更", "周复盘"]
ROLE_MARKERS = ["operator", "owner", "lead", "内容运营", "直播运营", "策略运营", "增长运营", "负责", "角色"]
OUTCOME_MARKERS = ["publish", "launch", "this week", "review", "发布", "本周", "复盘", "计划"]
VERTICAL_MARKERS = ["beauty", "skincare", "lip", "美妆", "护肤", "口红", "tiktok", "douyin"]
WORKFLOW_MARKERS = ["workflow", "flow", "pipeline", "流程", "工作流"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Recommend the best TikTok Growth Operator entry family and board slug from a natural-language request."
    )
    parser.add_argument("--query", required=True, help="Natural-language description of the operator request.")
    parser.add_argument("--format", default="markdown", choices=["markdown", "json"], help="Output format.")
    parser.add_argument(
        "--bundle-root",
        default="",
        help="Optional generated template bundle root for resolving real template and suite paths.",
    )
    return parser.parse_args()


def tokenize(text: str) -> list[str]:
    tokens = [token for token in re.split(r"[^a-zA-Z0-9\u4e00-\u9fff]+", text.lower()) if token]
    return [token for token in tokens if token not in STOPWORDS and (len(token) > 1 or re.search(r"[\u4e00-\u9fff]", token))]


def score_keywords(text: str, keywords: list[str]) -> tuple[int, list[str]]:
    lowered = text.lower()
    matched: list[str] = []
    score = 0
    for keyword in keywords:
        candidate = keyword.lower()
        if candidate in lowered:
            matched.append(keyword)
            score += max(2, len(candidate.split()))
    return score, matched


def detect_query_traits(query: str) -> dict:
    lowered = query.lower()
    return {
        "board_intent": [marker for marker in BOARD_INTENT_MARKERS if marker in lowered or marker in query],
        "cadence": [marker for marker in CADENCE_MARKERS if marker in lowered or marker in query],
        "role": [marker for marker in ROLE_MARKERS if marker in lowered or marker in query],
        "outcome": [marker for marker in OUTCOME_MARKERS if marker in lowered or marker in query],
        "vertical": [marker for marker in VERTICAL_MARKERS if marker in lowered or marker in query],
        "workflow": [marker for marker in WORKFLOW_MARKERS if marker in lowered or marker in query],
    }


def score_catalog_item(
    query_tokens: list[str],
    text: str,
    slug: str,
    label: str,
    description: str,
    presets: list[str],
    seed: dict | None = None,
) -> dict:
    lowered = text.lower()
    haystack_parts = [slug, label, description, *presets]
    if seed:
        haystack_parts.extend(seed.keys())
        haystack_parts.extend(str(value) for value in seed.values())
    haystack_tokens = tokenize(" ".join(haystack_parts))
    score = 0
    matched_terms: list[str] = []

    for exact in [slug, label]:
        if exact.lower() in lowered:
            score += 8
            matched_terms.append(exact)

    for preset in presets:
        if preset.lower() in lowered:
            score += 5
            matched_terms.append(preset)

    for token in query_tokens:
        if token in haystack_tokens:
            score += 2
            matched_terms.append(token)
        elif any(token in candidate or candidate in token for candidate in haystack_tokens):
            score += 1

    if seed:
        for key, value in seed.items():
            value_text = str(value).lower()
            if isinstance(value, str) and value and value_text in lowered:
                score += 3
                matched_terms.append(f"{key}:{value}")

    return {
        "slug": slug,
        "label": label,
        "description": description,
        "presets": presets,
        "score": score,
        "matched_terms": sorted(set(matched_terms)),
    }


def build_catalog() -> list[dict]:
    items: list[dict] = []
    family_maps = [
        ("single", PRESETS),
        ("combo", TEMPLATE_BUNDLES),
        ("vertical", VERTICAL_STARTERS),
        ("launch-board", LAUNCH_BOARDS),
        ("manager-board", MANAGER_BOARDS),
        ("cadence-board", CADENCE_BOARDS),
    ]
    for family, mapping in family_maps:
        for slug, item in mapping.items():
            presets = [slug] if family == "single" else list(item["presets"])
            items.append(
                {
                    "family": family,
                    "slug": slug,
                    "label": item["label"],
                    "description": item["description"],
                    "presets": presets,
                    "seed": item.get("seed", {}),
                }
            )
    return items


def recommend_family(query: str) -> tuple[dict, list[dict]]:
    scores = []
    traits = detect_query_traits(query)

    for family in ENTRY_FAMILIES:
        score, matched = score_keywords(query, family["keywords"])
        if traits["board_intent"]:
            score += 2
            matched.append("explicit-board-intent")
        if family["family"] == "cadence-board" and traits["cadence"]:
            score += 4
            matched.append("cadence-priority")
        if family["family"] == "manager-board" and traits["role"]:
            score += 3
            matched.append("role-priority")
        if family["family"] == "launch-board" and traits["outcome"]:
            score += 3
            matched.append("outcome-priority")
        if family["family"] == "vertical" and traits["vertical"]:
            score += 1
            matched.append("vertical-context")
        if family["family"] == "vertical" and traits["workflow"]:
            score -= 2
            matched.append("workflow-penalty")
        if family["family"] == "vertical" and traits["vertical"] and traits["cadence"] and traits["board_intent"]:
            score += 5
            matched.append("hybrid-vertical-cadence-priority")
        scores.append(
            {
                "family": family["family"],
                "label": family["label"],
                "description": family["description"],
                "score": score,
                "matched_signals": sorted(set(matched)),
                "fallbacks": family["fallbacks"],
            }
        )

    scores.sort(key=lambda item: item["score"], reverse=True)
    top = scores[0]
    if top["score"] == 0:
        default_family = next(item for item in scores if item["family"] == "launch-board")
        top = {**default_family, "matched_signals": ["default-launch-board-fallback"]}
    return top, scores


def recommend_items(query: str, family: str, limit: int = 3) -> list[dict]:
    query_tokens = tokenize(query)
    traits = detect_query_traits(query)
    candidates = []
    for item in build_catalog():
        if item["family"] != family:
            continue
        scored = score_catalog_item(
            query_tokens,
            query,
            item["slug"],
            item["label"],
            item["description"],
            item["presets"],
            item.get("seed"),
        )

        if family == "vertical" and traits["vertical"] and traits["cadence"] and traits["board_intent"]:
            if "category:Beauty" in scored["matched_terms"] or "platform:TikTok" in scored["matched_terms"] or "platform:Douyin" in scored["matched_terms"]:
                scored["score"] += 6
                scored["matched_terms"] = sorted(set([*scored["matched_terms"], "hybrid-query-boost"]))
        if family == "cadence-board" and traits["vertical"] and traits["cadence"] and traits["board_intent"]:
            scored["score"] += 2
            scored["matched_terms"] = sorted(set([*scored["matched_terms"], "cadence-board-intent"]))

        candidates.append({"family": family, **scored})
    candidates.sort(key=lambda item: item["score"], reverse=True)
    return candidates[:limit]


def recommend_fallbacks(query: str, families: list[str], per_family: int = 2) -> list[dict]:
    fallback_items: list[dict] = []
    seen: set[str] = set()
    for family in families:
        for item in recommend_items(query, family, limit=per_family):
            key = f"{family}:{item['slug']}"
            if key in seen:
                continue
            seen.add(key)
            fallback_items.append({"family": family, **item})
    return fallback_items


def load_bundle_index(bundle_root: str) -> dict[str, dict]:
    if not bundle_root.strip():
        return {}
    index_path = Path(bundle_root).expanduser().resolve() / "template-index.json"
    if not index_path.exists():
        return {}
    payload = json.loads(index_path.read_text(encoding="utf-8-sig"))
    items = payload.get("items", [])
    if not isinstance(items, list):
        return {}
    result: dict[str, dict] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        slug = str(item.get("slug", "")).strip()
        item_type = str(item.get("type", "")).strip()
        if slug and item_type:
            result[f"{item_type}:{slug}"] = item
    return result


def build_bundle_generation_command() -> str:
    workspace_root = Path(__file__).resolve().parents[2]
    suggested_root = workspace_root / ".codex-tmp" / "preset-template-bundle-latest"
    return f'python scripts/generate_batch_preset.py --template-bundle-root "{suggested_root}"'


def discover_latest_bundle_root() -> str:
    workspace_root = Path(__file__).resolve().parents[2]
    search_roots = [
        workspace_root / ".codex-tmp",
        Path(__file__).resolve().parents[1] / "tmp",
    ]
    candidates: list[Path] = []
    for root in search_roots:
        if not root.exists():
            continue
        for path in root.glob("preset-template-bundle*"):
            if (path / "template-index.json").exists():
                candidates.append(path.resolve())
    if not candidates:
        return ""
    candidates.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    return str(candidates[0])


def resolve_bundle_root(bundle_root: str) -> str:
    if bundle_root.strip():
        index_path = Path(bundle_root).expanduser().resolve() / "template-index.json"
        return str(index_path.parent) if index_path.exists() else ""
    return discover_latest_bundle_root()


def enrich_with_bundle_paths(items: list[dict], bundle_items: dict[str, dict]) -> list[dict]:
    enriched = []
    for item in items:
        bundle_key = f"{item['family']}:{item['slug']}"
        if item["family"] == "vertical":
            bundle_key = f"vertical:{item['slug']}"
        bundle_item = bundle_items.get(bundle_key, {})
        merged = {**item}
        for key in [
            "template_file",
            "suggested_output_file",
            "suite_root",
            "suite_config_json",
            "suite_queue_json",
            "suite_generate_ps1",
            "suite_dry_run_ps1",
            "suite_run_ps1",
        ]:
            if key in bundle_item:
                merged[key] = bundle_item[key]
        enriched.append(merged)
    return enriched


def build_next_steps(item: dict) -> list[str]:
    steps: list[str] = []
    if item.get("suite_generate_ps1"):
        steps.append(f'powershell -ExecutionPolicy Bypass -File "{item["suite_generate_ps1"]}"')
    elif item.get("template_file"):
        steps.append(f'python scripts/generate_batch_preset.py --config "{item["template_file"]}"')
    if item.get("suite_dry_run_ps1"):
        steps.append(f'powershell -ExecutionPolicy Bypass -File "{item["suite_dry_run_ps1"]}"')
    if item.get("suite_run_ps1"):
        steps.append(f'powershell -ExecutionPolicy Bypass -File "{item["suite_run_ps1"]}"')
    return steps


def render_markdown(
    query: str,
    family_pick: dict,
    family_scores: list[dict],
    picks: list[dict],
    fallbacks: list[dict],
) -> str:
    resolved_bundle_root = family_pick.get("resolved_bundle_root", "")
    lines = [
        "# Entry Board Recommendation",
        "",
        f"- query: `{query}`",
        f"- recommended family: `{family_pick['family']}`",
        f"- why: {family_pick['description']}",
        f"- matched signals: `{', '.join(family_pick['matched_signals']) if family_pick['matched_signals'] else 'none'}`",
        "",
        "## Bundle Context",
        "",
        f"- resolved bundle root: `{resolved_bundle_root or 'none'}`",
        "",
        "## Recommended Boards",
        "",
    ]
    for item in picks:
        lines.extend(
            [
                f"### {item['label']}",
                f"- slug: `{item['slug']}`",
                f"- score: `{item['score']}`",
                f"- presets: `{', '.join(item['presets'])}`",
                f"- matched terms: `{', '.join(item['matched_terms']) if item['matched_terms'] else 'none'}`",
                f"- description: {item['description']}",
                f"- template file: `{item.get('template_file', '') or 'n/a'}`",
                f"- suite root: `{item.get('suite_root', '') or 'n/a'}`",
                "",
            ]
        )
        next_steps = build_next_steps(item)
        if next_steps:
            lines.append("#### Next Steps")
            for step in next_steps:
                lines.append(f"- `{step}`")
            lines.append("")

    lines.extend(["## Fallback Suggestions", ""])
    for item in fallbacks:
        lines.append(f"- `{item['family']}` -> `{item['slug']}`: {item['description']}")

    lines.extend(["", "## Family Scoreboard", ""])
    for item in family_scores:
        signals = ", ".join(item["matched_signals"]) if item["matched_signals"] else "none"
        lines.append(f"- `{item['family']}` score=`{item['score']}` signals=`{signals}`")
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    family_pick, family_scores = recommend_family(args.query)
    picks = recommend_items(args.query, family_pick["family"])
    if not picks and family_pick["family"] == "single":
        fallback_family = "combo"
        picks = recommend_items(args.query, fallback_family)
        family_pick = {
            **family_pick,
            "family": fallback_family,
            "label": "Combo Board",
            "description": "Single-preset requests without a direct single-board catalog fall back to combo-board selection.",
            "matched_signals": family_pick["matched_signals"] + ["single-family-fallback-to-combo"],
        }

    fallbacks = recommend_fallbacks(args.query, family_pick["fallbacks"])
    resolved_bundle_root = resolve_bundle_root(args.bundle_root)
    bundle_items = load_bundle_index(resolved_bundle_root)
    picks = enrich_with_bundle_paths(picks, bundle_items)
    fallbacks = enrich_with_bundle_paths(fallbacks, bundle_items)
    family_pick = {**family_pick, "resolved_bundle_root": resolved_bundle_root}

    payload = {
        "query": args.query,
        "bundle_root": args.bundle_root,
        "resolved_bundle_root": resolved_bundle_root,
        "suggested_bundle_generation_command": "" if resolved_bundle_root else build_bundle_generation_command(),
        "recommended_family": family_pick["family"],
        "family_description": family_pick["description"],
        "matched_signals": family_pick["matched_signals"],
        "recommended_boards": picks,
        "fallback_suggestions": fallbacks,
        "family_scoreboard": family_scores,
    }

    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print(render_markdown(args.query, family_pick, family_scores, picks, fallbacks))


if __name__ == "__main__":
    main()
