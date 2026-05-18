from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from clipcat_client import normalize_shop_product
from text_normalization import normalize_text

DEFAULT_PARTNER_BASE = "https://open-api.tiktokglobalshop.com"
DEFAULT_API_VERSION = "202309"


def partner_app_key() -> str:
    return normalize_text(os.environ.get("TIKTOK_SHOP_APP_KEY")) or normalize_text(os.environ.get("TTS_APP_KEY"))


def partner_app_secret() -> str:
    return normalize_text(os.environ.get("TIKTOK_SHOP_APP_SECRET")) or normalize_text(os.environ.get("TTS_APP_SECRET"))


def partner_shop_cipher() -> str:
    return normalize_text(os.environ.get("TIKTOK_SHOP_CIPHER")) or normalize_text(os.environ.get("TTS_SHOP_CIPHER"))


def partner_access_token() -> str:
    return normalize_text(os.environ.get("TIKTOK_SHOP_ACCESS_TOKEN")) or normalize_text(os.environ.get("TTS_ACCESS_TOKEN"))


def partner_api_version() -> str:
    return normalize_text(os.environ.get("TIKTOK_SHOP_API_VERSION")) or DEFAULT_API_VERSION


def partner_base_url() -> str:
    return normalize_text(os.environ.get("TIKTOK_SHOP_OPEN_API_BASE")) or DEFAULT_PARTNER_BASE


def partner_configured() -> bool:
    return bool(partner_app_key() and partner_app_secret() and partner_shop_cipher() and partner_access_token())


def products_search_path() -> str:
    version = partner_api_version()
    return f"/product/{version}/products/search"


def generate_signature(*, path: str, query: dict[str, str], body: str, app_secret: str) -> str:
    filtered = {k: str(v) for k, v in query.items() if k not in {"sign", "access_token"} and v is not None}
    pieces = "".join(f"{key}{filtered[key]}" for key in sorted(filtered))
    sign_string = f"{app_secret}{path}{pieces}{body}{app_secret}"
    return hmac.new(app_secret.encode("utf-8"), sign_string.encode("utf-8"), hashlib.sha256).hexdigest()


def _first_product_rows(payload: object) -> list[dict]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    data = payload.get("data")
    if isinstance(data, dict):
        for key in ("products", "product_list", "items", "list"):
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    for key in ("products", "product_list", "items"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def normalize_partner_product(raw: dict) -> dict:
    title = normalize_text(raw.get("title")) or normalize_text(raw.get("product_name")) or normalize_text(
        (raw.get("product") or {}).get("title") if isinstance(raw.get("product"), dict) else ""
    )
    product_id = normalize_text(raw.get("product_id")) or normalize_text(raw.get("id")) or title
    price_block = raw.get("price") if isinstance(raw.get("price"), dict) else {}
    price = (
        normalize_text(raw.get("sale_price"))
        or normalize_text(raw.get("price"))
        or normalize_text(price_block.get("sale_price"))
        or normalize_text(price_block.get("amount"))
        or "待补"
    )
    return normalize_shop_product(
        {
            "product_id": product_id,
            "title": title,
            "platform": "TikTok Shop",
            "price": price,
            "rating": normalize_text(raw.get("rating")) or "待补",
            "review_count": normalize_text(raw.get("review_count")) or "待补",
            "sales_signal": normalize_text(raw.get("sold_count"))
            or normalize_text(raw.get("sales"))
            or normalize_text(raw.get("status"))
            or "待补",
            "url": normalize_text(raw.get("product_url")) or normalize_text(raw.get("url")),
        },
        source="tiktok_shop_partner_api",
    )


def build_search_body(*, keyword: str, limit: int) -> dict[str, Any]:
    template = normalize_text(os.environ.get("TIKTOK_SHOP_PARTNER_SEARCH_BODY_JSON"))
    if template:
        try:
            body = json.loads(template)
            if isinstance(body, dict):
                body.setdefault("page_size", limit)
                return body
        except json.JSONDecodeError:
            pass
    body: dict[str, Any] = {"page_size": min(max(limit, 1), 50)}
    if keyword:
        # Partner search filters vary by API version; title keyword is applied client-side as fallback too.
        body["filters"] = {"product_name": keyword}
    status = normalize_text(os.environ.get("TIKTOK_SHOP_PARTNER_SEARCH_STATUS"))
    if status:
        body["status"] = status
    return body


def filter_products_by_keyword(products: list[dict], keyword: str) -> list[dict]:
    needle = normalize_text(keyword).lower()
    if not needle:
        return products
    filtered = []
    for product in products:
        hay = " ".join(
            [
                normalize_text(product.get("title")),
                normalize_text(product.get("product_id")),
            ]
        ).lower()
        if needle in hay:
            filtered.append(product)
    return filtered or products


def search_partner_products(*, keyword: str, region: str, limit: int) -> dict[str, Any]:
    del region  # Partner list API is scoped to authorized shop_cipher, not open region search.
    if not partner_configured():
        return {
            "ok": False,
            "reason": "partner-not-configured",
            "hint": "Set TIKTOK_SHOP_APP_KEY, TIKTOK_SHOP_APP_SECRET, TIKTOK_SHOP_CIPHER, TIKTOK_SHOP_ACCESS_TOKEN.",
        }

    path = products_search_path()
    body_obj = build_search_body(keyword=keyword, limit=limit)
    body_str = json.dumps(body_obj, ensure_ascii=False, separators=(",", ":"))
    timestamp = str(int(time.time()))
    query = {
        "app_key": partner_app_key(),
        "timestamp": timestamp,
        "shop_cipher": partner_shop_cipher(),
        "sign_method": "HmacSHA256",
        "access_token": partner_access_token(),
    }
    sign = generate_signature(path=path, query=query, body=body_str, app_secret=partner_app_secret())
    query["sign"] = sign
    url = f"{partner_base_url()}{path}?{urllib.parse.urlencode(query)}"
    request = urllib.request.Request(
        url,
        data=body_str.encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-tts-access-token": partner_access_token(),
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return {"ok": False, "reason": "partner-http-error", "status": exc.code, "detail": detail, "url": url}
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"ok": False, "reason": "partner-request-failed", "detail": str(exc), "url": url}

    code = payload.get("code") if isinstance(payload, dict) else None
    message = normalize_text(payload.get("message")) if isinstance(payload, dict) else ""
    if code not in (None, 0, "0") and str(code) not in {"0", "success"}:
        return {"ok": False, "reason": "partner-api-error", "code": code, "message": message, "response": payload}

    rows = _first_product_rows(payload)
    products = [normalize_partner_product(row) for row in rows]
    products = filter_products_by_keyword(products, keyword)[:limit]
    return {
        "ok": True,
        "products": products,
        "provider": "tiktok_shop_partner_api",
        "path": path,
        "request_body": body_obj,
        "response": payload,
        "note": "Partner products/search returns the authorized shop catalog, not a global competitor keyword index.",
    }
