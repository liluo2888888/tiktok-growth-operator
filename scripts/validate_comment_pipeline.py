from __future__ import annotations

import json
import sys
from pathlib import Path

from comment_pipeline import ensure_comment_pack_artifacts, process_comment_pack
from import_tiktok_capture_pack import collect_comment_entries, load_comment_pack
def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def fixture_capture_root(name: str) -> Path:
    return skill_root() / "testdata" / "validation" / "captures" / name


def assert_pack_shape(pack: dict, *, label: str) -> None:
    for key in ("cleaned", "rejected", "reply_chains", "stats", "snapshot"):
        if key not in pack:
            raise AssertionError(f"{label} missing pack key: {key}")
    stats = pack["stats"]
    if safe_int(stats.get("cleaned_count")) != len(pack["cleaned"]):
        raise AssertionError(f"{label} cleaned_count mismatch")
    snapshot = pack["snapshot"]
    if snapshot.get("top_reply_chain") and not pack["reply_chains"]:
        raise AssertionError(f"{label} top_reply_chain without reply_chains")


def safe_int(value: object) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def validate_scene08_fixture() -> dict:
    capture_root = fixture_capture_root("scene08-multi-product-home-goods-comments")
    raw_entries = collect_comment_entries(capture_root)
    pack = load_comment_pack(capture_root)
    assert_pack_shape(pack, label="scene08")
    if not pack["cleaned"]:
        raise AssertionError("scene08 fixture produced zero cleaned comments")
    if not pack["reply_chains"]:
        raise AssertionError("scene08 fixture produced zero reply chains")
    for artifact in (
        "comments_cleaned.json",
        "comments_rejected.json",
        "comment_reply_chains.json",
        "comment_cleaning_stats.json",
    ):
        if not (capture_root / artifact).exists():
            raise AssertionError(f"scene08 missing artifact: {artifact}")
    return {
        "capture_root": str(capture_root),
        "raw_count": len(raw_entries),
        "cleaned_count": len(pack["cleaned"]),
        "reply_chain_count": len(pack["reply_chains"]),
    }


def validate_multiweek_fixture(name: str) -> dict:
    capture_root = fixture_capture_root(name)
    raw_entries = collect_comment_entries(capture_root)
    if not raw_entries:
        return {"capture_root": str(capture_root), "skipped": "no comment entries in fixture"}
    pack = ensure_comment_pack_artifacts(capture_root, raw_entries)
    assert_pack_shape(pack, label=name)
    return {
        "capture_root": str(capture_root),
        "raw_count": len(raw_entries),
        "cleaned_count": len(pack["cleaned"]),
        "reply_chain_count": len(pack["reply_chains"]),
    }


def validate_in_memory_smoke() -> dict:
    raw = [
        {
            "text": "Is this real or fake???",
            "digg_count": 12,
            "reply_comment_total": 4,
            "source_product": "SKU-A",
            "video_url": "https://www.tiktok.com/@demo/video/1",
        },
        {
            "text": "lol",
            "digg_count": 1,
            "reply_comment_total": 0,
        },
        {
            "text": "Shipping took forever and the box arrived crushed",
            "digg_count": 8,
            "reply_comment_total": 5,
            "is_reply": True,
            "parent_comment_id": "c1",
            "source_product": "SKU-A",
            "video_url": "https://www.tiktok.com/@demo/video/1",
        },
    ]
    pack = process_comment_pack(raw)
    assert_pack_shape(pack, label="smoke")
    if len(pack["rejected"]) < 1:
        raise AssertionError("smoke pack should reject at least one noisy comment")
    return {"smoke_cleaned": len(pack["cleaned"]), "smoke_rejected": len(pack["rejected"])}


def main() -> None:
    results = {
        "scene08": validate_scene08_fixture(),
        "scene18": validate_multiweek_fixture("scene18-19-multi-week-account"),
        "scene19": validate_multiweek_fixture("scene19-roi-multiwindow-account"),
        "smoke": validate_in_memory_smoke(),
    }
    print(json.dumps({"ok": True, "results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1) from exc
