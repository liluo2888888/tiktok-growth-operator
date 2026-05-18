from __future__ import annotations

import argparse
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import urlparse

from tiktok_shop_official_client import official_credentials_configured, official_source_metadata, search_official_products
from text_normalization import normalize_text


class GatewayHandler(BaseHTTPRequestHandler):
    server_version = "TikTokShopOfficialGateway/1.0"

    def log_message(self, format: str, *args) -> None:
        return

    def _json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        if self.path != "/v1/shop/products/search":
            self._json(404, {"error": "not_found", "path": self.path})
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid_json"})
            return
        if not isinstance(payload, dict):
            self._json(400, {"error": "invalid_payload"})
            return

        keyword = normalize_text(payload.get("keyword")) or "beauty"
        region = normalize_text(payload.get("region")) or "US"
        limit = int(payload.get("limit") or 10)

        if not official_credentials_configured():
            self._json(
                503,
                {
                    "error": "official_credentials_not_configured",
                    "hint": (
                        "Register TikTok Research API or TikTok Shop Partner Center app, then set "
                        "TIKTOK_RESEARCH_ACCESS_TOKEN or TIKTOK_RESEARCH_CLIENT_KEY/SECRET."
                    ),
                    "docs": [
                        "https://developers.tiktok.com/products/research-api",
                        "https://partner.tiktokshop.com/doc",
                    ],
                },
            )
            return

        result = search_official_products(keyword=keyword, region=region, limit=limit)
        if not result.get("ok"):
            self._json(502, {"error": "official_query_failed", "detail": result})
            return

        products = result.get("products") or []
        source = result.get("source") if isinstance(result.get("source"), dict) else official_source_metadata()
        self._json(
            200,
            {
                "products": products,
                "source": source,
                "provider": normalize_text(result.get("provider")) or "tiktok_research_api",
                "keyword": keyword,
                "region": region,
            },
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Local HTTP gateway for Scene 06 that proxies TikTok official Research/Partner APIs."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8791)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = HTTPServer((args.host, args.port), GatewayHandler)
    base = f"http://{args.host}:{args.port}"
    print(
        json.dumps(
            {
                "status": "listening",
                "url": base,
                "search_endpoint": f"{base}/v1/shop/products/search",
                "official_credentials_configured": official_credentials_configured(),
                "hostname": urlparse(base).hostname,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        thread.join()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
