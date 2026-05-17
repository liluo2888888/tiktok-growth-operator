# Feishu Setup

Use this file when you want `tiktok-growth-operator.skill` to push scene reports into Feishu.

## Current State

Feishu delivery is already working in this workspace.

Real runtime confirmed on `2026-05-08`:

- direct OpenAPI auth succeeds
- direct Feishu Doc creation succeeds
- direct Feishu Bitable creation and row writes succeed
- bundle push succeeds
- `run_operator_workflow.py --push-feishu` succeeds
- `start_scene_run.py --push-feishu` succeeds
- `start_capture_pack_run.py --push-feishu` succeeds

Verified real outputs created in Feishu:

- Doc:
  - `https://pizvgz6mvgi.feishu.cn/docx/MDe0dLQVmo84WdxvW9Hc7gtsn4c`
  - `https://pizvgz6mvgi.feishu.cn/docx/YzFKdnxFYok5IGxfW8scOP1Kn1f`
  - `https://pizvgz6mvgi.feishu.cn/docx/DDvTdtFi2oho4hxw5KcclQ2Fnlf`
  - `https://pizvgz6mvgi.feishu.cn/docx/LsRRd0rpcoPR8KxfhWucu5dLnqA`
  - `https://pizvgz6mvgi.feishu.cn/docx/MY6HdoxLgoFl8jxI67ec5VlQnMc`
  - `https://pizvgz6mvgi.feishu.cn/docx/X8JtdWVH1owbPbxRTh1cUW4Nnub`
- Bitable:
  - `https://pizvgz6mvgi.feishu.cn/base/RqG9bUWPuaiPceseemGcpMCVnsb`
  - `https://pizvgz6mvgi.feishu.cn/base/TtMmbuahKaNCLYsK9yXc4iyLnIg`
  - `https://pizvgz6mvgi.feishu.cn/base/I1OwbLUrEaJjTMscTTGcm2Mgntd`
  - `https://pizvgz6mvgi.feishu.cn/base/MjlfbW1rCaaQA6sQT5zckGlRnpe`
  - `https://pizvgz6mvgi.feishu.cn/base/WJovbxFQ7afmFOsnWdDcmqhPnId`

Current default runtime decision:

- primary path: direct OpenAPI
- optional fallback: local `lark-cli`

Why:

- the direct OpenAPI path is already verified end to end
- `lark-cli` works locally but Hermes-backed auth can still give false `app secret invalid`

## What You Need

Before running the scripts, prepare:

1. A Feishu self-built app in Open Platform.
2. Its `App ID`.
3. Its `App Secret`.
4. These scopes enabled and approved:
   - `docx:document`
   - `docx:document:create`
   - `bitable:app`
   - `base:app:create`

## Environment Variables

In PowerShell:

```powershell
$env:FEISHU_APP_ID="cli_xxx"
$env:FEISHU_APP_SECRET="xxx"
```

Session-only is fine for the first run.

## Fastest Paths

### 1. Push One Finished Report As Both Doc And Bitable

```powershell
python scripts/push_report_to_feishu_bundle.py `
  --input "D:\path\scene-18-report.json" `
  --app-id $env:FEISHU_APP_ID `
  --app-secret $env:FEISHU_APP_SECRET `
  --title "竞品账号周报 | 2026-W19" `
  --base-name "竞品账号周报 | 2026-W19"
```

What it does:

- creates one Feishu Doc
- creates one Feishu Bitable
- pushes default Bitable slices for the same report

### 2. Push One Finished Report As Doc Only

```powershell
python scripts/push_report_to_feishu_doc.py `
  --input "D:\path\scene-18-report.json" `
  --mode create `
  --title "竞品账号周报 | 2026-W19" `
  --backend api
```

### 2.1 Push Several Existing Scene JSON Files As Chinese Finished Docs

Use this when you already have several scene report JSON files on disk and want to batch repush them into Feishu Docs without rebuilding a `batch_result.json`:

```powershell
$env:FEISHU_APP_ID="cli_xxx"
$env:FEISHU_APP_SECRET="xxx"
python scripts/push_scene_reports_to_feishu_doc.py `
  --inputs "D:\path\scene-01-report.json" "D:\path\scene-08-report.json" `
  --app-id $env:FEISHU_APP_ID `
  --app-secret $env:FEISHU_APP_SECRET `
  --title-prefix "中文成品复推"
