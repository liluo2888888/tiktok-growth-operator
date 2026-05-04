from __future__ import annotations

import argparse
import json
import traceback
from datetime import datetime
from pathlib import Path

from run_operator_workflow import (
    infer_mode_from_request,
    run_board_mode,
    run_capture_pack_mode,
    run_goal_mode,
    run_history_mode,
    run_pack_mode,
    run_scene_mode,
)


def slugify(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in value.strip())
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-")


def read_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def has_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def build_namespace(item: dict, defaults: dict) -> argparse.Namespace:
    merged = {
        "mode": item.get("mode", defaults.get("mode", "auto")),
        "request": item.get("request", defaults.get("request")),
        "scene": item.get("scene", defaults.get("scene")),
        "goal": item.get("goal", defaults.get("goal")),
        "query": item.get("query", defaults.get("query")),
        "bundle_root": item.get("bundle_root", defaults.get("bundle_root", "")),
        "top_k": item.get("top_k", defaults.get("top_k", 3)),
        "generate": item.get("generate", defaults.get("generate", False)),
        "dry_run": item.get("dry_run", defaults.get("dry_run", False)),
        "run": item.get("run", defaults.get("run", False)),
        "type": item.get("type", defaults.get("type")),
        "capture_root": item.get("capture_root", defaults.get("capture_root", "")),
        "target_markets": item.get("target_markets", defaults.get("target_markets", "")),
        "target_languages": item.get("target_languages", defaults.get("target_languages", "")),
        "name": item.get("name", defaults.get("name", "")),
        "project": item.get("project", defaults.get("project", "")),
        "context_file": item.get("context_file", defaults.get("context_file")),
        "output_root": item.get("output_root", defaults.get("output_root", "")),
        "output_dir": item.get("output_dir", defaults.get("output_dir", "")),
        "formats": item.get("formats", defaults.get("formats", "md")),
        "platform": item.get("platform", defaults.get("platform", "Douyin")),
        "market": item.get("market", defaults.get("market", "China")),
        "source_report": item.get("source_report", defaults.get("source_report")),
        "history_root": item.get("history_root", defaults.get("history_root", "")),
        "history_output_json": item.get("history_output_json", defaults.get("history_output_json", "")),
        "history_output_md": item.get("history_output_md", defaults.get("history_output_md", "")),
        "history_limit": item.get("history_limit", defaults.get("history_limit", 50)),
    }
    return argparse.Namespace(**merged)


def run_item(args: argparse.Namespace) -> dict:
    route_meta: dict = {"requested_mode": args.mode}

    if args.mode == "auto":
        routed_mode, routed = infer_mode_from_request(args)
        route_meta["resolved_mode"] = routed_mode
        route_meta.update(routed)
        if routed_mode == "scene":
            result = run_scene_mode(args, scene_override=routed.get("scene"), request_text=routed.get("request", ""))
        elif routed_mode == "board":
            result = run_board_mode(args, query_override=routed.get("query"))
        elif routed_mode == "goal":
            result = run_goal_mode(args, goal_override=routed.get("goal"), query_override=routed.get("query"))
        elif routed_mode == "capture-pack":
            result = run_capture_pack_mode(
                args,
                scene_override=routed.get("scene"),
                request_text=routed.get("request", ""),
            )
        elif routed_mode == "history":
            result = run_history_mode(args)
        else:
            result = run_pack_mode(args, pack_type_override=routed.get("type"), request_text=routed.get("request", ""))
        return {"route": route_meta, **result}

    if args.mode == "scene":
        return run_scene_mode(args)
    if args.mode == "board":
        return run_board_mode(args)
    if args.mode == "goal":
        return run_goal_mode(args)
    if args.mode == "capture-pack":
        return run_capture_pack_mode(args)
    if args.mode == "history":
        return run_history_mode(args)
    if args.mode == "pack":
        return run_pack_mode(args)
    raise SystemExit(f"Unsupported mode: {args.mode}")


