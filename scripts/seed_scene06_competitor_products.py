from __future__ import annotations

import argparse
import json
from pathlib import Path

from text_normalization import normalize_text, read_json_file, write_json_file


DEFAULT_BEAUTY_SKUS = [
    {
        "product_id": "fixture-velvet-lip-glaze-01",
        "title": "Velvet Lip Glaze - Rose Nude",
        "platform": "TikTok Shop",
        "price": "18.99",
        "rating": "4.6",
        "review_count": "842",
        "sales_signal": "rising-in-category",
        "url": "https://www.tiktok.com/shop/pdp/velvet-lip-glaze-rose-nude",
        "evidence_source": "structured_fixture",
    },
    {
        "product_id": "fixture-hydrating-serum-02",
        "title": "Hydrating Barrier Serum 30ml",
        "platform": "TikTok Shop",
        "price": "24.50",
        "rating": "4.8",
        "review_count": "1204",
        "sales_signal": "stable-top-seller",
        "url": "https://www.tiktok.com/shop/pdp/hydrating-barrier-serum-30ml",
        "evidence_source": "structured_fixture",
    },
]


def load_ranked_videos(capture_root: Path) -> list[dict]:
    for name in ("aggregate_ranked_videos.json", "aggregate_qualified_videos.json"):
        path = capture_root / name
        if not path.exists():
            continue
        payload = read_json_file(path)
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
    return []


def infer_products_from_videos(videos: list[dict], *, limit: int) -> list[dict]:
    rows: list[dict] = []
    for video in videos:
        shop = normalize_text(video.get("tkshop_signal"))
        commerce = int(video.get("commerce_confidence") or 0)
        if shop and shop != "未检测到":
            signal = shop
        elif commerce >= 10:
            signal = f"commerce_confidence={commerce}"
        else:
            continue
        title = (
            normalize_text(video.get("core_topic"))
            or normalize_text(video.get("hook_text"))
            or normalize_text(video.get("desc"))
            or "未命名竞品线索"
        )[:72]
        rows.append(
            {
                "product_id": normalize_text(video.get("video_id")) or normalize_text(video.get("video_url")),
                "title": title,
                "platform": "TikTok / inferred-from-video",
                "price": normalize_text(video.get("price")) or "待补",
                "rating": normalize_text(video.get("rating")) or "待补",
                "review_count": str(video.get("comment_count", "")) or "待补",
                "sales_signal": signal,
                "url": normalize_text(video.get("video_url")),
                "evidence_source": "ranked_video_proxy",
            }
        )
        if len(rows) >= limit:
            break
    return rows


def seed_products(capture_root: Path, *, mode: str, limit: int, force: bool) -> dict:
    capture_root.mkdir(parents=True, exist_ok=True)
    out_path = capture_root / "competitor_products.json"
    meta_path = capture_root / "tiktok_shop_source_meta.json"
    if out_path.exists() and not force:
        existing = read_json_file(out_path)
        count = len(existing) if isinstance(existing, list) else 0
        return {"status": "cached", "path": str(out_path), "product_count": count}

    mode = normalize_text(mode).lower() or "auto"
    products: list[dict] = []
    source = "structured_fixture"
    if mode in {"fixture", "auto"}:
        products = list(DEFAULT_BEAUTY_SKUS)[:limit]
        source = "structured_fixture"
    if not products and mode in {"proxy", "auto"}:
        products = infer_products_from_videos(load_ranked_videos(capture_root), limit=limit)
        source = "ranked_video_proxy"

    if not products:
        return {
            "status": "skipped",
            "reason": "no-seed-source",
            "hint": "Provide ranked videos with commerce signals or use --mode fixture.",
        }

    write_json_file(out_path, products[:limit])
    from datetime import datetime

    write_json_file(
        meta_path,
        {
            "source": source,
            "provider": "local_seed",
            "product_count": len(products[:limit]),
            "source_attestation": "unverified",
            "require_verified_source": False,
            "require_source_metadata": False,
            "updated_at": datetime.now().isoformat(timespec="seconds"),
            "seed_mode": mode,
        },
    )
    return {
        "status": "ok",
        "path": str(out_path),
        "product_count": len(products[:limit]),
        "source": source,
        "data_source_mode": "tiktok_shop_structured",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed Scene 06 competitor_products.json for unverified structured runs.")
    parser.add_argument("--capture-root", required=True)
    parser.add_argument("--mode", default="auto", choices=["auto", "fixture", "proxy"])
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = seed_products(Path(args.capture_root).resolve(), mode=args.mode, limit=args.limit, force=args.force)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get("status") not in {"ok", "cached"}:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
