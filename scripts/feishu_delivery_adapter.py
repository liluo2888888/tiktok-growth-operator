from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path

from feishu_naming import translate_field_name
from text_normalization import normalize_text, read_json_file, write_json_file

REGISTRY_FILENAME = "feishu_delivery_registry.json"
RUN_DATE_FIELD = "采集日期"
APPEND_SCOPE_FIELD = "追加批次"

BOARD_SPECS: dict[str, dict[str, str]] = {
    "scene01_collection_board": {
        "board_key": "collection_board",
        "default_table_name": "Scene01采集看板",
        "skip_reason": "no-collection-board",
    },
    "scene02_patrol_board": {
        "board_key": "patrol_board",
        "default_table_name": "Scene02巡检主表",
        "skip_reason": "no-patrol-board",
    },
    "scene18_competitor_weekly": {
        "board_key": "competitor_weekly_board",
        "default_table_name": "Scene18竞品周报主表",
        "skip_reason": "no-competitor-weekly-board",
    },
    "scene06_competitor_product_board": {
        "board_key": "competitor_product_board",
        "default_table_name": "Scene06竞品商品主表",
        "skip_reason": "no-competitor-product-board",
    },
    "scene07_category_entry": {
        "board_key": "category_entry_board",
        "default_table_name": "Scene07类目进入主表",
        "skip_reason": "no-category-entry-board",
    },
    "scene08_comment_persona": {
        "board_key": "comment_persona_board",
        "default_table_name": "Scene08评论人设主表",
        "skip_reason": "no-comment-persona-board",
    },
    "scene17_creator_formula": {
        "board_key": "creator_formula_board",
        "default_table_name": "Scene17创作者公式主表",
        "skip_reason": "no-creator-formula-board",
    },
    "scene19_account_retro": {
        "board_key": "account_retro_board",
        "default_table_name": "Scene19账号复盘主表",
        "skip_reason": "no-account-retro-board",
    },
}


def registry_path_for(capture_root: Path | None, report_json: Path | None) -> Path:
    if capture_root is not None:
        return capture_root / REGISTRY_FILENAME
    if report_json is not None:
        return report_json.parent / REGISTRY_FILENAME
    raise ValueError("capture_root or report_json is required for Feishu delivery registry")


def load_registry(path: Path) -> dict:
    if path.exists():
        payload = read_json_file(path)
        if isinstance(payload, dict):
            return payload
    return {"tables": {}, "append_log": []}


def save_registry(path: Path, registry: dict) -> None:
    write_json_file(path, registry)


def headers_fingerprint(headers: list[str]) -> str:
    joined = "|".join(normalize_text(item) for item in headers)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:16]


def build_board_append_records(
    board: dict,
    *,
    run_date: str | None = None,
    append_scope: str = "",
) -> tuple[list[str], list[dict]]:
    headers = [normalize_text(item) for item in (board.get("headers") or []) if normalize_text(item)]
    rows = board.get("rows") or []
    stamp = run_date or datetime.now().strftime("%Y-%m-%d")
    scope = append_scope or stamp
    feishu_headers = [RUN_DATE_FIELD, APPEND_SCOPE_FIELD, *headers]
    records: list[dict] = []
    for row in rows:
        if not isinstance(row, list):
            continue
        padded = list(row) + [""] * max(0, len(headers) - len(row))
        field_map = {headers[index]: normalize_text(padded[index]) for index in range(len(headers))}
        fields = {
            translate_field_name(RUN_DATE_FIELD): stamp,
            translate_field_name(APPEND_SCOPE_FIELD): scope,
        }
        for key, value in field_map.items():
            fields[translate_field_name(key)] = value
        records.append({"fields": fields})
    return feishu_headers, records


def _board_from_report(report: dict, board_key: str) -> dict | None:
    board = report.get(board_key)
    if isinstance(board, dict) and board.get("rows"):
        return board
    return None


def plan_structured_board_append(
    report: dict,
    *,
    table_key: str,
    run_date: str | None = None,
    append_scope: str = "",
) -> dict:
    spec = BOARD_SPECS.get(table_key)
    if spec is None:
        return {"status": "skipped", "reason": "unknown-table-key", "table_key": table_key}
    board = _board_from_report(report, spec["board_key"])
    if board is None:
        return {"status": "skipped", "reason": spec["skip_reason"], "table_key": table_key}
    headers, records = build_board_append_records(board, run_date=run_date, append_scope=append_scope)
    return {
        "status": "planned",
        "table_key": table_key,
        "board_key": spec["board_key"],
        "headers": headers,
        "headers_fingerprint": headers_fingerprint(headers),
        "record_count": len(records),
        "run_date": run_date or datetime.now().strftime("%Y-%m-%d"),
        "append_scope": append_scope or run_date or datetime.now().strftime("%Y-%m-%d"),
        "records_preview": records[:2],
    }


def plan_board_append(report: dict, *, run_date: str | None = None, append_scope: str = "") -> dict:
    return plan_structured_board_append(
        report,
        table_key="scene01_collection_board",
        run_date=run_date,
        append_scope=append_scope,
    )


