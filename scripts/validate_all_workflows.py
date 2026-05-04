from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


VALIDATORS = [
    "validate_skill_docs.py",
    "validate_scene_presets.py",
    "validate_capture_pack_workflows.py",
    "validate_export_outputs.py",
]

EXTRA_COMPILE_ONLY = [
    "recommend_entry_board.py",
    "start_entry_board.py",
]


def run(command: list[str]) -> dict:
    completed = subprocess.run(command, text=True, capture_output=True)
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def force_failure(result: dict, message: str) -> dict:
    result["returncode"] = 1
    result["stderr"] = message
    return result


def parse_json_stdout(result: dict, command_name: str) -> tuple[dict | None, dict]:
    try:
        payload = json.loads(result["stdout"])
    except json.JSONDecodeError:
        return None, force_failure(result, f"{command_name} did not return valid JSON")
    return payload, result


def main() -> None:
    skill_root = Path(__file__).resolve().parents[1]
    scripts_root = skill_root / "scripts"

    results = []
    for script_name in VALIDATORS:
        results.append(run([sys.executable, "-m", "py_compile", str(scripts_root / script_name)]))
    for script_name in EXTRA_COMPILE_ONLY:
        results.append(run([sys.executable, "-m", "py_compile", str(scripts_root / script_name)]))

    export_root = skill_root / "tmp" / "20260504_validate_all_export_suite"
    for script_name in VALIDATORS:
        command = [sys.executable, str(scripts_root / script_name)]
        if script_name == "validate_export_outputs.py":
            command.extend(["--output-root", str(export_root)])
        results.append(run(command))

    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "start_entry_board.py"),
                "--query",
                "Give me a daily board for TikTok beauty ops",
                "--output-root",
                str(skill_root / "tmp" / "20260505_validate_entry_board_starter"),
                "--generate",
                "--dry-run",
            ]
        )
    )

    auto_board_result = run(
        [
            sys.executable,
            str(scripts_root / "run_operator_workflow.py"),
            "--request",
            "Give me a daily board for TikTok beauty ops",
            "--output-root",
            str(skill_root / "tmp" / "20260505_validate_auto_board_route"),
        ]
    )
    if auto_board_result["returncode"] == 0:
        payload, auto_board_result = parse_json_stdout(auto_board_result, "run_operator_workflow.py")
        if payload is not None:
            resolved_mode = payload.get("route", {}).get("resolved_mode")
            if resolved_mode != "board":
                auto_board_result = force_failure(
                    auto_board_result,
                    f"run_operator_workflow.py should auto-route board-style requests to board mode, got: {resolved_mode!r}",
                )
    results.append(auto_board_result)

    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "start_project_workflow.py"),
                "--request",
                "Give me a daily board for TikTok beauty ops",
                "--name",
                "validate-board-project",
                "--output-root",
                str(skill_root / "tmp" / "20260505_validate_project_board_route"),
            ]
        )
    )

    batch_board_file = skill_root / "tmp" / "20260505_validate_board_batch.json"
    batch_board_file.write_text(
        json.dumps(
            [
                {
                    "mode": "board",
                    "query": "I'm the live operator for tonight's session",
                    "bundle_root": str(skill_root.parents[0] / ".codex-tmp" / "preset-template-bundle-v9"),
                    "name": "validate-board-batch-item",
                    "output_root": str(skill_root / "tmp" / "20260505_validate_board_batch_item"),
                }
            ],
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8-sig",
    )
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "batch_run_operator_workflows.py"),
                "--batch-file",
                str(batch_board_file),
                "--dry-run",
                "--batch-root",
                str(skill_root / "tmp" / "20260505_validate_board_batch_preview"),
            ]
        )
    )
    if results[-1]["returncode"] == 0:
        batch_payload, batch_result = parse_json_stdout(results[-1], "batch_run_operator_workflows.py")
        if batch_payload is not None:
            batch_results = batch_payload.get("results", [])
            if len(batch_results) != 1:
                batch_result = force_failure(batch_result, "batch_run_operator_workflows.py should return exactly one validation batch item")
            else:
                item = batch_results[0]
                if item.get("status") != "preview":
                    batch_result = force_failure(batch_result, "batch board validation item should stay in preview status")
                preview = item.get("result", {}).get("preview", {})
                if preview.get("would_run_mode") != "board":
                    batch_result = force_failure(batch_result, "batch board preview should resolve to board mode")
                elif preview.get("bundle_root") != str(skill_root.parents[0] / ".codex-tmp" / "preset-template-bundle-v9"):
                    batch_result = force_failure(batch_result, "batch board preview should preserve bundle_root")
                elif preview.get("top_k") != 3:
                    batch_result = force_failure(batch_result, "batch board preview should expose top_k=3")
                elif preview.get("generate") is not False:
                    batch_result = force_failure(batch_result, "batch board preview should expose generate=false by default")
                elif preview.get("task_dry_run") is not False:
                    batch_result = force_failure(batch_result, "batch board preview should keep board-task dry_run=false")
                elif preview.get("task_run") is not False:
                    batch_result = force_failure(batch_result, "batch board preview should expose task_run=false by default")
        results[-1] = batch_result

    failures = [item for item in results if item["returncode"] != 0]
    payload = {
        "success": not failures,
        "validators": VALIDATORS,
        "extra_compile_only": EXTRA_COMPILE_ONLY,
        "results": results,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
