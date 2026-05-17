from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

import requests
from requests import Response

from feishu_naming import build_report_title, build_table_name, translate_field_name
from text_normalization import normalize_text, read_json_file


AUTH_URL = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
BITABLE_APP_CREATE_URL = "https://open.feishu.cn/open-apis/bitable/v1/apps"
BITABLE_TABLE_LIST_URL = "https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables"
BITABLE_TABLE_CREATE_URL = "https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables"
BITABLE_FIELD_LIST_URL = "https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
BITABLE_FIELD_CREATE_URL = "https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
BITABLE_RECORD_BATCH_CREATE_URL = "https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create"

DEFAULT_TIMEOUT = 30


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Push a TikTok Growth Operator scene report JSON into Feishu Bitable for beginner-friendly delivery."
    )
    parser.add_argument("--input", required=True, help="Structured scene report JSON path.")
    parser.add_argument("--app-id", default=os.environ.get("FEISHU_APP_ID", ""), help="Feishu app ID. Can also come from FEISHU_APP_ID.")
    parser.add_argument(
        "--app-secret",
        default=os.environ.get("FEISHU_APP_SECRET", ""),
        help="Feishu app secret. Can also come from FEISHU_APP_SECRET.",
    )
    parser.add_argument("--app-token", default="", help="Existing Feishu Bitable app token. If omitted, create a new one.")
    parser.add_argument("--table-id", default="", help="Existing Bitable table ID. If omitted, create or reuse by scene title.")
    parser.add_argument("--table-name", default="", help="Optional explicit table name. Defaults to report scene title.")
    parser.add_argument("--base-name", default="", help="Optional explicit Bitable app name when creating a new app.")
    parser.add_argument("--folder-token", default="", help="Optional Feishu folder token for app creation.")
    parser.add_argument(
        "--mode",
        choices=["summary", "section_overview", "evidence", "assets"],
        default="summary",
        help="Which report surface to push first. Start with summary if you are new to Feishu.",
    )
    return parser.parse_args()


def require(value: str, label: str) -> str:
    text = normalize_text(value)
    if not text:
        raise SystemExit(f"Missing required {label}. Pass --{label.replace('_', '-')} or set the matching env var.")
    return text


def compact(text: object, *, limit: int = 400) -> str:
    value = " ".join(normalize_text(text).split())
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."


def slugify_sheet_name(text: str) -> str:
    cleaned = normalize_text(text) or "场景报告"
    cleaned = re.sub(r"[\r\n\t]+", " ", cleaned)
    cleaned = re.sub(r"[\\/:*?\"<>|]+", "-", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:100] or "场景报告"


def auth_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }


def parse_error_response(response: Response) -> dict:
    try:
        body = response.json()
    except ValueError:
        body = {
            "code": response.status_code,
            "msg": normalize_text(response.text, strip=False) or f"HTTP {response.status_code}",
        }
    if not isinstance(body, dict):
        body = {
            "code": response.status_code,
            "msg": normalize_text(str(body), strip=False) or f"HTTP {response.status_code}",
        }
    return body


def raise_feishu_api_error(url: str, body: dict) -> None:
    violations = []
    for item in ((body.get("error") or {}).get("permission_violations") or []):
        subject = normalize_text((item or {}).get("subject"))
        if subject:
            violations.append(subject)

    hints = []
    if violations:
        hints.append(f"required_scopes={', '.join(violations)}")

    message = normalize_text(body.get("msg"), strip=False)
    auth_link = ""
    if "https://open.feishu.cn/app/" in message:
        start = message.find("https://open.feishu.cn/app/")
        auth_link = message[start:].split()[0]
    if auth_link:
        hints.append(f"auth_link={auth_link}")

    suffix = f" ({'; '.join(hints)})" if hints else ""
    raise SystemExit(f"Feishu API error at {url}: code={body.get('code')} msg={body.get('msg')}{suffix}")


def post_json(url: str, payload: dict, *, headers: dict[str, str] | None = None) -> dict:
    response = requests.post(
        url,
        headers=headers or {"Content-Type": "application/json; charset=utf-8"},
        json=payload,
        timeout=DEFAULT_TIMEOUT,
    )
    body = parse_error_response(response)
    if response.status_code >= 400 or body.get("code") not in (0, None):
        raise_feishu_api_error(url, body)
    return body


def get_json(url: str, *, headers: dict[str, str]) -> dict:
    response = requests.get(url, headers=headers, timeout=DEFAULT_TIMEOUT)
    body = parse_error_response(response)
    if response.status_code >= 400 or body.get("code") not in (0, None):
        raise_feishu_api_error(url, body)
    return body


