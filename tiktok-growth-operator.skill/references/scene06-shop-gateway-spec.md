# Scene 06 Shop Gateway — 一页实施 Spec

目标：让 `tiktok-growth-operator.skill` 的 Scene 06 在 **不冒充官方** 的前提下，支持两种数据路径：

| 路径 | 声明 | 谁实现 |
|------|------|--------|
| **A. 结构化本地** | `unverified` / `tiktok_shop_structured` | 运营维护 `competitor_products.json` 或 `run_scene06.py --data-path structured` |
| **B. 官方网关** | `official` + HTTP `source` metadata 验真 | 你们自建 Gateway（背后 Partner OAuth 或 Research API） |

Skill 只消费 **B 的 HTTP 契约**；不在 skill 内保存 TikTok Client Secret。

---

## 1. 唯一必需端点

### `POST /v1/shop/products/search`

**用途**：按关键词/区域拉竞品 SKU 列表（Gateway 内部可映射为「店铺列表 + SKU 详情」或 Partner 搜索，Skill 不关心实现细节）。

#### Request

```http
POST /v1/shop/products/search HTTP/1.1
Host: your-gateway.internal.example
Authorization: Bearer <gateway-api-key>   # 可选；对应 TIKTOK_SHOP_HTTP_API_KEY
Content-Type: application/json
```

```json
{
  "keyword": "beauty",
  "region": "US",
  "limit": 10
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `keyword` | string | 是 | 运营搜索词；Gateway 可映射为类目/标签/内部 SKU 池 |
| `region` | string | 建议 | 如 `US`、`GB`；Research API 偏 EU 时需在网关内转换 |
| `limit` | int | 建议 | 默认 10，上限建议 50 |

#### Response `200`

```json
{
  "products": [
    {
      "product_id": "1738291000123456789",
      "title": "Velvet Lip Glaze - Rose Nude",
      "platform": "TikTok Shop",
      "price": "18.99",
      "rating": "4.6",
      "review_count": "842",
      "sales_signal": "12400",
      "url": "https://www.tiktok.com/shop/pdp/..."
    }
  ],
  "source": {
    "source_type": "official",
    "provider": "tiktok_shop_open_platform",
    "auth_mode": "merchant_oauth",
    "issuer": "tiktok",
    "gateway_id": "prod-gateway-01",
    "api_family": "partner_center",
    "scopes": ["product.read"],
    "fetched_at": "2026-05-17T12:00:00Z"
  }
}
```

#### Product 字段（Gateway → Skill 归一化）

| 字段 | 必填 | 说明 |
|------|------|------|
| `product_id` | 是 | 稳定主键 |
| `title` | 是 | 商品标题 |
| `platform` | 建议 | 默认 `TikTok Shop` |
| `price` | 建议 | 字符串即可，如 `18.99` |
| `rating` | 建议 | 如 `4.6` |
| `review_count` | 建议 | 评论量 |
| `sales_signal` | 建议 | 销量/热度 proxy |
| `url` | 建议 | PDP 链接 |

Skill 侧归一化：`scripts/clipcat_client.normalize_shop_product()`（`evidence_source` 由 skill 写入）。

---

## 2. `source` metadata 验真规则（代码已 enforce）

当 CLI 传入 `--shop-source-attestation official`（或 `authorized-partner` / `internal-gateway`）且 `--shop-require-verified-source` 时，**响应必须包含 `source` 对象**，且字段匹配下表，否则 **blocked**，不入库 `competitor_products.json`。

### `official`

| 字段 | 要求值 |
|------|--------|
| `source_type` | `official` |
| `provider` | `tiktok_shop_open_platform` |
| `auth_mode` | `merchant_oauth` |

### `authorized-partner`

| 字段 | 要求值 |
|------|--------|
| `source_type` | `authorized-partner` |
| `provider` | `tiktok_shop_open_platform` |
| `auth_mode` | `partner_oauth` **或** `authorized_partner` **或** `merchant_oauth` |

### `internal-gateway`

| 字段 | 要求值 |
|------|--------|
| `source_type` | `internal-gateway` |
| `provider` | `internal-gateway` **或** `tiktok_shop_open_platform` |
| `auth_mode` | `service_account` **或** `internal_token` **或** `merchant_oauth` **或** `partner_oauth` |

可选：`issuer` 若出现，须为 `tiktok` / `bytedance` / `tiktok_shop` 之一。

实现位置：`scripts/tiktok_shop_source.validate_source_metadata()`。

---

## 3. 错误响应（Gateway 建议）

| HTTP | body.error | Skill 行为 |
|------|------------|------------|
| 401 | `unauthorized` | sync 失败，不写入 |
| 403 | `forbidden` | 同上 |
| 503 | `official_credentials_not_configured` | 参考 `tiktok_shop_official_gateway.py` |
| 502 | `official_query_failed` | 同上 |

---

## 4. 域名白名单（可选加固）

```text
TIKTOK_SHOP_HTTP_ALLOWED_HOSTS=your-gateway.internal.example,open.tiktokapis.com
```

或 CLI：`--shop-http-allowed-hosts "your-gateway.internal.example"`

---

## 5. Skill 调用方式

### 路径 A — 结构化（无 Gateway）

```powershell
python scripts/run_scene06.py `
  --capture-root "D:\path\capture-pack" `
  --data-path structured `
  --seed-mode fixture
```