def preview_payload(args: argparse.Namespace, resolved_mode: str, routed: dict | None = None) -> dict:
    routed = routed or {}
    return {
        "would_run_mode": resolved_mode,
        "project": args.project,
        "name": args.name,
        "request": routed.get("request", args.request),
        "query": routed.get("query", args.query),
        "scene": routed.get("scene", args.scene),
        "goal": routed.get("goal", args.goal),
        "bundle_root": args.bundle_root,
        "top_k": args.top_k,
        "generate": args.generate,
        "task_dry_run": args.dry_run,
        "task_run": args.run,
        "pack_type": routed.get("type", args.type),
        "capture_root": args.capture_root,
        "target_markets": args.target_markets,
        "target_languages": args.target_languages,
        "output_root": args.output_root,
        "output_dir": args.output_dir,
        "history_root": args.history_root,
        "history_output_json": args.history_output_json,
        "history_output_md": args.history_output_md,
        "history_limit": args.history_limit,
        "formats": args.formats,
        "platform": args.platform,
        "market": args.market,
    }


def preview_item(args: argparse.Namespace) -> dict:
    route_meta: dict = {"requested_mode": args.mode}

    if args.mode == "auto":
        routed_mode, routed = infer_mode_from_request(args)
        route_meta["resolved_mode"] = routed_mode
        route_meta.update(routed)
        return {
            "route": route_meta,
            "preview": preview_payload(args, routed_mode, routed),
        }

    return {
        "preview": preview_payload(args, args.mode),
    }


def add_warning_if_present(warnings: list[str], value: object, message: str) -> None:
    if has_text(value):
        warnings.append(message)


def add_mode_specific_warnings(args: argparse.Namespace, resolved_mode: str, warnings: list[str]) -> None:
    if resolved_mode in {"scene", "goal", "board", "capture-pack", "history"}:
        add_warning_if_present(warnings, args.output_dir, "output_dir is ignored outside pack mode.")
    if resolved_mode == "pack":
        add_warning_if_present(warnings, args.output_root, "output_root is ignored in pack mode.")
    if resolved_mode != "pack":
        add_warning_if_present(warnings, args.source_report, "source_report is ignored outside pack mode.")
    if resolved_mode != "capture-pack":
        add_warning_if_present(warnings, args.capture_root, "capture_root is ignored outside capture-pack mode.")
        add_warning_if_present(warnings, args.target_markets, "target_markets is ignored outside capture-pack mode.")
        add_warning_if_present(warnings, args.target_languages, "target_languages is ignored outside capture-pack mode.")
    if resolved_mode != "goal":
        add_warning_if_present(warnings, args.goal, "goal is ignored outside goal mode.")
    if resolved_mode not in {"goal", "board"}:
        add_warning_if_present(warnings, args.query, "query is ignored outside goal/board mode unless auto routing uses it.")
    if resolved_mode not in {"scene", "capture-pack"}:
        add_warning_if_present(warnings, args.scene, "scene is ignored outside scene mode unless routing uses it.")
    if resolved_mode != "pack":
        add_warning_if_present(warnings, args.type, "type is ignored outside pack mode unless routing uses it.")
    if resolved_mode != "board":
        add_warning_if_present(warnings, args.bundle_root, "bundle_root is ignored outside board mode unless auto routing uses it.")
        if args.top_k != 3:
            warnings.append("top_k is ignored outside board mode.")
        if args.generate:
            warnings.append("generate is ignored outside board mode.")
        if args.dry_run:
            warnings.append("dry_run is ignored outside board mode.")
        if args.run:
            warnings.append("run is ignored outside board mode.")
    if resolved_mode != "history":
        add_warning_if_present(warnings, args.history_root, "history_root is ignored outside history mode unless auto routing uses it.")
        add_warning_if_present(warnings, args.history_output_json, "history_output_json is ignored outside history mode unless auto routing uses it.")
        add_warning_if_present(warnings, args.history_output_md, "history_output_md is ignored outside history mode unless auto routing uses it.")


