from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from generate_scene_report import load_catalog


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
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


GOAL_CHAINS = {
    "viral-discovery": {
        "label": "Viral Discovery",
        "description": "Find winning content patterns from search through teardown.",
        "scenes": ["01", "03", "17"],
        "keywords": [
            "viral",
            "discovery",
            "search",
            "teardown",
            "hook",
            "viral video",
            "topic mining",
            "爆款",
            "选题",
            "拆解",
            "钩子",
        ],
        "why": [
            "Scene 01 collects and ranks candidate videos.",
            "Scene 03 converts the shortlist into reusable pattern rules.",
            "Scene 17 helps distill repeatable creator patterns when one creator dominates the shortlist.",
        ],
    },
    "category-entry": {
        "label": "Category Entry",
        "description": "Decide whether a category is worth entering and what angle to pursue.",
        "scenes": ["01", "07", "08", "09"],
        "keywords": [
            "category",
            "entry",
            "market",
            "insight",
            "opportunity",
            "category research",
            "market opportunity",
            "选品",
            "品类",
            "市场",
            "机会",
        ],
        "why": [
            "Scene 01 builds the initial candidate board.",
            "Scene 07 produces the market-level judgment.",
            "Scene 08 extracts user language and unmet needs.",
            "Scene 09 converts the insight into a replication-ready brief.",
        ],
    },
    "creative-testing": {
        "label": "Creative Testing",
        "description": "Turn one product into a repeatable multi-angle testing program.",
        "scenes": ["10", "12", "11", "14"],
        "keywords": [
            "creative",
            "testing",
            "matrix",
            "variant",
            "brief",
            "creative test",
            "asset family",
            "素材",
            "测试",
            "矩阵",
            "脚本",
        ],
        "why": [
            "Scene 10 creates the first video brief from available product assets.",
            "Scene 12 expands one product into multiple testable styles.",
            "Scene 11 turns those directions into a repeatable pipeline.",
            "Scene 14 defines the wider launch asset family around the same message.",
        ],
    },
    "localization": {
        "label": "Localization",
        "description": "Adapt one product or concept across markets and localized assets.",
        "scenes": ["13", "15", "16"],
        "keywords": [
            "localization",
            "translate",
            "market",
            "language",
            "multi-market",
            "localized launch",
            "本地化",
            "翻译",
            "多市场",
            "主图",
        ],
        "why": [
            "Scene 13 handles market-level adaptation of concept and hook.",
            "Scene 15 localizes image copy and text hierarchy.",
            "Scene 16 benchmarks the main image direction against competitors.",
        ],
    },
    "competitor-monitoring": {
        "label": "Competitor Monitoring",
        "description": "Track products, accounts, and weekly shifts from competitors.",
        "scenes": ["06", "18", "17"],
        "keywords": [
            "competitor",
            "monitoring",
            "weekly",
            "dashboard",
            "competitor weekly",
            "account tracking",
            "对手",
            "竞品",
            "监控",
            "周报",
        ],
        "why": [
            "Scene 06 sets up the competitor product tracking layer.",
            "Scene 18 reviews weekly content and pattern changes across accounts.",
            "Scene 17 helps distill one standout creator or account into reusable patterns.",
        ],
    },
    "account-improvement": {
        "label": "Account Improvement",
        "description": "Review your own account, compare with the market, and define the next cycle.",
        "scenes": ["19", "18", "12"],
        "keywords": [
            "account",
            "improvement",
            "retro",
            "optimization",
            "content review",
            "next cycle",
            "复盘",
            "优化",
            "账号",
            "下一轮测试",
        ],
        "why": [
            "Scene 19 diagnoses what is working and failing on your own account.",
            "Scene 18 adds competitor context for what changed in the market.",
            "Scene 12 converts the retro into the next testing matrix.",
        ],
    },
    "publish-handoff": {
        "label": "Publish Handoff",
        "description": "Move from brief to publish-ready operator materials.",
        "scenes": ["09", "12", "14"],
        "keywords": [
            "publish",
            "handoff",
            "title",
            "cover",
            "caption",
            "publish prep",
            "launch handoff",
            "发布",
            "封面",
            "标题",
            "交付",
        ],
        "why": [
            "Scene 09 creates the adapted execution brief.",
            "Scene 12 creates the test matrix for variant planning.",
            "Scene 14 organizes the asset family needed for launch or posting.",
        ],
        "packs": ["publish-prep", "creative-production-handoff"],
    },
    "creative-production-handoff": {
        "label": "Creative Production Handoff",
        "description": "Turn creative briefs into production-ready handoff packs for scripting, editing, design, or localization.",
        "scenes": ["09", "10", "12", "13", "14", "15", "16"],
        "keywords": [
            "creative handoff",
            "production handoff",
            "render handoff",
            "design handoff",
            "script handoff",
            "制作交接",
            "创意交付",
            "渲染交接",
            "设计交接",
            "脚本交接",
        ],
        "why": [
            "Scene 09 defines the adapted reference logic and shot order.",
            "Scene 10 translates limited product assets into executable video structure.",
            "Scene 12 separates invariant message from variant production lanes.",
            "Scenes 13, 15, and 16 surface localization, layout, and visual-direction handoff needs.",
            "Scene 14 prioritizes the asset family and production sequence.",
        ],
        "packs": ["creative-production-handoff"],
    },
    "live-support": {
        "label": "Live Support",
        "description": "Prepare inputs for a live-room operator pack.",
        "scenes": ["08", "18", "19"],
        "keywords": [
            "live",
            "support",
            "moderator",
            "room",
            "live session",
            "host prompts",
            "直播",
            "场控",
            "主持",
            "话术",
        ],
        "why": [
            "Scene 08 clarifies audience pains and language.",
            "Scene 18 provides competitor live-content context and recent shifts.",
            "Scene 19 surfaces your own account lessons before the live session.",
        ],
        "packs": ["live-assist"],
    },
}

