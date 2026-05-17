from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

from text_normalization import normalize_text


DEFAULT_LARK_CLI = Path(r"E:\飞书\lark-cli-bin\v1.0.25\lark-cli.exe")
DEFAULT_SETUP_HELPER = Path(__file__).resolve().parent / "setup_hermes_feishu_env.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap Hermes -> lark-cli Feishu binding by syncing env, then running config bind and doctor."
    )
    parser.add_argument(
        "--lark-cli",
        default=str(DEFAULT_LARK_CLI),
        help="Path to lark-cli.exe.",
    )
    parser.add_argument(
        "--setup-helper",
        default=str(DEFAULT_SETUP_HELPER),
        help="Path to setup_hermes_feishu_env.py.",
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
        "--identity",
        choices=["bot-only", "user-default"],
        default="bot-only",
        help="Identity preset for lark-cli config bind.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the exact commands without executing them.",
    )
    return parser.parse_args()


def run_command(command: list[str]) -> dict:
    completed = subprocess.run(
        command,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return {
        "command": command,
        "exit_code": completed.returncode,
        "stdout": normalize_text(completed.stdout, strip=False),
        "stderr": normalize_text(completed.stderr, strip=False),
    }


def main() -> None:
    args = parse_args()
    lark_cli = Path(args.lark_cli)
    setup_helper = Path(args.setup_helper)

    commands = [
        [
            "python",
            str(setup_helper),
            "--app-id",
            normalize_text(args.app_id),
            "--app-secret",
            normalize_text(args.app_secret),
        ],
        [str(lark_cli), "config", "bind", "--identity", args.identity],
        [str(lark_cli), "doctor", "--offline"],
    ]

    if args.dry_run:
        print(
            json.dumps(
                {
                    "status": "ok",
                    "dry_run": True,
                    "commands": [" ".join(command) for command in commands],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    results = [run_command(command) for command in commands]
    ok = all(item["exit_code"] == 0 for item in results)
    payload = {
        "status": "ok" if ok else "error",
        "results": results,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