def build_validation_suggestions(args: argparse.Namespace, resolved_mode: str, warnings: list[str], errors: list[str]) -> list[str]:
    suggestions: list[str] = []
    if resolved_mode == "pack":
        if not has_text(args.type):
            suggestions.append("Add type=publish-prep or type=live-assist.")
        if not has_text(args.project) and not has_text(args.source_report):
            suggestions.append("Provide project, or provide source_report pointing to a structured scene report JSON.")
    if resolved_mode == "capture-pack":
        if not has_text(args.scene):
            suggestions.append("Add scene with a supported capture-pack scene such as 03, 08, 13, 15, 17, 18, or 19.")
        if not has_text(args.capture_root):
            suggestions.append("Provide capture_root pointing to a real TikTok capture-pack directory.")
        if str(args.scene).strip() == "15" and not has_text(args.target_languages):
            suggestions.append("Add target_languages for scene 15, for example English,Japanese,German.")
    if resolved_mode == "scene" and not has_text(args.scene):
        suggestions.append("Add scene with a concrete scene id such as 03 or 12.")
    if resolved_mode == "goal" and bool(has_text(args.goal)) == bool(has_text(args.query)):
        suggestions.append("Provide exactly one of goal or query for goal mode.")
    if resolved_mode == "board" and not (has_text(args.query) or has_text(args.request)):
        suggestions.append("Provide query or request for board mode.")
    if resolved_mode == "history" and args.history_limit <= 0:
        suggestions.append("Set history_limit to a positive integer.")
    if args.mode == "auto" and errors:
        suggestions.append("Add request, or provide explicit mode fields such as scene, goal, type, or capture_root.")
    for warning in warnings:
        if "output_dir is ignored outside pack mode" in warning:
            suggestions.append("Remove output_dir, or switch the task to pack mode.")
        elif "output_root is ignored in pack mode" in warning:
            suggestions.append("Remove output_root, or move the path into output_dir for pack mode.")
        elif "source_report is ignored outside pack mode" in warning:
            suggestions.append("Remove source_report, or switch the task to pack mode.")
        elif "capture_root is ignored outside capture-pack mode" in warning:
            suggestions.append("Remove capture_root, or switch the task to capture-pack mode.")
        elif "target_markets is ignored outside capture-pack mode" in warning:
            suggestions.append("Remove target_markets, or switch the task to capture-pack mode.")
        elif "target_languages is ignored outside capture-pack mode" in warning:
            suggestions.append("Remove target_languages, or switch the task to capture-pack mode.")
        elif "goal is ignored outside goal mode" in warning:
            suggestions.append("Remove goal, or switch the task to goal mode.")
        elif "query is ignored outside goal/board mode" in warning:
            suggestions.append("Remove query, or use auto/goal/board mode so query participates in routing.")
        elif "scene is ignored outside scene mode" in warning:
            suggestions.append("Remove scene, or switch the task to scene or capture-pack mode.")
        elif "type is ignored outside pack mode" in warning:
            suggestions.append("Remove type, or switch the task to pack mode.")
        elif "bundle_root is ignored outside board mode" in warning:
            suggestions.append("Remove bundle_root, or switch the task to board mode.")
        elif "top_k is ignored outside board mode" in warning:
            suggestions.append("Remove top_k, or switch the task to board mode.")
        elif "generate is ignored outside board mode" in warning:
            suggestions.append("Remove generate, or switch the task to board mode.")
        elif "dry_run is ignored outside board mode" in warning:
            suggestions.append("Remove dry_run, or switch the task to board mode.")
        elif "run is ignored outside board mode" in warning:
            suggestions.append("Remove run, or switch the task to board mode.")
        elif "history_root is ignored outside history mode" in warning:
            suggestions.append("Remove history_root, or switch the task to history mode.")
        elif "history_output_json is ignored outside history mode" in warning:
            suggestions.append("Remove history_output_json, or switch the task to history mode.")
        elif "history_output_md is ignored outside history mode" in warning:
            suggestions.append("Remove history_output_md, or switch the task to history mode.")
    deduped: list[str] = []
    for suggestion in suggestions:
        if suggestion not in deduped:
            deduped.append(suggestion)
    return deduped