def get_app_access_token(app_id: str, app_secret: str) -> str:
    body = post_json(AUTH_URL, {"app_id": app_id, "app_secret": app_secret})
    token = normalize_text(body.get("app_access_token"))
    if not token:
        raise SystemExit("Feishu auth succeeded but no app_access_token was returned.")
    return token


def create_bitable_app(token: str, name: str, folder_token: str = "") -> tuple[str, str]:
    payload = {"name": name}
    if folder_token:
        payload["folder_token"] = folder_token
    body = post_json(BITABLE_APP_CREATE_URL, payload, headers=auth_headers(token))
    data = body.get("data") or {}
    app = data.get("app") or {}
    app_token = normalize_text(app.get("app_token"))
    url = normalize_text(app.get("url"))
    if not app_token:
        raise SystemExit("Feishu created the Bitable app but no app_token was returned.")
    return app_token, url


def list_tables(token: str, app_token: str) -> list[dict]:
    body = get_json(BITABLE_TABLE_LIST_URL.format(app_token=app_token), headers=auth_headers(token))
    items = ((body.get("data") or {}).get("items")) or []
    return [item for item in items if isinstance(item, dict)]


def create_table(token: str, app_token: str, table_name: str) -> str:
    body = post_json(
        BITABLE_TABLE_CREATE_URL.format(app_token=app_token),
        {"table": {"name": table_name}},
        headers=auth_headers(token),
    )
    data = body.get("data") or {}
    table_id = normalize_text(data.get("table_id"))
    if not table_id:
        table_id = normalize_text(((data.get("table") or {}).get("table_id")))
    if not table_id:
        raise SystemExit("Feishu created the table but no table_id was returned.")
    return table_id


def list_fields(token: str, app_token: str, table_id: str) -> list[dict]:
    body = get_json(BITABLE_FIELD_LIST_URL.format(app_token=app_token, table_id=table_id), headers=auth_headers(token))
    items = ((body.get("data") or {}).get("items")) or []
    return [item for item in items if isinstance(item, dict)]


def ensure_fields(token: str, app_token: str, table_id: str, field_names: list[str]) -> None:
    existing = {
        normalize_text(item.get("field_name"))
        for item in list_fields(token, app_token, table_id)
        if normalize_text(item.get("field_name"))
    }
    for field_name in field_names:
        normalized = normalize_text(field_name)
        if not normalized or normalized in existing:
            continue
        post_json(
            BITABLE_FIELD_CREATE_URL.format(app_token=app_token, table_id=table_id),
            {"field_name": normalized, "type": 1},
            headers=auth_headers(token),
        )
        existing.add(normalized)


def resolve_or_create_table(token: str, app_token: str, table_id: str, table_name: str) -> tuple[str, str]:
    if table_id:
        return table_id, table_name or table_id
    normalized_name = slugify_sheet_name(table_name)
    for item in list_tables(token, app_token):
        existing_name = normalize_text(item.get("name"))
        existing_id = normalize_text(item.get("table_id"))
        if existing_name == normalized_name and existing_id:
            return existing_id, existing_name
    return create_table(token, app_token, normalized_name), normalized_name


def report_title(report: dict) -> str:
    metadata = report.get("metadata") or {}
    return build_report_title(
        metadata.get("project"),
        metadata.get("scene"),
        metadata.get("scene_title"),
    )


def build_summary_records(report: dict) -> list[dict]:
    metadata = report.get("metadata") or {}
    executive = report.get("executive_summary") or {}
    context = report.get("working_context") or {}
    sections = report.get("sections") or []
    return [
        {
            "fields": {
                "场景": normalize_text(metadata.get("scene")),
                "场景标题": normalize_text(metadata.get("scene_title")),
                "项目": normalize_text(metadata.get("project")),
                "交付物类型": normalize_text(metadata.get("deliverable_type")),
                "生成时间": normalize_text(metadata.get("generated_at")),
                "状态": normalize_text(metadata.get("status")),
                "核心结论": compact(executive.get("conclusion"), limit=1000),
                "为什么重要": compact(executive.get("why_it_matters"), limit=1000),
                "下一步动作": compact(executive.get("next_action"), limit=1000),
                "置信度": normalize_text(executive.get("confidence")),
                "工作上下文": compact(context.get("summary"), limit=1500),
                "章节数": len(sections),
                "证据数": len(report.get("evidence") or []),
                "资产数": len(report.get("assets") or []),
                "来源数": len(report.get("sources") or []),
            }
        }
    ]


