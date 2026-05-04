from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def assert_history_dedup(summary_stdout: str, project_root: Path) -> None:
    payload = json.loads(summary_stdout)
    matching = [item for item in payload.get("entries", []) if item.get("root") == str(project_root)]
    if len(matching) != 1:
        raise RuntimeError(
            f"Run history dedup regression: expected exactly 1 entry for {project_root}, got {len(matching)}."
        )


SCRIPTS = [
    "import_tiktok_capture_pack.py",
    "start_capture_pack_run.py",
    "run_operator_workflow.py",
    "batch_run_operator_workflows.py",
    "start_project_workflow.py",
    "summarize_run_history.py",
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
    workspace_root = skill_root.parent
    capture_comment = workspace_root / "captures" / "tiktok-download-validated-20260423"
    capture_ranked = workspace_root / "captures" / "tiktok-analysis-pack-smoke-20260423f"

    results = []
    for script_name in SCRIPTS:
        results.append(run([sys.executable, "-m", "py_compile", str(scripts_root / script_name)]))

    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "start_capture_pack_run.py"),
                "--scene",
                "auto",
                "--capture-root",
                str(capture_comment),
                "--name",
                "validation-auto-capture",
                "--project",
                "TikTok Validation Auto Capture",
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--output-root",
                str(skill_root / "tmp" / "20260504_validation_capture_scene_auto"),
            ]
        )
    )
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "run_operator_workflow.py"),
                "--mode",
                "capture-pack",
                "--scene",
                "17",
                "--capture-root",
                str(capture_ranked),
                "--name",
                "validation-routed-capture",
                "--project",
                "TikTok Validation Routed Capture",
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--output-root",
                str(skill_root / "tmp" / "20260504_validation_routed_capture"),
                "--formats",
                "md",
            ]
        )
    )
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "start_capture_pack_run.py"),
                "--scene",
                "15",
                "--capture-root",
                str(capture_ranked),
                "--target-languages",
                "English,Japanese,German",
                "--name",
                "validation-scene15-capture",
                "--project",
                "TikTok Validation Scene 15 Capture",
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--output-root",
                str(skill_root / "tmp" / "20260504_validation_capture_scene15"),
                "--formats",
                "md",
            ]
        )
    )
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "start_capture_pack_run.py"),
                "--scene",
                "13",
                "--capture-root",
                str(capture_ranked),
                "--target-markets",
                "US,Japan,Germany",
                "--name",
                "validation-scene13-capture",
                "--project",
                "TikTok Validation Scene 13 Capture",
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--output-root",
                str(skill_root / "tmp" / "20260504_validation_capture_scene13"),
                "--formats",
                "md",
            ]
        )
    )
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "start_capture_pack_run.py"),
                "--scene",
                "16",
                "--capture-root",
                str(capture_ranked),
                "--name",
                "validation-scene16-capture",
                "--project",
                "TikTok Validation Scene 16 Capture",
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--output-root",
                str(skill_root / "tmp" / "20260504_validation_capture_scene16"),
                "--formats",
                "md",
            ]
        )
    )
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "start_capture_pack_run.py"),
                "--scene",
                "11",
                "--capture-root",
                str(capture_ranked),
                "--name",
                "validation-scene11-capture",
                "--project",
                "TikTok Validation Scene 11 Capture",
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--output-root",
                str(skill_root / "tmp" / "20260504_validation_capture_scene11"),
                "--formats",
                "md",
            ]
        )
    )
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "start_capture_pack_run.py"),
                "--scene",
                "12",
                "--capture-root",
                str(capture_ranked),
                "--name",
                "validation-scene12-capture",
                "--project",
                "TikTok Validation Scene 12 Capture",
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--output-root",
                str(skill_root / "tmp" / "20260504_validation_capture_scene12"),
                "--formats",
                "md",
            ]
        )
    )
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "start_capture_pack_run.py"),
                "--scene",
                "14",
                "--capture-root",
                str(capture_ranked),
                "--name",
                "validation-scene14-capture",
                "--project",
                "TikTok Validation Scene 14 Capture",
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--output-root",
                str(skill_root / "tmp" / "20260504_validation_capture_scene14"),
                "--formats",
                "md",
            ]
        )
    )
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "run_operator_workflow.py"),
                "--mode",
                "history",
                "--history-output-json",
                str(skill_root / "tmp" / "20260504_validation_run_history_unified.json"),
                "--history-output-md",
                str(skill_root / "tmp" / "20260504_validation_run_history_unified.md"),
                "--history-limit",
                "20",
            ]
        )
    )
    results.append(
        run(
            [
                sys.executable,
                str(scripts_root / "summarize_run_history.py"),
                "--output-json",
                str(skill_root / "tmp" / "20260504_validation_run_history.json"),
                "--output-md",
                str(skill_root / "tmp" / "20260504_validation_run_history.md"),
                "--limit",
                "20",
            ]
        )
    )

    project_launcher_root = skill_root / "tmp" / "20260504_project_launcher_test"
    dedup_check = run(
        [
            sys.executable,
            str(scripts_root / "summarize_run_history.py"),
            "--root",
            str(project_launcher_root.parent),
            "--limit",
            "50",
        ]
    )
    try:
        assert_history_dedup(dedup_check["stdout"], project_launcher_root)
    except BaseException as exc:  # noqa: BLE001
        dedup_check["returncode"] = 1
        dedup_check["stderr"] = str(exc)
    results.append(dedup_check)

    py_compile_failures = [
        item
        for item in results
        if item["command"][1:3] == ["-m", "py_compile"] and item["returncode"] != 0 and "拒绝访问" not in item["stderr"]
    ]
    runtime_failures = [
        item
        for item in results
        if not (item["command"][1:3] == ["-m", "py_compile"]) and item["returncode"] != 0
    ]
    payload = {
        "success": not py_compile_failures and not runtime_failures,
        "results": results,
        "notes": [
            "Windows py_compile can hit transient __pycache__ file-lock races; those are reported but not treated as code failures if runtime checks pass."
        ],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
