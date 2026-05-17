# 验证夹具说明

这个目录存放 `tiktok-growth-operator.skill` 的包内验证夹具。

## 目的

- 即使旧的 `tmp/` 运行目录被删掉，也能保持 validator 输入稳定
- 避免硬依赖 `E:\tiktok\TikMatrix\tmp\...` 这类外部可变目录
- 为导出、capture-pack、bridge 校验提供小而有代表性的证据切片

## 夹具分组

### `capture-packs/`

- 包内自带的 capture-pack 根目录，用于 capture-pack 工作流校验
- 当前主夹具：
  - `scene02-patrol-capture-pack/`
- 主要被这些脚本使用：
  - `scripts/validate_capture_pack_workflows.py`

### `captures/`

- 用于验证场景导入和报告渲染的代表性采集根目录
- 当前主夹具：
  - `tiktok-analysis-pack-smoke-20260423f/`
  - `tiktok-download-validated-20260423/`
  - `scene01-strong-inputs-pass/`
  - `scene18-19-multi-week-account/`
  - `scene18-matrix-multi-account/`
  - `scene18-matrix-divergent-account/`
  - `scene08-multi-product-home-goods-comments/`
  - `scene19-roi-multiwindow-account/`
- 主要被这些脚本使用：
  - `scripts/validate_capture_pack_workflows.py`
  - `scripts/validate_export_outputs.py`

### `reports/`

- 用于富导出校验和 operator-pack 生成的稳定 `scene-*.json` 报告夹具
- 当前夹具包括：
  - `scene-15-validation-scene15-capture.json`
  - `scene-17-validation-routed-capture.json`
- 主要被这些脚本使用：
  - `scripts/validate_export_outputs.py`
  - `scripts/validate_capture_pack_workflows.py`

### `tikmatrix/`

- 包内冻结的 TikMatrix 采集结果夹具副本
- 这些夹具来自真实 TikMatrix 运行，再被冻结到这里，保证验证可重复
- 当前夹具族包括：
  - `search-live-orange-cat/`
  - `topic-live-orangecat/`
  - `live-profile-posts-browser-batch/`
  - `comments-live-mrorangecat-paged/`
  - `skill-batch-download/`
  - 账号操作类夹具：
    - `live-newest-reply-final-2/`
    - `live-notice-multi-final-3/`
    - `live-following-requests-final/`
    - `live-following-list-final/`
    - `live-follower-list-final/`
    - `live-following-final/`
- 主要被这些脚本使用：
  - `scripts/validate_capture_pack_workflows.py`
  - `scripts/validate_tikmatrix_bridge.py`
  - `scripts/validate_tikmatrix_account_ops_bridge.py`

## 归属规则

- 夹具保持小而有代表性
- 优先使用包内夹具副本，不依赖 `tmp/` 或外部项目输出目录
- 不要手工修改生成型验证产物；只有当 validator 合同变化时，才从所属工作流刷新夹具
- 如果某个 validator 还需要兼容旧 fallback 路径，把它视为兼容层，而不是主测试路径

## 当前写入行为

- validators 应优先从这个目录读取
- 大多数 validator 运行时产物现在写到工作区本地的 `.codex-tmp/` 临时目录
- 只有被明确提升为 durable testdata 的长期证据，才应该落在这里

## 夹具到 Validator 映射