def build_section_overview_records(report: dict) -> list[dict]:
    records: list[dict] = []
    for index, section in enumerate(report.get("sections") or [], start=1):
        table = section.get("table") or {}
        records.append(
            {
                "fields": {
                    "序号": index,
                    "章节": normalize_text(section.get("heading")),
                    "填写说明": compact(section.get("instruction"), limit=600),
                    "段落数": len(section.get("paragraphs") or []),
                    "要点数": len(section.get("bullets") or []),
                    "步骤数": len(section.get("numbered") or []),
                    "表格标题": normalize_text(table.get("title")),
                    "表格列": ", ".join(str(item).strip() for item in (table.get("headers") or []) if str(item).strip()),
                }
            }
        )
    return records


def build_evidence_records(report: dict) -> list[dict]:
    records: list[dict] = []
    for index, item in enumerate(report.get("evidence") or [], start=1):
        records.append(
            {
                "fields": {
                    "序号": index,
                    "标签": normalize_text(item.get("label")),
                    "详情": compact(item.get("detail"), limit=1500),
                    "来源": normalize_text(item.get("source")),
                }
            }
        )
    return records


def build_asset_records(report: dict) -> list[dict]:
    records: list[dict] = []
    for index, item in enumerate(report.get("assets") or [], start=1):
        records.append(
            {
                "fields": {
                    "序号": index,
                    "标签": normalize_text(item.get("label")),
                    "路径": normalize_text(item.get("path")),
                    "备注": compact(item.get("note"), limit=1000),
                }
            }
        )
    return records


def build_records(report: dict, mode: str) -> list[dict]:
    if mode == "summary":
        return build_summary_records(report)
    if mode == "section_overview":
        return build_section_overview_records(report)
    if mode == "evidence":
        return build_evidence_records(report)
    if mode == "assets":
        return build_asset_records(report)
    raise SystemExit(f"Unsupported mode: {mode}")


def stringify_record_fields(records: list[dict]) -> list[dict]:
    normalized_records: list[dict] = []
    for record in records:
        fields = record.get("fields") or {}
        if not isinstance(fields, dict):
            normalized_records.append(record)
            continue
        normalized_fields = {}
        for key, value in fields.items():
            normalized_key = translate_field_name(key)
            if isinstance(value, bool):
                normalized_value = "true" if value else "false"
            elif value is None:
                normalized_value = ""
            else:
                normalized_value = normalize_text(value, strip=False)
            normalized_fields[normalized_key] = normalized_value
        normalized_records.append({"fields": normalized_fields})
    return normalized_records


def batch_create_records(token: str, app_token: str, table_id: str, records: list[dict]) -> int:
    if not records:
        return 0
    records = stringify_record_fields(records)
    field_names: list[str] = []
    seen: set[str] = set()
    for record in records:
        fields = record.get("fields") or {}
        if not isinstance(fields, dict):
            continue
        for name in fields.keys():
            normalized = normalize_text(name)
            if normalized and normalized not in seen:
                seen.add(normalized)
                field_names.append(normalized)
    ensure_fields(token, app_token, table_id, field_names)
    created = 0
    batch_size = 200
    for start in range(0, len(records), batch_size):
        chunk = records[start : start + batch_size]
        body = post_json(
            BITABLE_RECORD_BATCH_CREATE_URL.format(app_token=app_token, table_id=table_id),
            {"records": chunk},
            headers=auth_headers(token),
        )
        created += len(((body.get("data") or {}).get("records")) or chunk)
    return created


def main() -> None:
    args = parse_args()
    report = read_json_file(Path(args.input))
    if not isinstance(report, dict):
        raise SystemExit("Expected structured report JSON object.")

    app_id = require(args.app_id, "app_id")
    app_secret = require(args.app_secret, "app_secret")
    token = get_app_access_token(app_id, app_secret)

    base_name = slugify_sheet_name(args.base_name or report_title(report))
    app_token = normalize_text(args.app_token)
    app_url = ""
    if not app_token:
        app_token, app_url = create_bitable_app(token, base_name, folder_token=normalize_text(args.folder_token))

    table_name = args.table_name or build_table_name(
        (report.get("metadata") or {}).get("scene"),
        (report.get("metadata") or {}).get("scene_title"),
        args.mode,
    )
    table_id, resolved_table_name = resolve_or_create_table(token, app_token, normalize_text(args.table_id), table_name)
    records = build_records(report, args.mode)
    created = batch_create_records(token, app_token, table_id, records)

    payload = {
        "status": "ok",
        "mode": args.mode,
        "app_token": app_token,
        "app_url": app_url,
        "table_id": table_id,
        "table_name": resolved_table_name,
        "records_created": created,
        "next_steps": [
            "摘要推送成功后，复用返回的 app_token 继续推送章节概览、证据和资产。",
            "如果之前创建 Base 或数据表被拒绝，先去飞书开放平台补齐缺失的 Bitable 权限。",
            "如果还想把完整报告同步成飞书文档，再运行 push_report_to_feishu_doc.py。",
        ],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
