from __future__ import annotations

import json
from pathlib import Path

from generate_scene_report import build_report_payload, load_catalog
from scene_report_presets import SCENE_OPERATOR_GUIDE, SCENE_PRESETS


def main() -> int:
    skill_root = Path(__file__).resolve().parents[1]
    catalog = load_catalog(skill_root)
    catalog_ids = [item["id"] for item in catalog]
    errors: list[str] = []
    warnings: list[str] = []

    for scene_id in catalog_ids:
        if scene_id not in SCENE_PRESETS:
            errors.append(f"Missing preset for scene {scene_id}")

    for scene_id in sorted(SCENE_PRESETS):
        if scene_id not in catalog_ids:
            errors.append(f"Preset exists for unknown scene {scene_id}")
    for scene_id in catalog_ids:
        if scene_id not in SCENE_OPERATOR_GUIDE:
            warnings.append(f"Missing operator guide for scene {scene_id}")

    for scene in catalog:
        payload = build_report_payload(scene, f"validation-{scene['id']}", "")
        sections = payload.get("sections", [])
        if not sections:
            errors.append(f"Scene {scene['id']} has no sections")
            continue

        working_context = payload.get("working_context", {})
        if not working_context.get("inputs"):
            warnings.append(f"Scene {scene['id']} has no suggested inputs")
        if not working_context.get("minimum_evidence"):
            warnings.append(f"Scene {scene['id']} has no minimum evidence checklist")
        if not working_context.get("ideal_evidence"):
            warnings.append(f"Scene {scene['id']} has no ideal evidence checklist")
        if not working_context.get("requested_outputs"):
            warnings.append(f"Scene {scene['id']} has no requested outputs")
        if not working_context.get("ready_checklist"):
            warnings.append(f"Scene {scene['id']} has no ready checklist")

        operator_guide = payload.get("operator_guide", {})
        if not operator_guide.get("operator_checklist"):
            warnings.append(f"Scene {scene['id']} has no operator checklist")
        if not operator_guide.get("common_failure_modes"):
            warnings.append(f"Scene {scene['id']} has no common failure modes")

        execution_template = payload.get("execution_template", {})
        recommended_request = str(execution_template.get("recommended_request", "")).strip()
        if not recommended_request:
            errors.append(f"Scene {scene['id']} has no execution-template recommended request")

        runner_args = [
            str(item).strip()
            for item in execution_template.get("recommended_runner_args", [])
            if str(item).strip()
        ]
        if not runner_args:
            errors.append(f"Scene {scene['id']} has no execution-template runner args")

        variable_inputs = execution_template.get("variable_inputs", []) or []
        if not variable_inputs:
            errors.append(f"Scene {scene['id']} has no execution-template variable inputs")
        else:
            for index, item in enumerate(variable_inputs, start=1):
                for key in ["name", "meaning", "example", "required"]:
                    value = str(item.get(key, "")).strip()
                    if not value:
                        errors.append(
                            f"Scene {scene['id']} variable input {index} is missing '{key}'"
                        )

        prompt_scaffold = [
            str(item).strip()
            for item in execution_template.get("codex_prompt_scaffold", [])
            if str(item).strip()
        ]
        if not prompt_scaffold:
            errors.append(f"Scene {scene['id']} has no execution-template prompt scaffold")

        workflow_steps = [
            str(item).strip()
            for item in execution_template.get("workflow_steps", [])
            if str(item).strip()
        ]
        if not workflow_steps:
            errors.append(f"Scene {scene['id']} has no execution-template workflow steps")

        output_checklist = [
            str(item).strip()
            for item in execution_template.get("output_checklist", [])
            if str(item).strip()
        ]
        if not output_checklist:
            errors.append(f"Scene {scene['id']} has no execution-template output checklist")

        table_count = 0
        for index, section in enumerate(sections, start=1):
            heading = str(section.get("heading", "")).strip()
            instruction = str(section.get("instruction", "")).strip()
            table = section.get("table") or {}
            headers = [str(item).strip() for item in table.get("headers", []) if str(item).strip()]
            rows = table.get("rows", []) or []
            has_content_hint = bool(
                instruction
                or section.get("paragraphs")
                or section.get("bullets")
                or section.get("numbered")
                or headers
            )
            if not heading:
                errors.append(f"Scene {scene['id']} section {index} is missing heading")
            if not has_content_hint:
                warnings.append(f"Scene {scene['id']} section '{heading}' has no starter guidance")
            if headers:
                table_count += 1
                if rows and any(len(row) > len(headers) for row in rows):
                    errors.append(f"Scene {scene['id']} section '{heading}' has a row longer than its headers")

        if table_count == 0:
            warnings.append(f"Scene {scene['id']} has no starter tables")

    result = {
        "ok": not errors,
        "scene_count": len(catalog),
        "preset_count": len(SCENE_PRESETS),
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
