from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

from text_normalization import normalize_text


SCRIPT_ROOT = Path(__file__).resolve().parent
DOC_SCRIPT = SCRIPT_ROOT / "push_report_to_feishu_doc.py"
BITABLE_SCRIPT = SCRIPT_ROOT / "push_report_to_feishu.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Push one scene report to Feishu as both a Doc and a full Bitable bundle."
    )
    parser.add_argument("--input", required=True, help="Structured scene report JSON path.")
    parser.add_argument("--app-id", default=os.environ.get("FEISHU_APP_ID", ""), help="Feishu app ID.")
    parser.add_argument("--app-secret", default=os.environ.get("FEISHU_APP_SECRET", ""), help="Feishu app secret.")
    parser.add_argument("--title", default="", help="Optional explicit Feishu Doc title.")
    parser.add_argument("--base-name", default="", help="Optional explicit Feishu Bitable app name.")
    parser.add_argument(
        "--bitable-modes",
        default="summary,section_overview,evidence,assets",
        help="Comma-separated Bitable surfaces to push.",
    )
    parser.add_argument("--skip-doc", action="store_true", help="Skip Feishu Doc creation.")
    parser.add_argument("--skip-bitable", action="store_true", help="Skip Feishu Bitable creation.")
    return parser.parse_args()


def require(value: str, label: str) -> str:
    text = normalize_text(value)
    if not text:
        raise SystemExit(f"Missing required {label}.")
    return text


def run_command(command: list[str]) -> dict:
    completed = subprocess.run(
        command,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    stdout = normalize_text(completed.stdout, strip=False)
    stderr = normalize_text(completed.stderr, strip=False)
    parsed_stdout: object
    try:
        parsed_stdout = json.loads(stdout) if stdout.strip() else {}
    except json.JSONDecodeError:
        parsed_stdout = {"raw_stdout": stdout}
    return {
        "command": command,
        "exit_code": completed.returncode,
        "stdout": parsed_stdout,
        "stderr": stderr,
    }


def main() -> None:
    args = parse_args()
    app_id = require(args.app_id, "app_id")
    app_secret = require(args.app_secret, "app_secret")
    input_path = str(Path(args.input))

    results: dict[str, object] = {}
    app_token = ""

    if not args.skip_doc:
        command = [
            "python",
            str(DOC_SCRIPT),
            "--input",
            input_path,
            "--mode",
            "create",
            "--backend",
            "api",
            "--app-id",
            app_id,
            "--app-secret",
            app_secret,
        ]
        if normalize_text(args.title):
            command.extend(["--title", normalize_text(args.title)])
        doc_result = run_command(command)
        results["doc"] = doc_result
        if doc_result["exit_code"] != 0:
            print(json.dumps({"status": "error", "results": results}, ensure_ascii=False, indent=2))
            raise SystemExit(1)

    if not args.skip_bitable:
        modes = [normalize_text(item) for item in args.bitable_modes.split(",") if normalize_text(item)]
        bitable_results = []
        for index, mode in enumerate(modes):
            command = [
                "python",
                str(BITABLE_SCRIPT),
                "--input",
                input_path,
                "--mode",
                mode,
                "--app-id",
                app_id,
                "--app-secret",
                app_secret,
            ]
            if app_token:
                command.extend(["--app-token", app_token])
            elif normalize_text(args.base_name):
                command.extend(["--base-name", normalize_text(args.base_name)])
            result = run_command(command)
            bitable_results.append(result)
            if result["exit_code"] != 0:
                results["bitable"] = bitable_results
                print(json.dumps({"status": "error", "results": results}, ensure_ascii=False, indent=2))
                raise SystemExit(1)
            if index == 0:
                app_token = normalize_text(((result["stdout"] or {}).get("app_token"))) if isinstance(result["stdout"], dict) else ""
        results["bitable"] = bitable_results

    summary = {
        "status": "ok",
        "doc_url": "",
        "bitable_app_url": "",
        "bitable_app_token": app_token,
        "results": results,
    }
    doc_stdout = ((results.get("doc") or {}).get("stdout")) if isinstance(results.get("doc"), dict) else {}
    if isinstance(doc_stdout, dict):
        summary["doc_url"] = normalize_text(doc_stdout.get("document_url"))
    bitable_runs = results.get("bitable") or []
    if isinstance(bitable_runs, list) and bitable_runs:
        first_stdout = bitable_runs[0].get("stdout") or {}
        if isinstance(first_stdout, dict):
            summary["bitable_app_url"] = normalize_text(first_stdout.get("app_url"))

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
