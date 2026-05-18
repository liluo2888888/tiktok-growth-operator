from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from clipcat_client import (
    clipcat_configured,
    fetch_product_detail,
    normalize_shop_product,
    search_shop_items,
)
from text_normalization import normalize_text, read_json_file, write_json_file

PRODUCTS_FILENAME = "competitor_products.json"
META_FILENAME = "tiktok_shop_source_meta.json"
VERIFIED_ATTESTATIONS = {"official", "authorized-partner", "internal-gateway"}

# Gateway must echo these fields under response.source (or source_metadata) when attestation is verified.
METADATA_RULES_BY_ATTESTATION: dict[str, dict[str, str | tuple[str, ...]]] = {
    "official": {
        "source_type": "official",
        "provider": "tiktok_shop_open_platform",
        "auth_mode": "merchant_oauth",
    },
    "authorized-partner": {
        "source_type": "authorized-partner",
        "provider": "tiktok_shop_open_platform",
        "auth_mode": ("partner_oauth", "authorized_partner", "merchant_oauth"),
    },
    "internal-gateway": {
        "source_type": "internal-gateway",
        "provider": ("internal-gateway", "tiktok_shop_open_platform"),
        "auth_mode": ("service_account", "internal_token", "merchant_oauth", "partner_oauth"),
    },
}


def products_path(capture_root: Path) -> Path:
    return capture_root / PRODUCTS_FILENAME


def meta_path(capture_root: Path) -> Path:
    return capture_root / META_FILENAME


def load_products_file(capture_root: Path) -> list[dict]:
    path = products_path(capture_root)
    if not path.exists():
        return []
    payload = read_json_file(path)
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return []


def save_products(capture_root: Path, products: list[dict], *, source: str, meta: dict | None = None) -> Path:
    cleaned = []
    for item in products:
        row = {key: value for key, value in item.items() if key != "raw"}
        cleaned.append(row)
    write_json_file(products_path(capture_root), cleaned)
    payload = {
        "source": source,
        "product_count": len(cleaned),
        "updated_at": meta.get("updated_at") if meta else "",
        **(meta or {}),
    }
    if not payload.get("updated_at"):
        from datetime import datetime

        payload["updated_at"] = datetime.now().isoformat(timespec="seconds")
    write_json_file(meta_path(capture_root), payload)
    return products_path(capture_root)


def shop_source_mode(explicit_mode: str = "") -> str:
    return normalize_text(explicit_mode).lower() or normalize_text(os.environ.get("TIKTOK_SHOP_SOURCE")).lower() or "auto"


def shop_http_url(explicit_url: str = "") -> str:
    return (normalize_text(explicit_url) or normalize_text(os.environ.get("TIKTOK_SHOP_HTTP_URL"))).rstrip("/")


def shop_source_attestation(explicit_attestation: str = "") -> str:
    return (
        normalize_text(explicit_attestation).lower()
        or normalize_text(os.environ.get("TIKTOK_SHOP_SOURCE_ATTESTATION")).lower()
        or "unverified"
    )


def requires_verified_source(explicit_require_verified: bool = False) -> bool:
    if explicit_require_verified:
        return True
    return normalize_text(os.environ.get("TIKTOK_SHOP_REQUIRE_VERIFIED")).lower() in {"1", "true", "yes", "on"}


def requires_source_metadata_validation(attestation: str, require_verified: bool) -> bool:
    if requires_verified_source(require_verified) or is_verified_attestation(attestation):
        return True
    return normalize_text(os.environ.get("TIKTOK_SHOP_REQUIRE_SOURCE_METADATA")).lower() in {"1", "true", "yes", "on"}


def is_verified_attestation(attestation: str) -> bool:
    return normalize_text(attestation).lower() in VERIFIED_ATTESTATIONS


def http_allowed_hosts(explicit_hosts: str = "") -> list[str]:
    raw = normalize_text(explicit_hosts) or normalize_text(os.environ.get("TIKTOK_SHOP_HTTP_ALLOWED_HOSTS"))
    return [item.strip().lower() for item in raw.split(",") if item.strip()]


def extract_source_metadata(body: Any) -> dict[str, Any]:
    if not isinstance(body, dict):
        return {}
    for key in ("source", "source_metadata"):
        value = body.get(key)
        if isinstance(value, dict):
            return value
    return {}


