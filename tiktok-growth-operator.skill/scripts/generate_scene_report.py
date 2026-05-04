from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from scene_report_presets import get_scene_preset


DELIVERABLE_SECTIONS = {
    "collection_board": [
        "Executive Conclusion",
        "Objects To Track",
        "Why They Matter",
        "Fields To Capture Next Time",
        "Next Action",
    ],
    "breakdown_report": [
        "Executive Conclusion",
        "Structure Logic",
        "Core Mechanism",
        "Reusable Formula",
        "Risks And Adaptation Notes",
        "Next Action",
    ],
    "insight_report": [
        "Executive Conclusion",
        "High-Level Judgment",
        "Evidence Clusters",
        "Recommended Action",
        "Open Questions",
    ],
    "creation_brief": [
        "Executive Conclusion",
        "Target",
        "Audience",
        "Message",
        "Structure",
        "Creative Constraints",
        "Next Action",
    ],
    "testing_matrix": [
        "Executive Conclusion",
        "Core Invariant",
        "Variable Matrix",
        "Expected Effect",
        "What To Learn",
        "Next Action",
    ],
}


def load_catalog(skill_root: Path) -> list[dict]:
    path = skill_root / "references" / "scene-catalog.json"
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_scene(catalog: list[dict], scene: str) -> dict:
    normalized = scene.strip().lower()
    for item in catalog:
        if normalized in {item["id"].lower(), item["slug"].lower()}:
            return item
        if normalized == f"scene-{item['id']}":
            return item
    raise SystemExit(f"Unknown scene: {scene}")


def build_report_payload(scene: dict, project: str, context: str) -> dict:
    generated_at = datetime.now().isoformat(timespec="seconds")
    preset = get_scene_preset(scene["id"])
    sections = []
    if preset.get("sections"):
        sections = preset["sections"]
    else:
        for heading in DELIVERABLE_SECTIONS[scene["deliverable_type"]]:
            sections.append(
                {
                    "heading": heading,
                    "instruction": f"Fill this section for scene {scene['id']} using direct evidence and reusable conclusions.",
                    "paragraphs": [],
                    "bullets": [],
                    "numbered": [],
                    "table": {
                        "title": "",
                        "headers": [],
                        "rows": [],
                    },
                }
            )

    working_context_preset = preset.get("working_context", {})
    executive_preset = preset.get("executive_summary", {})
    operator_guide_preset = preset.get("operator_guide", {})
    execution_template = preset.get("execution_template", {})

    return {
        "metadata": {
            "scene": scene["id"],
            "scene_slug": scene["slug"],
            "scene_title": scene["title"],
            "project": project,
            "title": f"Scene {scene['id']} Report - {project}",
            "deliverable_type": scene["deliverable_type"],
            "generated_at": generated_at,
            "scenario_file": scene["scenario_file"],
            "status": "draft",
        },
        "working_context": {
            "summary": context.strip(),
            "inputs": working_context_preset.get("inputs", []),
            "constraints": working_context_preset.get("constraints", []),
            "requested_outputs": working_context_preset.get("requested_outputs", []),
            "minimum_evidence": working_context_preset.get("minimum_evidence", []),
            "ideal_evidence": working_context_preset.get("ideal_evidence", []),
            "ready_checklist": working_context_preset.get("ready_checklist", []),
        },
        "executive_summary": {
            "conclusion": executive_preset.get("conclusion", ""),
            "why_it_matters": executive_preset.get("why_it_matters", ""),
            "next_action": executive_preset.get("next_action", ""),
            "confidence": executive_preset.get("confidence", ""),
        },
        "operator_guide": {
            "operator_checklist": operator_guide_preset.get("operator_checklist", []),
            "common_failure_modes": operator_guide_preset.get("common_failure_modes", []),
        },
        "execution_template": {
            "recommended_request": execution_template.get("recommended_request", ""),
            "recommended_request_zh": execution_template.get("recommended_request_zh", ""),
            "recommended_runner_args": execution_template.get("recommended_runner_args", []),
            "variable_inputs": execution_template.get("variable_inputs", []),
            "codex_prompt_scaffold": execution_template.get("codex_prompt_scaffold", []),
            "codex_prompt_scaffold_zh": execution_template.get("codex_prompt_scaffold_zh", []),
            "workflow_steps": execution_template.get("workflow_steps", []),
            "output_checklist": execution_template.get("output_checklist", []),
        },
        "evidence": preset.get("evidence", []),
        "sections": sections,
        "assets": preset.get("assets", []),
        "notes": preset.get("notes", []),
        "sources": preset.get("sources", []),
    }


