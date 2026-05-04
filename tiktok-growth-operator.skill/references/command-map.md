# Command Map

This file captures the public `clipcat` CLI surface that this skill can orchestrate.

Source of truth snapshot:

- installer shell script fetched on `2026-05-04`
- `clipcat_windows_amd64.exe -h`
- subcommand help output captured locally on `2026-05-04`

## Global Notes

- binary name: `clipcat`
- API key env: `CLIPCAT_API_KEY`
- base URL env: `CLIPCAT_BASE_URL`
- default output: JSON
- install flow downloads both the binary and Clipcat's own `SKILL.md`

## Read-Only / Analysis Commands

### `search`

Use for viral TikTok video search.

Key flags:

- `--query`
- `--limit`
- `--page`
- `--region`
- `--require-shop`
- `--sort-by relevance|likes`
- `--time-range any|day|week|month|quarter|half_year`

### `search_items`

Use for TikTok Shop product/category search.

Key flags:

- `--keyword`
- `--region`
- `--offset`
- `--page-token`

### `product_detail`

Use for one product lookup.

Key flags:

- `--input <product_id_or_url>`
- `--region`

### `product_comment`

Use for product review retrieval.

Key flags:

- `--input <product_id_or_url>`
- `--region`
- `--page-start`
- `--sort-rule`
- `--filter-type 1|2|3`
- `--filter-value 6|5|4|3|2|1`

### `breakdown`

Use for one video analysis job.

Key flags:

- `--url`

Behavior:

- async
- returns task ID
- cached result can be returned immediately on re-analysis

### `download`

Use for TikTok/Douyin video download.

Behavior:

- signed URL output
- still treat as external-dependent and potentially async-adjacent in user communication

### `user_videos`

Use for account-level analytics.

Key flags:

- `--unique-id`
- `--count`
- `--max-cursor`
- `--sec-user-id`
- `--sort-type 0|1`

## Paid / Generation Commands

Always show the user the planned command first and get confirmation.

### `replicate`

Use for reference-video-based product replication.

Key flags:

- `--url`
- `--image` repeatable
- `--image-url` repeatable
- `--model veo3.1fast|grok_imagine|sora2_official_exp`
- `--duration`
- `--size`
- `--lang`
- `--resolution`
- `--character-id`
- `--prompt`

Important behavior:

- async
- TikTok/Douyin social URL costs 1 extra credit versus direct video URL
- default prompt tries to keep script/visual logic while replacing the product

### `product_video`

Use for product-image-only video generation.

Key flags:

- `--image` repeatable
- `--image-url` repeatable
- `--model`
- `--duration`
- `--size`
- `--lang`
- `--resolution`
- `--character-id`
- `--prompt`

Behavior:

- async

### `image`

Use for e-commerce or product image generation.

Key flags:

- `--prompt`
- `--aspect-ratio 1:1|16:9|9:16`
- `--image` repeatable
- `--image-url` repeatable

Behavior:

- async
- the prompt should also include aspect hints, not only the flag

## Task Tracking Commands

### `query_task`

Use to poll one task.

Key flags:

- `--task-id`
- `--type replicate|product|breakdown|download|image`

Behavior:

- if no task ID is given, uses the latest local task automatically

### `list_tasks`

Use to list server-side task history.

Key flags:

- `--type replicate|product|breakdown|download`
- `--status pending|processing|completed|failed|cancelled`
- `--limit`
- `--page`

### `list_images`

Use for image task history rather than `list_tasks`.

## Default Command Handling Pattern

1. inspect with `clipcat -h` or subcommand help if uncertain
2. decide whether the request is read-only or paid
3. if paid, show planned command and request confirmation
4. execute
5. if async, return task ID and polling plan
6. use `query_task` across turns until completed or failed
