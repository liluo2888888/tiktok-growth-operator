from __future__ import annotations

import argparse
import json
from pathlib import Path

from text_normalization import read_json_file, write_json_file


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seed Scene 02 patrol runtime files (snapshot, delta, alerts, scene03_candidates) from ranked videos."
    )
    parser.add_argument("--capture-root", required=True, help="Capture-pack directory to update in place.")
    parser.add_argument("--category", default="General")
    parser.add_argument("--market", default="US")
    parser.add_argument("--cadence", default="daily")
    parser.add_argument("--queries", default="", help="Comma-separated patrol queries.")
    parser.add_argument("--topics", default="", help="Comma-separated patrol topics.")
    parser.add_argument("--scene03-count", type=int, default=3)
    parser.add_argument("--min-likes", type=int, default=1000)
    parser.add_argument("--shortlist-count", type=int, default=5)
    parser.add_argument("--force", action="store_true", help="Overwrite existing patrol runtime files.")
    return parser.parse_args()


def split_csv(raw: str) -> list[str]:
    items: list[str] = []
    for part in raw.split(","):
        text = part.strip()
        if text and text not in items:
            items.append(text)
    return items


def load_ranked_videos(capture_root: Path) -> list[dict]:
    for name in ("aggregate_ranked_videos.json", "ranked_videos.json"):
        path = capture_root / name
        if not path.exists():
            continue
        payload = read_json_file(path)
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
    raise FileNotFoundError(f"No ranked video list under {capture_root}")


def patrol_files_present(capture_root: Path) -> bool:
    required = (
        "patrol_snapshot.json",
        "patrol_delta.json",
        "patrol_alerts.json",
        "scene03_candidates.json",
    )
    return all((capture_root / name).exists() for name in required)


def main() -> None:
    args = parse_args()
    capture_root = Path(args.capture_root).expanduser().resolve()
    if not capture_root.exists():
        raise SystemExit(f"Capture root not found: {capture_root}")

    if patrol_files_present(capture_root) and not args.force:
        print(
            json.dumps(
                {
                    "status": "skipped",
                    "reason": "patrol runtime already present",
                    "capture_root": str(capture_root),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    ranked_rows = load_ranked_videos(capture_root)
    if not ranked_rows:
        raise SystemExit(f"No ranked videos to seed patrol pack: {capture_root}")

    from run_scene02_patrol import (
        build_alerts,
        build_delta,
        scene03_candidates,
        write_capture_pack,
    )

    queries = split_csv(args.queries)
    topics = split_csv(args.topics)
    previous_snapshot: dict = {}
    prior_path = capture_root / "patrol_snapshot.json"
    if prior_path.exists() and not args.force:
        prior = read_json_file(prior_path)
        if isinstance(prior, dict):
            previous_snapshot = prior

    delta = build_delta(ranked_rows, previous_snapshot, alert_like_jump=500, alert_score_jump=1200)
    alerts = build_alerts(delta)
    scene03_rows = scene03_candidates(
        ranked_rows,
        delta,
        scene03_count=args.scene03_count,
        min_likes=args.min_likes,
    )
    source_manifest = read_json_file(capture_root / "source_manifest.json")
    if not isinstance(source_manifest, list):
        source_manifest = [
            {
                "source_kind": "seed",
                "source_label": "ranked_videos",
                "item_count": len(ranked_rows),
            }
        ]

    snapshot = write_capture_pack(
        capture_root=capture_root,
        category=args.category,
        market=args.market,
        cadence=args.cadence,
        queries=queries,
        topics=topics,
        ranked_rows=ranked_rows,
        source_manifest=source_manifest,
        previous_snapshot=previous_snapshot,
        delta=delta,
        alerts=alerts,
        scene03_rows=scene03_rows,
        min_likes=args.min_likes,
        shortlist_count=args.shortlist_count,
    )
    print(
        json.dumps(
            {
                "status": "ok",
                "capture_root": str(capture_root),
                "ranked_count": len(ranked_rows),
                "scene03_candidate_count": len(scene03_rows),
                "alert_count": len(alerts),
                "snapshot_at": snapshot.get("snapshot_at"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
