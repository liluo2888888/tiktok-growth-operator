from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

# Allow imports from tiktok-growth-operator.skill/scripts
_SKILL_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _SKILL_ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from tiktok_shop_official_client import (  # noqa: E402
    official_credentials_configured,
    official_source_metadata,
    search_official_products,
)
from tiktok_shop_partner_client import (  # noqa: E402
    partner_access_token,
    partner_configured,
    search_partner_products,
)
from text_normalization import normalize_text, read_json_file  # noqa: E402

app = FastAPI(
    title="TikTok Shop Gateway (Scene 06)",
    version="1.0.0",
    description="Minimal gateway for tiktok-growth-operator Scene 06. See references/scene06-shop-gateway-spec.md",
)


class ProductSearchRequest(BaseModel):
    keyword: str = Field(default="beauty", examples=["beauty"])
    region: str = Field(default="US", examples=["US"])
    limit: int = Field(default=10, ge=1, le=50)


class SourceMetadata(BaseModel):
    source_type: str
    provider: str
    auth_mode: str
    issuer: str = "tiktok"
    gateway_id: str = "shop-gateway-v1"
    api_family: str = ""
    scopes: list[str] = Field(default_factory=list)
    fetched_at: str = ""


class ProductSearchResponse(BaseModel):
    products: list[dict[str, Any]]
    source: SourceMetadata
    provider: str
    keyword: str
    region: str


def gateway_api_key() -> str:
    return normalize_text(os.environ.get("SHOP_GATEWAY_API_KEY")) or normalize_text(
        os.environ.get("TIKTOK_SHOP_HTTP_API_KEY")
    )


def gateway_backend() -> str:
    return normalize_text(os.environ.get("SHOP_GATEWAY_BACKEND")).lower() or "auto"


def require_gateway_auth(authorization: str | None = Header(default=None)) -> None:
    expected = gateway_api_key()
    if not expected:
        return
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing_bearer_token")
    token = authorization.split(" ", 1)[1].strip()
    if token != expected:
        raise HTTPException(status_code=401, detail="invalid_bearer_token")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_source(*, auth_mode: str, api_family: str, source_type: str = "official") -> SourceMetadata:
    meta = official_source_metadata(auth_mode=auth_mode)
    return SourceMetadata(
        source_type=source_type,
        provider=meta["provider"],
        auth_mode=auth_mode,
        issuer=meta.get("issuer", "tiktok"),
        gateway_id=normalize_text(os.environ.get("SHOP_GATEWAY_ID")) or "shop-gateway-v1",
        api_family=api_family,
        scopes=[s.strip() for s in normalize_text(os.environ.get("SHOP_GATEWAY_SCOPES")).split(",") if s.strip()],
        fetched_at=utc_now_iso(),
    )


def load_structured_fallback(limit: int) -> list[dict]:
    path = normalize_text(os.environ.get("SHOP_GATEWAY_STRUCTURED_JSON"))
    if not path:
        default = _SKILL_ROOT / "testdata" / "validation" / "captures" / "scene01-strong-inputs-pass" / "competitor_products.json"
        path = str(default) if default.exists() else ""
    if not path or not Path(path).exists():
        return []
    payload = read_json_file(Path(path))
    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)][:limit]


def fetch_via_research(*, keyword: str, region: str, limit: int) -> tuple[list[dict], SourceMetadata]:
    os.environ.setdefault("TIKTOK_SHOP_NAME", keyword)
    result = search_official_products(keyword=keyword, region=region, limit=limit)
    if not result.get("ok"):
        raise HTTPException(status_code=502, detail={"error": "official_query_failed", "detail": result})
    products = result.get("products") or []
    source_dict = result.get("source") if isinstance(result.get("source"), dict) else {}
    auth_mode = normalize_text(source_dict.get("auth_mode")) or "research_client_credentials"
    return products, build_source(auth_mode=auth_mode, api_family="research_api")


def partner_mock_enabled() -> bool:
    return normalize_text(os.environ.get("SHOP_GATEWAY_PARTNER_MOCK")).lower() in {"1", "true", "yes", "on"}


def fetch_via_partner_mock(*, keyword: str, limit: int) -> tuple[list[dict], SourceMetadata]:
    mock_path = _SKILL_ROOT / "testdata" / "validation" / "partner_search_mock_response.json"
    payload = read_json_file(mock_path)
    rows = []
    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, dict) and isinstance(data.get("products"), list):
            rows = [item for item in data["products"] if isinstance(item, dict)]
    from tiktok_shop_partner_client import normalize_partner_product, filter_products_by_keyword  # noqa: WPS433

    products = filter_products_by_keyword([normalize_partner_product(row) for row in rows], keyword)[:limit]
    return products, build_source(auth_mode="merchant_oauth", api_family="partner_center_mock")


