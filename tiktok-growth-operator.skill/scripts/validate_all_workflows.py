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