写入：`competitor_products.json`，`source_attestation=unverified`，`data_source_mode=tiktok_shop_structured`。

### 路径 B — 官方 Gateway

**终端 A**（Gateway 进程，推荐 FastAPI）：

```powershell
cd tiktok-growth-operator.skill
python scripts/run_shop_gateway.py --install-deps --port 8791
# Partner token / Research key 只设在网关进程环境，勿写入 skill 仓库
```

备选（stdlib，无 FastAPI）：`python scripts/tiktok_shop_official_gateway.py --port 8791`

实现代码：`services/shop_gateway/app.py` · Partner 签名客户端：`scripts/tiktok_shop_partner_client.py` · 运行说明：`services/shop_gateway/README.md`

Partner 本地 mock（无 TikTok 凭证）：

```powershell
$env:SHOP_GATEWAY_PARTNER_MOCK = "1"
$env:SHOP_GATEWAY_BACKEND = "partner"
python scripts/run_shop_gateway.py --port 8791
```

**终端 B**（Scene 06）：

```powershell
python scripts/run_scene06.py `
  --capture-root "D:\path\capture-pack" `
  --data-path official `
  --shop-http-url "http://127.0.0.1:8791" `
  --shop-source-attestation official `
  --shop-require-verified-source `
  --shop-http-allowed-hosts "127.0.0.1"
```

成功产物：

- `competitor_products.json`
- `tiktok_shop_source_meta.json`（含 `response_source`、`source_metadata_validation.ok: true`）
- 报告内 `data_source_mode`: `tiktok_shop_verified_http`（或 `verified_<provider>`）

---

## 6. Gateway 背后推荐实现（你们侧）

| 后端 | 官方文档 | 适合 Scene 06 的方式 |
|------|----------|----------------------|
| **Partner Center** | https://partner.tiktokshop.com/doc | 内置客户端 `scripts/tiktok_shop_partner_client.py` → `POST /product/{version}/products/search`（授权店铺目录，非全网竞品搜索） |
| **Research API** | https://developers.tiktok.com/products/research-api | `POST /v2/research/tts/shop/` 按 `shop_name`；**不能**替代 keyword 全网搜索 |
| **本地 structured** | N/A | 运营 Excel/飞书 → 导出 JSON，声明 `unverified` |

参考客户端：`scripts/tiktok_shop_official_client.py`（Research shop 查询 + OAuth token）。

---

## 7. 最小验收清单

- [ ] `POST /v1/shop/products/search` 返回 ≥1 条 `products`，字段齐全
- [ ] `source` 块在 `official`  attestation 下通过 skill 验真
- [ ] 去掉 `source` 时 skill 返回 `invalid-source-metadata`，且不写 `competitor_products.json`
- [ ] `python scripts/run_scene06.py --data-path structured` → `tiktok_shop_structured`
- [ ] `python scripts/validate_platform_integrations.py` 通过

---

## 8. 环境变量速查

可复制模板（勿提交真实密钥）：`services/shop_gateway/.env.example` → 复制为同目录 `.env`。

```text
# Skill → Gateway
TIKTOK_SHOP_HTTP_URL=https://your-gateway.example
TIKTOK_SHOP_HTTP_API_KEY=...
TIKTOK_SHOP_SOURCE_ATTESTATION=official|authorized-partner|internal-gateway|unverified
TIKTOK_SHOP_REQUIRE_VERIFIED=1
TIKTOK_SHOP_HTTP_ALLOWED_HOSTS=your-gateway.example

# Gateway → TikTok（仅网关进程，勿写入 skill repo）
TIKTOK_RESEARCH_CLIENT_KEY=...
TIKTOK_RESEARCH_CLIENT_SECRET=...
TIKTOK_RESEARCH_ACCESS_TOKEN=...
TIKTOK_SHOP_NAME=...          # Research：按店名查
TIKTOK_SHOP_ACCESS_TOKEN=...  # Partner：merchant OAuth token
```

---

## 9. 不在本 Spec 范围内

- Cursor / MCP 渲染后端（Scene 09–16 另见 `GENERATION_RENDERER_URL`）
- Clipcat CLI（第三方，默认 `unverified`）
- 全网竞品自动发现（需你们网关或运营流程定义，非 TikTok 公开 API）
