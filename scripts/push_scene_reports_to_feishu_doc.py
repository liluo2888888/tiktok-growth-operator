from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

from feishu_naming import build_report_title
from text_normalization import normalize_text, read_json_file


SCRIPT_ROOT = Path(__file__).resolve().parent
DOC_SCRIPT = SCRIPT_ROOT / "push_report_to_feishu_doc.py"
DEFAULT_CONFIRMED_INPUT_FILE = SCRIPT_ROOT.parent / "references" / "feishu-confirmed-scene-inputs.txt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Push selected scene report JSON files into Feishu Docs with the Chinese finished-doc renderer."
    )
    parser.add_argument("--inputs", nargs="+", help="One or more scene report JSON files.")
    parser.add_argument("--input-file", default="", help="Optional text file listing one scene report JSON path per line.")
    parser.add_argument(
        "--confirmed",
        action="store_true",
        help="Use the built-in confirmed real-scene input list under references/feishu-confirmed-scene-inputs.txt.",
    )
    parser.add_argument("--app-id", default=os.environ.get("FEISHU_APP_ID", ""), help="Feishu app ID.")
    parser.add_argument("--app-secret", default=os.environ.get("FEISHU_APP_SECRET", ""), help="Feishu app secret.")
    parser.add_argument("--title-prefix", default="", help="Optional title prefix added before the auto title.")
    return parser.parse_args()


def require(value: str, label: str) -> str:
    text = normalize_text(value)
    if not text:
        raise SystemExit(f"Missing required {label}.")
    return text


def load_inputs(args: argparse.Namespace) -> list[Path]:
    values: list[str] = []
    if args.inputs:
        values.extend(args.inputs)
    input_file = normalize_text(args.input_file)
    if args.confirmed:
        input_file = str(DEFAULT_CONFIRMED_INPUT_FILE)
    if input_file:
        for line in Path(input_file).read_text(encoding="utf-8").splitlines():
            candidate = normalize_text(line)
            if candidate and not candidate.startswith("#"):
                values.append(candidate)
    resolved = []
    seen = set()
    for value in values:
        path = Path(value).expanduser().resolve()
        key = str(path).lower()
        if key in seen:
            continue
        if not path.is_file():
            raise SystemExit(f"Input report not found: {path}")
        seen.add(key)
        resolved.append(path)
    if not resolved:
        raise SystemExit("No report inputs provided.")
    return resolved


def build_title(path: Path, title_prefix: str) -> str:
    payload = read_json_file(path)
    if not isinstance(payload, dict):
        return f"{title_prefix}{path.stem}" if title_prefix else path.stem
    metadata = payload.get("metadata") or {}
    auto_title = build_report_title(
        metadata.get("project"),
        metadata.get("scene"),
        metadata.get("scene_title"),
    )
    prefix = normalize_text(title_prefix)
    if prefix:
        return f"{prefix} | {auto_title}"
    return auto_title


def run_push(path: Path, app_id: str, app_secret: str, title: str) -> dict:
    command = [
        "python",
        str(DOC_SCRIPT),
        "--input",
        str(path),
        "--mode",
        "create",
        "--backend",
        "api",
        "--app-id",
        app_id,
        "--app-secret",
        app_secret,
        "--title",
        title,
    ]
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
        parsed = json.loads(stdout) if stdout.strip() else {}
    except json.JSONDecodeError:
        parsed = {"raw_stdout": stdout}
    return {
        "command": command,
        "exit_code": completed.returncode,
        "stdout": parsed,
        "stderr": stderr,
    }


def main() -> None:
    args = parse_args()
    app_id = require(args.app_id, "app_id")
    app_secret = require(args.app_secret, "app_secret")
    inputs = load_inputs(args)

    results = []
    any_failure = False
    for path in inputs:
        title = build_title(path, args.title_prefix)
        outcome = run_push(path, app_id, app_secret, title)
        if outcome["exit_code"] != 0:
            any_failure = True
        results.append(
            {
                "input": str(path),
                "title": title,
                "push_result": outcome,
            }
        )

    summary = {
        "status": "error" if any_failure else "ok",
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