GOAL_TEMPLATES = [
    {
        "slug": "topic-to-publish",
        "label": "Topic To Publish",
        "description": "Go from topic selection to creative testing and publish handoff.",
        "keywords": [
            "topic to publish",
            "topic selection to publish",
            "creative testing to publish",
            "douyin workflow",
            "选题到发布",
            "素材测试到发布",
            "发布交付",
        ],
        "goals": ["category-entry", "creative-testing", "publish-handoff"],
    },
    {
        "slug": "competitor-weekly-and-breakdown",
        "label": "Competitor Weekly And Breakdown",
        "description": "Track competitors weekly and distill the strongest creator or content pattern.",
        "keywords": [
            "competitor weekly",
            "creator breakdown",
            "competitor monitoring",
            "竞品周报",
            "达人拆解",
            "竞品监控",
        ],
        "goals": ["competitor-monitoring"],
    },
    {
        "slug": "account-retro-to-next-test",
        "label": "Account Retro To Next Test",
        "description": "Review account performance and turn it into the next testing cycle.",
        "keywords": [
            "account retro",
            "account improvement",
            "next test",
            "content retro",
            "账号复盘",
            "下一轮测试",
            "内容优化",
        ],
        "goals": ["account-improvement"],
    },
    {
        "slug": "viral-to-testing",
        "label": "Viral To Testing",
        "description": "Go from viral discovery and teardown to a structured testing program.",
        "keywords": [
            "viral to testing",
            "teardown to testing",
            "hook testing",
            "爆款拆解到测试",
            "选题拆解到测试",
            "爆款到矩阵",
        ],
        "goals": ["viral-discovery", "creative-testing"],
    },
    {
        "slug": "category-to-localized-launch",
        "label": "Category To Localized Launch",
        "description": "Research a category, localize the angle, and prepare publish-ready launch materials.",
        "keywords": [
            "localized launch",
            "multi market launch",
            "category to localization",
            "本地化发布",
            "多市场发布",
            "选品到本地化",
        ],
        "goals": ["category-entry", "localization", "publish-handoff"],
    },
    {
        "slug": "competitor-to-publish",
        "label": "Competitor To Publish",
        "description": "Use competitor monitoring to drive creative testing and publish handoff.",
        "keywords": [
            "competitor to publish",
            "monitoring to launch",
            "competitor inspired launch",
            "竞品到发布",
            "竞品复刻",
            "竞品监控到发布",
        ],
        "goals": ["competitor-monitoring", "creative-testing", "publish-handoff"],
    },
    {
        "slug": "audience-to-live",
        "label": "Audience To Live",
        "description": "Turn category insight and audience language into a live-room operator workflow.",
        "keywords": [
            "audience to live",
            "comment to live",
            "live selling workflow",
            "评论到直播",
            "人群语言到直播",
            "直播话术",
        ],
        "goals": ["category-entry", "live-support"],
    },
    {
        "slug": "weekly-monitor-to-next-test",
        "label": "Weekly Monitor To Next Test",
        "description": "Use competitor monitoring and account retro to define the next testing cycle.",
        "keywords": [
            "weekly monitor to next test",
            "weekly review to next cycle",
            "competitor and retro",
            "周报到下一轮测试",
            "监控到复盘",
            "竞品周报到测试",
        ],
        "goals": ["competitor-monitoring", "account-improvement"],
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Recommend an end-to-end scene chain for a TikTok Growth Operator business goal."
    )
    parser.add_argument("--goal", choices=sorted(GOAL_CHAINS), help="Goal slug to map into a recommended scene chain.")
    parser.add_argument("--query", help="Free-text business goal to match to the closest chain.")
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="markdown",
        help="Output format.",
    )
    return parser.parse_args()


