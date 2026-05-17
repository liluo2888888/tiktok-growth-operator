from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

from feishu_naming import build_task_title, normalize_scene_id, scene_label_zh
from text_normalization import normalize_text, read_json_file


SCRIPT_ROOT = Path(__file__).resolve().parent
BUNDLE_SCRIPT = SCRIPT_ROOT / "push_report_to_feishu_bundle.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Push every successful scene report found in one batch_result.json payload into Feishu."
    )
    parser.add_argument("--batch-result", required=True, help="Path to batch_result.json or the combined result JSON file.")
    parser.add_argument("--app-id", default=os.environ.get("FEISHU_APP_ID", ""), help="Feishu app ID.")
    parser.add_argument("--app-secret", default=os.environ.get("FEISHU_APP_SECRET", ""), help="Feishu app secret.")
    parser.add_argument(
        "--scenes",
        default="",
        help="Optional comma-separated scene ids to push, for example 01,03,18,19.",
    )
    parser.add_argument("--skip-doc", action="store_true", help="Skip Feishu Doc creation.")
    parser.add_argument("--skip-bitable", action="store_true", help="Skip Feishu Bitable creation.")
    return parser.parse_args()


def require(value: str, label: str) -> str:
    text = normalize_text(value)
    if not text:
        raise SystemExit(f"Missing required {label}.")
    return text


def build_period(scene_id: str) -> str:
    now = datetime.now()
    if scene_id in {"18", "19"}:
        iso_year, iso_week, _ = now.isocalendar()
        return f"{iso_year}-W{iso_week:02d}"
    return now.strftime("%Y-%m-%d")


def build_title(task: dict, result: dict) -> str:
    del result
    return build_task_title(task)


def load_payload(path: Path) -> dict:
    payload = read_json_file(path)
    if not isinstance(payload, dict) or "results" not in payload:
        raise SystemExit("batch-result must point to a prior batch_result.json-style payload.")
    return payload


def parse_scene_filter(raw: str) -> set[str]:
    values = set()
    for chunk in raw.split(","):
        scene_id = normalize_scene_id(chunk)
        if scene_id:
            values.add(scene_id)
    return values


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


def extract_push_jobs(payload: dict, scene_filter: set[str]) -> list[dict]:
    jobs: list[dict] = []
    for item in payload.get("results", []):
        if not isinstance(item, dict) or item.get("status") != "success":
            continue
        task = item.get("task", {})
        result = item.get("result", {})
        if not isinstance(task, dict) or not isinstance(result, dict):
            continue
        report_json = normalize_text(result.get("report_json"))
        if not report_json:
            continue
        scene_id = normalize_scene_id(task.get("scene"))
        if scene_filter and scene_id not in scene_filter:
            continue
        jobs.append(
            {
                "index": item.get("index"),
                "scene": scene_id,
                "task": task,
                "result": result,
                "report_json": report_json,
                "title": build_title(task, result),
            }
        )
    return jobs


def main() -> None:
    args = parse_args()
    app_id = require(args.app_id, "app_id")
    app_secret = require(args.app_secret, "app_secret")
    payload = load_payload(Path(args.batch_result).expanduser().resolve())
    scene_filter = parse_scene_filter(args.scenes)
    jobs = extract_push_jobs(payload, scene_filter)

    results = []
    any_failure = False
    for job in jobs:
        command = [
            "python",
            str(BUNDLE_SCRIPT),
            "--input",
            job["report_json"],
            "--app-id",
            app_id,
            "--app-secret",
            app_secret,
            "--title",
            job["title"],
            "--base-name",
            job["title"],
        ]
        if args.skip_doc:
            command.append("--skip-doc")
        if args.skip_bitable:
            command.append("--skip-bitable")
        outcome = run_command(command)
        row = {
            "index": job["index"],
            "scene": job["scene"],
            "title": job["title"],
            "report_json": job["report_json"],
            "push_result": outcome,
        }
        if outcome["exit_code"] != 0:
            any_failure = True
        results.append(row)

    summary = {
        "status": "error" if any_failure else "ok",
        "batch_result": str(Path(args.batch_result).expanduser().resolve()),
        "count": len(results),
        "pushed": sum(1 for item in results if item["push_result"]["exit_code"] == 0),
        "failed": sum(1 for item in results if item["push_result"]["exit_code"] != 0),
        "results": results,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if any_failure:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