def validate_task_args(args: argparse.Namespace) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    resolved_mode = args.mode
    route_meta: dict | None = None

    if args.mode == "auto":
        try:
            routed_mode, routed = infer_mode_from_request(args)
            resolved_mode = routed_mode
            route_meta = {"requested_mode": args.mode, "resolved_mode": routed_mode, **routed}
            if routed_mode == "capture-pack" and not has_text(routed.get("scene")):
                errors.append(
                    "Auto routing resolved to capture-pack, but no concrete scene was identified. Add scene or a stronger request."
                )
        except SystemExit as exc:
            errors.append(str(exc))
    elif args.mode == "scene":
        if not has_text(args.scene):
            errors.append("scene mode requires scene.")
    elif args.mode == "goal":
        if bool(has_text(args.goal)) == bool(has_text(args.query)):
            errors.append("goal mode requires exactly one of goal or query.")
    elif args.mode == "board":
        if not has_text(args.query) and not has_text(args.request):
            errors.append("board mode requires query or request.")
    elif args.mode == "pack":
        if not has_text(args.type):
            errors.append("pack mode requires type.")
        if not has_text(args.project) and not has_text(args.source_report):
            errors.append("pack mode requires project or source_report.")
    elif args.mode == "capture-pack":
        if not has_text(args.scene):
            errors.append("capture-pack mode requires scene.")
        if not has_text(args.capture_root):
            errors.append("capture-pack mode requires capture_root.")
        if str(args.scene).strip() == "15" and not has_text(args.target_languages):
            errors.append("capture-pack mode scene 15 requires target_languages.")
    elif args.mode == "history":
        if args.history_limit <= 0:
            errors.append("history mode requires history_limit > 0.")

    add_mode_specific_warnings(args, resolved_mode, warnings)
    suggestions = build_validation_suggestions(args, resolved_mode, warnings, errors)
    return {
        "resolved_mode": resolved_mode,
        "route": route_meta,
        "warnings": warnings,
        "errors": errors,
        "suggestions": suggestions,
    }


def summarize_results(results: list[dict]) -> dict:
    summary = {
        "total": len(results),
        "success": 0,
        "failed": 0,
        "preview": 0,
        "invalid": 0,
        "by_mode": {},
        "failed_indexes": [],
        "invalid_indexes": [],
    }
    for item in results:
        mode = item.get("task", {}).get("mode", "auto")
        status = item.get("status")
        summary["by_mode"].setdefault(mode, {"success": 0, "failed": 0, "preview": 0, "invalid": 0})
        if status == "success":
            summary["success"] += 1
            summary["by_mode"][mode]["success"] += 1
        elif status == "preview":
            summary["preview"] += 1
            summary["by_mode"][mode]["preview"] += 1
        elif status == "invalid":
            summary["invalid"] += 1
            summary["by_mode"][mode]["invalid"] += 1
            summary["invalid_indexes"].append(item["index"])
        else:
            summary["failed"] += 1
            summary["by_mode"][mode]["failed"] += 1
            summary["failed_indexes"].append(item["index"])
    return summary


def build_batch_root(batch_name: str, output_root: str) -> Path:
    if output_root.strip():
        return Path(output_root).expanduser().resolve()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = slugify(batch_name) or "operator-batch"
    skill_root = Path(__file__).resolve().parents[1]
    return skill_root / "tmp" / f"{timestamp}-batch-{safe_name}"


def write_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8-sig")


def shorten_path(value: str) -> str:
    return value.replace("\\", "/")


def collect_result_paths(result: dict) -> list[str]:
    keys = [
        "starter_root",
        "run_root",
        "goal_root",
        "outputs_dir",
        "history_root",
        "output_json",
        "output_md",
        "report_json",
        "report_json_path",
        "report_path",
        "output_path",
        "manifest_path",
    ]
    paths: list[str] = []
    for key in keys:
        value = result.get(key)
        if isinstance(value, str) and value.strip():
            paths.append(f"{key}: `{shorten_path(value)}`")
    for pack in result.get("operator_packs", []):
        if not isinstance(pack, dict):
            continue
        pack_type = pack.get("type", "pack")
        output_path = pack.get("output_path")
        if isinstance(output_path, str) and output_path.strip():
            paths.append(f"{pack_type}: `{shorten_path(output_path)}`")
    return paths


