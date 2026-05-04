from __future__ import annotations

import json
import re
from pathlib import Path


REFERENCE_FILES = [
    "SKILL.md",
    "references/direct-use.md",
    "references/automation-workflows.md",
    "references/final-handoff.md",
    "references/entry-selector.md",
    "references/article-2640429-feature-parity.md",
    "references/command-map.md",
    "references/prompt-library.md",
    "references/scene-report-contract.md",
    "references/scene-report-example.json",
    "references/scene-quick-reference.md",
    "references/creative-brief-quick-reference.md",
    "references/route-eval-fixtures.json",
    "references/source-map.md",
]

MOJIBAKE_PATTERNS = [
    "Ã",
    "Â",
    "鈥",
    "锟",
    "�",
    "閳",
    "閿",
    "鐢",
    "闂",
    "鍙",
    "鎴",
    "涓€",
    "缁欐垜",
    "璺戝満鏅",
    "鍋氫竴涓",
    "鐩存帴鐢",
    "宸ヤ綔娴",
    "鐩存挱杩愯惀",
    "鑳借窇",
    "\ufffd",
]


def extract_relative_markdown_links(text: str) -> list[str]:
    matches = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
    return [
        target
        for target in matches
        if target
        and not target.startswith("http://")
        and not target.startswith("https://")
        and not re.match(r"^[A-Za-z]:/", target)
        and not target.startswith("/D:/")
        and not target.startswith("file:")
        and not target.startswith("#")
    ]


def extract_absolute_local_markdown_links(text: str) -> list[str]:
    matches = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
    return [target for target in matches if target.startswith("/D:/")]


def find_mojibake_lines(text: str) -> list[tuple[int, str]]:
    findings: list[tuple[int, str]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if any(pattern in line for pattern in MOJIBAKE_PATTERNS):
            findings.append((line_number, line.strip()))
    return findings


def main() -> int:
    skill_root = Path(__file__).resolve().parents[1]
    errors: list[str] = []
    checked: list[str] = []

    for relative_path in REFERENCE_FILES:
        path = skill_root / relative_path
        if not path.exists():
            errors.append(f"Missing required file: {relative_path}")
            continue
        checked.append(relative_path)
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".json":
            try:
                json.loads(text)
            except json.JSONDecodeError as exc:
                errors.append(f"{relative_path} is not valid JSON: {exc}")
        for target in extract_relative_markdown_links(text):
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                errors.append(f"{relative_path} references missing path: {target}")
        for target in extract_absolute_local_markdown_links(text):
            resolved = Path(target.lstrip("/"))
            if not resolved.exists():
                errors.append(f"{relative_path} references missing absolute local path: {target}")
        for line_number, line in find_mojibake_lines(text):
            errors.append(f"{relative_path} contains mojibake at line {line_number}: {line}")

    required_mentions = {
        "SKILL.md": [
            "references/final-handoff.md",
            "references/direct-use.md",
            "references/automation-workflows.md",
            "references/entry-selector.md",
        ],
        "references/direct-use.md": [
            "final-handoff.md",
            "validate_all_workflows.py",
            "recommend_entry_board.py",
            "start_entry_board.py",
            "scene-quick-reference.md",
            "creative-brief-quick-reference.md",
            "One-Line Chinese Starter",
            "Chinese Copy-Ready Commands",
            "给我一套从选题、拆解、素材测试到发布交付的 Douyin 工作流",
        ],
        "references/automation-workflows.md": [
            "scripts/validate_all_workflows.py",
            "scripts/validate_export_outputs.py",
            "scripts/recommend_entry_board.py",
            "scripts/start_entry_board.py",
        ],
        "references/final-handoff.md": [
            "scripts/validate_all_workflows.py",
            "scripts/run_operator_workflow.py",
            "scripts/recommend_entry_board.py",
            "scripts/start_entry_board.py",
        ],
        "references/entry-selector.md": [
            "recommend_entry_board.py",
            "start_entry_board.py",
            "launch-board",
            "manager-board",
            "cadence-board",
        ],
        "references/scene-report-contract.md": [
            "execution_template",
            "recommended_request",
            "recommended_runner_args",
            "scene-report-example.json",
        ],
        "references/scene-report-example.json": [
            "\"operator_guide\"",
            "\"execution_template\"",
            "\"minimum_evidence\"",
            "\"ready_checklist\"",
            "\"recommended_request_zh\"",
            "\"codex_prompt_scaffold_zh\"",
        ],
        "references/route-eval-fixtures.json": [
            "\"run_operator_auto_cases\"",
            "\"recommend_entry_board_cases\"",
            "\"expected_mode\"",
            "\"expected_slug\"",
        ],
        "references/scene-quick-reference.md": [
            "19 One-Line Chinese Requests",
            "Scene 01",
            "中文请求",
            "English Request",
            "Main Runner",
            "Quick Copy CN",
        ],
        "references/creative-brief-quick-reference.md": [
            "Creative Brief Quick Reference",
            "Scene 09",
            "只复制这一句",
            "Brief Blocks To Fill",
            "中文 Prompt Scaffold",
        ],
    }

    for relative_path, snippets in required_mentions.items():
        path = skill_root / relative_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for snippet in snippets:
            if snippet not in text:
                errors.append(f"{relative_path} is missing expected reference: {snippet}")

    payload = {
        "ok": not errors,
        "checked_files": checked,
        "errors": errors,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
