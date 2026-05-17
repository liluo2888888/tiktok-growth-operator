from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from generate_batch_preset import render_helper_cmd, render_helper_ps1
from recommend_entry_board import (
    build_bundle_generation_command,
    build_next_steps,
    enrich_with_bundle_paths,
    load_bundle_index,
    recommend_fallbacks,
    recommend_family,
    recommend_items,
    resolve_bundle_root,
)
from text_normalization import read_json_file, write_json_file, write_utf8_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Choose the best entry board from a natural-language request and scaffold a runnable local starter."
    )
    parser.add_argument("--query", required=True, help="Natural-language operator request.")
    parser.add_argument(
        "--bundle-root",
        default="",
        help="Optional template bundle root created by generate_batch_preset.py. If omitted, the latest local bundle is auto-discovered.",
    )
    parser.add_argument("--name", default="", help="Optional starter folder name override.")
    parser.add_argument("--project", default="", help="Optional project title override.")
    parser.add_argument("--output-root", default="", help="Optional explicit starter output root.")
    parser.add_argument("--top-k", type=int, default=3, help="How many ranked board recommendations to keep.")
    parser.add_argument("--generate", action="store_true", help="Generate the local queue immediately after scaffolding.")
    parser.add_argument("--dry-run", action="store_true", help="Run a batch dry-run after generation.")
    parser.add_argument("--run", action="store_true", help="Run the batch after generation.")
    return parser.parse_args()


def slugify(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in value.strip())
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-")


def first_non_empty(*values: str) -> str:
    for value in values:
        if value and value.strip():
            return value.strip()
    return ""


def resolve_output_root(args: argparse.Namespace, selected_slug: str) -> Path:
    if args.output_root.strip():
        return Path(args.output_root).expanduser().resolve()
    skill_root = Path(__file__).resolve().parents[1]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    seed = slugify(first_non_empty(args.name, selected_slug, "entry-board"))
    return (skill_root / "tmp" / f"{timestamp}-entry-board-{seed}").resolve()


def copy_if_exists(source: str, destination: Path) -> str:
    if not source:
        return ""
    source_path = Path(source)
    if not source_path.exists():
        return ""
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, destination)
    return str(destination)


def read_json(path: Path) -> dict:
    loaded = read_json_file(path)
    if not isinstance(loaded, dict):
        raise SystemExit(f"Expected JSON object: {path}")
    return loaded


def write_json(path: Path, payload: dict) -> None:
    write_json_file(path, payload)


def prepare_local_config(selected_item: dict, starter_root: Path) -> dict[str, str]:
    slug = selected_item["slug"]
    local_template_path = starter_root / f"{slug}.template.json"
    local_config_path = starter_root / f"{slug}.config.json"
    local_queue_path = starter_root / f"{slug}.json"
    local_batch_root = starter_root / "batch-run"
    local_result_path = starter_root / f"{slug}.result.json"
    local_manifest_path = starter_root / f"{slug}.manifest.json"
    local_report_path = starter_root / f"{slug}.report.md"
    local_input_path = starter_root / f"{slug}.input.json"
    local_batch_input_path = local_batch_root / "batch_input.json"
    local_batch_summary_path = local_batch_root / "summary.json"
    local_batch_result_path = local_batch_root / "batch_result.json"
    local_batch_report_path = local_batch_root / "batch_report.md"

    source_config = first_non_empty(selected_item.get("suite_config_json", ""), selected_item.get("template_file", ""))
    copied_template = copy_if_exists(selected_item.get("template_file", ""), local_template_path)

    if source_config:
        payload = read_json(Path(source_config))
    else:
        payload = {}

    payload["output"] = str(local_queue_path)
    notes = payload.get("_notes")
    if not isinstance(notes, dict):
        notes = {}
        payload["_notes"] = notes
    notes["starter_root"] = str(starter_root)
    notes["starter_queue_output"] = str(local_queue_path)
    notes["starter_batch_root"] = str(local_batch_root)
    notes["starter_result_file"] = str(local_result_path)
    write_json(local_config_path, payload)

    return {
        "template_file": copied_template,
        "suite_config_json": str(local_config_path),
        "suite_queue_json": str(local_queue_path),
        "local_batch_root": str(local_batch_root),
        "local_result_json": str(local_result_path),
        "local_manifest_json": str(local_manifest_path),
        "local_report_md": str(local_report_path),
        "local_input_json": str(local_input_path),
        "local_batch_input_json": str(local_batch_input_path),
        "local_batch_summary_json": str(local_batch_summary_path),
        "local_batch_result_json": str(local_batch_result_path),
        "local_batch_report_md": str(local_batch_report_path),
    }


