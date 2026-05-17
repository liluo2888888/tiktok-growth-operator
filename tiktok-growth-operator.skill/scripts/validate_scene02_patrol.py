from __future__ import annotations

import json
import sys
from pathlib import Path

from import_tiktok_capture_pack import load_scene02_runtime_files, scene02_change_digest_rows
from run_scene02_patrol import build_delta
from text_normalization import read_json_file


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def patrol_fixture_root() -> Path:
    candidates = [
        skill_root() / "testdata" / "validation" / "capture-packs" / "scene02-patrol-capture-pack",
        skill_root() / "tmp" / "20260507_validation_capture_scene02" / "capture-pack",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("scene02 patrol capture-pack fixture not found")


def validate_patrol_fixture() -> dict:
    capture_root = patrol_fixture_root()
    snapshot, delta, alerts, scene03_candidates = load_scene02_runtime_files(capture_root)
    patrol_config = read_json_file(capture_root / "patrol_config.json")
    watchlist_board = read_json_file(capture_root / "watchlist_board.json") if (capture_root / "watchlist_board.json").exists() else {}

    if not isinstance(patrol_config, dict):
        raise AssertionError("patrol_config.json must be an object")
    append_scope_key = clean_text(patrol_config.get("append_scope_key"))
    if not append_scope_key:
        category = clean_text(patrol_config.get("category") or snapshot.get("category"))
        market = clean_text(patrol_config.get("market") or snapshot.get("market"))
        cadence = clean_text(patrol_config.get("cadence") or snapshot.get("cadence")) or "daily"
        append_scope_key = f"{category}::{market}::{cadence}" if category and market else ""
    if not append_scope_key:
        raise AssertionError("patrol_config missing append_scope_key")

    # Optional artifact for newer packs; synthesize rising_videos when older fixtures omit it.
    rising_videos = delta.get("rising_videos")
    if rising_videos is None:
        synthetic = build_delta(
            snapshot.get("ranked_videos") or [],
            {"ranked_videos": (snapshot.get("ranked_videos") or [])[:1]},
            alert_like_jump=500,
            alert_score_jump=50,
        )
        rising_videos = synthetic.get("rising_videos") or []
        delta = {**delta, "rising_videos": rising_videos}

    digest_rows = scene02_change_digest_rows(
        alerts,
        delta.get("new_videos") or [],
        delta.get("breakout_videos") or [],
        delta.get("repeated_hooks") or [],
        scene03_candidates or [],
        rising_videos,
    )
    if not digest_rows:
        raise AssertionError("scene02 change digest produced zero rows")

    return {
        "capture_root": str(capture_root),
        "alert_count": len(alerts),
        "rising_count": len(rising_videos),
        "digest_row_count": len(digest_rows),
        "has_watchlist_board": bool(watchlist_board),
        "append_scope_key": append_scope_key,
    }


def clean_text(value: object) -> str:
    return str(value or "").strip()


def main() -> None:
    result = validate_patrol_fixture()
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1) from exc