def plan_all_board_appends(report: dict, *, run_date: str | None = None, append_scope: str = "") -> list[dict]:
    plans: list[dict] = []
    for table_key in BOARD_SPECS:
        plan = plan_structured_board_append(report, table_key=table_key, run_date=run_date, append_scope=append_scope)
        if plan.get("status") == "planned":
            plans.append(plan)
    return plans


def append_structured_board(
    report: dict,
    *,
    table_key: str,
    app_id: str,
    app_secret: str,
    registry_file: Path,
    dry_run: bool = False,
    run_date: str | None = None,
    append_scope: str = "",
    base_name: str = "",
) -> dict:
    spec = BOARD_SPECS.get(table_key)
    if spec is None:
        return {"status": "skipped", "reason": "unknown-table-key", "table_key": table_key}

    plan = plan_structured_board_append(report, table_key=table_key, run_date=run_date, append_scope=append_scope)
    if plan.get("status") != "planned":
        return plan

    board = report[spec["board_key"]]
    headers, records = build_board_append_records(board, run_date=run_date, append_scope=append_scope)
    registry = load_registry(registry_file)
    table_state = registry.get("tables", {}).get(table_key, {})
    fingerprint = plan["headers_fingerprint"]

    if dry_run:
        return {
            **plan,
            "dry_run": True,
            "registry_file": str(registry_file),
            "reuse_table_id": normalize_text(table_state.get("table_id")),
            "fixed_headers": headers,
        }

    if not normalize_text(app_id) or not normalize_text(app_secret):
        return {"status": "skipped", "reason": "missing-feishu-credentials", **plan}

    from push_report_to_feishu import (
        batch_create_records,
        create_bitable_app,
        get_app_access_token,
        resolve_or_create_table,
        slugify_sheet_name,
    )

    token = get_app_access_token(app_id, app_secret)
    app_token = normalize_text(table_state.get("app_token"))
    app_url = normalize_text(table_state.get("app_url"))
    if not app_token:
        title = normalize_text(base_name) or normalize_text((report.get("metadata") or {}).get("project")) or "TikTok Growth Operator"
        app_token, app_url = create_bitable_app(token, title)

    table_id = normalize_text(table_state.get("table_id"))
    table_name = normalize_text(table_state.get("table_name")) or slugify_sheet_name(spec["default_table_name"])
    if table_state.get("headers_fingerprint") and table_state.get("headers_fingerprint") != fingerprint and table_id:
        table_name = f"{table_name}-{append_scope or run_date or 'append'}"
        table_id = ""
    resolved_table_id, resolved_table_name = resolve_or_create_table(token, app_token, table_id, table_name)
    created = batch_create_records(token, app_token, resolved_table_id, records)

    registry.setdefault("tables", {})[table_key] = {
        "app_token": app_token,
        "app_url": app_url,
        "table_id": resolved_table_id,
        "table_name": resolved_table_name,
        "headers_fingerprint": fingerprint,
        "fixed_headers": headers,
        "last_append_at": datetime.now().isoformat(timespec="seconds"),
        "last_append_scope": append_scope or run_date,
        "last_record_count": created,
    }
    registry.setdefault("append_log", []).append(
        {
            "at": datetime.now().isoformat(timespec="seconds"),
            "table_key": table_key,
            "record_count": created,
            "append_scope": append_scope or run_date,
        }
    )
    save_registry(registry_file, registry)
    return {
        "status": "ok",
        "table_key": table_key,
        "app_token": app_token,
        "app_url": app_url,
        "table_id": resolved_table_id,
        "table_name": resolved_table_name,
        "records_created": created,
        "registry_file": str(registry_file),
        "fixed_headers": headers,
    }


def append_collection_board(
    report: dict,
    *,
    app_id: str,
    app_secret: str,
    registry_file: Path,
    dry_run: bool = False,
    run_date: str | None = None,
    append_scope: str = "",
    base_name: str = "",
) -> dict:
    return append_structured_board(
        report,
        table_key="scene01_collection_board",
        app_id=app_id,
        app_secret=app_secret,
        registry_file=registry_file,
        dry_run=dry_run,
        run_date=run_date,
        append_scope=append_scope,
        base_name=base_name,
    )


def append_all_report_boards(
    report: dict,
    *,
    app_id: str,
    app_secret: str,
    registry_file: Path,
    dry_run: bool = False,
    run_date: str | None = None,
    append_scope: str = "",
    base_name: str = "",
) -> dict:
    results: list[dict] = []
    for table_key in BOARD_SPECS:
        plan = plan_structured_board_append(report, table_key=table_key, run_date=run_date, append_scope=append_scope)
        if plan.get("status") != "planned":
            continue
        results.append(
            append_structured_board(
                report,
                table_key=table_key,
                app_id=app_id,
                app_secret=app_secret,
                registry_file=registry_file,
                dry_run=dry_run,
                run_date=run_date,
                append_scope=append_scope,
                base_name=base_name,
            )
        )
    if not results:
        return {"status": "skipped", "reason": "no-boards-in-report", "boards": []}
    return {"status": "ok", "boards": results}
