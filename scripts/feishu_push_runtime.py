from __future__ import annotations

import json
import subprocess
from pathlib import Path

from text_normalization import normalize_text


def run_subprocess(command: list[str]) -> dict:
    completed = subprocess.run(
        command,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    stdout_text = completed.stdout
    stderr_text = completed.stderr
    try:
        stdout_payload = json.loads(stdout_text) if stdout_text.strip() else {}
    except json.JSONDecodeError:
        stdout_payload = {"raw_stdout": stdout_text}
    return {
        "command": command,
        "exit_code": completed.returncode,
        "stdout": stdout_payload,
        "stderr": stderr_text,
    }


def looks_retryable_feishu_error(result: dict) -> bool:
    stderr = normalize_text(result.get("stderr", ""), strip=False)
    if "code=10071" in stderr:
        return True
    stdout = result.get("stdout")
    if isinstance(stdout, dict):
        text = json.dumps(stdout, ensure_ascii=False)
        if "code=10071" in text:
            return True
    return False


def maybe_push_feishu_bundle(
    report_json: str,
    app_id: str,
    app_secret: str,
    *,
    title: str = "",
    base_name: str = "",
) -> dict:
    resolved_report_json = normalize_text(report_json)
    resolved_app_id = normalize_text(app_id)
    resolved_app_secret = normalize_text(app_secret)
    if not resolved_report_json:
        return {"status": "skipped", "reason": "no-report-json"}
    if not resolved_app_id or not resolved_app_secret:
        return {"status": "skipped", "reason": "missing-feishu-credentials"}

    bundle_script = Path(__file__).resolve().parent / "push_report_to_feishu_bundle.py"
    command = [
        "python",
        str(bundle_script),
        "--input",
        resolved_report_json,
        "--app-id",
        resolved_app_id,
        "--app-secret",
        resolved_app_secret,
    ]
    if normalize_text(title):
        command.extend(["--title", normalize_text(title)])
    if normalize_text(base_name):
        command.extend(["--base-name", normalize_text(base_name)])

    push_result = run_subprocess(command)
    attempts = [push_result]
    if push_result["exit_code"] != 0 and looks_retryable_feishu_error(push_result):
        retry_result = run_subprocess(command)
        retry_result["retried_after"] = "feishu-code-10071"
        attempts.append(retry_result)
        push_result = retry_result
    if push_result["exit_code"] != 0:
        return {
            "status": "error",
            "report_json": resolved_report_json,
            "attempts": attempts,
            **push_result,
        }
    return {
        "status": "ok",
        "report_json": resolved_report_json,
        "attempts": attempts,
        **push_result["stdout"],
    }