def tokenize(text: str) -> list[str]:
    tokens = [token for token in re.split(r"[^a-zA-Z0-9\u4e00-\u9fff]+", text.lower()) if token]
    return [token for token in tokens if token not in STOPWORDS and (len(token) > 1 or re.search(r"[\u4e00-\u9fff]", token))]


def keyword_score(query: str, keywords: list[str]) -> int:
    lowered = query.lower()
    score = 0
    for keyword in keywords:
        key = keyword.lower().strip()
        if key and key in lowered:
            score += max(2, len(key))
    return score


def build_multi_goal_payload(goals: list[str], label: str, description: str) -> dict:
    skill_root = Path(__file__).resolve().parents[1]
    catalog = {item["id"]: item for item in load_catalog(skill_root)}
    ordered_scene_ids: list[str] = []
    combined_why: list[str] = []
    combined_packs: list[str] = []
    for goal in goals:
        chain = GOAL_CHAINS[goal]
        for scene_id in chain["scenes"]:
            if scene_id not in ordered_scene_ids:
                ordered_scene_ids.append(scene_id)
        for item in chain["why"]:
            if item not in combined_why:
                combined_why.append(item)
        for pack in chain.get("packs", []):
            if pack not in combined_packs:
                combined_packs.append(pack)
    ordered_scenes = []
    for scene_id in ordered_scene_ids:
        scene = catalog[scene_id]
        ordered_scenes.append(
            {
                "id": scene["id"],
                "title": scene["title"],
                "slug": scene["slug"],
                "deliverable_type": scene["deliverable_type"],
                "summary": scene["summary"],
                "scenario_file": scene["scenario_file"],
            }
        )
    return {
        "goal": "+".join(goals),
        "label": label,
        "description": description,
        "scenes": ordered_scenes,
        "why": combined_why,
        "packs": combined_packs,
        "component_goals": goals,
    }