def collect_preview_fields(preview: dict) -> list[str]:
    lines: list[str] = []
    if preview.get("would_run_mode"):
        lines.append(f"would run mode: `{preview['would_run_mode']}`")
    if preview.get("request"):
        lines.append(f"request: `{preview['request']}`")
    if preview.get("query"):
        lines.append(f"query: `{preview['query']}`")
    if preview.get("scene"):
        lines.append(f"scene: `{preview['scene']}`")
    if preview.get("goal"):
        lines.append(f"goal: `{preview['goal']}`")
    if preview.get("bundle_root"):
        lines.append(f"bundle root: `{shorten_path(preview['bundle_root'])}`")
    if preview.get("top_k") is not None:
        lines.append(f"top k: `{preview['top_k']}`")
    if "generate" in preview:
        lines.append(f"generate: `{preview['generate']}`")
    if "task_dry_run" in preview:
        lines.append(f"task dry run: `{preview['task_dry_run']}`")
    if "task_run" in preview:
        lines.append(f"task run: `{preview['task_run']}`")
    if preview.get("pack_type"):
        lines.append(f"pack type: `{preview['pack_type']}`")
    if preview.get("capture_root"):
        lines.append(f"capture root: `{shorten_path(preview['capture_root'])}`")
    if preview.get("output_root"):
        lines.append(f"output root: `{shorten_path(preview['output_root'])}`")
    if preview.get("output_dir"):
        lines.append(f"output dir: `{shorten_path(preview['output_dir'])}`")
    if preview.get("history_root"):
        lines.append(f"history root: `{shorten_path(preview['history_root'])}`")
    if preview.get("history_output_json"):
        lines.append(f"history output json: `{shorten_path(preview['history_output_json'])}`")
    if preview.get("history_output_md"):
        lines.append(f"history output md: `{shorten_path(preview['history_output_md'])}`")
    return lines


def render_validation_lines(validation: dict) -> list[str]:
    lines: list[str] = []
    warnings = validation.get("warnings", [])
    errors = validation.get("errors", [])
    suggestions = validation.get("suggestions", [])
    for warning in warnings:
        lines.append(f"warning: `{warning}`")
    for error in errors:
        lines.append(f"validation error: `{error}`")
    for suggestion in suggestions:
        lines.append(f"suggestion: `{suggestion}`")
    return lines


def render_source_summary(source: dict) -> list[str]:
    lines = [
        f"- source type: `{source.get('type', '')}`",
        f"- source path: `{shorten_path(source.get('path', ''))}`",
    ]
    selected_indexes = source.get("selected_indexes", [])
    if selected_indexes:
        lines.append(f"- selected indexes: `{', '.join(str(item) for item in selected_indexes)}`")
    failed_indexes = source.get("failed_indexes", [])
    if failed_indexes:
        lines.append(f"- prior failed indexes: `{', '.join(str(item) for item in failed_indexes)}`")
    invalid_indexes = source.get("invalid_indexes", [])
    if invalid_indexes:
        lines.append(f"- prior invalid indexes: `{', '.join(str(item) for item in invalid_indexes)}`")
    override_file = source.get("override_file", "")
    if isinstance(override_file, str) and override_file.strip():
        lines.append(f"- override file: `{shorten_path(override_file)}`")
    return lines