def render_markdown_from_payload(report: dict) -> str:
    metadata = report["metadata"]
    working_context = report.get("working_context", {})
    executive_summary = report.get("executive_summary", {})
    lines = [
        f"# {metadata['title']}",
        "",
        f"- Scene: {metadata['scene']} - {metadata['scene_title']}",
        f"- Project: {metadata['project']}",
        f"- Deliverable Type: {metadata['deliverable_type']}",
        f"- Generated: {metadata['generated_at']}",
        f"- Status: {metadata.get('status', '') or 'draft'}",
        f"- Scenario File: `{metadata['scenario_file']}`",
        "",
        "## Working Context",
        "",
        working_context.get("summary", "").strip() or "_Add the user brief, market, product, and evidence notes here._",
        "",
    ]

    for label, key in [
        ("Inputs", "inputs"),
        ("Minimum Evidence", "minimum_evidence"),
        ("Ideal Evidence", "ideal_evidence"),
        ("Constraints", "constraints"),
        ("Requested Outputs", "requested_outputs"),
        ("Ready Checklist", "ready_checklist"),
    ]:
        values = [str(item).strip() for item in working_context.get(key, []) if str(item).strip()]
        if values:
            lines.append(f"### {label}")
            lines.append("")
            for item in values:
                lines.append(f"- {item}")
            lines.append("")

    lines.extend(
        [
            "## Executive Summary",
            "",
            f"- Conclusion: {executive_summary.get('conclusion', '').strip() or '_Fill this field._'}",
            f"- Why It Matters: {executive_summary.get('why_it_matters', '').strip() or '_Fill this field._'}",
            f"- Next Action: {executive_summary.get('next_action', '').strip() or '_Fill this field._'}",
            f"- Confidence: {executive_summary.get('confidence', '').strip() or '_Optional._'}",
            "",
        ]
    )

    operator_guide = report.get("operator_guide", {})
    for label, key in [
        ("Operator Checklist", "operator_checklist"),
        ("Common Failure Modes", "common_failure_modes"),
    ]:
        values = [str(item).strip() for item in operator_guide.get(key, []) if str(item).strip()]
        if values:
            lines.extend([f"## {label}", ""])
            for item in values:
                lines.append(f"- {item}")
            lines.append("")

    execution_template = report.get("execution_template", {})
    if any(execution_template.get(key) for key in [
        "recommended_request",
        "recommended_request_zh",
        "recommended_runner_args",
        "variable_inputs",
        "codex_prompt_scaffold",
        "codex_prompt_scaffold_zh",
        "workflow_steps",
        "output_checklist",
    ]):
        lines.extend(["## Direct-Use Template", ""])
        recommended_request = str(execution_template.get("recommended_request", "")).strip()
        if recommended_request:
            lines.append(f"- Recommended Request: `{recommended_request}`")
        recommended_request_zh = str(execution_template.get("recommended_request_zh", "")).strip()
        if recommended_request_zh:
            lines.append(f"- 推荐请求: `{recommended_request_zh}`")
        runner_args = [str(item).strip() for item in execution_template.get("recommended_runner_args", []) if str(item).strip()]
        if runner_args:
            lines.append("- Runner Args:")
            for item in runner_args:
                lines.append(f"  - `{item}`")
        lines.append("")

        variable_inputs = execution_template.get("variable_inputs", []) or []
        if variable_inputs:
            lines.extend(["### Variable Inputs", ""])
            lines.append("| Variable | Meaning | Example | Required |")
            lines.append("| --- | --- | --- | --- |")
            for item in variable_inputs:
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            str(item.get("name", "")).strip(),
                            str(item.get("meaning", "")).strip(),
                            str(item.get("example", "")).strip(),
                            str(item.get("required", "")).strip(),
                        ]
                    )
                    + " |"
                )
            lines.append("")

        prompt_scaffold = [str(item).strip() for item in execution_template.get("codex_prompt_scaffold", []) if str(item).strip()]
        if prompt_scaffold:
            lines.extend(["### Codex Prompt Scaffold", ""])
            for item in prompt_scaffold:
                lines.append(f"- {item}")
            lines.append("")

        prompt_scaffold_zh = [str(item).strip() for item in execution_template.get("codex_prompt_scaffold_zh", []) if str(item).strip()]
        if prompt_scaffold_zh:
            lines.extend(["### 中文 Prompt Scaffold", ""])
            for item in prompt_scaffold_zh:
                lines.append(f"- {item}")
            lines.append("")

        workflow_steps = [str(item).strip() for item in execution_template.get("workflow_steps", []) if str(item).strip()]
        if workflow_steps:
            lines.extend(["### Workflow Steps", ""])
            for index, item in enumerate(workflow_steps, start=1):
                lines.append(f"{index}. {item}")
            lines.append("")

        output_checklist = [str(item).strip() for item in execution_template.get("output_checklist", []) if str(item).strip()]
        if output_checklist:
            lines.extend(["### Output Checklist", ""])
            for item in output_checklist:
                lines.append(f"- {item}")
            lines.append("")

    evidence = report.get("evidence", [])
    if evidence:
        lines.extend(
            [
                "## Evidence",
                "",
                "| Label | Detail | Source |",
                "| --- | --- | --- |",
            ]
        )
        for item in evidence:
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(item.get("label", "")).replace("\n", " ").strip(),
                        str(item.get("detail", "")).replace("\n", " ").strip(),
                        str(item.get("source", "")).replace("\n", " ").strip(),
                    ]
                )
                + " |"
            )
        lines.append("")

    for section in report.get("sections", []):
        lines.extend([f"## {section['heading']}", ""])
        instruction = str(section.get("instruction", "")).strip()
        if instruction:
            lines.extend([f"_{instruction}_", ""])

        paragraphs = [str(item).strip() for item in section.get("paragraphs", []) if str(item).strip()]
        bullets = [str(item).strip() for item in section.get("bullets", []) if str(item).strip()]
        numbered = [str(item).strip() for item in section.get("numbered", []) if str(item).strip()]
        table = section.get("table") or {}

        for paragraph in paragraphs:
            lines.extend([paragraph, ""])
        for bullet in bullets:
            lines.append(f"- {bullet}")
        if bullets:
            lines.append("")
        for index, item in enumerate(numbered, start=1):
            lines.append(f"{index}. {item}")
        if numbered:
            lines.append("")
        headers = [str(item).strip() for item in table.get("headers", []) if str(item).strip()]
        rows = table.get("rows", [])
        if headers:
            title = str(table.get("title", "")).strip()
            if title:
                lines.extend([f"### {title}", ""])
            lines.append("| " + " | ".join(headers) + " |")
            lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
            for row in rows:
                cells = [str(cell).replace("\n", " ").strip() for cell in row]
                if len(cells) < len(headers):
                    cells.extend([""] * (len(headers) - len(cells)))
                lines.append("| " + " | ".join(cells[: len(headers)]) + " |")
            lines.append("")
        if not any([paragraphs, bullets, numbered, headers]):
            lines.extend(["_Fill this section._", ""])

    assets = report.get("assets", [])
    if assets:
        lines.extend(["## Assets", ""])
        for asset in assets:
            label = str(asset.get("label", "")).strip() or "Asset"
            path = str(asset.get("path", "")).strip()
            note = str(asset.get("note", "")).strip()
            detail = " | ".join(item for item in [path, note] if item)
            lines.append(f"- {label}: {detail}" if detail else f"- {label}")
        lines.append("")

    notes = [str(item).strip() for item in report.get("notes", []) if str(item).strip()]
    if notes:
        lines.extend(["## Notes", ""])
        for item in notes:
            lines.append(f"- {item}")
        lines.append("")

    sources = [str(item).strip() for item in report.get("sources", []) if str(item).strip()]
    if sources:
        lines.extend(["## Sources", ""])
        for item in sources:
            lines.append(f"- {item}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_report(scene: dict, project: str, context: str) -> str:
    return render_markdown_from_payload(build_report_payload(scene, project, context))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a scene report scaffold for one TikTok Growth Operator scene.")
    parser.add_argument("--scene", required=True, help="Scene id or slug.")
    parser.add_argument("--project", required=True, help="Human-readable project name.")
    parser.add_argument("--context-file", default=None, help="Optional UTF-8 text file with user context.")
    parser.add_argument("--output", required=True, help="Output Markdown path.")
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Scaffold output format.",
    )
    args = parser.parse_args()

    skill_root = Path(__file__).resolve().parents[1]
    catalog = load_catalog(skill_root)
    scene = resolve_scene(catalog, args.scene)
    context = ""
    if args.context_file:
        context = Path(args.context_file).read_text(encoding="utf-8")
    payload = build_report_payload(scene, args.project, context)
    report = (
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        if args.format == "json"
        else render_markdown_from_payload(payload)
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
