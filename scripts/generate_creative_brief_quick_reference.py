from __future__ import annotations

import json
from pathlib import Path

from generate_scene_report import build_report_payload, load_catalog


CREATIVE_SCENE_IDS = {"09", "10", "11", "12", "13", "14", "15", "16"}


def _safe_list(values: object) -> list[str]:
    return [str(item).strip() for item in (values or []) if str(item).strip()]


def _render_table_contract(section: dict) -> list[str]:
    table = section.get("table") or {}
    headers = _safe_list(table.get("headers"))
    if not headers:
        return []
    rows = table.get("rows") or []
    lines = [f"- {section.get('heading', '').strip()}: `{' | '.join(headers)}`"]
    if rows:
        sample_rows = []
        for row in rows[:2]:
            sample_rows.append(" | ".join(str(cell).strip() for cell in row))
        if sample_rows:
            lines.append(f"- Sample Rows: `{'` / `'.join(sample_rows)}`")
    return lines


def render_creative_quick_reference(skill_root: Path) -> str:
    catalog = [scene for scene in load_catalog(skill_root) if scene["id"] in CREATIVE_SCENE_IDS]
    lines = [
        "# Creative Brief Quick Reference",
        "",
        "Use this file when you want the creative-production half of the skill without scanning all 19 scenes.",
        "",
        "It focuses on scenes 09-16:",
        "",
        "- reference-video adaptation",
        "- image-to-video briefing",
        "- replication pipeline design",
        "- multi-style testing matrix",
        "- multi-market localization",
        "- launch asset family planning",
        "- image-copy localization",
        "- competitor main-image benchmarking",
        "",
        "## Fast Pick",
        "",
        "Copy one of these requests directly into Codex when you already know the brief type you need:",
        "",
    ]

    for scene in catalog:
        payload = build_report_payload(scene, f"creative-quick-ref-{scene['id']}", "")
        request_zh = str(payload.get("execution_template", {}).get("recommended_request_zh", "")).strip()
        lines.append(f"- Scene {scene['id']} - {scene['title']}: `{request_zh}`")

    lines.extend(
        [
            "",
            "## How To Choose Quickly",
            "",
            "- Choose `09` when you already have one strong reference video and want an adapted replication brief.",
            "- Choose `10` when you mainly have product images or product facts and need a first video concept from scratch.",
            "- Choose `11` when you need a repeatable hot-video intake and replication system, not one brief.",
            "- Choose `12` when one product needs several clearly different creative directions to test.",
            "- Choose `13` when one product concept must be translated into several markets without doing naive literal localization.",
            "- Choose `14` when you need a launch asset family with production priority and role assignment.",
            "- Choose `15` when the main task is translating or localizing image copy while preserving layout logic.",
            "- Choose `16` when the main task is benchmarking competitor main images and defining a stronger visual route.",
            "",
            "## Missing Evidence That Usually Blocks Good Output",
            "",
            "- `09`: no clear reference logic, no product truth, no restriction on what cannot be copied literally",
            "- `10`: no asset inventory, no proof material, no clarity on whether talent or hands-on footage exists",
            "- `11`: no discovery scope, no ranking rule, no cadence owner",
            "- `12`: no invariant message, no audience split, no definition of what each variant is supposed to teach",
            "- `13`: no market nuance evidence, no native review context, no banned claims or compliance notes",
            "- `14`: no asset dependency map, no priority rule, no owner for each production lane",
            "- `15`: no source layout capture, no target-language limits, no reviewer for local tone and fit",
            "- `16`: no click context, no category baseline set, no proof for why the proposed direction is stronger",
        ]
    )

    for scene in catalog:
        payload = build_report_payload(scene, f"creative-quick-ref-{scene['id']}", "")
        metadata = payload.get("metadata", {})
        working_context = payload.get("working_context", {})
        execution_template = payload.get("execution_template", {})
        sections = payload.get("sections", [])
        runner = _safe_list(execution_template.get("recommended_runner_args"))

        lines.extend(
            [
                "",
                f"## Scene {scene['id']} - {metadata.get('scene_title', scene['title'])}",
                "",
                f"- Deliverable Type: `{metadata.get('deliverable_type', scene['deliverable_type'])}`",
                f"- Use When: {scene['summary']}",
                f"- 中文直呼请求: `{str(execution_template.get('recommended_request_zh', '')).strip()}`",
                "",
                "### 只复制这一句",
                "",
                f"`{str(execution_template.get('recommended_request_zh', '')).strip()}`",
                "",
                "### Main Runner",
                "",
            ]
        )
        if runner:
            lines.append(f"`{runner[0]}`")
        else:
            lines.append("`python scripts/run_operator_workflow.py --mode scene --scene <scene-id> --project \"<project-name>\"`")

        lines.extend(["", "### Minimum Inputs", ""])
        for item in _safe_list(working_context.get("minimum_evidence")):
            lines.append(f"- {item}")

        lines.extend(["", "### Ideal Inputs", ""])
        for item in _safe_list(working_context.get("ideal_evidence")):
            lines.append(f"- {item}")

        lines.extend(["", "### Workflow Focus", ""])
        for item in _safe_list(execution_template.get("workflow_steps")):
            lines.append(f"- {item}")

        lines.extend(["", "### Brief Blocks To Fill", ""])
        rendered_any_table = False
        for section in sections:
            table_lines = _render_table_contract(section)
            if table_lines:
                rendered_any_table = True
                lines.extend(table_lines)
        if not rendered_any_table:
            lines.append("- No table-driven brief blocks were found for this scene.")

        lines.extend(["", "### Output Must Include", ""])
        for item in _safe_list(execution_template.get("output_checklist")):
            lines.append(f"- {item}")

        lines.extend(["", "### 中文 Prompt Scaffold", ""])
        for item in _safe_list(execution_template.get("codex_prompt_scaffold_zh")):
            lines.append(f"- {item}")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    skill_root = Path(__file__).resolve().parents[1]
    output = skill_root / "references" / "creative-brief-quick-reference.md"
    output.write_text(render_creative_quick_reference(skill_root), encoding="utf-8")
    print(json.dumps({"output": str(output)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