def build_local_helper_scripts(selected_item: dict, starter_root: Path, local_paths: dict[str, str]) -> dict[str, str]:
    skill_root = Path(__file__).resolve().parents[1]
    slug = selected_item["slug"]
    local_generate_ps1 = starter_root / "generate.ps1"
    local_dry_run_ps1 = starter_root / "dry-run.ps1"
    local_run_ps1 = starter_root / "run.ps1"
    local_generate_cmd = starter_root / "generate.cmd"
    local_dry_run_cmd = starter_root / "dry-run.cmd"
    local_run_cmd = starter_root / "run.cmd"

    generate_args = [
        str(Path(__file__).resolve().parent / "generate_batch_preset.py"),
        "--config",
        local_paths["suite_config_json"],
    ]
    dry_run_args = [
        str(Path(__file__).resolve().parent / "batch_run_operator_workflows.py"),
        "--batch-file",
        local_paths["suite_queue_json"],
        "--dry-run",
        "--batch-root",
        local_paths["local_batch_root"],
    ]
    run_args = [
        str(Path(__file__).resolve().parent / "batch_run_operator_workflows.py"),
        "--batch-file",
        local_paths["suite_queue_json"],
        "--batch-root",
        local_paths["local_batch_root"],
        "--output-file",
        local_paths["local_result_json"],
    ]

    write_utf8_text(
        local_generate_ps1,
        render_helper_ps1(f"TikTok Growth Operator Starter Generate - {slug}", "python", generate_args, skill_root),
    )
    write_utf8_text(
        local_dry_run_ps1,
        render_helper_ps1(f"TikTok Growth Operator Starter Dry Run - {slug}", "python", dry_run_args, skill_root),
    )
    write_utf8_text(
        local_run_ps1,
        render_helper_ps1(f"TikTok Growth Operator Starter Run - {slug}", "python", run_args, skill_root),
    )
    write_utf8_text(local_generate_cmd, render_helper_cmd(local_generate_ps1))
    write_utf8_text(local_dry_run_cmd, render_helper_cmd(local_dry_run_ps1))
    write_utf8_text(local_run_cmd, render_helper_cmd(local_run_ps1))

    return {
        "local_generate_ps1": str(local_generate_ps1),
        "local_dry_run_ps1": str(local_dry_run_ps1),
        "local_run_ps1": str(local_run_ps1),
        "local_generate_cmd": str(local_generate_cmd),
        "local_dry_run_cmd": str(local_dry_run_cmd),
        "local_run_cmd": str(local_run_cmd),
    }


def build_local_next_steps(local_paths: dict[str, str], selected_item: dict) -> list[str]:
    steps: list[str] = []
    if local_paths.get("local_generate_ps1"):
        steps.append(f'powershell -ExecutionPolicy Bypass -File "{local_paths["local_generate_ps1"]}"')
    elif local_paths.get("template_file"):
        steps.append(f'python scripts/generate_batch_preset.py --config "{local_paths["template_file"]}"')
    if local_paths.get("local_dry_run_ps1"):
        steps.append(f'powershell -ExecutionPolicy Bypass -File "{local_paths["local_dry_run_ps1"]}"')
    if local_paths.get("local_run_ps1"):
        steps.append(f'powershell -ExecutionPolicy Bypass -File "{local_paths["local_run_ps1"]}"')
    if not steps:
        steps = build_next_steps(selected_item)
    return steps


