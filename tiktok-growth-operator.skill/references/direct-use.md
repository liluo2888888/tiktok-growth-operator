# 直接使用（中文优先 / Direct Use）

当用户希望直接让 Codex 运行 TikTok 或 Douyin 工作流，而不是依赖 Clipcat 或 OpenClaw 时，优先看这份文档。

参考导航：

- 读 [final-handoff.md](final-handoff.md)：看最短完成态摘要、验证入口和真实 fixture 路径
- 读 [command-map.md](command-map.md)：看最短的 Clipcat 对标命令索引
- 读 [feishu-setup.md](feishu-setup.md)：如果你要把 scene 结果推到飞书，且你对飞书还不熟
- 本节下方 [运营调度 / 飞书追加（P1）](#运营调度--飞书追加p1)：场景 01–08、17–19 的调度 JSON、`operator_schedule_scene_*.json` 与看板追加命令
- 读 [scene-quick-reference.md](scene-quick-reference.md)：看 19 个 scene 的一页式可复制索引
- 读 [creative-brief-quick-reference.md](creative-brief-quick-reference.md)：看场景 `09` 到 `16` 的创意制作简报速查
- 读 [creative-production-handoff-pack.md](creative-production-handoff-pack.md)：看适合脚本、剪辑、设计或本地化执行的安全交付包
- 场景 `09` 到 `16` 的结构化报告导出会走专用 renderer hooks：封面 spotlight 优先展示 Message / Structure / Production Handoff（或 Variable Matrix / Execution Handoff），便于直接交接制作
- 读 [clipcat-openclaw-parity-audit.md](clipcat-openclaw-parity-audit.md)：看哪些能力已完整复刻，哪些仍依赖外部基础设施
- 读 [account-ops-assist-pack.md](account-ops-assist-pack.md)：看 TikTok 收件箱、通知、关注请求和关系监控操作包

## 一句话中文起步

如果你只想复制一句话给 Codex，就从这里开始：

- Scene 模式：`按场景 12 执行：为一个产品做多风格测试矩阵，先锁定 invariant message，再设计真正有差异的测试风格，并写出每个变体要验证什么。`
- Board 模式：`给我一个适合 TikTok 美妆运营的日常 board，要能直接排今天要跑的任务。`
- Capture-pack 模式：`基于这个 TikTok 素材包执行场景 15，输出图片文案翻译与本地化制作简报，保留原版层级并标出需要本地审核的地方。`
- Goal 模式：`给我一套从选题、拆解、素材测试到发布交付的 Douyin 工作流，要求输出可直接执行的步骤和交付物。`

兼容性校验保留语句：`给我一套从选题、拆解、素材测试到发布交付的 Douyin 工作流`
Validator 纯文本保留语句：`给我一套从选题、拆解、素材测试到发布交付的 Douyin 工作流`

### 可直接复制的中文命令

如果你更想走本地 shell，而不是自然语言对话，可以直接复制下面的命令：

```powershell
python scripts/run_operator_workflow.py `
  --request "按场景 12 执行：为一个产品做多风格测试矩阵，先锁定 invariant message，再设计真正有差异的测试风格，并写出每个变体要验证什么。" `
  --project "Lip Liner Style Matrix CN"
```

```powershell
python scripts/run_operator_workflow.py `
  --mode board `
  --query "给我一个适合 TikTok 美妆运营的日常 board，要能直接排今天要跑的任务。"
```

```powershell
python scripts/run_operator_workflow.py `
  --mode capture-pack `
  --scene 15 `
  --capture-root "D:\path\tiktok-analysis-pack" `
  --project "TikTok Image Localization CN" `
  --platform TikTok `
  --market US `
  --target-languages "English,Japanese,German"
```

```powershell
python scripts/run_operator_workflow.py `
  --request "给我一套从选题、拆解、素材测试到发布交付的 Douyin 工作流，要求输出可直接执行的步骤和交付物。" `
  --name douyin-topic-to-launch-cn `
  --project "Douyin Topic To Launch CN"
```
```

```powershell
python scripts/run_operator_workflow.py `
  --mode pack `
  --type creative-production-handoff `
  --source-report "D:\path\scene-15-report.json" `
  --platform TikTok `
  --market US `
  --output-dir "D:\path\creative-handoff-pack"
```

把已完成的 scene 报告推送到飞书多维表：

```powershell
$env:FEISHU_APP_ID="cli_xxx"
$env:FEISHU_APP_SECRET="xxx"
python scripts/push_report_to_feishu.py `
  --input "D:\path\scene-18-report.json" `
  --mode summary `
  --base-name "竞品账号周报"
```

通过飞书 OpenAPI 直推到飞书文档：

```powershell
python scripts/push_report_to_feishu_doc.py `
  --input "D:\path\scene-18-report.json" `
  --mode create `
  --title "竞品账号周报" `
  --backend api
```

把多个已有的 scene JSON 直接推到中文成品飞书文档：

```powershell
$env:FEISHU_APP_ID="cli_xxx"
$env:FEISHU_APP_SECRET="xxx"
python scripts/push_scene_reports_to_feishu_doc.py `
  --inputs "D:\path\scene-01-report.json" "D:\path\scene-08-report.json" `
  --app-id $env:FEISHU_APP_ID `
  --app-secret $env:FEISHU_APP_SECRET `
  --title-prefix "中文成品复推"
```

一条命令推送内置的已确认真实场景 bundle：

```powershell
$env:FEISHU_APP_ID="cli_xxx"
$env:FEISHU_APP_SECRET="xxx"
python scripts/push_scene_reports_to_feishu_doc.py `
  --confirmed `
  --app-id $env:FEISHU_APP_ID `
  --app-secret $env:FEISHU_APP_SECRET `
  --title-prefix "中文成品复推"
```

一条命令同时推到飞书文档和飞书多维表：

```powershell
python scripts/push_report_to_feishu_bundle.py `
  --input "D:\path\scene-18-report.json" `
  --app-id $env:FEISHU_APP_ID `
  --app-secret $env:FEISHU_APP_SECRET `
  --title "竞品账号周报 | 2026-W19" `
  --base-name "竞品账号周报 | 2026-W19"
```

从统一工作流入口直接推送：

```powershell
python scripts/run_operator_workflow.py `
  --mode scene `
  --scene 18 `
  --project "竞品账号周报" `
  --push-feishu `
  --feishu-app-id $env:FEISHU_APP_ID `
  --feishu-app-secret $env:FEISHU_APP_SECRET `
  --feishu-title "竞品账号周报 | 2026-W19" `
  --feishu-base-name "竞品账号周报 | 2026-W19"
```

从原生 scene runner 直接推送：

```powershell
python scripts/start_scene_run.py `
  --scene 18 `
  --name tiktok-competitor-weekly `
  --project "竞品账号周报" `
  --formats md,docx,xlsx `
  --push-feishu `
  --feishu-app-id $env:FEISHU_APP_ID `
  --feishu-app-secret $env:FEISHU_APP_SECRET `
  --feishu-title "竞品账号周报 | 2026-W19" `
  --feishu-base-name "竞品账号周报 | 2026-W19"
```

从原生 capture-pack runner 直接推送：

```powershell
python scripts/start_capture_pack_run.py `
  --scene 04 `
  --capture-root "D:\path\capture-pack" `
  --name tiktok-single-video-teardown `
  --project "单视频拆解" `
  --platform TikTok `
  --market US `
  --formats md,docx,xlsx `
  --push-feishu `
  --feishu-app-id $env:FEISHU_APP_ID `
  --feishu-app-secret $env:FEISHU_APP_SECRET `
  --feishu-title "单视频拆解 | 2026-05-08" `
  --feishu-base-name "单视频拆解 | 2026-05-08"
```

如果你明确要走本地官方 CLI 兜底，而不是 API 直推：

```powershell
python scripts/push_report_to_feishu_doc.py `
  --input "D:\path\scene-18-report.json" `
  --mode create `
  --title "竞品账号周报" `
  --backend lark-cli `
  --identity bot
```

如果 `lark-cli` 提示当前 Codex/Hermes 工作区还没绑定，就先做一次性绑定：

```powershell
python scripts/setup_hermes_feishu_env.py
& "E:\飞书\lark-cli-bin\v1.0.25\lark-cli.exe" config bind `
  --identity bot-only
```

一条命令完成 bootstrap：

```powershell
$env:FEISHU_APP_ID="cli_xxx"
$env:FEISHU_APP_SECRET="xxx"
python scripts/bootstrap_feishu_lark_cli.py `
  --app-id $env:FEISHU_APP_ID `
  --app-secret $env:FEISHU_APP_SECRET
```

把章节总览一并写进同一个飞书多维表：

```powershell
python scripts/push_report_to_feishu.py `
  --input "D:\path\scene-18-report.json" `
  --mode section_overview `
  --app-token "bascn_xxx"
```

高价值飞书命名建议：

- Scene `01`: `爆款视频采集 | <topic> | <market> | <date>`
- Scene `02`: `日常巡检 | <category> | <market> | <date>`
- Scene `03`: `批量爆款深拆 | <topic> | <market> | <date>`
- Scene `18`: `竞品账号周报 | <category> | <market> | <week>`
- Scene `19`: `自家账号复盘优化 | <account> | <market> | <week>`

## 运营调度 / 飞书追加（P1）

场景 `01`–`08`、`17`–`19` 在 `import_tiktok_capture_pack.py` 导入后会自动写入 **`operator_schedule`**（推送/定时真源），并尽量落到采集包目录：

- `operator_schedule_scene_<N>.json`：完整调度 JSON（`dispatch`、`next_runs`、`delivery.feishu`）
- 报告内 **Next Action** 或 **Recommended Action** 表会追加「运营调度 / 推送计划」行（时间、动作、负责人、渠道）
- 同节 `bullets` 会写建议 cron、`run_command`、飞书表键与 `append_scope`（追加批次）

### 先看调度单，再推飞书

```powershell
python scripts/import_tiktok_capture_pack.py `
  --capture-root "D:\path\capture-pack" `
  --scene 02 `
  --project "日常巡检" `
  --output "D:\path\scene-02.json"

Get-Content "D:\path\capture-pack\operator_schedule_scene_2.json" -Encoding utf8 | ConvertFrom-Json | Select-Object scene, dispatch, next_runs
```

### 与飞书对接的三条路径

| 目标 | 适用场景 | 命令要点 |
|------|----------|----------|
| **文档 + 摘要多维表** | 任意已完成 scene JSON | `push_report_to_feishu_bundle.py` 或 `--push-feishu` |
| **结构化看板按批次追加** | 报告含 `collection_board` 和/或 `patrol_board` | `deliver_operator_run.py --targets feishu --feishu-append-board` |
| **本地交付包归档** | 不推飞书、只打包 | `deliver_operator_run.py --targets local-bundle` |

Scene `01` 采集看板追加（固定表头 + `采集日期` / `追加批次` 列，写入 `feishu_delivery_registry.json` 复用同一多维表）：

```powershell
$env:FEISHU_APP_ID="cli_xxx"
$env:FEISHU_APP_SECRET="xxx"

python scripts/deliver_operator_run.py `
  --report-json "D:\path\scene-01.json" `
  --targets feishu `
  --feishu-append-board `
  --feishu-app-id $env:FEISHU_APP_ID `
  --feishu-app-secret $env:FEISHU_APP_SECRET `
  --feishu-base-name "爆款视频采集 | Lip Combo | US | 2026-05-17" `
  --feishu-run-date "2026-05-17" `
  --feishu-append-scope "2026-05-17-morning"
```

Scene `18` 竞品周报主表追加（矩阵模式按账号一行；单账号模式含调度动作行）：

```powershell
python scripts/deliver_operator_run.py `
  --report-json "D:\path\scene-18.json" `
  --targets feishu `
  --feishu-append-board `
  --feishu-app-id $env:FEISHU_APP_ID `
  --feishu-app-secret $env:FEISHU_APP_SECRET `
  --feishu-base-name "竞品周报 | Beauty | US | 2026-W19" `
  --feishu-run-date "2026-05-17" `
  --feishu-append-scope "2026-W19-matrix"
```

Scene `02` 巡检看板追加（与 Scene 01 相同机制；`--feishu-append-board` 会扫描报告内所有已注册看板并分别写入 registry）：

```powershell
python scripts/deliver_operator_run.py `
  --report-json "D:\path\scene-02.json" `
  --targets feishu `
  --feishu-append-board `
  --feishu-app-id $env:FEISHU_APP_ID `
  --feishu-app-secret $env:FEISHU_APP_SECRET `
  --feishu-base-name "品类巡检 | Beauty | US | 2026-05-17" `
  --feishu-run-date "2026-05-17" `
  --feishu-append-scope "beauty-us-daily"
```

无凭证时先 dry-run（只出计划，不调 OpenAPI）：

```powershell
python scripts/deliver_operator_run.py `
  --report-json "D:\path\scene-01.json" `
  --targets feishu `
  --feishu-append-board `
  --dry-run
```

从 capture-pack 跑完再推（`--push-feishu` 默认同时推送文档/摘要 **并** 追加结构化主表；仅要文档时用 `--no-feishu-append-board`）：

```powershell
python scripts/start_capture_pack_run.py `
  --scene 18 `
  --capture-root "D:\path\scene18-19-multi-week-account" `
  --name weekly-competitor `
  --project "竞品账号周报" `
  --formats md,docx,xlsx `
  --push-feishu `
  --feishu-app-id $env:FEISHU_APP_ID `
  --feishu-app-secret $env:FEISHU_APP_SECRET `
  --feishu-title "竞品账号周报 | Beauty | US | 2026-W19" `
  --feishu-base-name "竞品账号周报 | Beauty | US | 2026-W19"
```

日更巡检 + 周报一键（同样带主表追加）：

```powershell
python scripts/run_scene0203.py --source fixture --formats md,docx --push-feishu `
  --feishu-app-id $env:FEISHU_APP_ID --feishu-app-secret $env:FEISHU_APP_SECRET

python scripts/run_scene1819.py --preset multiweek --formats md,docx --push-feishu `
  --feishu-app-id $env:FEISHU_APP_ID --feishu-app-secret $env:FEISHU_APP_SECRET
```

### 各场景 `delivery.feishu.table_key`（追加/命名对照）

| Scene | `table_key` | 典型飞书动作（见 `dispatch`） |
|-------|-------------|-------------------------------|
| 01 | `scene01_collection_board` | 看板追加 + Top3 交接 Scene 03 |
| 02 | `scene02_patrol_board` | 巡检主表按批次追加（`patrol_board.json`）+ 日报摘要 |
| 06 | `scene06_competitor_product_board` | 竞品商品主表按批次追加（`competitor_product_board.json`） |
| 07 | `scene07_category_entry` | 类目进入判断主表按批次追加（`category_entry_board.json`） |
| 08 | `scene08_comment_persona` | 评论洞察主表按批次追加（`comment_persona_board.json`） |
| 17 | `scene17_creator_formula` | 创作者公式主表按批次追加（`creator_formula_board.json`） |
| 18 | `scene18_competitor_weekly` | 竞品周报主表按批次追加（`competitor_weekly_board.json`）+ 调度单 |
| 19 | `scene19_account_retro` | 账号复盘调度主表按批次追加（`account_retro_board.json`） |

一键日更 / 周报入口仍会生成上述调度字段：

```powershell
python scripts/run_scene0203.py --source fixture --formats md,docx
python scripts/run_scene1819.py --preset multiweek --formats md,docx
```

### 本地飞书 CLI（`E:\飞书`）

OpenAPI 为主路径；文档 CLI 兜底见 [feishu-setup.md](feishu-setup.md)。本机 CLI：

- `E:\飞书\lark-cli-bin\v1.0.25\lark-cli.exe`
- 一次性绑定：`python scripts/bootstrap_feishu_lark_cli.py` 或 `python scripts/setup_hermes_feishu_env.py`（默认写 `D:\hermes\.env`）

### 自动化验收 vs 真网推送

| 检查 | 覆盖什么 | 是否打真飞书 |
|------|----------|--------------|
| `validate_scene_ops.py` | 01/02/03/08/18/19 的 `operator_schedule` + 落盘 JSON | 否 |
| `validate_capture_pack_workflows.py` | 全量 capture-pack + 04/05/06/07/17 P1 调度 | 否 |
| `validate_delivery_adapters.py` | `deliver_operator_run`；无凭证时 `feishu` → `skipped` | 否 |
| `validate_platform_p0.py` | Scene 01 `plan_board_append` 表头与行数 | 否 |
| 你本机设 `$env:FEISHU_APP_ID` / `SECRET` 后跑 `--push-feishu` 或 `deliver_operator_run --targets feishu` | 文档 + 多维表真写入 | **是** |

历史真网打通记录（含示例 Doc/Bitable 链接）见 [feishu-setup.md](feishu-setup.md)（`2026-05-08`）。**当前 Codex 会话若未注入 `FEISHU_APP_*`，不会自动做 live 推送**；需要你在 PowerShell 里设好凭证后再跑上表命令。

## 默认定位

把这个包理解为：

- 面向 19 个 scene 的 Codex 原生路由器
- 报告与工作区生成器
- 规划与证据综合系统
- 用于发布准备、直播辅助、创意制作交接的 handoff 包生成器
- 面向多场景业务请求的目标工作流扩展器
- 统一的 scene / goal / pack 工作流执行入口
- 可从一句自然语言请求自动判断 scene、goal 或 pack 的路由器
- 可在生成前推荐最佳 preset family 和 board slug 的 board 选择器
- 可脚手架并按需预览本地可运行 board 的 board 启动器

不要假装当前工作区已经具备：

- Douyin 官方 API 凭证
- 云手机集群
- 可安全执行发布、评论或私信的 RPA 模板

## 最快调用路径

如果你还不知道该从哪个 board family 起步，先跑透明选择器：

```powershell
python scripts/recommend_entry_board.py `
  --query "I need a publish plan for this week" `
  --format markdown
```

如果你已经生成过 template bundle，希望选择器直接返回本地真实模板和 suite 路径：

```powershell
python scripts/recommend_entry_board.py `
  --query "Give me a daily board" `
  --bundle-root "D:\path\preset-template-bundle" `
  --format markdown
```

如果不传 `--bundle-root`，选择器会自动发现最新的本地 `preset-template-bundle*` 导出。

关于 `single`、`combo`、`vertical`、`launch-board`、`manager-board`、`cadence-board` 这些 family 的选型规则，见 [entry-selector.md](entry-selector.md)。

如果你想让这个包一步完成 board 选择和本地 starter 文件夹脚手架：

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

一步完成 starter、队列生成和预览：

```powershell
python scripts/start_entry_board.py `
  --query "Give me a daily board for TikTok beauty ops" `
  --generate `
  --dry-run
```

统一路由预览版本：

```powershell
python scripts/run_operator_workflow.py `
  --mode board `
  --query "Give me a daily board for TikTok beauty ops" `
  --generate `
  --dry-run
```

board 脚手架生成后的建议阅读顺序：

- 先读 starter `README.md`，它会指向队列、preset 报告、batch 报告和 rerun 产物路径
- 生成后再读 `<board>.report.md`，里面有标准 dry-run、正式执行和 rerun 命令
- dry-run 后读 `batch-run/batch_report.md`，它会总结排队任务和正式执行前的告警

如果你不想用自动发现，而是要锁定某个具体 bundle，就传 `--bundle-root`。

### 在 Codex 对话里

示例：

- `Run scene 03 for morning makeup hooks and output a teardown report`
- `Run scene 08 and summarize audience pain points from four competitor comment sets`
- `Build a full Douyin workflow from topic selection to publish handoff`
- `按场景 12 执行：为一个产品做多风格测试矩阵，先锁定 invariant message，再设计真正有差异的测试风格，并写出每个变体要验证什么。`
- `按场景 18 执行：输出竞品账号周报，要求按账号和周维度比较内容变化，不只看总量，并明确本周该跟进的动作。`

### 在本地 shell 里

创建轻量 scene 工作区和报告：

```powershell
python scripts/run_operator_workflow.py `
  --request "Run scene 03 for morning makeup hooks and output a teardown report" `
  --project "Morning Makeup Hook Teardown"
```

创建完整的 durable scene run，并带 starter 输出：

```powershell
python scripts/start_scene_run.py `
  --scene 12 `
  --name lip-liner-style-matrix `
  --project "Lip Liner Style Matrix" `
  --platform Douyin `
  --market China
```

直接从真实 TikTok capture pack 创建完整 durable run：

```powershell
python scripts/start_capture_pack_run.py `
  --scene 17 `
  --capture-root "D:\path\tiktok-analysis-pack-smoke-20260423f" `
  --name tiktok-official-capture-run `
  --project "TikTok Official Account Creator Distillation" `
  --platform TikTok `
  --market US
```

基于 TikMatrix 搜索 / topic 导出，把 Scene `02` 跑成真实巡检循环：

```powershell
python scripts/run_scene02_patrol.py `
  --name tiktok-beauty-patrol `
  --project "TikTok Beauty Patrol" `
  --category "Beauty" `
  --market US `
  --mode mixed `
  --queries "lip combo,lip liner" `
  --topics "makeup,beautytok" `
  --count 10 `
  --download-top 3 `
  --formats md,docx,xlsx
```

If you already have TikMatrix search/topic export folders, skip live collection and import them directly:

```powershell
python scripts/run_scene02_patrol.py `
  --name tiktok-orangecat-patrol `
  --project "TikTok Orange Cat Patrol" `
  --category "Orange Cat" `
  --market US `
  --mode mixed `
  --queries "orange cat" `
  --topics "orangecat" `
  --query-root "E:\tiktok\TikMatrix\tmp\search-live-orange-cat" `
  --topic-root "E:\tiktok\TikMatrix\tmp\topic-live-orangecat" `
  --skip-live `
  --also-run-scene03 `
  --formats md
```

Behavior:

- writes a Scene `02` capture-pack with `patrol_snapshot.json`, `patrol_delta.json`, `patrol_alerts.json`, and `scene03_candidates.json`
- persists prior patrol state under `tiktok-growth-operator.skill\tmp\scene02-state\...`
- generates a normal Scene `02` operator run through the existing report pipeline
- can optionally auto-run a downstream Scene `03` follow-up from the derived shortlist

**日更巡检 02→03 一键包**（已有 patrol capture-pack 或 validation 夹具，无需 TikMatrix）：

```powershell
python scripts/run_scene0203.py `
  --source fixture `
  --name daily-patrol-teardown `
  --project "TikTok Daily Patrol + Deep Teardown" `
  --formats md,docx,xlsx
```

若 capture pack 里只有 `ranked_videos.json`、还没有 `patrol_snapshot.json`，先补巡检运行时字段：

```powershell
python scripts/seed_scene02_patrol_pack.py `
  --capture-root "D:\path\your-capture-pack" `
  --category "Beauty" `
  --queries "lip combo,lip liner" `
  --force

python scripts/run_scene0203.py --capture-root "D:\path\your-capture-pack"
```

**周报复盘 18+19 一键包**（多周 / 矩阵 / ROI 夹具）：

```powershell
python scripts/run_scene1819.py --preset multiweek --formats md,docx,xlsx
python scripts/run_scene1819.py --preset matrix
python scripts/run_scene1819.py --preset roi --scene19-only
```

专项验收（02/03/18/19，约 10 秒）：

```powershell
python scripts/validate_scene_ops.py
```

Scene `06` competitor product dashboard with explicit TikTok Shop sync:

```powershell
python scripts/start_capture_pack_run.py `
  --scene 06 `
  --capture-root "D:\path\tiktok-analysis-pack-smoke-20260423f" `
  --name tiktok-competitor-product-dashboard `
  --project "TikTok Competitor Product Dashboard" `
  --platform TikTok `
  --market US `
  --shop-sync `
  --shop-source-mode http `
  --shop-keyword "beauty" `
  --shop-region US `
  --shop-limit 10 `
  --shop-http-url "http://127.0.0.1:8787"
```

Preferred unified entrypoint version:

```powershell
python scripts/run_operator_workflow.py `
  --mode capture-pack `
  --scene 06 `
  --capture-root "D:\path\tiktok-analysis-pack-smoke-20260423f" `
  --name tiktok-competitor-product-dashboard `
  --project "TikTok Competitor Product Dashboard" `
  --platform TikTok `
  --market US `
  --shop-sync `
  --shop-source-mode http `
  --shop-keyword "beauty" `
  --shop-region US `
  --shop-limit 10 `
  --shop-http-url "http://127.0.0.1:8787"
```

Behavior:

- runs an explicit competitor-product sync before Scene `06` import
- writes `competitor_products.json` and `tiktok_shop_source_meta.json` into the capture root
- upgrades Scene `06` from schema-only or fallback-only mode into a live structured product-board mode when the source returns data
- keeps the existing fallback path when no live source is available

If you only want sources that are explicitly declared as official or authorized, add:

```powershell
  --shop-source-attestation official `
  --shop-require-verified-source `
  --shop-http-allowed-hosts "open.tiktokapis.com,your-gateway.internal.example"
```

Accepted verified attestations are:

- `official`
- `authorized-partner`
- `internal-gateway`

If no verified attestation is provided, Scene `06` now treats the source as `unverified` by default.

### Scene 06 quick start (no Clipcat / no Partner credentials yet)

Use structured competitor products from the capture pack or the built-in seed script:

```powershell
python scripts/run_scene06.py `
  --capture-root "D:\path\tiktok-analysis-pack-smoke-20260423f" `
  --data-path structured `
  --seed-mode fixture `
  --formats md,docx,xlsx
```

This writes `competitor_products.json`, imports Scene `06`, and renders the dashboard with `data_source_mode=tiktok_shop_structured` (explicitly **unverified**, not official).

### Scene 06 official path (TikTok Research API or Shop Partner OAuth)

Correct **official** sources (as of 2026-05):

| API family | Who can use it | What Scene 06 can get today |
|------------|----------------|-----------------------------|
| [TikTok Research API](https://developers.tiktok.com/products/research-api) | Approved researchers (`research.data.basic`) | EU shop aggregates via `POST https://open.tiktokapis.com/v2/research/tts/shop/` (shop_name, not global keyword catalog) |
| [TikTok Shop Partner Center](https://partner.tiktokshop.com/doc) | Authorized apps + merchant OAuth | Seller/partner product APIs after merchant approval (implement in your gateway) |

There is **no** anonymous public “search all TikTok Shop products” endpoint. Clipcat and scrapers are third-party and must stay `unverified` unless you wrap them in your own gateway with honest metadata.

1. Start the local shop gateway (terminal A, FastAPI):

```powershell
$env:TIKTOK_RESEARCH_CLIENT_KEY = "your-client-key"
$env:TIKTOK_RESEARCH_CLIENT_SECRET = "your-client-secret"
# or: $env:TIKTOK_RESEARCH_ACCESS_TOKEN = "clt...."
$env:TIKTOK_SHOP_NAME = "Your Shop Name"
python scripts/run_shop_gateway.py --install-deps --port 8791
```

See `services/shop_gateway/README.md` for partner / structured dev backends.

2. Run Scene 06 through the gateway (terminal B):

```powershell
python scripts/run_scene06.py `
  --capture-root "D:\path\tiktok-analysis-pack-smoke-20260423f" `
  --data-path official `
  --shop-http-url "http://127.0.0.1:8791" `
  --shop-source-attestation official `
  --shop-require-verified-source `
  --shop-http-allowed-hosts "127.0.0.1"
```

Full one-page implementation spec: [scene06-shop-gateway-spec.md](scene06-shop-gateway-spec.md).

Environment templates (no secrets in repo):

- General: `services/shop_gateway/.env.example` → `.env`
- Internal forward / shop-bridge: `services/shop_gateway/.env.internal-forward.example` → `.env`

See [services/shop_gateway/README.md](../services/shop_gateway/README.md).

### Verified HTTP gateway contract

When attestation is `official`, `authorized-partner`, or `internal-gateway`, the sync layer no longer trusts the CLI flag alone. The HTTP gateway must return a `source` object (or `source_metadata`) on `POST /v1/shop/products/search`.

For `official`, the gateway response must include:

```json
{
  "products": [ ... ],
  "source": {
    "source_type": "official",
    "provider": "tiktok_shop_open_platform",
    "auth_mode": "merchant_oauth",
    "issuer": "tiktok"
  }
}
```

If metadata is missing or mismatched, sync is blocked with `invalid-source-metadata` and nothing is written to `competitor_products.json`.

Recommended gateway behavior behind `official`:

1. Complete TikTok Shop Partner Center / merchant OAuth on your side.
2. Call the official Shop or Research API with the approved token.
3. Normalize products into the operator schema.
4. Echo the `source` block above on every search response so the skill can verify provenance in code.

Environment equivalents:

- `TIKTOK_SHOP_SOURCE_ATTESTATION=official`
- `TIKTOK_SHOP_REQUIRE_VERIFIED=1`
- `TIKTOK_SHOP_HTTP_ALLOWED_HOSTS=open.tiktokapis.com,your-gateway.internal.example`
- `TIKTOK_SHOP_HTTP_URL=https://your-gateway.internal.example`

Creative-testing examples from the same real TikTok pack:

```powershell
python scripts/start_capture_pack_run.py `
  --scene 11 `
  --capture-root "D:\path\tiktok-analysis-pack-smoke-20260423f" `
  --name tiktok-hot-video-pipeline `
  --project "TikTok Hot Video Replication Pipeline" `
  --platform TikTok `
  --market US
```

```powershell
python scripts/start_capture_pack_run.py `
  --scene 12 `
  --capture-root "D:\path\tiktok-analysis-pack-smoke-20260423f" `
  --name tiktok-style-matrix `
  --project "TikTok One Product Multi Style Matrix" `
  --platform TikTok `
  --market US
```

```powershell
python scripts/start_capture_pack_run.py `
  --scene 13 `
  --capture-root "D:\path\tiktok-analysis-pack-smoke-20260423f" `
  --target-markets "US,Japan,Germany" `
  --name tiktok-multi-market-localization-blueprint `
  --project "TikTok Multi-Market Localization Blueprint" `
  --platform TikTok `
  --market US
```

```powershell
python scripts/start_capture_pack_run.py `
  --scene 14 `
  --capture-root "D:\path\tiktok-analysis-pack-smoke-20260423f" `
  --name tiktok-launch-asset-blueprint `
  --project "TikTok Launch Asset Family Blueprint" `
  --platform TikTok `
  --market US
```

```powershell
python scripts/start_capture_pack_run.py `
  --scene 15 `
  --capture-root "D:\path\tiktok-analysis-pack-smoke-20260423f" `
  --target-languages "English,Japanese,German" `
  --name tiktok-image-translation-blueprint `
  --project "TikTok Image Translation Blueprint" `
  --platform TikTok `
  --market US
```

```powershell
python scripts/start_capture_pack_run.py `
  --scene 16 `
  --capture-root "D:\path\tiktok-analysis-pack-smoke-20260423f" `
  --name tiktok-main-image-benchmark-blueprint `
  --project "TikTok Main Image Benchmark Blueprint" `
  --platform TikTok `
  --market US
```

Preferred unified entrypoint version:

```powershell
python scripts/run_operator_workflow.py `
  --mode capture-pack `
  --scene 15 `
  --capture-root "D:\path\tiktok-analysis-pack-smoke-20260423f" `
  --target-languages "English,Japanese,German" `
  --name tiktok-image-translation-blueprint `
  --project "TikTok Image Translation Blueprint" `
  --platform TikTok `
  --market US `
  --output-root "D:\path\capture-run-scene15"
```

```powershell
python scripts/run_operator_workflow.py `
  --mode capture-pack `
  --scene 17 `
  --capture-root "D:\path\tiktok-analysis-pack-smoke-20260423f" `
  --name tiktok-official-capture-run `
  --project "TikTok Official Account Creator Distillation" `
  --platform TikTok `
  --market US `
  --output-root "D:\path\capture-run"
```

Comment-signal and live-assist example:

```powershell
python scripts/start_capture_pack_run.py `
  --scene 08 `
  --capture-root "D:\path\tiktok-download-validated-20260423" `
  --name tiktok-comment-capture-run `
  --project "TikTok Comment Signal Synthesis" `
  --platform TikTok `
  --market US
```

Preferred unified entrypoint version:

```powershell
python scripts/run_operator_workflow.py `
  --mode capture-pack `
  --scene 08 `
  --capture-root "D:\path\tiktok-download-validated-20260423" `
  --name tiktok-comment-capture-run `
  --project "TikTok Comment Signal Synthesis" `
  --platform TikTok `
  --market US `
  --output-root "D:\path\comment-capture-run"
```

### 真实 TikMatrix Bridge

If your real TikTok collection already lives in `E:\tiktok\TikMatrix`, bridge those exports directly without changing `TikMatrix` itself:

Preferred current collector runtime:

```powershell
E:\tiktok\TikMatrix\.venv\Scripts\python.exe E:\tiktok\TikMatrix\scripts\run_from_skill.py `
  profile-posts-browser-download `
  --url "https://www.tiktok.com/@mustsharenews" `
  --count 8 `
  --max-pages 1 `
  --new-only `
  --output-dir "E:\tiktok\TikMatrix\tmp\codex-mustsharenews-profile-post-downloads-venv-20260507"
```

Then bridge that real collector export into the operator runtime:

```powershell
python scripts/run_tikmatrix_capture_bridge.py `
  --profile-posts-json "E:\tiktok\TikMatrix\tmp\codex-mustsharenews-profile-post-downloads-venv-20260507\mustsharenews\profile_posts.json" `
  --downloads-json "E:\tiktok\TikMatrix\tmp\codex-mustsharenews-profile-post-downloads-venv-20260507\mustsharenews\downloads.json" `
  --scene 01 `
  --name mustsharenews-scene01-venv-restored `
  --project "MustShareNews Venv Restored Runtime" `
  --market SG `
  --min-likes 1000 `
  --qualified-count 5 `
  --formats md
```

```powershell
python scripts/run_tikmatrix_capture_bridge.py `
  --profile-posts-json "E:\tiktok\TikMatrix\tmp\live-profile-posts-browser-batch\mrorangecat555\profile_posts.json" `
  --comments-json "E:\tiktok\TikMatrix\tmp\comments-live-mrorangecat-paged\7624057229930450192\comments.json" `
  --downloads-json "E:\tiktok\TikMatrix\tmp\skill-batch-download\downloads.json" `
  --scene 08 `
  --name mrorangecat-comment-signal `
  --project "Mr Orange Cat Comment Signal" `
  --market US
```

Account distillation from the same real TikMatrix exports:

```powershell
python scripts/run_tikmatrix_capture_bridge.py `
  --profile-posts-json "E:\tiktok\TikMatrix\tmp\live-profile-posts-browser-batch\mrorangecat555\profile_posts.json" `
  --downloads-json "E:\tiktok\TikMatrix\tmp\skill-batch-download\downloads.json" `
  --scene 17 `
  --name mrorangecat-account-distill `
  --project "Mr Orange Cat Creator Distillation" `
  --market US
```

Real TikMatrix account-operations bridge:

```powershell
python scripts/run_tikmatrix_account_ops_bridge.py `
  --name orangecat-account-ops `
  --project "Orange Cat Account Ops" `
  --platform TikTok `
  --market US `
  --newest-reply-json "E:\tiktok\TikMatrix\tmp\live-newest-reply-final-2\newest-reply\newest_reply.json" `
  --notice-multi-json "E:\tiktok\TikMatrix\tmp\live-notice-multi-final-3\notice-multi\notice_multi.json" `
  --following-requests-json "E:\tiktok\TikMatrix\tmp\live-following-requests-final\following-requests\following_request_list.json" `
  --following-list-json "E:\tiktok\TikMatrix\tmp\live-following-list-final\following\following_list.json" `
  --follower-list-json "E:\tiktok\TikMatrix\tmp\live-follower-list-final\followers\follower_list.json"
```

Batch version:

```powershell
python scripts/batch_run_operator_workflows.py `
  --batch-file "D:\path\capture-batch.json" `
  --output-file "D:\path\capture-batch-result.json"
```

Push every successful scene report from that batch result into Feishu:

```powershell
$env:FEISHU_APP_ID="cli_xxx"
$env:FEISHU_APP_SECRET="xxx"
python scripts/push_batch_results_to_feishu.py `
  --batch-result "D:\path\capture-batch-result.json"
```

If you do not have `batch_result.json` and only want to repush a few already generated scene JSON files, use:

```powershell
python scripts/push_scene_reports_to_feishu_doc.py `
  --inputs "D:\path\scene-01-report.json" "D:\path\scene-08-report.json" `
  --app-id $env:FEISHU_APP_ID `
  --app-secret $env:FEISHU_APP_SECRET `
  --title-prefix "中文成品复推"
```

If you want the currently confirmed real-scene bundle instead of manually listing paths, use:

```powershell
python scripts/push_scene_reports_to_feishu_doc.py `
  --confirmed `
  --app-id $env:FEISHU_APP_ID `
  --app-secret $env:FEISHU_APP_SECRET `
  --title-prefix "中文成品复推"
```

If the preset was generated by `generate_batch_preset.py`, you can also use the generated helper:

```powershell
& "D:\path\your-preset.push-feishu.ps1"
```

Behavior:

- scenes `09` to `16` auto-generate `publish-prep`
- scenes `08`, `18`, `19` auto-generate `live-assist`
- override with `--operator-packs publish-prep,live-assist`

Scene `15` is intentionally a blueprint-only flow:

- it requires explicit `--target-languages`
- it does not claim OCR already exists
- it does not fabricate final translated image copy from ranked TikTok captions

Summarize recent runs and derived packs:

```powershell
python scripts/summarize_run_history.py `
  --output-json "D:\path\run-history.json" `
  --output-md "D:\path\run-history.md" `
  --limit 25
```

Preferred unified entrypoint version:

```powershell
python scripts/run_operator_workflow.py `
  --mode history `
  --history-output-json "D:\path\run-history.json" `
  --history-output-md "D:\path\run-history.md" `
  --history-limit 25
```

Run the export regression suite after changing report rendering:

```powershell
python scripts/validate_export_outputs.py `
  --output-root "D:\path\export-validation-suite"
```

Re-render historical scene outputs from existing `scene-*.json` files after an encoding or renderer fix:

```powershell
python scripts/rerender_scene_outputs.py `
  --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp" `
  --formats md
```

Preview the repair scope without writing files:

```powershell
python scripts/rerender_scene_outputs.py `
  --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp" `
  --formats md `
  --dry-run
```

Run the full durable validation surface after broader workflow changes:

```powershell
python scripts/validate_all_workflows.py
```

Run the real TikMatrix bridge validation after changing the bridge layer:

```powershell
python scripts/validate_tikmatrix_bridge.py
```

Run the real TikMatrix account-ops bridge validation after changing the logged-in account bridge layer:

```powershell
python scripts/validate_tikmatrix_account_ops_bridge.py
```

Create only a scene-aware JSON scaffold:

```powershell
python scripts/generate_scene_report.py `
  --scene 12 `
  --project "Lip Liner Style Matrix" `
  --output "D:\path\scene-12-report.json" `
  --format json
```

Recommend a scene chain from a business goal:

```powershell
python scripts/recommend_scene_chain.py `
  --goal creative-testing `
  --format markdown
```

Recommend a scene chain from a free-text goal:

```powershell
python scripts/recommend_scene_chain.py `
  --query "I want a Douyin workflow from topic selection to creative testing to publish handoff" `
  --format markdown
```

Free-text matching can now hit built-in workflow templates, not only one goal slug.

当前内置模板：

- `topic-to-publish` -> `category-entry + creative-testing + publish-handoff`
- `competitor-weekly-and-breakdown` -> `competitor-monitoring`
- `account-retro-to-next-test` -> `account-improvement`
- `viral-to-testing` -> `viral-discovery + creative-testing`
- `category-to-localized-launch` -> `category-entry + localization + publish-handoff`
- `competitor-to-publish` -> `competitor-monitoring + creative-testing + publish-handoff`
- `audience-to-live` -> `category-entry + live-support`
- `weekly-monitor-to-next-test` -> `competitor-monitoring + account-improvement`

当前更高层的 board family：

- `combo` -> 可复用的多 preset 组合包，例如 `beauty-ops-board`
- `vertical` -> 带默认参数的 starter，例如 `beauty-us-ops-starter`
- `launch-board` -> 结果优先入口，例如 `publish-week-board`
- `manager-board` -> 角色优先入口，例如 `growth-operator-board`
- `cadence-board` -> 节奏优先入口，例如 `weekly-ops-board`

当请求语言明显更像节奏优先、角色优先、结果优先，或者 seeded-vertical，而不是单个 scene 或多阶段 workflow 时，会自动路由到 `board`。

创建完整的多 scene goal 工作区：

```powershell
python scripts/run_operator_workflow.py `
  --request "I want a Douyin workflow from topic selection to creative testing to publish handoff" `
  --name douyin-growth-workflow `
  --project "Douyin Growth Workflow" `
  --formats md
```

当查询命中某个 workflow template 时：

- 所有组件 goal 的 scenes 会合并成一条有序链路
- 重复 scene 会自动去重
- `publish-prep`、`live-assist` 等派生 pack 仍会基于合并后的 workflow 生成
- 生成出的 `README.md` 与 `goal_manifest.json` 会记录命中的模板以及对应的组件 goals

当前内置的 goal 模板清单见 `references/goal-templates.md`。

## 文章能力映射与安全替代

当用户提到腾讯云那篇 OpenClaw / Douyin 相关文章时，把能力映射到以下 Codex 原生路径：

- 智能选题 -> scenes `01`, `02`, `03`, `07`
- AI 视频制作简报生成 -> scenes `09`, `10`, `11`, `12`, `13`, `14`, `15`, `16`
- 竞品监控与复盘 -> scenes `06`, `17`, `18`
- 评论挖掘与人群语言提取 -> scene `08`
- 账号复盘与下一步规划 -> scene `19`
- 发布准备 -> 工作区生成 + 标题 / hook / 封面 / checklist 输出
- 直播辅助 -> 监控模板、场控回复提示和异常检查清单

## 直接生成交付包

生成 `publish-prep` 交付包：

```powershell
python scripts/run_operator_workflow.py `
  --request "Create a publish prep pack for a morning makeup sell-through video" `
  --project "Morning Makeup Sell-Through Video" `
  --platform Douyin `
  --market China `
  --output-dir "D:\path\publish-pack"
```

基于已有的 scene report JSON 生成 `publish-prep` 交付包：

```powershell
python scripts/generate_operator_pack.py `
  --type publish-prep `
  --source-report "D:\path\scene-03-report.json" `
  --platform Douyin `
  --market China `
  --output-dir "D:\path\publish-pack"
```

生成 `live-assist` 交付包：

```powershell
python scripts/run_operator_workflow.py `
  --request "Create a live assist pack for an evening skincare live session" `
  --project "Evening Skincare Live Session" `
  --platform Douyin `
  --market China `
  --output-dir "D:\path\live-pack"
```

## 自动路由规则

`scripts/run_operator_workflow.py` 现在默认使用 `--mode auto`。

路由优先级：

- 显式传入 `--scene`、`--goal` 或 `--type` 时，始终优先采用显式指定
- 显式传入 `--mode board` 时，始终优先走 starter-board 生成
- 如果请求明显是在要发布包或直播辅助包，会路由到 `pack`
- 如果请求更适合表达成可复用 starter board，会路由到 `board`
- 如果请求直接点名 scene 编号，或与某个单一 scene 高强度匹配，会路由到 `scene`
- 其他情况统一先路由到 `goal`，再与内置 workflow template 或单目标链做匹配

自动路由结果现在会附带这些解释字段：

- `route.reason`
- `route.explanation.reasons`
- `route.explanation.pack_scores`
- `route.explanation.scene_preview`
- `route.explanation.goal_preview`
- `route.explanation.board_preview`
- `route.explanation.multi_stage`

如果你想核对为什么请求被路由到 `scene`、`goal`、`board` 或 `pack`，就看这些字段。

推荐使用方式：

- 优先用 `--request` 走自然语言路由
- 只有在你要强制指定某种 pack 类型时，才补 `--type`
- 想让工作区名字更干净时，补 `--project`
- 只有在你需要精确控制 run 文件夹 slug 时，才补 `--name`

## 批量执行

如果你想一次排入多条混合任务，用：

```powershell
python scripts/batch_run_operator_workflows.py `
  --batch-file "D:\path\operator-batch.json" `
  --output-file "D:\path\operator-batch-result.json"
```

如果你不想手写 batch JSON，可以先从 preset 生成：

```powershell
python scripts/generate_batch_preset.py `
  --preset topic-to-publish `
  --name spring-lip-launch `
  --project "Spring Lip Launch" `
  --product "Velvet Lip Glaze" `
  --category "Beauty" `
  --output "D:\path\topic-to-publish-batch.json"
```

如果你想先拿一个可填写模板，再去生成真实队列，就先建 starter config：

```powershell
python scripts/generate_batch_preset.py `
  --preset competitor-to-publish,audience-to-live,tiktok-account-watch-capture `
  --ordering mode `
  --template-output "D:\path\beauty-ops-board.template.json"
```

如果你想一开始就拿到完整的 preset-template board，可以直接导出 template bundle：

```powershell
python scripts/generate_batch_preset.py `
  --template-bundle-root "D:\path\preset-template-bundle"
```

这个 bundle 现在会包含：

- 每个单独 preset 对应一份模板
- 精选的组合模板，例如 `beauty-ops-board`、`topic-to-publish-board`
- 带默认参数的 vertical starter，例如 `beauty-us-ops-starter`
- 一份 `template-index.json`，用于标记每个条目属于 `single`、`combo` 还是 `vertical`
- 一份 `README.md`，说明如何填写并直接运行

如果你想直接拿到一个接近可运行的基线配置，而且平台、市场、命名、capture fixture 默认值已经填好，就优先用 vertical starter。

如果 bundle 里已经带了 `vertical-suites/`，就可以跳过手工拼命令，直接用 suite 级脚本。

同样的 suite 模式也适用于 `launch-board`，适合像 `publish-week-board`、`competitor-review-board` 这种结果优先入口。

现在它也适用于 `manager-board`，适合像 `content-operator-board`、`growth-operator-board` 这种角色优先入口。

它同样适用于 `cadence-board`，适合像 `daily-ops-board`、`weekly-ops-board` 这种节奏优先入口。

如果你要把某个 combo template 变成真实队列，就先填好生成出的 JSON，再运行：

```powershell
python scripts/generate_batch_preset.py `
  --config "D:\path\preset-template-bundle\beauty-ops-board.template.json"
```

如果你要把某个 seeded vertical starter 变成真实队列，通常可以先直接运行，再基于生成出的 board 微调：

```powershell
python scripts/generate_batch_preset.py `
  --config "D:\path\preset-template-bundle\beauty-us-ops-starter.template.json"
```

或者直接用导出的 suite 脚本：

```powershell
D:\path\preset-template-bundle\vertical-suites\beauty-us-ops-starter\generate.ps1
```

```powershell
D:\path\preset-template-bundle\vertical-suites\beauty-us-ops-starter\dry-run.ps1
```

You can also merge multiple presets into one combined ops queue:

```powershell
python scripts/generate_batch_preset.py `
  --preset competitor-to-publish,audience-to-live,tiktok-account-watch-capture `
  --ordering mode `
  --name beauty-ops-board `
  --project "Beauty Ops Board" `
  --product "Velvet Lip Glaze" `
  --category "Beauty" `
  --audience "Skincare Deal Seekers" `
  --account-name "GlowOfficial" `
  --capture-root "D:\path\tiktok-analysis-pack-smoke-20260423f" `
  --output "D:\path\beauty-ops-board.json"
```

If a chosen preset depends on `product`, `category`, `audience`, or `account-name`, generation now fails fast until you pass the required variable flag.

Each generated preset queue now also includes:

- one `.manifest.json` file for machine-readable metadata
- one `.report.md` file for quick human inspection before batch execution

That preset report now doubles as a run handoff:

- it shows the suggested batch artifact directory
- it shows the suggested combined result JSON path
- it gives copy-ready dry-run, execute, and rerun commands
- it gives a copy-ready regenerate-from-config command
- it points to generated `.ps1` and `.cmd` helper scripts for the same actions

If you want to inspect the routing and task plan before real execution, use:

```powershell
python scripts/batch_run_operator_workflows.py `
  --batch-file "D:\path\operator-batch.json" `
  --dry-run `
  --batch-root "D:\path\operator-batch-preview"
```

Each batch item can be:

- one `auto` request
- one direct `scene` task
- one direct `goal` task
- one direct `pack` task
- one direct `capture-pack` task

See `references/automation-workflows.md` for the batch JSON shape.

The batch result now also tells you which items failed without aborting the rest of the queue.

The batch runner now also performs preflight validation before execution:

- invalid tasks are marked `invalid` and blocked before running
- warning-bearing tasks still run, but the warnings are written into the batch artifacts
- rerun from a previous batch now includes both `failed` and `invalid` tasks
- each invalid or warning-bearing task now includes concrete fix suggestions in JSON and Markdown artifacts

Each batch run now also creates a dedicated batch artifact directory with:

- the original batch input
- a summary file
- the full combined result
- a human-readable `batch_report.md`
- one per-item result file

With `--dry-run`, the batch artifacts are still written, but each item is marked as `preview` instead of `success` or `failed`.

If a batch partially fails, you can rerun only the failed tasks from the prior batch result or batch directory.

You can also rerun selected previous batch indexes when you want to reprocess a known subset:

```powershell
python scripts/batch_run_operator_workflows.py `
  --rerun-failed-from "D:\path\previous-batch" `
  --rerun-indexes 1,3 `
  --batch-root "D:\path\rerun-selected"
```

Generate a live assist pack from an existing scene report JSON:

```powershell
python scripts/generate_operator_pack.py `
  --type live-assist `
  --source-report "D:\path\scene-08-report.json" `
  --platform Douyin `
  --market China `
  --output-dir "D:\path\live-pack"
```

## 证据模式

执行前先选一种模式：

- `live-analysis`：当前链接、URL 或公开数据可以立即检查
- `evidence-pack-analysis`：用户已经有截图、表格、导出文件或笔记
- `planning-only`：用户想先确认完整 workflow 与交付物结构

## 不作为直接自动化支持的事项

这个包刻意不实现以下能力：

- 冷启动刷量式的模拟播放、点赞、评论、分享链路
- 竞品评论截流
- 大规模私信转化工作流
- 设备指纹伪装、反检测调参、养号
- 云手机批量控制

如果用户要求这些能力，就把输出降级为：

- 风险说明
- 安全替代工作流
- manual checklist
- prompt pack for human review