def match_template_from_query(query: str) -> tuple[str, dict] | None:
    lowered = query.lower()
    scored_templates: list[tuple[int, dict]] = []
    for template in GOAL_TEMPLATES:
        score = keyword_score(lowered, template["keywords"])
        if score > 0:
            scored_templates.append((score, template))
    if not scored_templates:
        return None
    scored_templates.sort(key=lambda item: item[0], reverse=True)
    best_score, template = scored_templates[0]
    payload = build_multi_goal_payload(template["goals"], template["label"], template["description"])
    payload["matched_from_query"] = query
    payload["match_score"] = best_score
    payload["matched_template"] = template["slug"]
    payload["candidate_templates"] = [
        {"template": item["slug"], "score": score} for score, item in scored_templates[:3]
    ]
    return payload["goal"], payload


def build_payload(goal: str) -> dict:
    skill_root = Path(__file__).resolve().parents[1]
    catalog = {item["id"]: item for item in load_catalog(skill_root)}
    chain = GOAL_CHAINS[goal]
    ordered_scenes = []
    for scene_id in chain["scenes"]:
        scene = catalog[scene_id]
        ordered_scenes.append(
            {
                "id": scene["id"],
                "title": scene["title"],
                "slug": scene["slug"],
                "deliverable_type": scene["deliverable_type"],
                "summary": scene["summary"],
                "scenario_file": scene["scenario_file"],
            }
        )
    return {
        "goal": goal,
        "label": chain["label"],
        "description": chain["description"],
        "scenes": ordered_scenes,
        "why": chain["why"],
        "packs": chain.get("packs", []),
    }


def match_goal_from_query(query: str) -> tuple[str, dict]:
    template_match = match_template_from_query(query)
    if template_match is not None:
        return template_match

    query_tokens = tokenize(query)
    scores: list[tuple[int, str]] = []
    for goal, config in GOAL_CHAINS.items():
        score = keyword_score(query, [goal, config["label"], config["description"], *config.get("keywords", [])])
        haystack = tokenize(" ".join([goal, config["label"], config["description"], *config.get("keywords", [])]))
        for token in query_tokens:
            if token in haystack:
                score += 3
            elif any(token in item or item in token for item in haystack):
                score += 1
        scores.append((score, goal))
    scores.sort(reverse=True)
    best_score, best_goal = scores[0]
    payload = build_payload(best_goal)
    payload["matched_from_query"] = query
    payload["match_score"] = best_score
    payload["candidate_goals"] = [{"goal": goal, "score": score} for score, goal in scores[:3]]
    return best_goal, payload


def render_markdown(payload: dict) -> str:
    lines = [
        f"# {payload['label']}",
        "",
        payload["description"],
        "",
        "## Recommended Scene Chain",
        "",
    ]
    for index, scene in enumerate(payload["scenes"], start=1):
        lines.append(
            f"{index}. Scene {scene['id']} - {scene['title']} | `{scene['deliverable_type']}` | `{scene['scenario_file']}`"
        )
    lines.append("")
    lines.append("## Why This Order")
    lines.append("")
    for item in payload["why"]:
        lines.append(f"- {item}")
    if payload["packs"]:
        lines.append("")
        lines.append("## Recommended Operator Packs")
        lines.append("")
        for item in payload["packs"]:
            lines.append(f"- {item}")
    if payload.get("matched_from_query") is not None:
        lines.append("")
        lines.append("## Match Detail")
        lines.append("")
        lines.append(f"- Query: {payload['matched_from_query']}")
        lines.append(f"- Chosen Goal: {payload['goal']}")
        lines.append(f"- Match Score: {payload.get('match_score', 0)}")
        if payload.get("matched_template"):
            lines.append(f"- Matched Template: {payload['matched_template']}")
        if payload.get("component_goals"):
            lines.append(f"- Component Goals: {', '.join(payload['component_goals'])}")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    args = parse_args()
    if bool(args.goal) == bool(args.query):
        raise SystemExit("Provide exactly one of --goal or --query.")
    payload = build_payload(args.goal) if args.goal else match_goal_from_query(args.query)[1]
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(payload), end="")


if __name__ == "__main__":
    main()