def build_readme(
    query: str,
    family_pick: dict,
    selected_item: dict,
    starter_root: Path,
    local_paths: dict[str, str],
    fallbacks: list[dict],
    next_steps: list[str],
) -> str:
    lines = [
        "# Entry Board Starter",
        "",
        f"- query: `{query}`",
        f"- recommended family: `{family_pick['family']}`",
        f"- selected board: `{selected_item['slug']}`",
        f"- board label: `{selected_item['label']}`",
        f"- presets: `{', '.join(selected_item['presets'])}`",
        f"- starter root: `{starter_root}`",
        "",
        "## Why This Board",
        "",
        f"- {family_pick['description']}",
        f"- matched signals: `{', '.join(family_pick['matched_signals']) if family_pick['matched_signals'] else 'none'}`",
        f"- matched terms: `{', '.join(selected_item['matched_terms']) if selected_item['matched_terms'] else 'none'}`",
        "",
        "## Local Files",
        "",
        f"- recommendation JSON: `{local_paths.get('recommendation_json', '')}`",
        f"- copied template: `{local_paths.get('template_file', '') or 'n/a'}`",
        f"- copied suite config: `{local_paths.get('suite_config_json', '') or 'n/a'}`",
        f"- local queue path: `{local_paths.get('suite_queue_json', '') or 'n/a'}`",
        f"- expected preset manifest: `{local_paths.get('local_manifest_json', '') or 'n/a'}`",
        f"- expected preset report: `{local_paths.get('local_report_md', '') or 'n/a'}`",
        f"- expected reusable input file: `{local_paths.get('local_input_json', '') or 'n/a'}`",
        f"- local batch root: `{local_paths.get('local_batch_root', '') or 'n/a'}`",
        f"- expected batch report: `{local_paths.get('local_batch_report_md', '') or 'n/a'}`",
        f"- expected batch result JSON: `{local_paths.get('local_batch_result_json', '') or 'n/a'}`",
        f"- local result file: `{local_paths.get('local_result_json', '') or 'n/a'}`",
        "",
        "## Recommended Operator Order",
        "",
        "- 1. run the local `generate.ps1` helper to create the queue, preset report, manifest, and reusable input file",
        "- 2. read the generated preset report before execution because it contains the batch dry-run, run, and rerun commands in one place",
        "- 3. run the local `dry-run.ps1` helper to preview routing and artifact paths into the local batch root",
        "- 4. read the generated batch report before real execution because it summarizes each queued task and any warnings",
        "- 5. run the local `run.ps1` helper when the dry-run output looks correct",
        "- 6. if some items fail later, rerun from the generated batch root with `batch_run_operator_workflows.py --rerun-failed-from`",
        "",
        "## Next Steps",
        "",
    ]
    if next_steps:
        for step in next_steps:
            lines.append(f"- `{step}`")
    else:
        lines.append("- no helper scripts were available from this bundle item")
    lines.extend(["", "## Local Helper Scripts", ""])
    for key in ["local_generate_ps1", "local_dry_run_ps1", "local_run_ps1", "local_generate_cmd", "local_dry_run_cmd", "local_run_cmd"]:
        if local_paths.get(key):
            lines.append(f"- `{key}`: `{local_paths[key]}`")
    lines.extend(["", "## Generated-After-Run Artifacts", ""])
    for key in [
        "local_manifest_json",
        "local_report_md",
        "local_input_json",
        "local_batch_input_json",
        "local_batch_summary_json",
        "local_batch_result_json",
        "local_batch_report_md",
    ]:
        if local_paths.get(key):
            lines.append(f"- `{key}`: `{local_paths[key]}`")
    lines.extend(["", "## Fallback Boards", ""])
    for item in fallbacks:
        lines.append(f"- `{item['family']}` -> `{item['slug']}`: {item['description']}")
    return "\n".join(lines) + "\n"