def _field_matches(actual: str, expected: str | tuple[str, ...]) -> bool:
    actual_norm = normalize_text(actual).lower()
    if not actual_norm:
        return False
    if isinstance(expected, tuple):
        return actual_norm in {normalize_text(item).lower() for item in expected}
    return actual_norm == normalize_text(expected).lower()


def validate_source_metadata(metadata: dict[str, Any], attestation: str) -> tuple[bool, list[str]]:
    attestation = normalize_text(attestation).lower()
    rules = METADATA_RULES_BY_ATTESTATION.get(attestation)
    if not rules:
        return False, [f"unsupported-attestation:{attestation or 'missing'}"]

    errors: list[str] = []
    for field, expected in rules.items():
        if not _field_matches(normalize_text(metadata.get(field)), expected):
            errors.append(
                f"{field}: expected {expected!r}, got {normalize_text(metadata.get(field))!r}"
            )
    issuer = normalize_text(metadata.get("issuer"))
    if issuer and issuer.lower() not in {"tiktok", "bytedance", "tiktok_shop"}:
        errors.append(f"issuer: unexpected value {issuer!r}")
    return not errors, errors


def validate_http_host_allowed(base_url: str, explicit_hosts: str = "") -> tuple[bool, str]:
    allowed = http_allowed_hosts(explicit_hosts)
    if not allowed:
        return True, ""
    host = (urlparse(base_url).hostname or "").lower()
    if host not in allowed:
        return False, f"http-host-not-allowed:{host or 'missing-host'}"
    return True, ""


