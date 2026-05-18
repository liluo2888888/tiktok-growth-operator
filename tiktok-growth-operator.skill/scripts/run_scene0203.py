from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from seed_scene02_patrol_pack import load_ranked_videos, patrol_files_present
from start_capture_pack_run import create_capture_pack_run
from text_normalization import normalize_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Scene 02 daily patrol report and auto-chain Scene 03 deep teardown from scene03_candidates."
    )
    parser.add_argument("--capture-root", default="", help="Capture-pack directory. Default: validation patrol fixture.")
    parser.add_argument(
        "--source",
        default="auto",
        choices=["auto", "fixture", "seed", "patrol-loop"],
        help=(
            "auto=use --capture-root or default fixture, seed patrol files if missing; "
            "fixture=default patrol capture pack only; "
            "seed=force seed patrol runtime then run; "
            "patrol-loop=run run_scene02_patrol --skip-live then scene 02+03."
        ),
    )
    parser.add_argument("--name", default="scene0203-run")
    parser.add_argument("--project", default="TikTok Daily Patrol + Deep Teardown")
    parser.add_argument("--platform", default="TikTok")
    parser.add_argument("--market", default="US")
    parser.add_argument("--formats", default="md,docx,xlsx")
    parser.add_argument("--output-root", default="")
    parser.add_argument("--category", default="Orange Cat")
    parser.add_argument("--queries", default="orange cat")
    parser.add_argument("--topics", default="orangecat")
    parser.add_argument("--query-root", default="")
    parser.add_argument("--topic-root", default="")
    parser.add_argument("--operator-packs", default="")
    parser.add_argument("--push-feishu", action="store_true", help="Push Feishu doc/bundle and patrol board after Scene 02 run.")
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


def default_patrol_capture() -> Path:
    return skill_root() / "testdata" / "validation" / "capture-packs" / "scene02-patrol-capture-pack"


def default_tikmatrix_query_root() -> Path:
    env = normalize_text(os.environ.get("TIKMATRIX_FIXTURE_QUERY_ROOT"))
    if env:
        return Path(env)
    candidate = skill_root() / "testdata" / "validation" / "tikmatrix" / "search-live-orange-cat"
    fallback = Path(r"E:\tiktok\TikMatrix\tmp\search-live-orange-cat")
    return candidate if candidate.exists() else fallback


def default_tikmatrix_topic_root() -> Path:
    env = normalize_text(os.environ.get("TIKMATRIX_FIXTURE_TOPIC_ROOT"))
    if env:
        return Path(env)
    candidate = skill_root() / "testdata" / "validation" / "tikmatrix" / "topic-live-orangecat"
    fallback = Path(r"E:\tiktok\TikMatrix\tmp\topic-live-orangecat")
    return candidate if candidate.exists() else fallback


def seed_patrol(capture_root: Path, *, force: bool, category: str, market: str, queries: str, topics: str) -> dict:
    command = [
        sys.executable,
        str(skill_root() / "scripts" / "seed_scene02_patrol_pack.py"),
        "--capture-root",
        str(capture_root),
        "--category",
        category,
        "--market",
        market,
        "--queries",
        queries,
        "--topics",
        topics,
    ]
    if force:
        command.append("--force")
    completed = subprocess.run(command, text=True, capture_output=True, encoding="utf-8", check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.stderr or completed.stdout or "seed_scene02_patrol_pack failed")
    return json.loads(completed.stdout or "{}")


def run_patrol_loop(args: argparse.Namespace, run_root: Path) -> dict:
    query_root = args.query_root.strip() or str(default_tikmatrix_query_root())
    topic_root = args.topic_root.strip() or str(default_tikmatrix_topic_root())
    command = [
        sys.executable,
        str(skill_root() / "scripts" / "run_scene02_patrol.py"),
        "--name",
        f"{args.name}-patrol",
        "--project",
        args.project,
        "--category",
        args.category,
        "--market",
        args.market,
        "--mode",
        "mixed",
        "--queries",
        args.queries,
        "--topics",
        args.topics,
        "--query-root",
        query_root,
        "--topic-root",
        topic_root,
        "--skip-live",
        "--also-run-scene03",
        "--formats",
        args.formats,
        "--output-root",
        str(run_root / "patrol-loop"),
    ]
    if args.operator_packs.strip():
        command.extend(["--operator-packs", args.operator_packs])
    completed = subprocess.run(command, text=True, capture_output=True, encoding="utf-8", check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.stderr or completed.stdout or "run_scene02_patrol failed")
    return json.loads(completed.stdout or "{}")


def main() -> None:
    args = parse_args()
    if args.capture_root.strip():
        capture_root = Path(args.capture_root).expanduser().resolve()
    else:
        capture_root = default_patrol_capture()

    prelude: dict = {"source": args.source, "capture_root": str(capture_root)}

    if args.source == "patrol-loop":
        run_root = Path(args.output_root).expanduser().resolve() if args.output_root.strip() else skill_root() / "tmp" / f"{args.name}-patrol-loop"
        patrol_result = run_patrol_loop(args, run_root)
        print(json.dumps({"ok": True, "mode": "patrol-loop", "patrol_result": patrol_result}, ensure_ascii=False, indent=2))
        return

    if args.source in {"auto", "seed"} and not patrol_files_present(capture_root):
        prelude["seed"] = seed_patrol(
            capture_root,
            force=args.source == "seed",
            category=args.category,
            market=args.market,
            queries=args.queries,
            topics=args.topics,
        )
    elif args.source == "seed":
        prelude["seed"] = seed_patrol(
            capture_root,
            force=True,
            category=args.category,
            market=args.market,
            queries=args.queries,
            topics=args.topics,
        )

    ranked_count = len(load_ranked_videos(capture_root))
    if ranked_count < 1:
        raise SystemExit(f"Capture pack has no ranked videos: {capture_root}")

    scene02_result = create_capture_pack_run(
        scene="02",
        capture_root_raw=str(capture_root),
        name=args.name,
        project=args.project,
        output_root=args.output_root,
        platform=args.platform,
        market=args.market,
        formats=args.formats,
        operator_packs_raw=args.operator_packs,
        push_feishu=args.push_feishu,
        feishu_app_id=args.feishu_app_id,
        feishu_app_secret=args.feishu_app_secret,
        feishu_title=args.feishu_title,
        feishu_base_name=args.feishu_base_name,
        feishu_append_board=not args.no_feishu_append_board,
        feishu_run_date=args.feishu_run_date,
        feishu_append_scope=args.feishu_append_scope,
    )
    chained = scene02_result.get("chained_runs") or []
    print(
        json.dumps(
            {
                "ok": True,
                "prelude": prelude,
                "ranked_count": ranked_count,
                "scene02_result": scene02_result,
                "chained_scene03": chained[0] if chained else None,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