def build_operator_handoff(local_paths: dict[str, str], next_steps: list[str]) -> dict:
    return {
        "read_order": [
            local_paths.get("recommendation_json", ""),
            local_paths.get("local_report_md", ""),
            local_paths.get("local_batch_report_md", ""),
            local_paths.get("local_batch_result_json", ""),
        ],
        "primary_files": {
            "starter_readme": str(Path(local_paths["recommendation_json"]).with_name("README.md")) if local_paths.get("recommendation_json") else "",
            "recommendation_json": local_paths.get("recommendation_json", ""),
            "queue_json": local_paths.get("suite_queue_json", ""),
            "preset_report_md": local_paths.get("local_report_md", ""),
            "batch_report_md": local_paths.get("local_batch_report_md", ""),
            "batch_result_json": local_paths.get("local_batch_result_json", ""),
            "result_json": local_paths.get("local_result_json", ""),
        },
        "commands": {
            "generate": next_steps[0] if len(next_steps) >= 1 else "",
            "dry_run": next_steps[1] if len(next_steps) >= 2 else "",
            "run": next_steps[2] if len(next_steps) >= 3 else "",
        },
        "recommended_flow": [
            "read starter README",
            "generate queue",
            "read preset report",
            "dry-run batch",
            "read batch report",
            "execute batch",
            "rerun failed items from batch root if needed",
        ],
    }


def build_status_summary(
    starter_root: Path,
    selected_item: dict,
    family_pick: dict,
    local_paths: dict[str, str],
    generate: bool,
    dry_run: bool,
    run: bool,
) -> dict:
    batch_report_exists = Path(local_paths["local_batch_report_md"]).exists() if local_paths.get("local_batch_report_md") else False
    batch_result_exists = Path(local_paths["local_batch_result_json"]).exists() if local_paths.get("local_batch_result_json") else False
    preset_report_exists = Path(local_paths["local_report_md"]).exists() if local_paths.get("local_report_md") else False
    queue_exists = Path(local_paths["suite_queue_json"]).exists() if local_paths.get("suite_queue_json") else False
    next_file_to_read = ""
    if batch_report_exists:
        next_file_to_read = local_paths["local_batch_report_md"]
    elif preset_report_exists:
        next_file_to_read = local_paths["local_report_md"]
    elif local_paths.get("recommendation_json"):
        next_file_to_read = local_paths["recommendation_json"]
    return {
        "starter_root": str(starter_root),
        "recommended_family": family_pick["family"],
        "selected_board_slug": selected_item["slug"],
        "selected_board_label": selected_item["label"],
        "generated_queue": generate or dry_run or run,
        "previewed_batch": dry_run,
        "executed_batch": run,
        "queue_exists": queue_exists,
        "preset_report_exists": preset_report_exists,
        "batch_report_exists": batch_report_exists,
        "batch_result_exists": batch_result_exists,
        "next_file_to_read": next_file_to_read,
    }


def run_python(script_path: Path, args: list[str]) -> None:
    subprocess.run([sys.executable, str(script_path), *args], cwd=str(Path(__file__).resolve().parents[1]), check=True)