def render_batch_report(payload: dict) -> str:
    summary = payload["summary"]
    source = payload["source"]
    lines = [
        "# Batch Report",
        "",
        "## Overview",
        "",
        f"- batch root: `{shorten_path(payload['batch_root'])}`",
        f"- total: `{summary['total']}`",
        f"- success: `{summary['success']}`",
        f"- failed: `{summary['failed']}`",
        f"- preview: `{summary['preview']}`",
        f"- invalid: `{summary['invalid']}`",
    ]
    lines.extend(render_source_summary(source))
    lines.extend(
        [
            "",
            "## Mode Summary",
            "",
        ]
    )
    for mode, counts in sorted(summary["by_mode"].items()):
        lines.append(
            f"- `{mode}`: success `{counts['success']}`, failed `{counts['failed']}`, preview `{counts['preview']}`, invalid `{counts['invalid']}`"
        )
    lines.extend(
        [
            "",
            "## Items",
            "",
        ]
    )
    for item in payload["results"]:
        task = item.get("task", {})
        mode = task.get("mode", "auto")
        project = task.get("project") or task.get("name") or task.get("request") or task.get("query") or ""
        title = project.strip() or f"Task {item['index']}"
        lines.append(f"### {item['index']:03d} {item['status'].upper()} - {title}")
        lines.append("")
        lines.append(f"- mode: `{mode}`")
        if task.get("scene"):
            lines.append(f"- scene: `{task['scene']}`")
        if task.get("goal"):
            lines.append(f"- goal: `{task['goal']}`")
        if task.get("type"):
            lines.append(f"- pack type: `{task['type']}`")
        if task.get("capture_root"):
            lines.append(f"- capture root: `{shorten_path(task['capture_root'])}`")
        for validation_line in render_validation_lines(item.get("validation", {})):
            lines.append(f"- {validation_line}")
        if item.get("status") == "success":
            result = item.get("result", {})
            route = result.get("route")
            if isinstance(route, dict) and route.get("resolved_mode"):
                lines.append(f"- resolved mode: `{route['resolved_mode']}`")
            for path_line in collect_result_paths(result):
                lines.append(f"- {path_line}")
            if mode == "board":
                local_paths = result.get("local_paths", {})
                next_steps = result.get("next_steps", [])
                if isinstance(local_paths, dict):
                    if local_paths.get("suite_queue_json"):
                        lines.append(f"- board queue: `{shorten_path(local_paths['suite_queue_json'])}`")
                    if local_paths.get("local_report_md"):
                        lines.append(f"- preset report: `{shorten_path(local_paths['local_report_md'])}`")
                    if local_paths.get("local_batch_root"):
                        lines.append(f"- board batch root: `{shorten_path(local_paths['local_batch_root'])}`")
                    if local_paths.get("local_batch_report_md"):
                        lines.append(f"- board batch report: `{shorten_path(local_paths['local_batch_report_md'])}`")
                if isinstance(next_steps, list):
                    for step in next_steps:
                        lines.append(f"- next step: `{step}`")
        elif item.get("status") == "preview":
            result = item.get("result", {})
            route = result.get("route")
            if isinstance(route, dict) and route.get("resolved_mode"):
                lines.append(f"- resolved mode: `{route['resolved_mode']}`")
            preview = result.get("preview", {})
            for preview_line in collect_preview_fields(preview):
                lines.append(f"- {preview_line}")
            if mode == "board":
                lines.append("- board preview flow: scaffold starter -> generate queue -> inspect preset report -> batch dry-run -> execute")
        elif item.get("status") == "invalid":
            lines.append("- task was blocked before execution")
        else:
            error = item.get("error", {})
            lines.append(f"- error type: `{error.get('type', '')}`")
            lines.append(f"- error message: `{error.get('message', '')}`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_batch_artifacts(
    batch_root: Path,
    payload: dict,
) -> None:
    items_dir = batch_root / "items"
    items_dir.mkdir(parents=True, exist_ok=True)
    write_json(batch_root / "batch_input.json", payload["tasks"])
    write_json(
        batch_root / "summary.json",
        {
            "source": payload["source"],
            "count": payload["count"],
            "summary": payload["summary"],
        },
    )
    write_json(batch_root / "batch_result.json", payload)
    (batch_root / "batch_report.md").write_text(render_batch_report(payload), encoding="utf-8-sig")
    for item in payload["results"]:
        item_file = items_dir / f"{item['index']:03d}-{item['status']}.json"
        write_json(item_file, item)


def merge_overrides(tasks: list[dict], override_payload: dict | None) -> list[dict]:
    if not override_payload:
        return tasks
    merged = []
    for item in tasks:
        next_item = dict(item)
        next_item.update(override_payload)
        merged.append(next_item)
    return merged


