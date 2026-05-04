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
    stdout = result["stdout"].strip()
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        last_object_start = stdout.rfind("\n{")
        candidate = stdout[last_object_start + 1 :] if last_object_start >= 0 else stdout
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            return None, force_failure(result, f"{command_name} did not return valid JSON")
    return payload, result


def require_existing_path(batch_result: dict, raw_path: object, message: str) -> dict:
    if not isinstance(raw_path, str) or not raw_path.strip():
        return force_failure(batch_result, message)
    if not Path(raw_path).exists():
        return force_failure(batch_result, f"{message}: {raw_path}")
    return batch_result


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

    batch_board_execute_file = skill_root / "tmp" / "20260505_validate_board_batch_execute.json"
    batch_board_execute_root = skill_root / "tmp" / "20260505_validate_board_batch_execute_item"
    batch_board_execute_file.write_text(
        json.dumps(
            [
                {
                    "mode": "board",
                    "query": "Give me a daily board for TikTok beauty ops",
                    "bundle_root": str(skill_root.parents[0] / ".codex-tmp" / "preset-template-bundle-v9"),
                    "name": "validate-board-batch-execute-item",
                    "output_root": str(batch_board_execute_root),
                    "generate": True,
                    "dry_run": True,
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
                str(batch_board_execute_file),
                "--batch-root",
                str(skill_root / "tmp" / "20260505_validate_board_batch_execute"),
            ]
        )
    )
    if results[-1]["returncode"] == 0:
        batch_payload, batch_result = parse_json_stdout(results[-1], "batch_run_operator_workflows.py")
        if batch_payload is not None:
            batch_results = batch_payload.get("results", [])
            if len(batch_results) != 1:
                batch_result = force_failure(batch_result, "batch board execute smoke should return exactly one validation item")
            else:
                item = batch_results[0]
                if item.get("status") != "success":
                    batch_result = force_failure(batch_result, "batch board execute smoke should finish with success status")
                result_payload = item.get("result", {})
                if result_payload.get("selected_board_slug") != "daily-ops-board":
                    batch_result = force_failure(
                        batch_result,
                        f"batch board execute smoke should scaffold daily-ops-board, got: {result_payload.get('selected_board_slug')!r}",
                    )
                executed_actions = result_payload.get("recommendation_manifest", {}).get("executed_actions", {})
                if executed_actions.get("generate") is not True:
                    batch_result = force_failure(batch_result, "batch board execute smoke should record generate=true")
                elif executed_actions.get("dry_run") is not True:
                    batch_result = force_failure(batch_result, "batch board execute smoke should record board-local dry_run=true")
                elif executed_actions.get("run") is not False:
                    batch_result = force_failure(batch_result, "batch board execute smoke should keep board-local run=false")

                local_paths = result_payload.get("local_paths", {})
                batch_result = require_existing_path(batch_result, result_payload.get("starter_root"), "batch board execute smoke should create starter_root")
                if batch_result["returncode"] == 0:
                    batch_result = require_existing_path(batch_result, local_paths.get("suite_queue_json"), "batch board execute smoke should create queue json")
                if batch_result["returncode"] == 0:
                    batch_result = require_existing_path(batch_result, local_paths.get("local_report_md"), "batch board execute smoke should create preset report")
                if batch_result["returncode"] == 0:
                    batch_result = require_existing_path(batch_result, local_paths.get("local_batch_report_md"), "batch board execute smoke should create batch report")
                if batch_result["returncode"] == 0:
                    batch_result = require_existing_path(batch_result, local_paths.get("local_batch_result_json"), "batch board execute smoke should create batch result json")
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
