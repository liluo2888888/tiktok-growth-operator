from __future__ import annotations

import argparse
import json
from pathlib import Path

from tiktok_shop_source import sync_competitor_products


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync TikTok Shop competitor products into a capture pack.")
    parser.add_argument("--capture-root", required=True, help="Capture-pack root directory.")
    parser.add_argument("--keyword", default="", help="Shop search keyword.")
    parser.add_argument("--region", default="", help="Shop region, e.g. US.")
    parser.add_argument("--limit", type=int, default=10, help="Maximum products to keep.")
    parser.add_argument("--force-refresh", action="store_true", help="Ignore cached competitor_products.json.")
    parser.add_argument(
        "--enrich-detail",
        action="store_true",
        help="When using Clipcat, call product_detail for each search hit.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    capture_root = Path(args.capture_root).resolve()
    result = sync_competitor_products(
        capture_root,
        keyword=args.keyword,
        region=args.region,
        limit=args.limit,
        force_refresh=args.force_refresh,
        enrich_detail=args.enrich_detail,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get("status") not in {"ok", "cached"}:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