def resolve_rerun_source(path_str: str) -> Path:
    path = Path(path_str).expanduser().resolve()
    if path.is_dir():
        candidate = path / "batch_result.json"
        if candidate.exists():
            return candidate
        raise SystemExit(f"Could not find batch_result.json under rerun source directory: {path}")
    return path


def parse_rerun_indexes(raw: str) -> list[int]:
    values: list[int] = []
    for chunk in raw.split(","):
        item = chunk.strip()
        if not item:
            continue
        if not item.isdigit():
            raise SystemExit(f"Invalid rerun index: {item}")
        index = int(item)
        if index <= 0:
            raise SystemExit(f"Rerun indexes must be positive integers: {item}")
        if index not in values:
            values.append(index)
    if not values:
        raise SystemExit("Rerun indexes were provided but no valid indexes were found.")
    return values


def select_rerun_items(previous: dict, rerun_indexes_raw: str) -> tuple[list[dict], dict]:
    results = previous.get("results", [])
    if rerun_indexes_raw.strip():
        selected_indexes = parse_rerun_indexes(rerun_indexes_raw)
        selected_items: list[dict] = []
        missing_indexes: list[int] = []
        for index in selected_indexes:
            match = next((item for item in results if item.get("index") == index), None)
            if match is None:
                missing_indexes.append(index)
            else:
                selected_items.append(match)
        if missing_indexes:
            missing = ", ".join(str(item) for item in missing_indexes)
            raise SystemExit(f"Requested rerun indexes were not present in prior batch results: {missing}")
        return selected_items, {
            "type": "rerun-indexes",
            "selected_indexes": selected_indexes,
        }

    failed_items = [item for item in results if item.get("status") == "failed"]
    invalid_items = [item for item in results if item.get("status") == "invalid"]
    return failed_items + invalid_items, {
        "type": "rerun-failed",
        "failed_indexes": previous.get("summary", {}).get("failed_indexes", []),
        "invalid_indexes": previous.get("summary", {}).get("invalid_indexes", []),
    }