```

What it does:

- creates one Feishu Doc per input JSON
- uses the same Chinese finished-doc renderer as `push_report_to_feishu_doc.py`
- auto infers the scene label when standalone spot-check JSON lacks `metadata.scene`

If you want the currently confirmed real-scene bundle without manually listing inputs:

```powershell
$env:FEISHU_APP_ID="cli_xxx"
$env:FEISHU_APP_SECRET="xxx"
python scripts/push_scene_reports_to_feishu_doc.py `
  --confirmed `
  --app-id $env:FEISHU_APP_ID `
  --app-secret $env:FEISHU_APP_SECRET `
  --title-prefix "中文成品复推"
```

Append to an existing doc:

```powershell
python scripts/push_report_to_feishu_doc.py `
  --input "D:\path\scene-18-report.json" `
  --mode append `
  --doc "https://xxx.feishu.cn/docx/xxxx" `
  --title "竞品账号周报 | 2026-W19" `
  --backend api
```

### 3. Push One Finished Report As Bitable Only

```powershell
python scripts/push_report_to_feishu.py `
  --input "D:\path\scene-18-report.json" `
  --mode summary `
  --base-name "竞品账号周报 | 2026-W19"
```

Then reuse the returned `app_token`:

```powershell
python scripts/push_report_to_feishu.py `
  --input "D:\path\scene-18-report.json" `
  --mode section_overview `
  --app-token "bascn_xxx"
```

```powershell
python scripts/push_report_to_feishu.py `
  --input "D:\path\scene-18-report.json" `
  --mode evidence `
  --app-token "bascn_xxx"
```

```powershell
python scripts/push_report_to_feishu.py `
  --input "D:\path\scene-18-report.json" `
  --mode assets `
  --app-token "bascn_xxx"
```

## Native Auto-Push From Workflow Entrypoints

### Unified Runner

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

### Native Scene Run

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

### Native Capture-Pack Run

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

## Recommended Naming By High-Value Scene

- Scene `01`: `爆款视频采集 | <topic> | <market> | <date>`
- Scene `02`: `日常巡检 | <category> | <market> | <date>`
- Scene `03`: `批量爆款深拆 | <topic> | <market> | <date>`
- Scene `18`: `竞品账号周报 | <category> | <market> | <week>`
- Scene `19`: `自家账号复盘优化 | <account> | <market> | <week>`

Use the same string for:

- `--feishu-title`
- `--feishu-base-name`

That keeps Doc and Bitable surfaces aligned.

## Transient Retry Behavior

One real transient Feishu Docs API error was observed:

- code `10071`

The shared helper now retries once automatically for workflow entrypoints.

Implication:

- if `start_scene_run.py`, `start_capture_pack_run.py`, or `run_operator_workflow.py` hits that transient once, it should recover automatically
- if a standalone doc push still fails, retry once before treating it as a real blocker

## Optional Local Official CLI

The official CLI is already downloaded locally:

- `E:\飞书\lark-cli-bin\v1.0.25\lark-cli.exe`

It remains optional.

Try it only when you explicitly want the CLI path:

```powershell
python scripts/push_report_to_feishu_doc.py `
  --input "D:\path\scene-18-report.json" `
  --mode create `
  --title "竞品账号周报 | 2026-W19" `
  --backend lark-cli `
  --identity bot
```

If the current workspace is not bound:

```powershell
python scripts/setup_hermes_feishu_env.py
& "E:\飞书\lark-cli-bin\v1.0.25\lark-cli.exe" config bind --identity bot-only
```

## Troubleshooting

### Auth fails

Check:

- `App ID`
- `App Secret`
- whether the app is available in the current tenant

### Permission denied

Check:

- whether the scopes are enabled for app identity
- whether approval is completed in Open Platform
- the exact missing-scope message printed by the script

### Which path should I use first

Use this order:

1. `push_report_to_feishu_bundle.py`
2. `push_report_to_feishu_doc.py --backend api`
3. `push_report_to_feishu.py --mode summary`
4. native `--push-feishu` from the workflow entrypoints
