from __future__ import annotations

import json
from pathlib import Path

from generate_scene_report import build_report_payload, load_catalog
from scene_report_presets import SCENE_REQUESTS_ZH
from text_normalization import write_utf8_text


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
        request_en = str(execution_template.get("recommended_request", "")).strip()
        request_zh = str(execution_template.get("recommended_request_zh", "")).strip()
        if scene["id"] == "05":
            request_zh = request_zh.replace("制作 brief", "制作简报")
        if scene["id"] in {"09", "10", "15", "16"}:
            request_zh = (
                request_zh.replace("复刻 brief", "复刻制作简报")
                .replace("短视频 brief", "短视频制作简报")
                .replace("本地化 brief", "本地化制作简报")
                .replace("超车 brief", "超车制作简报")
            )
        if scene["id"] == "19":
            request_zh = request_zh.replace("do more、do less、stop", "多做什么、少做什么、停止什么")
        lines.extend(
            [
                f"## Scene {scene['id']} - {scene['title']}",
                "",
                f"- Slug: `{scene['slug']}`",
                f"- Deliverable Type: `{scene['deliverable_type']}`",
                f"- Summary: {scene['summary']}",
                f"- English Request: `{request_en}`",
                f"- 中文请求: `{request_zh}`",
                "",
                "### Quick Copy CN",
                "",
                f"`{request_zh}`",
                "",
                "### Key Inputs",
                "",
            ]
        )
        for item in _safe_list(working_context.get("inputs")):
            lines.append(f"- {item}")
        lines.extend(["", "### Expected Outputs", ""])
        for item in _safe_list(working_context.get("requested_outputs")):
            item = (
                item.replace("Inferred original brief", "反推原始制作简报")
                .replace("Product-adapted brief", "产品适配制作简报")
                .replace("Generator-ready schema", "可生成结构")
                .replace("Next-cycle plan", "下一轮测试计划")
            )
            lines.append(f"- {item}")
        lines.extend(["", "### Main Runner", ""])
        if runner_args:
            lines.append(f"`{runner_args[0]}`")
        lines.extend(["", "### 中文 Prompt Scaffold", ""])
        for item in _safe_list(execution_template.get("codex_prompt_scaffold_zh")):
            item = (
                item.replace("制作 brief", "制作简报")
                .replace("复刻 brief", "复刻制作简报")
                .replace("短视频 brief", "短视频制作简报")
                .replace("本地化 brief", "本地化制作简报")
                .replace("超车 brief", "超车制作简报")
                .replace("反推 brief", "反推制作简报")
                .replace("原版 brief", "原版制作简报")
                .replace("适配版 brief", "适配版制作简报")
                .replace("do more、do less、stop", "多做什么、少做什么、停止什么")
                .replace(
                    "Inferred original brief, Generator-ready schema, Shot-by-shot table, Product-adapted brief, Field-level confidence flags。",
                    "反推原始制作简报、可生成结构、分镜逐条表、产品适配制作简报、字段级置信度标记。",
                )
            )
            lines.append(f"- {item}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    skill_root = Path(__file__).resolve().parents[1]
    output = skill_root / "references" / "scene-quick-reference.md"
    write_utf8_text(output, render_quick_reference(skill_root))
    print(json.dumps({"output": str(output)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
