from __future__ import annotations

import json
from pathlib import Path

from generate_scene_report import build_report_payload, load_catalog
from scene_report_presets import SCENE_REQUESTS_ZH


def _safe_list(values: object) -> list[str]:
    return [str(item).strip() for item in (values or []) if str(item).strip()]


def render_quick_reference(skill_root: Path) -> str:
    catalog = load_catalog(skill_root)
    lines = [
        "# Scene Quick Reference",
        "",
        "Use this file when you want one fast, copy-ready index across all 19 scenes.",
        "",
        "## 19 One-Line Chinese Requests",
        "",
        "Copy one line below directly into Codex when you already know which scene you want:",
        "",
    ]

    for scene in catalog:
        scene_id = scene["id"]
        lines.append(f"- Scene {scene_id}: `{SCENE_REQUESTS_ZH.get(scene_id, '')}`")

    lines.extend(
        [
            "",
        "Each scene block gives you:",
        "",
        "- the scene title and deliverable family",
        "- one English direct-call request",
        "- one Chinese direct-call request",
        "- the key required inputs",
        "- the expected outputs",
        "- the main runner command",
        "",
        ]
    )

    for scene in catalog:
        payload = build_report_payload(scene, f"quick-ref-{scene['id']}", "")
        working_context = payload.get("working_context", {})
        execution_template = payload.get("execution_template", {})
        runner_args = _safe_list(execution_template.get("recommended_runner_args"))
        lines.extend(
            [
                f"## Scene {scene['id']} - {scene['title']}",
                "",
                f"- Slug: `{scene['slug']}`",
                f"- Deliverable Type: `{scene['deliverable_type']}`",
                f"- Summary: {scene['summary']}",
                f"- English Request: `{str(execution_template.get('recommended_request', '')).strip()}`",
                f"- 中文请求: `{str(execution_template.get('recommended_request_zh', '')).strip()}`",
                "",
                "### Quick Copy CN",
                "",
                f"`{str(execution_template.get('recommended_request_zh', '')).strip()}`",
                "",
                "### Key Inputs",
                "",
            ]
        )
        for item in _safe_list(working_context.get("inputs")):
            lines.append(f"- {item}")
        lines.extend(["", "### Expected Outputs", ""])
        for item in _safe_list(working_context.get("requested_outputs")):
            lines.append(f"- {item}")
        lines.extend(["", "### Main Runner", ""])
        if runner_args:
            lines.append(f"`{runner_args[0]}`")
        lines.extend(["", "### 中文 Prompt Scaffold", ""])
        for item in _safe_list(execution_template.get("codex_prompt_scaffold_zh")):
            lines.append(f"- {item}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    skill_root = Path(__file__).resolve().parents[1]
    output = skill_root / "references" / "scene-quick-reference.md"
    output.write_text(render_quick_reference(skill_root), encoding="utf-8")
    print(json.dumps({"output": str(output)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