| Fixture Group | Primary Paths | Used By Validators | Purpose |
| --- | --- | --- | --- |
| `capture-packs/` | `capture-packs/scene02-patrol-capture-pack/` | `validate_capture_pack_workflows.py` | Patrol-to-teardown, capture-pack import, pack derivation |
| `captures/` | `captures/tiktok-analysis-pack-smoke-20260423f/`, `captures/tiktok-download-validated-20260423/` | `validate_capture_pack_workflows.py`, `validate_export_outputs.py` | Real TikTok capture-root import and export rendering |
| `captures/scene01-strong-inputs-pass/` | `aggregate_summary.json`, `aggregate_ranked_videos.json` | `validate_capture_pack_workflows.py` | Scene 01 positive gate validation where strong required inputs are present and Scene 03 handoff should be allowed |
| `captures/scene18-19-multi-week-account/` | `ranked_videos.json`, `summary.json`, `comments_sampled.json` | `validate_capture_pack_workflows.py` | Scene 18/19 multi-week compare-mode validation for weekly competitor review and self-account retro |
| `captures/scene18-matrix-multi-account/` | `ranked_videos.json`, `summary.json`, `comments_sampled.json` | `validate_capture_pack_workflows.py` | Scene 18 competitor-matrix validation with 3 accounts across 2 weeks |
| `captures/scene18-matrix-divergent-account/` | `ranked_videos.json`, `summary.json`, `comments_sampled.json` | `validate_capture_pack_workflows.py` | Scene 18 divergent matrix validation with one rising account, one declining account, and one likely-noise account |
| `captures/scene08-multi-product-home-goods-comments/` | `comments_sampled.json` | `validate_capture_pack_workflows.py` | Scene 08 non-beauty purchase-language validation for size-fit, packaging, return, authenticity, and durability signals |
| `captures/scene19-roi-multiwindow-account/` | `ranked_videos.json`, `summary.json`, `comments_sampled.json` | `validate_capture_pack_workflows.py` | Scene 19 self-account retro validation with ROI / conversion-proxy hints across two publish windows |
| `reports/` | `reports/scene-15-validation-scene15-capture.json`, `reports/scene-17-validation-routed-capture.json` | `validate_export_outputs.py`, `validate_capture_pack_workflows.py` | Stable scene-report fixtures for md/docx/xlsx rerender validation |
| `tikmatrix/search-live-orange-cat/` | `aggregate_ranked_videos.json`, `summary.json` | `validate_capture_pack_workflows.py`, `validate_tikmatrix_bridge.py` | Search-based Scene 01/02/03 and bridge inputs |
| `tikmatrix/topic-live-orangecat/` | `aggregate_ranked_videos.json`, `summary.json` | `validate_capture_pack_workflows.py`, `validate_tikmatrix_bridge.py` | Topic-based patrol inputs and mixed capture-pack validation |
| `tikmatrix/live-profile-posts-browser-batch/` | `profile_posts.json` families | `validate_tikmatrix_bridge.py` | Real account post bridge intake for multiple scenes |
| `tikmatrix/comments-live-mrorangecat-paged/` | `comments.json` | `validate_tikmatrix_bridge.py` | Comment-heavy bridge coverage for Scene 08 and related flows |
| `tikmatrix/skill-batch-download/` | `downloads.json` | `validate_tikmatrix_bridge.py` | Download-asset aware bridge coverage |
| `tikmatrix/live-newest-reply-final-2/`, `live-notice-multi-final-3/`, `live-following-requests-final/`, `live-following-list-final/`, `live-follower-list-final/`, `live-following-final/` | account-ops JSON exports | `validate_tikmatrix_account_ops_bridge.py` | Inbox, notice, following-request, and relationship-watch operator-pack validation |

## 临时运行目录策略

- validator 运行时目录应落在工作区本地的 `.codex-tmp/tgo-validate-*`
- 这些目录属于可丢弃执行产物，不是长期证据
- 只有 `scripts/validator_runtime.py` 应该负责创建 validator 临时父目录
- validators 应优先读取这里的 durable 夹具，只把派生出的临时产物写到 `.codex-tmp/`
- 包级保留和清理规则见 [`references/tmp-retention-policy.md`](../../references/tmp-retention-policy.md)

## 历史 `tmp/20260507_*` 策略

- 不要一条条手工删历史验证或检查产物
- `tiktok-growth-operator.skill/tmp/20260507_*` 默认视为历史证据，除非已经有更小、更稳的 durable 夹具被提升到当前目录
- 当某个历史运行反复被 validator 依赖时，只提升最小必要子集到 `testdata/validation/`，然后停止依赖旧 `tmp/` 根目录
- 当某个历史运行已经不再被依赖，就保持原样或通过明确脚本规则归档，不要用手工清理当维护模式
- 归一化修复走 `scripts/rerender_scene_outputs.py`，validator 临时目录清理由 `scripts/validator_runtime.py` 负责，这两件事不要混用
