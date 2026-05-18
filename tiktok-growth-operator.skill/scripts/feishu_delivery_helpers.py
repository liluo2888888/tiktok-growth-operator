from __future__ import annotations

from datetime import datetime
from pathlib import Path

from feishu_push_runtime import maybe_push_feishu_bundle
from text_normalization import normalize_text, read_json_file

BOARD_JSON_SUFFIXES = (
    "collection_board.json",
    "patrol_board.json",
    "competitor_weekly_board.json",
    "competitor_product_board.json",
    "category_entry_board.json",
    "comment_persona_board.json",
    "creator_formula_board.json",
    "account_retro_board.json",
)


def feishu_append_scope_from_report(report_json: str | Path) -> str:
    report = read_json_file(Path(report_json))
    schedule = report.get("operator_schedule") or {}
    feishu = (schedule.get("delivery") or {}).get("feishu") or {}
    scope = normalize_text(feishu.get("append_scope"))
    if scope:
        return scope
    return datetime.now().strftime("%Y-%m-%d")


def resolve_feishu_registry_for_report(report_json: str | Path) -> Path:
    report_path = Path(report_json).expanduser().resolve()
    report = read_json_file(report_path)
    for asset in report.get("assets") or []:
        if not isinstance(asset, dict):
            continue
        path = normalize_text(asset.get("path"))
        if path.endswith(BOARD_JSON_SUFFIXES):
            return Path(path).parent / "feishu_delivery_registry.json"
    return report_path.parent / "feishu_delivery_registry.json"


def deliver_feishu_report(
    report_json: str | Path,
    app_id: str,
    app_secret: str,
    *,
    title: str = "",
    base_name: str = "",
    append_board: bool = True,
    run_date: str = "",
    append_scope: str = "",
    registry_file: Path | None = None,
    dry_run: bool = False,
) -> dict:
    report_path = Path(report_json).expanduser().resolve()
    report = read_json_file(report_path)
    resolved_scope = normalize_text(append_scope) or feishu_append_scope_from_report(report_path)
    resolved_run_date = normalize_text(run_date) or datetime.now().strftime("%Y-%m-%d")
    registry = registry_file or resolve_feishu_registry_for_report(report_path)

    board_result = None
    if append_board:
        from feishu_delivery_adapter import append_all_report_boards

        board_result = append_all_report_boards(
            report,
            app_id=app_id,
            app_secret=app_secret,
            registry_file=registry,
            dry_run=dry_run,
            run_date=resolved_run_date,
            append_scope=resolved_scope,
            base_name=base_name.strip(),
        )
        if board_result.get("status") == "skipped" and normalize_text(board_result.get("reason")) == "no-boards-in-report":
            board_result = None

    if dry_run:
        payload: dict = {
            "status": "planned",
            "reason": "dry-run",
            "report_json": str(report_path),
            "append_board": append_board,
            "append_scope": resolved_scope,
            "run_date": resolved_run_date,
        }
        if board_result is not None:
            payload["feishu_board_append"] = board_result
        return payload

    bundle_result = maybe_push_feishu_bundle(
        str(report_path),
        app_id,
        app_secret,
        title=title.strip(),
        base_name=base_name.strip(),
    )
    if board_result is not None:
        bundle_result["feishu_board_append"] = board_result
    return bundle_result
