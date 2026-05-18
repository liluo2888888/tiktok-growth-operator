from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from clipcat_client import normalize_shop_product
from text_normalization import normalize_text

OPEN_API_BASE = "https://open.tiktokapis.com"
RESEARCH_SHOP_PATH = "/v2/research/tts/shop/"
OAUTH_TOKEN_PATH = "/v2/oauth/token/"


def research_client_key() -> str:
    return normalize_text(os.environ.get("TIKTOK_RESEARCH_CLIENT_KEY")) or normalize_text(
        os.environ.get("TIKTOK_CLIENT_KEY")
    )


def research_client_secret() -> str:
    return normalize_text(os.environ.get("TIKTOK_RESEARCH_CLIENT_SECRET")) or normalize_text(
        os.environ.get("TIKTOK_CLIENT_SECRET")
    )


def research_access_token() -> str:
    return normalize_text(os.environ.get("TIKTOK_RESEARCH_ACCESS_TOKEN")) or normalize_text(
        os.environ.get("TIKTOK_ACCESS_TOKEN")
    )


def partner_access_token() -> str:
    return normalize_text(os.environ.get("TIKTOK_SHOP_ACCESS_TOKEN")) or normalize_text(
        os.environ.get("TTS_ACCESS_TOKEN")
    )


def official_credentials_configured() -> bool:
    if research_access_token():
        return True
    if partner_access_token():
        return True
    return bool(research_client_key() and research_client_secret())


def _http_json(
    method: str,
    url: str,
    *,
    payload: dict | None = None,
    headers: dict[str, str] | None = None,
    timeout_s: int = 60,
) -> dict[str, Any]:
    data = None
    req_headers = {"Accept": "application/json"}
    if headers:
        req_headers.update(headers)
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req_headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=req_headers, method=method)
    with urllib.request.urlopen(request, timeout=timeout_s) as response:
        body = json.loads(response.read().decode("utf-8"))
    return body if isinstance(body, dict) else {"payload": body}


def fetch_client_access_token() -> dict[str, Any]:
    token = research_access_token()
    if token:
        return {"ok": True, "access_token": token, "source": "env-access-token"}

    client_key = research_client_key()
    client_secret = research_client_secret()
    if not client_key or not client_secret:
        return {
            "ok": False,
            "reason": "missing-research-credentials",
            "hint": "Set TIKTOK_RESEARCH_ACCESS_TOKEN or TIKTOK_RESEARCH_CLIENT_KEY + TIKTOK_RESEARCH_CLIENT_SECRET.",
        }

    # Client credentials token (Research API): https://developers.tiktok.com/doc/client-access-token-management
    payload = {
        "client_key": client_key,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    }
    try:
        body = _http_json("POST", f"{OPEN_API_BASE}{OAUTH_TOKEN_PATH}", payload=payload)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return {"ok": False, "reason": "oauth-token-http-error", "status": exc.code, "detail": detail}
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"ok": False, "reason": "oauth-token-failed", "detail": str(exc)}

    token = normalize_text(_dig(body, "access_token") or _dig(body, "data", "access_token"))
    if not token:
        return {"ok": False, "reason": "oauth-token-missing", "response": body}
    return {"ok": True, "access_token": token, "response": body}


def _dig(payload: object, *keys: str) -> object:
    current = payload
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _first_rows(payload: object, *keys: str) -> list[dict]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    for key in keys:
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        if isinstance(value, dict):
            nested = _first_rows(value, *keys)
            if nested:
                return nested
    data = payload.get("data")
    if isinstance(data, dict):
        return _first_rows(data, *keys)
    return []


def query_research_shop(*, shop_name: str, limit: int = 10, access_token: str = "") -> dict[str, Any]:
    token = access_token or research_access_token()
    if not token:
        token_result = fetch_client_access_token()
        if not token_result.get("ok"):
            return token_result
        token = normalize_text(token_result.get("access_token"))

    fields = "shop_name,shop_rating,shop_review_count,item_sold_count,shop_id,shop_performance_value"
    query = urllib.parse.urlencode({"fields": fields})
    url = f"{OPEN_API_BASE}{RESEARCH_SHOP_PATH}?{query}"
    body_payload = {"shop_name": shop_name, "limit": min(max(limit, 1), 10)}
    try:
        body = _http_json(
            "POST",
            url,
            payload=body_payload,
            headers={"Authorization": f"Bearer {token}"},
        )
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return {"ok": False, "reason": "research-shop-http-error", "status": exc.code, "detail": detail}
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"ok": False, "reason": "research-shop-failed", "detail": str(exc)}

    shops = _first_rows(body, "shop_data")
    products = []
    for shop in shops:
        shop_id = normalize_text(shop.get("shop_id"))
        products.append(
            normalize_shop_product(
                {
                    "product_id": shop_id or shop_name,
                    "title": normalize_text(shop.get("shop_name")) or shop_name,
                    "platform": "TikTok Shop (Research API / EU shop)",
                    "price": "待补",
                    "rating": normalize_text(shop.get("shop_rating")) or "待补",
                    "review_count": normalize_text(shop.get("shop_review_count")) or "待补",
                    "sales_signal": normalize_text(shop.get("item_sold_count")) or "待补",
                    "url": "",
                    "shop_id": shop_id,
                    "shop_performance_value": shop.get("shop_performance_value"),
                },
                source="tiktok_research_shop_api",
            )
        )
    return {
        "ok": True,
        "provider": "tiktok_research_api",
        "shops": shops,
        "products": products,
        "response": body,
        "note": "Research API returns EU shop aggregates by shop_name, not global keyword catalog search.",
    }


def official_source_metadata(*, auth_mode: str = "research_client_credentials") -> dict[str, str]:
    return {
        "source_type": "official",
        "provider": "tiktok_shop_open_platform",
        "auth_mode": auth_mode,
        "issuer": "tiktok",
        "api_family": "research_api",
    }


def search_official_products(*, keyword: str, region: str, limit: int) -> dict[str, Any]:
    if not official_credentials_configured():
        return {
            "ok": False,
            "reason": "official-credentials-not-configured",
            "hint": (
                "Apply for TikTok Research API (research.data.basic) or TikTok Shop Partner OAuth, then set "
                "TIKTOK_RESEARCH_ACCESS_TOKEN or TIKTOK_RESEARCH_CLIENT_KEY/SECRET."
            ),
        }

    # Research API documents shop lookup by shop_name, not open keyword product search.
    shop_name = normalize_text(os.environ.get("TIKTOK_SHOP_NAME")) or keyword
    result = query_research_shop(shop_name=shop_name, limit=limit)
    if not result.get("ok"):
        return result
    products = list(result.get("products") or [])[:limit]
    return {
        "ok": True,
        "products": products,
        "source": official_source_metadata(auth_mode="research_client_credentials"),
        "provider": "tiktok_research_api",
        "region": region,
        "keyword": keyword,
        "shop_name": shop_name,
    }
