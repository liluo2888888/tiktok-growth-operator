# 命令映射（Command Map）

这份文档是当前包里最短的 Clipcat 对标命令索引。

如果你要看 Codex 原生可直接执行的命令，请优先读 [direct-use.md](direct-use.md)。只有在你需要公开 `clipcat` 命令名、主要参数和安全处理模式时，再看这份文件。

信息来源快照：

- installer shell script fetched on `2026-05-04`
- `clipcat_windows_amd64.exe -h`
- subcommand help output captured locally on `2026-05-04`

## 全局说明

- binary name: `clipcat`
- env vars: `CLIPCAT_API_KEY`, `CLIPCAT_BASE_URL`
- default output: JSON
- install flow downloads both the binary and Clipcat's own `SKILL.md`

## 快速索引

### 只读分析

| Command | Primary use | Key flags | Notes |
| --- | --- | --- | --- |
| `search` | viral TikTok video search | `--query`, `--limit`, `--page`, `--region`, `--require-shop`, `--sort-by`, `--time-range` | good fit for Scene `01` / `03` style discovery |
| `search_items` | TikTok Shop product/category search | `--keyword`, `--region`, `--offset`, `--page-token` | relevant to Scene `06` parity only |
| `product_detail` | one product lookup | `--input`, `--region` | Shop-side detail lookup |
| `product_comment` | product review retrieval | `--input`, `--region`, `--page-start`, `--sort-rule`, `--filter-type`, `--filter-value` | Shop-side review evidence |
| `breakdown` | one video analysis job | `--url` | async, returns task ID, may hit cached result |
| `download` | TikTok/Douyin video download | no key flags captured here beyond input URL | signed URL output, still external-dependent |
| `user_videos` | account-level analytics | `--unique-id`, `--count`, `--max-cursor`, `--sec-user-id`, `--sort-type` | account feed analytics |

### 付费或生成类

这类命令必须先展示计划执行的命令，再获取确认。

| Command | Primary use | Key flags | Notes |
| --- | --- | --- | --- |
| `replicate` | reference-video-based product replication | `--url`, `--image*`, `--image-url*`, `--model`, `--duration`, `--size`, `--lang`, `--resolution`, `--character-id`, `--prompt` | async; TikTok/Douyin social URL costs one extra credit versus direct video URL |
| `product_video` | product-image-only video generation | `--image*`, `--image-url*`, `--model`, `--duration`, `--size`, `--lang`, `--resolution`, `--character-id`, `--prompt` | async |
| `image` | ecommerce or product image generation | `--prompt`, `--aspect-ratio`, `--image*`, `--image-url*` | async; prompt should include aspect hints too |

### 任务跟踪

| Command | Primary use | Key flags | Notes |
| --- | --- | --- | --- |
| `query_task` | poll one task | `--task-id`, `--type replicate|product|breakdown|download|image` | if no task ID is supplied, uses the latest local task |
| `list_tasks` | list server-side task history | `--type`, `--status`, `--limit`, `--page` | use for non-image task history |
| `list_images` | image-task history | no extra summary here | image history surface instead of `list_tasks` |

## 默认处理模式

1. 如果不确定，先看 `clipcat -h` 或子命令帮助。
2. 先判断请求属于只读分析还是付费生成。
3. 如果是付费类，必须先展示准确的计划命令并获得确认。
4. 再执行。
5. 如果是异步任务，返回 task ID 和轮询计划。
6. 后续跨轮使用 `query_task` 直到完成或失败。