def create_entry_board_starter(
    *,
    query: str,
    bundle_root: str = "",
    name: str = "",
    project: str = "",
    output_root: str = "",
    top_k: int = 3,
    generate: bool = False,
    dry_run: bool = False,
    run: bool = False,
) -> dict:
    requested_bundle_root = bundle_root
    resolved_bundle_root = resolve_bundle_root(bundle_root)
    bundle_items = load_bundle_index(resolved_bundle_root)
    if not bundle_items:
        raise SystemExit(
            "Bundle index not found or invalid. Generate one first with: "
            + build_bundle_generation_command()
        )
    bundle_root = Path(resolved_bundle_root)

    family_pick, family_scores = recommend_family(query)
    picks = recommend_items(query, family_pick["family"], limit=max(1, top_k))
    if not picks and family_pick["family"] == "single":
        fallback_family = "combo"
        picks = recommend_items(query, fallback_family, limit=max(1, top_k))
        family_pick = {
            **family_pick,
            "family": fallback_family,
            "label": "Combo Board",
            "description": "Single-preset requests without a direct single-board catalog fall back to combo-board selection.",
            "matched_signals": family_pick["matched_signals"] + ["single-family-fallback-to-combo"],
        }
    if not picks:
        raise SystemExit("No entry board candidates were found for this request.")

    picks = enrich_with_bundle_paths(picks, bundle_items)
    fallbacks = enrich_with_bundle_paths(
        recommend_fallbacks(query, family_pick["fallbacks"], per_family=2),
        bundle_items,
    )
    selected_item = picks[0]

    starter_args = argparse.Namespace(
        output_root=output_root,
        name=name,
    )
    starter_root = resolve_output_root(starter_args, selected_item["slug"])
    starter_root.mkdir(parents=True, exist_ok=True)

    local_paths = prepare_local_config(selected_item, starter_root)
    local_paths.update(build_local_helper_scripts(selected_item, starter_root, local_paths))
    local_next_steps = build_local_next_steps(local_paths, selected_item)

    if generate or dry_run or run:
        run_python(Path(__file__).resolve().parent / "generate_batch_preset.py", ["--config", local_paths["suite_config_json"]])
    if dry_run:
        run_python(
            Path(__file__).resolve().parent / "batch_run_operator_workflows.py",
            ["--batch-file", local_paths["suite_queue_json"], "--dry-run", "--batch-root", local_paths["local_batch_root"]],
        )
    if run:
        run_python(
            Path(__file__).resolve().parent / "batch_run_operator_workflows.py",
            [
                "--batch-file",
                local_paths["suite_queue_json"],
                "--batch-root",
                local_paths["local_batch_root"],
                "--output-file",
                local_paths["local_result_json"],
            ],
        )

    manifest = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "query": query,
        "requested_bundle_root": requested_bundle_root,
        "bundle_root": str(bundle_root),
        "starter_root": str(starter_root),
        "project": first_non_empty(project, selected_item["label"]),
        "recommended_family": family_pick["family"],
        "family_description": family_pick["description"],
        "matched_signals": family_pick["matched_signals"],
        "selected_board": selected_item,
        "ranked_boards": picks,
        "fallback_boards": fallbacks,
        "family_scoreboard": family_scores,
        "local_paths": local_paths,
        "next_steps": local_next_steps,
        "executed_actions": {
            "generate": generate or dry_run or run,
            "dry_run": dry_run,
            "run": run,
        },
    }

    recommendation_json = starter_root / "entry-board-recommendation.json"
    write_json_file(recommendation_json, manifest)
    local_paths["recommendation_json"] = str(recommendation_json)

    readme_path = starter_root / "README.md"
    write_utf8_text(
        readme_path,
        build_readme(query, family_pick, selected_item, starter_root, local_paths, fallbacks, local_next_steps),
    )
    operator_handoff = build_operator_handoff(local_paths, local_next_steps)
    status_summary = build_status_summary(
        starter_root,
        selected_item,
        family_pick,
        local_paths,
        generate,
        dry_run,
        run,
    )

    return {
        "starter_root": str(starter_root),
        "project": manifest["project"],
        "recommended_family": family_pick["family"],
        "selected_board_slug": selected_item["slug"],
        "selected_board_label": selected_item["label"],
        "status_summary": status_summary,
        "operator_handoff": operator_handoff,
        "local_paths": local_paths,
        "next_steps": local_next_steps,
        "recommendation_manifest": manifest,
    }


def main() -> None:
    args = parse_args()
    result = create_entry_board_starter(
        query=args.query,
        bundle_root=args.bundle_root,
        name=args.name,
        project=args.project,
        output_root=args.output_root,
        top_k=args.top_k,
        generate=args.generate,
        dry_run=args.dry_run,
        run=args.run,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