def load_batch_tasks(args: argparse.Namespace) -> tuple[list[dict], dict]:
    override_payload = None
    if args.override_file:
        override_payload = read_json(Path(args.override_file).expanduser().resolve())
        if not isinstance(override_payload, dict):
            raise SystemExit("Override file must contain one JSON object.")

    if args.batch_file:
        batch_path = Path(args.batch_file).expanduser().resolve()
        tasks = read_json(batch_path)
        if not isinstance(tasks, list):
            raise SystemExit("Batch file must contain a JSON array.")
        merged_tasks = merge_overrides(tasks, override_payload)
        source = {
            "type": "batch-file",
            "path": str(batch_path),
        }
        return merged_tasks, source

    rerun_path = resolve_rerun_source(args.rerun_failed_from)
    previous = read_json(rerun_path)
    if not isinstance(previous, dict) or "results" not in previous:
        raise SystemExit("Rerun source must be a prior batch_result.json payload.")
    selected_items, rerun_source = select_rerun_items(previous, args.rerun_indexes)
    tasks = [dict(item.get("task", {})) for item in selected_items]
    merged_tasks = merge_overrides(tasks, override_payload)
    source = {
        "type": rerun_source["type"],
        "path": str(rerun_path),
        "failed_indexes": previous.get("summary", {}).get("failed_indexes", []),
        "invalid_indexes": previous.get("summary", {}).get("invalid_indexes", []),
        "selected_indexes": rerun_source.get("selected_indexes", []),
        "failed_count": len(tasks),
        "override_file": str(Path(args.override_file).expanduser().resolve()) if args.override_file else "",
    }
    return merged_tasks, source


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run multiple TikTok Growth Operator tasks from one batch JSON file."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--batch-file", help="JSON file containing a list of workflow task objects.")
    group.add_argument(
        "--rerun-failed-from",
        help="Prior batch_result.json file or batch artifact directory. Only failed tasks will be re-run.",
    )
    parser.add_argument(
        "--rerun-indexes",
        default="",
        help="Optional comma-separated indexes from a prior batch result to rerun instead of only failed tasks.",
    )
    parser.add_argument(
        "--override-file",
        default="",
        help="Optional JSON object whose fields will be merged into every batch task before execution.",
    )
    parser.add_argument(
        "--output-file",
        default="",
        help="Optional JSON file path for the combined batch results.",
    )
    parser.add_argument(
        "--batch-root",
        default="",
        help="Optional directory where batch artifacts will be written.",
    )
    parser.add_argument(
        "--batch-name",
        default="",
        help="Optional friendly batch name used when auto-creating a batch artifact directory.",
    )
    parser.add_argument("--platform", default="Douyin", help="Default platform for tasks that omit it.")
    parser.add_argument("--market", default="China", help="Default market for tasks that omit it.")
    parser.add_argument("--formats", default="md", help="Default formats for goal tasks that omit it.")
    parser.add_argument("--bundle-root", default="", help="Default preset bundle root for board tasks that omit it.")
    parser.add_argument("--top-k", type=int, default=3, help="Default number of ranked board recommendations for board tasks that omit it.")
    parser.add_argument("--generate", action="store_true", help="Default board-task flag to generate the queue after starter scaffolding.")
    parser.add_argument("--run", action="store_true", help="Default board-task flag to execute the generated queue after scaffolding.")
    parser.add_argument("--target-markets", default="", help="Default target markets for capture-pack tasks that omit it.")
    parser.add_argument("--target-languages", default="", help="Default target languages for capture-pack tasks that omit it.")
    parser.add_argument("--history-root", default="", help="Default run-history scan root for tasks that omit it.")
    parser.add_argument("--history-output-json", default="", help="Default JSON output path for history tasks that omit it.")
    parser.add_argument("--history-output-md", default="", help="Default Markdown output path for history tasks that omit it.")
    parser.add_argument("--history-limit", type=int, default=50, help="Default history limit for tasks that omit it.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview routing and task shape without executing scene, goal, pack, or capture-pack workflows.",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop at the first failed task instead of continuing the batch.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tasks, source = load_batch_tasks(args)

    defaults = {
        "mode": "auto",
        "platform": args.platform,
        "market": args.market,
        "formats": args.formats,
        "bundle_root": args.bundle_root,
        "top_k": args.top_k,
        "generate": args.generate,
        "dry_run": False,
        "run": args.run,
        "capture_root": "",
        "target_markets": args.target_markets,
        "target_languages": args.target_languages,
        "history_root": args.history_root,
        "history_output_json": args.history_output_json,
        "history_output_md": args.history_output_md,
        "history_limit": args.history_limit,
    }

    results = []
    for index, item in enumerate(tasks, start=1):
        if not isinstance(item, dict):
            raise SystemExit(f"Batch item {index} must be a JSON object.")
        task_args = build_namespace(item, defaults)
        validation = validate_task_args(task_args)
        if validation["errors"]:
            results.append(
                {
                    "index": index,
                    "task": item,
                    "status": "invalid",
                    "validation": validation,
                }
            )
            if args.fail_fast:
                break
            continue
        try:
            result = preview_item(task_args) if args.dry_run else run_item(task_args)
            results.append(
                {
                    "index": index,
                    "task": item,
                    "status": "preview" if args.dry_run else "success",
                    "validation": validation,
                    "result": result,
                }
            )
        except BaseException as exc:  # noqa: BLE001
            failure = {
                "index": index,
                "task": item,
                "status": "failed",
                "validation": validation,
                "error": {
                    "type": exc.__class__.__name__,
                    "message": str(exc),
                    "trace": traceback.format_exc(limit=5),
                },
            }
            results.append(failure)
            if args.fail_fast:
                break

    batch_root = build_batch_root(args.batch_name or Path(source["path"]).stem, args.batch_root)
    payload = {
        "source": source,
        "batch_root": str(batch_root),
        "dry_run": args.dry_run,
        "count": len(results),
        "tasks": tasks,
        "summary": summarize_results(results),
        "results": results,
    }

    write_batch_artifacts(batch_root, payload)

    if args.output_file:
        output_path = Path(args.output_file).expanduser().resolve()
        write_json(output_path, payload)

    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