def fetch_via_http(
    *,
    keyword: str,
    region: str,
    limit: int,
    base_url: str = "",
    api_key: str = "",
) -> tuple[list[dict], dict[str, Any]]:
    base = shop_http_url(base_url)
    if not base:
        return [], {"status": "skipped", "reason": "no-http-url"}
    payload = json.dumps({"keyword": keyword, "region": region, "limit": limit}, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        f"{base}/v1/shop/products/search",
        data=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    api_key = normalize_text(api_key) or normalize_text(os.environ.get("TIKTOK_SHOP_HTTP_API_KEY"))
    if api_key:
        request.add_header("Authorization", f"Bearer {api_key}")
    with urllib.request.urlopen(request, timeout=60) as response:
        body = json.loads(response.read().decode("utf-8"))
    items = body.get("products") if isinstance(body, dict) else body
    if not isinstance(items, list):
        items = []
    products = [normalize_shop_product(item, source="http_shop_api") for item in items if isinstance(item, dict)]
    return products, {
        "status": "ok",
        "provider": "http",
        "response_source": extract_source_metadata(body),
        "gateway_url": base,
    }


def fetch_via_clipcat(*, keyword: str, region: str, limit: int, enrich_detail: bool) -> tuple[list[dict], dict[str, Any]]:
    if not clipcat_configured():
        return [], {"status": "skipped", "reason": "clipcat-not-configured"}
    search = search_shop_items(keyword=keyword, region=region)
    if not search.get("ok"):
        return [], {"status": "error", "reason": "clipcat-search-failed", "detail": search}
    products = list(search.get("products") or [])[:limit]
    if enrich_detail:
        enriched: list[dict] = []
        for product in products:
            product_input = normalize_text(product.get("url") or product.get("product_id"))
            if not product_input:
                enriched.append(product)
                continue
            detail = fetch_product_detail(product_input=product_input, region=region)
            if detail.get("ok") and isinstance(detail.get("product"), dict):
                enriched.append(detail["product"])
            else:
                enriched.append(product)
        products = enriched
    return products, {"status": "ok", "provider": "clipcat", "search": search}


def sync_competitor_products(
    capture_root: Path,
    *,
    keyword: str = "",
    region: str = "",
    limit: int = 10,
    force_refresh: bool = False,
    enrich_detail: bool = False,
    source_mode: str = "",
    http_url: str = "",
    http_api_key: str = "",
    source_attestation: str = "",
    require_verified_source: bool = False,
    http_allowed_hosts_override: str = "",
) -> dict[str, Any]:
    capture_root.mkdir(parents=True, exist_ok=True)
    keyword = keyword or normalize_text(os.environ.get("TIKTOK_SHOP_KEYWORD")) or "beauty"
    region = region or normalize_text(os.environ.get("TIKTOK_SHOP_REGION")) or "US"
    limit = int(os.environ.get("TIKTOK_SHOP_LIMIT") or limit or 10)

    if not force_refresh:
        existing = load_products_file(capture_root)
        if existing:
            return {
                "status": "cached",
                "source": "competitor_products.json",
                "product_count": len(existing),
                "path": str(products_path(capture_root)),
            }

    mode = shop_source_mode(source_mode)
    attestation = shop_source_attestation(source_attestation)
    require_verified = requires_verified_source(require_verified_source)
    require_metadata = requires_source_metadata_validation(attestation, require_verified)
    products: list[dict] = []
    meta: dict[str, Any] = {
        "keyword": keyword,
        "region": region,
        "limit": limit,
        "source_attestation": attestation,
        "require_verified_source": require_verified,
        "require_source_metadata": require_metadata,
    }

    if require_verified and not is_verified_attestation(attestation):
        return {
            "status": "blocked",
            "reason": "unverified-shop-source",
            "hint": "Pass a verified attestation such as official, authorized-partner, or internal-gateway.",
            "path": str(products_path(capture_root)),
            "meta": meta,
        }

    if mode in {"http", "auto"} and shop_http_url(http_url):
        base = shop_http_url(http_url)
        host_ok, host_reason = validate_http_host_allowed(base, http_allowed_hosts_override)
        if not host_ok:
            return {
                "status": "blocked",
                "reason": host_reason,
                "hint": "Set TIKTOK_SHOP_HTTP_ALLOWED_HOSTS or --shop-http-allowed-hosts to permit this gateway host.",
                "path": str(products_path(capture_root)),
                "meta": meta,
            }
        try:
            products, http_meta = fetch_via_http(
                keyword=keyword,
                region=region,
                limit=limit,
                base_url=http_url,
                api_key=http_api_key,
            )
            meta.update(http_meta)
            response_source = http_meta.get("response_source") if isinstance(http_meta.get("response_source"), dict) else {}
            meta["response_source"] = response_source
            if products and require_metadata:
                metadata_ok, metadata_errors = validate_source_metadata(response_source, attestation)
                meta["source_metadata_validation"] = {
                    "ok": metadata_ok,
                    "errors": metadata_errors,
                    "required_for_attestation": attestation,
                }
                if not metadata_ok:
                    return {
                        "status": "blocked",
                        "reason": "invalid-source-metadata",
                        "hint": (
                            "HTTP gateway must return source metadata matching the attestation, e.g. "
                            "source_type=official, provider=tiktok_shop_open_platform, auth_mode=merchant_oauth."
                        ),
                        "path": str(products_path(capture_root)),
                        "meta": meta,
                    }
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            meta.update({"status": "error", "provider": "http", "error": str(exc)})

    if not products and mode in {"clipcat", "auto"}:
        if require_metadata and is_verified_attestation(attestation):
            return {
                "status": "blocked",
                "reason": "verified-attestation-requires-http-metadata",
                "hint": (
                    "Verified attestations require an HTTP gateway that returns source metadata. "
                    "Clipcat alone cannot satisfy official/authorized-partner verification."
                ),
                "path": str(products_path(capture_root)),
                "meta": meta,
            }
        products, clipcat_meta = fetch_via_clipcat(
            keyword=keyword,
            region=region,
            limit=limit,
            enrich_detail=enrich_detail
            or normalize_text(os.environ.get("TIKTOK_SHOP_ENRICH_DETAIL")).lower() in {"1", "true", "yes"},
        )
        meta.update(clipcat_meta)

    if not products:
        return {
            "status": "skipped",
            "reason": "no-live-shop-source",
            "hint": "Set CLIPCAT_API_KEY + clipcat binary, or TIKTOK_SHOP_HTTP_URL, or provide competitor_products.json",
            "path": str(products_path(capture_root)),
            "meta": meta,
        }

    source = normalize_text(meta.get("provider")) or "live_sync"
    if is_verified_attestation(attestation) and meta.get("response_source"):
        source = f"verified_{source}"
    path = save_products(capture_root, products[:limit], source=source, meta=meta)
    return {
        "status": "ok",
        "source": source,
        "product_count": len(products[:limit]),
        "path": str(path),
        "meta": meta,
    }
