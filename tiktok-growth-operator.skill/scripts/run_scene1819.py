from __future__ import annotations

import argparse
import json
from pathlib import Path

from start_capture_pack_run import create_capture_pack_run
from text_normalization import normalize_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Scene 18 competitor weekly report and Scene 19 self-account retro on one capture pack."
    )
    parser.add_argument("--capture-root", default="", help="Capture-pack directory.")
    parser.add_argument(
        "--preset",
        default="multiweek",
        choices=["multiweek", "matrix", "roi"],
        help="Default validation fixture when --capture-root is omitted.",
    )
    parser.add_argument("--name", default="scene1819-run")
    parser.add_argument("--project", default="TikTok Weekly Account Ops")
    parser.add_argument("--platform", default="TikTok")
    parser.add_argument("--market", default="US")
    parser.add_argument("--formats", default="md,docx,xlsx")
    parser.add_argument("--output-root", default="")
    parser.add_argument("--scene18-only", action="store_true")
    parser.add_argument("--scene19-only", action="store_true")
    parser.add_argument("--operator-packs", default="")
    parser.add_argument("--push-feishu", action="store_true", help="Push Feishu doc/bundle and structured boards after each scene run.")
    parser.add_argument("--no-feishu-append-board", action="store_true", help="With --push-feishu, skip structured board append.")
    parser.add_argument("--feishu-app-id", default="")
    parser.add_argument("--feishu-app-secret", default="")
    parser.add_argument("--feishu-title", default="")
    parser.add_argument("--feishu-base-name", default="")
    parser.add_argument("--feishu-run-date", default="")
    parser.add_argument("--feishu-append-scope", default="")
    return parser.parse_args()


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def preset_capture(preset: str) -> Path:
    mapping = {
        "multiweek": "scene18-19-multi-week-account",
        "matrix": "scene18-matrix-multi-account",
        "roi": "scene19-roi-multiwindow-account",
    }
    folder = mapping.get(preset, mapping["multiweek"])
    return skill_root() / "testdata" / "validation" / "captures" / folder


def _feishu_kwargs(args: argparse.Namespace) -> dict:
    return {
        "push_feishu": args.push_feishu,
        "feishu_app_id": args.feishu_app_id,
        "feishu_app_secret": args.feishu_app_secret,
        "feishu_title": args.feishu_title,
        "feishu_base_name": args.feishu_base_name,
        "feishu_append_board": not args.no_feishu_append_board,
        "feishu_run_date": args.feishu_run_date,
        "feishu_append_scope": args.feishu_append_scope,
    }


def main() -> None:
    args = parse_args()
    capture_root = Path(args.capture_root).expanduser().resolve() if args.capture_root.strip() else preset_capture(args.preset)
    if not capture_root.exists():
        raise SystemExit(f"Capture root not found: {capture_root}")

    run18 = not args.scene19_only
    run19 = not args.scene18_only
    results: dict = {"capture_root": str(capture_root), "preset": args.preset}
    feishu = _feishu_kwargs(args)

    if run18:
        results["scene18"] = create_capture_pack_run(
            scene="18",
            capture_root_raw=str(capture_root),
            name=f"{args.name}-scene18",
            project=f"{args.project} — Scene 18",
            output_root=args.output_root,
            platform=args.platform,
            market=args.market,
            formats=args.formats,
            operator_packs_raw=args.operator_packs,
            **feishu,
        )

    if run19:
        results["scene19"] = create_capture_pack_run(
            scene="19",
            capture_root_raw=str(capture_root),
            name=f"{args.name}-scene19",
            project=f"{args.project} — Scene 19",
            output_root=args.output_root,
            platform=args.platform,
            market=args.market,
            formats=args.formats,
            operator_packs_raw=args.operator_packs,
            **feishu,
        )

    baseline_path = capture_root / "weekly_baseline_delta.json"
    results["weekly_baseline_delta"] = str(baseline_path) if baseline_path.exists() else ""
    print(json.dumps({"ok": True, **results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
