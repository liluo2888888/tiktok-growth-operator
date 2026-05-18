from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from seed_scene06_competitor_products import seed_products
from start_capture_pack_run import create_capture_pack_run
from tiktok_shop_official_client import official_credentials_configured
from text_normalization import normalize_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Scene 06 end-to-end: seed competitor products, optional official sync, import + render."
    )
    parser.add_argument("--capture-root", required=True, help="TikTok capture-pack directory.")
    parser.add_argument("--name", default="scene06-run", help="Run name.")
    parser.add_argument("--project", default="TikTok Competitor Product Dashboard", help="Project title.")
    parser.add_argument("--platform", default="TikTok")
    parser.add_argument("--market", default="US")
    parser.add_argument("--formats", default="md,docx,xlsx")
    parser.add_argument("--output-root", default="")
    parser.add_argument(
        "--data-path",
        default="auto",
        choices=["auto", "structured", "official"],
        help=(
            "auto=official gateway when credentials exist, else structured seed; "
            "structured=local competitor_products.json only; "
            "official=require official HTTP sync."
        ),
    )
    parser.add_argument("--seed-mode", default="auto", choices=["auto", "fixture", "proxy"])
    parser.add_argument("--shop-keyword", default="beauty")
    parser.add_argument("--shop-region", default="US")
    parser.add_argument("--shop-limit", type=int, default=10)
    parser.add_argument("--shop-http-url", default="", help="Official gateway base URL.")
    parser.add_argument("--shop-http-api-key", default="")
    parser.add_argument("--shop-source-attestation", default="")
    parser.add_argument("--shop-require-verified-source", action="store_true")
    parser.add_argument("--shop-http-allowed-hosts", default="")
    parser.add_argument("--force-seed", action="store_true")
    return parser.parse_args()


def resolve_data_path(requested: str) -> str:
    requested = normalize_text(requested).lower() or "auto"
    if requested == "structured":
        return "structured"
    if requested == "official":
        return "official"
    return "official" if official_credentials_configured() else "structured"


def main() -> None:
    args = parse_args()
    capture_root = Path(args.capture_root).expanduser().resolve()
    data_path = resolve_data_path(args.data_path)

    prelude: dict = {"data_path": data_path, "capture_root": str(capture_root)}

    if data_path == "structured":
        prelude["seed"] = seed_products(
            capture_root,
            mode=args.seed_mode,
            limit=args.shop_limit,
            force=args.force_seed,
        )
        shop_sync = False
        attestation = "unverified"
        require_verified = False
        http_url = ""
    else:
        if not args.shop_http_url.strip():
            raise SystemExit(
                "Official path requires --shop-http-url pointing at your gateway "
                "(run scripts/tiktok_shop_official_gateway.py in another terminal)."
            )
        shop_sync = True
        attestation = normalize_text(args.shop_source_attestation).lower() or "official"
        require_verified = args.shop_require_verified_source or True
        http_url = args.shop_http_url.strip()
        prelude["official_credentials_configured"] = official_credentials_configured()

    result = create_capture_pack_run(
        scene="06",
        capture_root_raw=str(capture_root),
        name=args.name,
        project=args.project,
        output_root=args.output_root,
        platform=args.platform,
        market=args.market,
        formats=args.formats,
        shop_sync=shop_sync,
        shop_keyword=args.shop_keyword,
        shop_region=args.shop_region,
        shop_limit=args.shop_limit,
        shop_source_mode="http",
        shop_http_url=http_url,
        shop_http_api_key=args.shop_http_api_key,
        shop_source_attestation=attestation,
        shop_require_verified_source=require_verified,
        shop_http_allowed_hosts=args.shop_http_allowed_hosts,
    )
    payload = {"ok": True, "prelude": prelude, **result}
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1) from exc
