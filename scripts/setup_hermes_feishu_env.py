from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from text_normalization import normalize_text, write_utf8_text


DEFAULT_HERMES_ENV = Path(r"D:\hermes\.env")
DEFAULT_LARK_CLI = Path(r"E:\飞书\lark-cli-bin\v1.0.25\lark-cli.exe")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Write or update FEISHU_APP_ID / FEISHU_APP_SECRET inside Hermes .env so official lark-cli binding can proceed."
    )
    parser.add_argument(
        "--env-file",
        default=str(DEFAULT_HERMES_ENV),
        help="Target Hermes .env path. Defaults to D:\\hermes\\.env.",
    )
    parser.add_argument(
        "--app-id",
        default=os.environ.get("FEISHU_APP_ID", ""),
        help="Feishu app ID. Can also come from FEISHU_APP_ID.",
    )
    parser.add_argument(
        "--app-secret",
        default=os.environ.get("FEISHU_APP_SECRET", ""),
        help="Feishu app secret. Can also come from FEISHU_APP_SECRET.",
    )
    parser.add_argument(
        "--domain",
        default=os.environ.get("FEISHU_DOMAIN", "feishu"),
        help="Optional FEISHU_DOMAIN value to ensure exists. Defaults to feishu.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the planned env edits without writing the file.",
    )
    return parser.parse_args()


def require(value: str, label: str) -> str:
    text = normalize_text(value)
    if not text:
        raise SystemExit(f"Missing required {label}. Pass --{label.replace('_', '-')} or set the matching env var.")
    return text


def parse_env_text(text: str) -> tuple[list[str], dict[str, str]]:
    lines = text.splitlines()
    values: dict[str, str] = {}
    for raw in lines:
        stripped = raw.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip()
    return lines, values


def upsert_env_lines(lines: list[str], updates: dict[str, str]) -> list[str]:
    remaining = dict(updates)
    new_lines: list[str] = []
    for raw in lines:
        stripped = raw.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key, _ = stripped.split("=", 1)
            key = key.strip()
            if key in remaining:
                new_lines.append(f"{key}={remaining.pop(key)}")
                continue
        new_lines.append(raw)
    if remaining:
        if new_lines and new_lines[-1].strip():
            new_lines.append("")
        for key, value in remaining.items():
            new_lines.append(f"{key}={value}")
    return new_lines


def main() -> None:
    args = parse_args()
    env_path = Path(args.env_file)
    env_path.parent.mkdir(parents=True, exist_ok=True)
    existing_text = env_path.read_text(encoding="utf-8-sig") if env_path.exists() else ""
    lines, existing_values = parse_env_text(existing_text)

    app_id = require(args.app_id, "app_id")
    app_secret = require(args.app_secret, "app_secret")
    domain = normalize_text(args.domain) or "feishu"

    updates = {
        "FEISHU_APP_ID": app_id,
        "FEISHU_APP_SECRET": app_secret,
    }
    if "FEISHU_DOMAIN" not in existing_values or normalize_text(existing_values.get("FEISHU_DOMAIN")) != domain:
        updates["FEISHU_DOMAIN"] = domain

    new_lines = upsert_env_lines(lines, updates)
    new_text = "\n".join(new_lines).rstrip() + "\n"

    payload = {
        "status": "ok",
        "env_file": str(env_path),
        "dry_run": bool(args.dry_run),
        "updated_keys": sorted(updates.keys()),
        "previously_present": {
            "FEISHU_APP_ID": "FEISHU_APP_ID" in existing_values,
            "FEISHU_APP_SECRET": "FEISHU_APP_SECRET" in existing_values,
            "FEISHU_DOMAIN": "FEISHU_DOMAIN" in existing_values,
        },
        "next_steps": [
            f'& "{DEFAULT_LARK_CLI}" config bind --identity bot-only',
            f'& "{DEFAULT_LARK_CLI}" doctor --offline',
        ],
    }

    if args.dry_run:
        preview_tail = []
        for line in new_lines[-8:]:
            if line.startswith("FEISHU_APP_SECRET="):
                preview_tail.append("FEISHU_APP_SECRET=<redacted>")
            else:
                preview_tail.append(line)
        payload["preview_tail"] = preview_tail
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    write_utf8_text(env_path, new_text)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
