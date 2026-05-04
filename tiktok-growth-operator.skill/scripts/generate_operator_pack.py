from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


PACK_DEFS = {
    "publish-prep": {
        "doc": "references/publish-prep-pack.md",
        "title": "Publish Preparation Pack",
        "filename": "publish-prep-pack.md",
        "sections": [
            ("Publish Goal", "State the specific publish objective for this asset."),
            ("Audience And Positioning", "Clarify who this post is for and how the account should sound."),
            ("Title Options", "Generate 5-10 publish title options."),
            ("Hook Options", "Generate short opening-hook options for caption or on-screen use."),
            ("Caption And CTA", "Draft 3-5 caption variants with CTA direction."),
            ("Hashtag Set", "List primary, secondary, and experimental hashtag groups."),
            ("Cover Direction", "Describe the recommended cover headline, image cue, and visual hierarchy."),
            ("Publish Checklist", "List the manual pre-publish checks."),
            ("Post-Publish Review Checklist", "List what to review in the first 30 minutes, 2 hours, and 24 hours."),
        ],
    },
    "live-assist": {
        "doc": "references/live-assist-pack.md",
        "title": "Live Assist Pack",
        "filename": "live-assist-pack.md",
        "sections": [
            ("Session Goal", "State what this live session needs to achieve."),
            ("Audience And Buying Context", "Clarify who is expected to watch and what buying context they are in."),
            ("Run Of Show", "Outline the live session flow from open to close."),
            ("Host Prompt Bank", "Write reusable host talking prompts."),
            ("Moderator Reply Bank", "Write reusable moderator replies for common chat situations."),
            ("Objection Handling", "List common objections and response frames."),
            ("Anomaly Checklist", "List what to watch for during the live session."),
            ("Escalation Rules", "Define when the operator should escalate or change flow."),
            ("Post-Live Review Checklist", "List what to review immediately after the session."),
        ],
    },
}

PUBLISH_FOCUS_BY_SCENE = {
    "09": "Keep the winning reference logic while replacing the product and CTA cleanly.",
    "10": "Turn static product assets into a simple publish-ready short-video angle without overcomplicating the first hook.",
    "11": "Convert the hot-video pipeline into a repeatable publish queue with clear variant ownership.",
    "12": "Preserve one invariant message while varying style families and hook packaging.",
    "13": "Localize titles, hooks, and CTA to the target market instead of literal translation only.",
    "14": "Coordinate title, cover, caption, and asset family so the launch message is consistent.",
    "15": "Protect text hierarchy and conversion clarity when localized copy is used on the cover or asset.",
    "16": "Outperform competitor click logic rather than imitate generic visual style.",
}

