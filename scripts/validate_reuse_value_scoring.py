from __future__ import annotations

import json
import sys
from pathlib import Path

from reuse_value_scoring import apply_reuse_value_scoring, compare_rank_orders, popularity_first_rank_key
from text_normalization import read_json_file


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def fixture_root() -> Path:
    return skill_root() / "testdata" / "validation" / "captures" / "scene01-strong-inputs-pass"


def assert_reorder_case() -> dict:
    videos = [
        {
            "video_url": "https://example.com/popular-thin",
            "video_id": "popular-thin",
            "digg_count": 500_000,
            "comment_count": 40,
            "share_count": 900,
            "play_count": 8_000_000,
            "hook_text": "wow",
            "desc": "wow",
        },
        {
            "video_url": "https://example.com/reusable-rich",
            "video_id": "reusable-rich",
            "digg_count": 18_000,
            "comment_count": 420,
            "share_count": 900,
            "play_count": 220_000,
            "author_verified": True,
            "author_signature": "Board-certified dermatologist",
            "caption_text": "3 ways to fix dull skin before summer. Part 2 shows the before/after proof.",
            "hook_text": "3 ways to fix dull skin before summer",
            "core_topic": "skincare routine proof series",
            "desc": "3 ways to fix dull skin before summer. Part 2 shows the before/after proof.",
            "hashtags": ["skincare", "beforeafter", "routine", "proof"],
            "downloaded_metadata_path": "fixtures/metadata.json",
        },
    ]
    comparison = compare_rank_orders(videos)
    if not comparison.get("order_changed"):
        raise RuntimeError("expected reuse-value scoring to reorder popularity-first candidates")
    if comparison["reuse_value_first_order"][0] != "https://example.com/reusable-rich":
        raise RuntimeError("rich reusable candidate should outrank thin high-like candidate")
    return {"check": "synthetic-reorder", "status": "ok", **comparison}


def assert_fixture_rescore() -> dict:
    ranked_path = fixture_root() / "aggregate_ranked_videos.json"
    videos = read_json_file(ranked_path)
    if not isinstance(videos, list) or not videos:
        raise RuntimeError("scene01 fixture ranked list missing")
    popularity_top = max(videos, key=popularity_first_rank_key)
    rescored = apply_reuse_value_scoring([dict(item) for item in videos])
    top = rescored[0]
    if safe_int(top.get("reuse_value_score")) <= 0:
        raise RuntimeError("top reuse_value_score should be populated after rescoring")
    if not isinstance(top.get("score_breakdown"), dict):
        raise RuntimeError("score_breakdown should be populated after rescoring")
    if not clean_text(top.get("why_selected")):
        raise RuntimeError("why_selected should be populated after rescoring")
    return {
        "check": "scene01-fixture-rescore",
        "status": "ok",
        "fixture": str(ranked_path),
        "popularity_top_url": clean_text(popularity_top.get("video_url")),
        "reuse_top_url": clean_text(top.get("video_url")),
        "reuse_top_score": safe_int(top.get("reuse_value_score")),
        "reuse_top_rank": safe_int(top.get("profile_rank")),
    }


def safe_int(value: object) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def clean_text(value: object) -> str:
    return "" if value is None else str(value).strip()


def main() -> None:
    results = [assert_reorder_case(), assert_fixture_rescore()]
    payload = {"success": True, "results": results}
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"success": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        raise SystemExit(1) from exc
