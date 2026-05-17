# 最终交接（Final Handoff）

把这份文档当作已完成的 Codex 原生 TikTok Growth Operator 包的最短 durable 入口。

## 已完成内容

这个包当前已经提供：

- one unified Codex-native operator surface across 19 scenes
- a real Scene `02` patrol runtime with persisted snapshot, delta, alert, and Scene `03` handoff outputs
- real TikTok capture-pack ingestion for supported scenes
- real TikMatrix inbox and relationship ingestion for account-ops packs
- durable report rendering to `md`, `docx`, and `xlsx`
- one shared text-normalization layer across the main scene, goal, project, bridge, and renderer entrypoints
- derived `publish-prep`, `live-assist`, `creative-production-handoff`, and `account-ops-assist` handoff packs where appropriate
- repeatable validation for scene presets, capture-pack workflows, export quality, and core skill docs
- one transparent entry selector for choosing among single/combo/vertical/launch/manager/cadence boards
- one unified `board` entry mode that can scaffold a local starter folder from the main operator router

## 参考文档分工

按角色阅读参考文档：

- `final-handoff.md`：最短完成态摘要和推荐入口
- `direct-use.md`：面向操作者的命令手册
- `automation-workflows.md`：脚本归属与自动化行为说明
- `batch-presets.md`：preset 队列生成和 suite 导出说明
- `entry-selector.md`：在生成队列前该选哪个 board family 和 slug
- `command-map.md`：最短命令索引和公开 Clipcat 对标说明
- `clipcat-openclaw-parity-audit.md`：对公开 Clipcat / OpenClaw 材料的完整 / 部分 / 缺失对标状态
- `account-ops-assist-pack.md`：对收件箱、通知和关系监控操作面的安全替代
- `rpa-and-account-farming-doc-only.md`：云手机、RPA、`养号` 等企业级话题的只文档边界
- `tmp-retention-policy.md`：历史 `tmp/` 与 `.codex-tmp/` 的保留和清理规则

优先用 `direct-use.md` 获取可直接复制的命令。只有在你需要 batch JSON 契约、rerun 语义或这些命令背后的 validator 行为时，再读 `automation-workflows.md`。

## 推荐入口

优先使用这些入口。

### 一次性真实 TikTok capture run

```powershell
python scripts/start_capture_pack_run.py `
  --scene 17 `
  --capture-root "D:\path\tiktok-analysis-pack-smoke-20260423f" `
  --name tiktok-official-capture-run `
  --project "TikTok Official Account Creator Distillation" `
  --platform TikTok `
  --market US
```

### 统一 operator 路由入口

```powershell
python scripts/run_operator_workflow.py `
  --request "Run scene 03 for morning makeup hooks and output a teardown report" `
  --project "Morning Makeup Hook Teardown"
```

### Board 选择器

```powershell
python scripts/recommend_entry_board.py `
  --query "Set up my weekly competitor review" `
  --format markdown
```

### 一步式 starter 脚手架

```powershell
python scripts/start_entry_board.py `
  --query "Give me a daily board for TikTok beauty ops"
```

统一路由版本：

```powershell
python scripts/run_operator_workflow.py `
  --mode board `
  --query "Give me a daily board for TikTok beauty ops"
```

预览版本：

```powershell
python scripts/start_entry_board.py `
  --query "Give me a daily board for TikTok beauty ops" `
  --generate `
  --dry-run
```

如果你不想使用自动发现，而是要锁定某个 bundle：

```powershell
python scripts/recommend_entry_board.py `
  --query "Give me a daily board" `
  --bundle-root "D:\path\preset-template-bundle" `
  --format markdown
```

更多 board family 示例和选择规则见 [entry-selector.md](entry-selector.md)。

### 完整 durable 验证

```powershell
python scripts/validate_all_workflows.py
```

### 历史 scene 导出修复

```powershell
python scripts/rerender_scene_outputs.py `
  --root ".\tiktok-growth-operator.skill\tmp" `
  --formats md