LIVE_FOCUS_BY_SCENE = {
    "08": "Use repeated user pains, desires, and exact user language as the backbone of live selling and moderation.",
    "18": "Use weekly competitor shifts to decide what themes, offers, and proof points the live session should emphasize or ignore.",
    "19": "Use self-account retro findings to reinforce winning talking tracks and remove weak live segments.",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def normalize_lines(values: list[str]) -> list[str]:
    return [item.strip() for item in values if item and item.strip()]


def unique_lines(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in normalize_lines(values):
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def take_section(report: dict, heading: str) -> dict:
    for section in report.get("sections", []) or []:
        if str(section.get("heading", "")).strip().lower() == heading.strip().lower():
            return section
    return {}


def section_to_lines(section: dict) -> list[str]:
    lines: list[str] = []
    for paragraph in section.get("paragraphs", []) or []:
        text = str(paragraph).strip()
        if text:
            lines.append(text)
    for bullet in section.get("bullets", []) or []:
        text = str(bullet).strip()
        if text:
            lines.append(f"- {text}")
    for index, item in enumerate(section.get("numbered", []) or [], start=1):
        text = str(item).strip()
        if text:
            lines.append(f"{index}. {text}")
    table = section.get("table") or {}
    headers = [str(item).strip() for item in table.get("headers", []) or [] if str(item).strip()]
    rows = table.get("rows", []) or []
    if headers:
        title = str(table.get("title", "")).strip()
        if title:
            lines.append(f"Table: {title}")
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for row in rows[:5]:
            cells = [str(cell).replace("\n", " ").strip() for cell in row]
            if len(cells) < len(headers):
                cells.extend([""] * (len(headers) - len(cells)))
            lines.append("| " + " | ".join(cells[: len(headers)]) + " |")
    return lines


def scene_text(scene_id: str, mapping: dict[str, str], fallback: str) -> str:
    return mapping.get(scene_id, fallback)


def scene_title_options(project: str, market: str, scene_id: str, executive_conclusion: str) -> list[str]:
    if scene_id == "09":
        return [
            f"- {project}: keep the winning structure, swap the product cleanly",
            f"- {project}: the reference logic worth adapting for {market}",
            f"- {project}: proof-first version of the winning short-video pattern",
            f"- {project}: same hook logic, stronger product fit",
            f"- {project}: adapt the reference, do not copy it blindly",
        ]
    if scene_id == "10":
        return [
            f"- {project}: turn product images into a result-first short video",
            f"- {project}: start from the final effect, not a static product intro",
            f"- {project}: simple product-image story that works faster",
            f"- {project}: image-to-video angle built for {market}",
            f"- {project}: quick visual proof before explanation",
        ]
    if scene_id == "11":
        return [
            f"- {project}: the next hot-video variant to publish first",
            f"- {project}: convert this trend into a safer new version",
            f"- {project}: one winning pattern, three publish directions",
            f"- {project}: publish queue from hot-video logic",
            f"- {project}: what to launch first from the current pipeline",
        ]
    if scene_id == "12":
        return [
            f"- {project}: one product, multiple styles, clearer first test",
            f"- {project}: same promise, different hook family",
            f"- {project}: which style version should go out first",
            f"- {project}: multi-style publish set for {market}",
            f"- {project}: keep the message, change the wrapper",
        ]
    if executive_conclusion:
        return [
            f"- {project}: result-first publish version",
            f"- {project}: fast proof version for {market}",
            f"- {project}: shorter path from hook to evidence",
            f"- {project}: what this content should lead with",
            f"- {project}: publish-ready angle from the source report",
        ]
    return [
        f"- {project}: result-first publish version",
        f"- {project}: simple hook + proof publish angle",
        f"- {project}: publish-ready message for {market}",
    ]


def scene_hook_options(project: str, scene_id: str, executive_conclusion: str) -> list[str]:
    base = executive_conclusion or f"Use the clearest proof path for {project} in the first seconds."
    if scene_id in {"09", "11"}:
        return unique_lines(
            [
                "- Start with the end result before any setup.",
                "- Show the winning pattern first, then explain why it transfers.",
                f"- {base}",
                f"- Do not introduce {project} slowly; prove the value immediately.",
            ]
        )
    if scene_id in {"10", "12"}:
        return unique_lines(
            [
                "- Lead with the clearest visual payoff, not the product image alone.",
                "- Show the easiest-to-understand proof before extra explanation.",
                f"- {base}",
                f"- For {project}, keep the first hook about result, not theory.",
            ]
        )
    return unique_lines(
        [
            "- Start from the strongest result or pain resolution.",
            f"- {base}",
            f"- Do not waste the first seconds with generic setup for {project}.",
        ]
    )


def build_publish_sections(report: dict, platform: str, market: str) -> dict[str, list[str]]:
    meta = report.get("metadata", {})
    ctx = report.get("working_context", {})
    executive = report.get("executive_summary", {})
    reusable = take_section(report, "Reusable Formula")
    structure = take_section(report, "Structure Logic")
    core = take_section(report, "Core Mechanism")
    next_action = take_section(report, "Next Action")
    evidence = report.get("evidence", []) or []

    scene_id = str(meta.get("scene", "")).strip()
    project = str(meta.get("project", "")).strip() or "this asset"
    conclusion = str(executive.get("conclusion", "")).strip()
    why = str(executive.get("why_it_matters", "")).strip()
    next_step = str(executive.get("next_action", "")).strip()
    scene_focus = scene_text(
        scene_id,
        PUBLISH_FOCUS_BY_SCENE,
        "Translate the source report into a publish-ready title, hook, cover, caption, and review pack.",
    )

    reusable_lines = section_to_lines(reusable)
    structure_lines = section_to_lines(structure)
    core_lines = section_to_lines(core)
    next_action_lines = section_to_lines(next_action)

    return {
        "Working Context": unique_lines(
            [
                str(ctx.get("summary", "")).strip(),
                f"Platform: {platform}",
                f"Market: {market}",
                f"Source scene: {scene_id} - {meta.get('scene_title', '')}".strip(),
                f"Publish focus: {scene_focus}",
            ]
        ),
        "Publish Goal": unique_lines(
            [
                next_step,
                why,
                f"Prepare a publish-ready handoff for {project}.",
                scene_focus,
            ]
        ),
        "Audience And Positioning": unique_lines(
            list(ctx.get("inputs", []) or [])
            + [
                conclusion,
                "Keep the account voice aligned with the winning content pattern instead of generic brand narration.",
            ]
        ),
        "Title Options": scene_title_options(project, market, scene_id, conclusion),
        "Hook Options": scene_hook_options(project, scene_id, conclusion),
        "Caption And CTA": unique_lines(
            [
                conclusion,
                "Caption variant 1: state the result first, then compress the proof path.",
                "Caption variant 2: lead with the strongest user-facing payoff and remove non-essential explanation.",
                "Caption variant 3: pair one clear conclusion with one simple action request.",
                "CTA direction: ask for one action only, such as comment, save, or view the next proof step.",
            ]
            + next_action_lines[:2]
        ),
        "Hashtag Set": unique_lines(
            [
                f"- Primary: #{platform.lower()} #shortvideo #contentstrategy",
                f"- Secondary: #{project.replace(' ', '')} #{market.replace(' ', '')}",
                f"- Experimental: #hooktest #prooffirst #scene{scene_id or 'x'}",
            ]
        ),
        "Cover Direction": unique_lines(
            [
                f"Use one high-clarity visual that matches the core promise for {project}.",
                "Put the promise or visible result in the largest text layer.",
                "Avoid crowded decorative copy. Tie the cover directly to the first hook.",
            ]
            + reusable_lines[:3]
            + core_lines[:2]
        ),
        "Publish Checklist": unique_lines(
            [
                "- Confirm title, hook, caption, and cover all express the same promise.",
                "- Check the first-frame visual matches the opening line.",
                "- Ensure the CTA asks for one action only.",
                "- Verify tags and market language fit the platform and audience.",
                "- Remove any claim that the source evidence does not support.",
            ]
        ),
        "Post-Publish Review Checklist": unique_lines(
            [
                "- 30 minutes: check whether viewers understand the hook and whether early comments match the intended angle.",
                "- 2 hours: compare engagement quality against recent baseline posts.",
                "- 24 hours: decide whether to iterate title family, proof device, or cover message next.",
                f"- Evidence references used: {len(evidence)} items from the source report.",
            ]
        ),
        "_reference": unique_lines(
            [
                f"Reference doc: {PACK_DEFS['publish-prep']['doc']}",
                f"Derived from source report: {meta.get('title', '')}",
            ]
            + structure_lines[:4]
        ),
    }


def build_live_sections(report: dict, platform: str, market: str) -> dict[str, list[str]]:
    meta = report.get("metadata", {})
    ctx = report.get("working_context", {})
    executive = report.get("executive_summary", {})
    evidence_clusters = take_section(report, "Evidence Clusters")
    recommended = take_section(report, "Recommended Action")
    high_level = take_section(report, "High-Level Judgment")
    open_questions = take_section(report, "Open Questions")
    evidence = report.get("evidence", []) or []

    scene_id = str(meta.get("scene", "")).strip()
    project = str(meta.get("project", "")).strip() or "this live session"
    conclusion = str(executive.get("conclusion", "")).strip()
    why = str(executive.get("why_it_matters", "")).strip()
    next_step = str(executive.get("next_action", "")).strip()
    scene_focus = scene_text(
        scene_id,
        LIVE_FOCUS_BY_SCENE,
        "Translate the source report into a live operator pack with stronger prompts, moderation logic, and review checkpoints.",
    )

    evidence_cluster_lines = section_to_lines(evidence_clusters)
    recommended_lines = section_to_lines(recommended)
    high_level_lines = section_to_lines(high_level)
    open_question_lines = section_to_lines(open_questions)

    host_lines = [
        "- Start with the clearest user-facing payoff before longer explanation.",
        "- Restate the audience's core concern in plain language, then answer it with proof.",
        "- Move back to evidence whenever trust or attention drops.",
        "- Keep each explanation short enough that the moderator can reinforce it in chat.",
    ]
    if scene_id == "08":
        host_lines.extend(
            [
                "- Reuse the highest-frequency user phrases instead of inventing polished marketing language.",
                "- When a pain point repeats, name it directly before offering a solution frame.",
            ]
        )
    elif scene_id == "18":
        host_lines.extend(
            [
                "- Emphasize what competitors shifted toward only if it matches the audience problem.",
                "- Do not chase every competitor theme; reinforce only the strongest weekly signal.",
            ]
        )
    elif scene_id == "19":
        host_lines.extend(
            [
                "- Double down on the talking tracks that already worked on the account.",
                "- Remove segments that mirror the account's recent weak content patterns.",
            ]
        )

    moderator_lines = [
        "- For repeated questions, summarize the concern first and answer with the shortest useful reply.",
        "- Group comments into price, trust, fit, and complexity before replying.",
        "- Pull the chat back to one clear thread if too many side questions appear at once.",
        "- Escalate to the host when the same objection appears three or more times.",
    ]
    if scene_id == "08":
        moderator_lines.append("- Reuse the audience's own wording when acknowledging pains or objections.")

    return {
        "Working Context": unique_lines(
            [
                str(ctx.get("summary", "")).strip(),
                f"Platform: {platform}",
                f"Market: {market}",
                f"Source scene: {scene_id} - {meta.get('scene_title', '')}".strip(),
                f"Live focus: {scene_focus}",
            ]
        ),
        "Session Goal": unique_lines(
            [
                next_step,
                why,
                f"Convert the source report into a live-session operator pack for {project}.",
                scene_focus,
            ]
        ),
        "Audience And Buying Context": unique_lines(
            list(ctx.get("inputs", []) or [])
            + [
                conclusion,
                "Use the strongest source-report language patterns instead of generic promotional wording.",
            ]
        ),
        "Run Of Show": unique_lines(
            [
                "1. Open with the clearest value promise in the first minute.",
                "2. Show proof early before long explanation.",
                "3. Reinforce the best audience-language cues during demonstration.",
                "4. Handle objections in short cycles instead of long monologues.",
                "5. Close with one clean action and one reason to act now.",
            ]
            + high_level_lines[:4]
        ),
        "Host Prompt Bank": unique_lines(host_lines + evidence_cluster_lines[:4]),
        "Moderator Reply Bank": unique_lines(moderator_lines),
        "Objection Handling": unique_lines(
            [
                "- Objection type: price -> explain value and proof before the offer.",
                "- Objection type: doubt -> lead with visible evidence or repeated user language.",
                "- Objection type: complexity -> reduce to one simple action or use case.",
                "- Objection type: fit -> clarify who this is for and who it is not for.",
            ]
            + recommended_lines[:4]
        ),
        "Anomaly Checklist": unique_lines(
            [
                "- Sudden repeated confusion in comments around the core claim.",
                "- Drop in engagement after a long explanation block.",
                "- Repeated trust objections that are not answered by current proof.",
                "- Off-topic chat pulling the host away from the conversion path.",
            ]
            + open_question_lines[:2]
        ),
        "Escalation Rules": unique_lines(
            [
                "- If the same objection repeats three or more times, the host should address it directly on stream.",
                "- If the current talking path is losing attention, switch back to proof or demonstration.",
                "- If chat splits across too many questions, the moderator should force a single question queue.",
                "- If trust is weak, increase evidence density before pushing CTA again.",
            ]
        ),
        "Post-Live Review Checklist": unique_lines(
            [
                "- Review which prompts created the strongest response.",
                "- Review which objections repeated and were not cleanly closed.",
                "- Review what proof moment increased attention or conversion confidence.",
                f"- Evidence references used: {len(evidence)} items from the source report.",
            ]
        ),
        "_reference": unique_lines(
            [
                f"Reference doc: {PACK_DEFS['live-assist']['doc']}",
                f"Derived from source report: {meta.get('title', '')}",
            ]
        ),
    }


def build_derived_sections(pack_type: str, report: dict, platform: str, market: str) -> dict[str, list[str]]:
    if pack_type == "publish-prep":
        return build_publish_sections(report, platform, market)
    if pack_type == "live-assist":
        return build_live_sections(report, platform, market)
    return {}


def render_pack(
    pack_type: str,
    project: str,
    platform: str,
    market: str,
    context: str,
    derived_sections: dict[str, list[str]] | None = None,
) -> str:
    pack = PACK_DEFS[pack_type]
    lines = [
        f"# {pack['title']}",
        "",
        f"- Project: {project}",
        f"- Platform: {platform}",
        f"- Market: {market}",
        f"- Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"- Pack Type: {pack_type}",
        "",
        "## Working Context",
        "",
    ]
    working_context_lines = (derived_sections or {}).get("Working Context", [])
    if working_context_lines:
        lines.extend(working_context_lines)
    else:
        lines.append(context.strip() or "_Add the user brief, product notes, asset notes, or live-session notes here._")
    lines.extend(["", "## Reference", ""])
    for item in (derived_sections or {}).get("_reference", [f"`{pack['doc']}`"]):
        lines.append(f"- {item}" if not item.startswith("`") else f"- {item}")
    lines.append("")

    for heading, instruction in pack["sections"]:
        lines.extend([f"## {heading}", "", f"_{instruction}_", ""])
        seeded = (derived_sections or {}).get(heading, [])
        if seeded:
            lines.extend(seeded)
        else:
            lines.append("_Fill this section._")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def generate_pack_output(
    pack_type: str,
    output_dir: Path,
    project: str = "",
    platform: str = "Douyin",
    market: str = "China",
    context: str = "",
    source_report_path: Path | None = None,
) -> dict:
    report = None
    derived_sections = None
    resolved_project = project.strip()
    if source_report_path:
        report = load_json(source_report_path.resolve())
        resolved_project = resolved_project or str(report.get("metadata", {}).get("project", "")).strip()
        derived_sections = build_derived_sections(pack_type, report, platform, market)
    if not resolved_project:
        raise SystemExit("Provide project, or provide source_report_path with metadata.project.")

    pack = PACK_DEFS[pack_type]
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / pack["filename"]
    output_path.write_text(
        render_pack(pack_type, resolved_project, platform, market, context, derived_sections),
        encoding="utf-8-sig",
    )
    manifest = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "type": pack_type,
        "project": resolved_project,
        "platform": platform,
        "market": market,
        "reference_doc": pack["doc"],
        "output_path": str(output_path),
        "source_report": str(source_report_path.resolve()) if source_report_path else "",
    }
    manifest_path = output_dir / f"{pack_type}-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    return {
        "output_path": str(output_path),
        "manifest_path": str(manifest_path),
        "type": pack_type,
        "project": resolved_project,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a direct-use operator pack for publish preparation or live assist."
    )
    parser.add_argument("--type", required=True, choices=sorted(PACK_DEFS.keys()), help="Operator pack type.")
    parser.add_argument("--project", default="", help="Project or campaign name.")
    parser.add_argument("--platform", default="Douyin", help="Platform label, e.g. Douyin or TikTok.")
    parser.add_argument("--market", default="China", help="Target market label.")
    parser.add_argument("--context-file", default=None, help="Optional UTF-8 context file.")
    parser.add_argument("--source-report", default=None, help="Optional structured scene report JSON file.")
    parser.add_argument("--output-dir", required=True, help="Output directory.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    context = Path(args.context_file).read_text(encoding="utf-8") if args.context_file else ""
    result = generate_pack_output(
        pack_type=args.type,
        output_dir=Path(args.output_dir).resolve(),
        project=args.project,
        platform=args.platform,
        market=args.market,
        context=context,
        source_report_path=Path(args.source_report).resolve() if args.source_report else None,
    )
    print(json.dumps({"output_path": result["output_path"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
