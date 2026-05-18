# Scene 06 Shop Gateway (FastAPI)

Minimal HTTP gateway for `tiktok-growth-operator.skill` Scene 06.

Spec: [references/scene06-shop-gateway-spec.md](../../references/scene06-shop-gateway-spec.md)

## Environment template

```powershell
copy services\shop_gateway\.env.example services\shop_gateway\.env
# Edit .env with your Partner / Research credentials (never commit .env)
```

Load into the current PowerShell session before starting the gateway:

```powershell
cd services\shop_gateway
Get-Content .env | ForEach-Object {
  if ($_ -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$') {
    Set-Item -Path "env:$($matches[1])" -Value $matches[2].Trim('"')
  }
}
cd ..\..
```

For local E2E without TikTok credentials, keep `SHOP_GATEWAY_PARTNER_MOCK=1` in `.env`.

### Internal forward preset (shop-bridge / 内网转发)

If TikTok Partner signing lives in your own service—not in this repo—use:

```powershell
copy services\shop_gateway\.env.internal-forward.example services\shop_gateway\.env
```

Then set:

- `SHOP_GATEWAY_PARTNER_SEARCH_URL` — your internal `POST` search endpoint
- `TIKTOK_SHOP_ACCESS_TOKEN` — merchant OAuth token (gateway process only)
- `TIKTOK_SHOP_SOURCE_ATTESTATION=internal-gateway` on the Skill side

The preset file documents the upstream JSON contract and verification checklist.

## Install and run

```powershell
cd "d:\path\tiktok-growth-operator.skill"
python scripts/run_shop_gateway.py --install-deps --port 8791
```

## Backends (`SHOP_GATEWAY_BACKEND`)

| Value | Behavior |
|-------|----------|
| `auto` | partner (mock / Open API / forward URL) → research → structured JSON |
| `partner` | See partner modes below |
| `research` | `TIKTOK_RESEARCH_CLIENT_KEY/SECRET` or `TIKTOK_RESEARCH_ACCESS_TOKEN` |
| `structured` | `SHOP_GATEWAY_STRUCTURED_JSON` (dev fallback) |

### Partner modes (priority order)

1. **Mock** — `SHOP_GATEWAY_PARTNER_MOCK=1`  
   Reads `testdata/validation/partner_search_mock_response.json` for local E2E without TikTok credentials.

2. **Custom forward** — `SHOP_GATEWAY_PARTNER_SEARCH_URL` + `TIKTOK_SHOP_ACCESS_TOKEN`  
   POST `{keyword, region, limit}` to your internal service; response must include `products[]`.

3. **Open API (built-in)** — Partner Center signing client  
   Requires all of:

```text
TIKTOK_SHOP_APP_KEY=...
TIKTOK_SHOP_APP_SECRET=...
TIKTOK_SHOP_CIPHER=...
TIKTOK_SHOP_ACCESS_TOKEN=...
# optional:
TIKTOK_SHOP_API_VERSION=202309
TIKTOK_SHOP_OPEN_API_BASE=https://open-api.tiktokglobalshop.com
TIKTOK_SHOP_PARTNER_SEARCH_BODY_JSON={"page_size":20,"status":"ACTIVATE"}
```

Calls `POST /product/{version}/products/search` with HmacSHA256 signing (`scripts/tiktok_shop_partner_client.py`).

**Important:** Partner `products/search` returns the **authorized shop catalog**, not a global competitor keyword index. For competitor monitoring, maintain SKU IDs in structured JSON or map keyword filters in `TIKTOK_SHOP_PARTNER_SEARCH_BODY_JSON`.

## Scene 06 client

```powershell
# Official metadata (Research, Partner Open API, or Partner mock)
python scripts/run_scene06.py `
  --capture-root "D:\path\capture-pack" `
  --data-path official `
  --shop-http-url "http://127.0.0.1:8791" `
  --shop-source-attestation official `
  --shop-require-verified-source

# Partner mock local test
$env:SHOP_GATEWAY_PARTNER_MOCK = "1"
$env:SHOP_GATEWAY_BACKEND = "partner"
python scripts/run_shop_gateway.py --port 8791
```

Structured path (no gateway): `run_scene06.py --data-path structured`