```

### 真实 TikMatrix bridge 验证

```powershell
python scripts/validate_tikmatrix_bridge.py
```

### 真实 TikMatrix account-ops bridge 验证

```powershell
python scripts/validate_tikmatrix_account_ops_bridge.py
```

## 导出质量状态

当前 `docx` 导出质量已包括：

- cover page with deliverable banner and metadata block
- table of contents field
- section overview with internal links
- explicit section return links back to contents and overview
- repeated table headers for long tables
- image captions for embedded asset previews
- shared execution-template and operator-guide blocks rendered from the normalized scene-report contract

当前 `xlsx` 导出质量已包括：

- `Summary`, `Section Overview`, and `Section Index`
- stable section-sheet naming even when headings repeat
- native Excel tables on key sheets
- top-line volume dashboard cards
- second-line quality status cards for empty sections and missing evidence/assets
- section-to-index and index-to-section navigation links
- sheet-specific width and row-height tuning for `Summary`, `Evidence`, and `Assets` heavy-text cases

当前编码 / 输出层已包括：

- shared UTF-8 normalization for JSON/text reads
- UTF-8 BOM Markdown/text writes for Windows-friendly open behavior
- common mojibake cleanup for historical cp1252-style artifacts before rendering
- historical scene-report repair through `scripts/rerender_scene_outputs.py`

## 验证覆盖面

durable 验证层包括：

- `scripts/validate_skill_docs.py`
- `scripts/validate_scene_presets.py`
- `scripts/validate_capture_pack_workflows.py`
- `scripts/validate_export_outputs.py`
- `scripts/validate_all_workflows.py`

`validate_export_outputs.py` 当前覆盖：

- representative real TikTok reports
- synthetic duplicate-heading and sparse-section edge cases

`validate_all_workflows.py` 当前覆盖：

- board preview routing and preview-field assertions inside batch mode
- one hermetic board execute smoke that scaffolds a starter, generates a queue, and performs board-local dry-run output checks
- a hermetic Scene `04` single-video runtime smoke through `run_tikmatrix_single_video_scene.py` using a frozen local download fixture
- route regressions for weekly-review, Chinese cadence-board, hybrid vertical-cadence-board, and multi-stage goal requests
- long free-text goal routing with bounded `run_name` output for safer Windows path lengths

## 真实验证夹具

当前最强的真实 TikTok 验证输入包括：

- ranked/account pack: `captures/tiktok-analysis-pack-smoke-20260423f`
- comment-bearing pack: `captures/tiktok-download-validated-20260423`
- richer real collector export for authority-led packaging: `E:\tiktok\TikMatrix\tmp\codex-mustsharenews-profile-post-downloads-20260507\mustsharenews`
- richer real collector export for creator-native hooks: `E:\tiktok\TikMatrix\tmp\codex-sherrinandyixi-profile-post-downloads-20260507\sherrinandyixi`
- restored original-runtime smoke export: `E:\tiktok\TikMatrix\tmp\codex-smoke-mustsharenews-browser-venv-20260507`
- restored original-runtime download export: `E:\tiktok\TikMatrix\tmp\codex-mustsharenews-profile-post-downloads-venv-20260507\mustsharenews`
- real external collector bridge source: `E:\tiktok\TikMatrix\tmp\live-profile-posts-browser-batch\mrorangecat555\profile_posts.json`
- real external collector bridge comment source: `E:\tiktok\TikMatrix\tmp\comments-live-mrorangecat-paged\7624057229930450192\comments.json`
- real external collector bridge downloads source: `E:\tiktok\TikMatrix\tmp\skill-batch-download\downloads.json`
- real scene coverage already confirmed from TikMatrix bridge:
  - scenes `01` and `03` from `mustsharenews`
  - scenes `01` and `03` from `sherrinandyixi`
  - scenes `04`, `05`, `07`, `08`, `09`, `10`, `11`, `12`, `13`, `14`, `15`, `16`, `17`, `18`, `19`
- real account-ops bridge sources:
  - `E:\tiktok\TikMatrix\tmp\live-newest-reply-final-2\newest-reply\newest_reply.json`
  - `E:\tiktok\TikMatrix\tmp\live-notice-multi-final-3\notice-multi\notice_multi.json`
  - `E:\tiktok\TikMatrix\tmp\live-following-requests-final\following-requests\following_request_list.json`
  - `E:\tiktok\TikMatrix\tmp\live-following-list-final\following\following_list.json`
  - `E:\tiktok\TikMatrix\tmp\live-follower-list-final\followers\follower_list.json`
  - `E:\tiktok\TikMatrix\tmp\live-following-final\live-following\live_following.json`
- representative real bridge output roots:
  - `tiktok-growth-operator.skill/tmp/20260507_010741-tikmatrix-bridge-mustsharenews-scene01-real-rerun`
  - `tiktok-growth-operator.skill/tmp/20260507_010740-tikmatrix-bridge-mustsharenews-scene03-real-rerun`
  - `tiktok-growth-operator.skill/tmp/20260507_010741-tikmatrix-bridge-sherrinandyixi-scene01-real-rerun`
  - `tiktok-growth-operator.skill/tmp/20260507_010741-tikmatrix-bridge-sherrinandyixi-scene03-real-rerun`
  - `tiktok-growth-operator.skill/tmp/20260507_014554-tikmatrix-bridge-mustsharenews-scene01-venv-restored`
  - `tiktok-growth-operator.skill/tmp/20260507_014554-tikmatrix-bridge-mustsharenews-scene03-venv-restored`
  - `tiktok-growth-operator.skill/tmp/20260507_002608-tikmatrix-bridge-mrorangecat-scene11`
  - `tiktok-growth-operator.skill/tmp/20260507_002609-tikmatrix-bridge-mrorangecat-scene12`
  - `tiktok-growth-operator.skill/tmp/20260507_002608-tikmatrix-bridge-mrorangecat-scene13`
  - `tiktok-growth-operator.skill/tmp/20260507_002608-tikmatrix-bridge-mrorangecat-scene14`
  - `tiktok-growth-operator.skill/tmp/20260507_002639-tikmatrix-bridge-mrorangecat-scene15`
  - `tiktok-growth-operator.skill/tmp/20260507_002639-tikmatrix-bridge-mrorangecat-scene16`
  - `tiktok-growth-operator.skill/tmp/20260507_002639-tikmatrix-bridge-mrorangecat-scene18`
  - `tiktok-growth-operator.skill/tmp/20260507_002641-tikmatrix-bridge-mrorangecat-scene19`
  - `tiktok-growth-operator.skill/tmp/20260507_validate_tikmatrix_account_ops_bridge`

Representative export validation outputs:

- `.codex-tmp/tgo-validate-all-*`
- `.codex-tmp/tgo-validate-export-*`
- package-local rerender summaries written only when explicitly requested

历史 rerender 状态：

- workflow-family rerender coverage is effectively closed for discovered `20260505_*goal-workflow`, `20260505_*goal-goal-workflow`, `20260505_*build-a-full-douyin-workflow-from-topic-selectio`, `20260506_*`, and `20260507_*` scene-report workspaces
- the only uncovered workflow-family directory from reconciliation is `20260505_014318-goal-build-a-full-douyin-workflow-from-topic-selection-to-publish-handoff`
- that directory is not a real export gap because it contains no canonical `scene-*.json`

validator 与历史运行清理策略：

- validator 运行目录统一放在 `.codex-tmp/tgo-validate-*`
- 历史 `tiktok-growth-operator.skill/tmp/2026050*_...` 根目录仍作为证据保留，不作为主验证 fixture
- durable 清理规则以 [tmp-retention-policy.md](tmp-retention-policy.md) 为准

## 推荐操作顺序

1. Pick `run_operator_workflow.py` for normal use.
2. Use `run_operator_workflow.py --mode board` when the request is role-first, cadence-first, outcome-first, or vertical-first.
3. Use `start_capture_pack_run.py` when a real TikTok capture folder already exists.
4. Prefer the original `E:\tiktok\TikMatrix\.venv` runtime when you need to collect fresh real TikTok account data.
5. Use `run_tikmatrix_capture_bridge.py` when the collection already exists in `E:\tiktok\TikMatrix` and you need operator outputs without changing the collector.
6. Use `clipcat-openclaw-parity-audit.md` when you need the exact replication status instead of only the runnable commands.
7. Use `run_tikmatrix_account_ops_bridge.py` when the collection already exists in `E:\tiktok\TikMatrix` and you need inbox, notice, or relationship-watch operator outputs without changing the collector.
8. Use `validate_tikmatrix_bridge.py` after changing the capture-pack bridge path.
9. Use `validate_tikmatrix_account_ops_bridge.py` after changing the account-ops bridge path.
10. Use `validate_all_workflows.py` after durable script or rendering changes.
11. Use `validate_export_outputs.py` when the change is export-only.

## 当前边界

这个包仍然不宣称支持：

- platform API automation without credentials
- direct publishing
- fake engagement or account-farming behavior
- fabricated OCR or translated image copy in scene `15`
- unsupported data extraction from capture packs that do not contain the needed evidence

## P3 收口状态（2026-05-17）

已完成：

1. docs and operator guidance cleanup — `direct-use.md`、`command-map.md`、本文件与 `creative-production-handoff-pack.md` 对齐当前入口与创意场景导出行为
2. downstream renderer hooks for scenes `09` to `16` — `render_scene_report.py` 为创意简报场景与矩阵场景增加封面 spotlight、章节动作卡和表格版式
3. route-eval expansion and fixture hardening — `references/route-eval-fixtures.json` 扩充 scene / pack / board 语料；`testdata/validation/reports/scene-11-pipeline-scaffold.json` 进入导出验证

4. delivery adapters and operator push surfaces — `scripts/deliver_operator_run.py` 支持 `local-bundle` 与 `feishu`；`start_scene_run.py --deliver` 已接入；`validate_delivery_adapters.py` 已纳入全量验证
5. visual-only export polish — 场景 `09` 到 `16` 的 DOCX / XLSX 封面主题色与项目卡 kicker 已区分创意简报与创意流程场景

仍建议后续单独推进：

1. 更完整的 delivery 目标（例如批量 board 结果、历史 run 归档包）
2. 创意场景 XLSX 章节热力图与 section overview 的进一步平台卡强化

除非出现新的验证缺口或可见缺陷，否则不要重开核心 exporter 结构。