def fetch_via_partner_forward(*, keyword: str, region: str, limit: int) -> tuple[list[dict], SourceMetadata]:
    token = partner_access_token()
    if not token:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "partner_token_not_configured",
                "hint": "Set TIKTOK_SHOP_ACCESS_TOKEN in the gateway process only.",
            },
        )
    partner_url = normalize_text(os.environ.get("SHOP_GATEWAY_PARTNER_SEARCH_URL"))
    if not partner_url:
        raise HTTPException(
            status_code=501,
            detail={
                "error": "partner_forward_url_missing",
                "hint": "Set SHOP_GATEWAY_PARTNER_SEARCH_URL for custom forward mode.",
            },
        )
    import urllib.error
    import urllib.request

    payload = json.dumps({"keyword": keyword, "region": region, "limit": limit}, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        partner_url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise HTTPException(status_code=502, detail={"error": "partner_upstream_failed", "status": exc.code, "detail": detail}) from exc

    items = body.get("products") if isinstance(body, dict) else body
    if not isinstance(items, list):
        items = []
    upstream_source = body.get("source") if isinstance(body, dict) else None
    if isinstance(upstream_source, dict) and normalize_text(upstream_source.get("source_type")):
        source = SourceMetadata(
            source_type=normalize_text(upstream_source.get("source_type")) or "internal-gateway",
            provider=normalize_text(upstream_source.get("provider")) or "internal-gateway",
            auth_mode=normalize_text(upstream_source.get("auth_mode")) or "service_account",
            issuer=normalize_text(upstream_source.get("issuer")) or "tiktok",
            gateway_id=normalize_text(upstream_source.get("gateway_id"))
            or normalize_text(os.environ.get("SHOP_GATEWAY_ID"))
            or "shop-gateway-v1",
            api_family=normalize_text(upstream_source.get("api_family")) or "partner_forward",
            scopes=upstream_source.get("scopes") if isinstance(upstream_source.get("scopes"), list) else [],
            fetched_at=normalize_text(upstream_source.get("fetched_at")) or utc_now_iso(),
        )
        return items[:limit], source
    return items[:limit], build_source(
        auth_mode="service_account",
        api_family="partner_forward",
        source_type="internal-gateway",
    )


def fetch_via_partner_open_api(*, keyword: str, region: str, limit: int) -> tuple[list[dict], SourceMetadata]:
    del region
    result = search_partner_products(keyword=keyword, region="", limit=limit)
    if not result.get("ok"):
        raise HTTPException(status_code=502, detail={"error": "partner_open_api_failed", "detail": result})
    return (result.get("products") or [])[:limit], build_source(auth_mode="merchant_oauth", api_family="partner_center")


def fetch_via_partner(*, keyword: str, region: str, limit: int) -> tuple[list[dict], SourceMetadata]:
    if partner_mock_enabled():
        return fetch_via_partner_mock(keyword=keyword, limit=limit)
    if normalize_text(os.environ.get("SHOP_GATEWAY_PARTNER_SEARCH_URL")):
        return fetch_via_partner_forward(keyword=keyword, region=region, limit=limit)
    return fetch_via_partner_open_api(keyword=keyword, region=region, limit=limit)


def resolve_backend() -> str:
    mode = gateway_backend()
    if mode != "auto":
        return mode
    if partner_mock_enabled() or partner_configured() or (
        partner_access_token() and normalize_text(os.environ.get("SHOP_GATEWAY_PARTNER_SEARCH_URL"))
    ):
        return "partner"
    if official_credentials_configured():
        return "research"
    if load_structured_fallback(1):
        return "structured"
    return "none"


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "backend": resolve_backend(),
        "official_credentials_configured": official_credentials_configured(),
        "partner_token_configured": bool(partner_access_token()),
        "partner_open_api_configured": partner_configured(),
        "partner_mock": partner_mock_enabled(),
    }


@app.post("/v1/shop/products/search", response_model=ProductSearchResponse)
def search_products(
    body: ProductSearchRequest,
    _: None = Depends(require_gateway_auth),
) -> ProductSearchResponse:
    keyword = normalize_text(body.keyword) or "beauty"
    region = normalize_text(body.region) or "US"
    limit = body.limit

    backend = resolve_backend()
    if backend == "research":
        products, source = fetch_via_research(keyword=keyword, region=region, limit=limit)
        provider = "tiktok_research_api"
    elif backend == "partner":
        products, source = fetch_via_partner(keyword=keyword, region=region, limit=limit)
        provider = "tiktok_shop_partner_api"
    elif backend == "structured":
        products = load_structured_fallback(limit)
        if not products:
            raise HTTPException(status_code=503, detail={"error": "structured_fallback_empty"})
        source = SourceMetadata(
            source_type="internal-gateway",
            provider="tiktok_shop_open_platform",
            auth_mode="service_account",
            issuer="tiktok",
            gateway_id=normalize_text(os.environ.get("SHOP_GATEWAY_ID")) or "shop-gateway-v1",
            api_family="structured_fallback",
            fetched_at=utc_now_iso(),
        )
        provider = "structured_fallback"
    else:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "official_credentials_not_configured",
                "hint": (
                    "Set TIKTOK_RESEARCH_CLIENT_KEY/SECRET, TIKTOK_SHOP_ACCESS_TOKEN, "
                    "or SHOP_GATEWAY_BACKEND=structured with SHOP_GATEWAY_STRUCTURED_JSON."
                ),
                "docs": [
                    "https://developers.tiktok.com/products/research-api",
                    "https://partner.tiktokshop.com/doc",
                ],
            },
        )

    return ProductSearchResponse(
        products=products,
        source=source,
        provider=provider,
        keyword=keyword,
        region=region,
    )
