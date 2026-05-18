# Batch Presets

Use this file when you want one reusable batch queue without hand-writing the JSON array.

## Why This Exists

The package already supports mixed batch execution, dry-run preview, validation, recovery, and remediation.

The next operator bottleneck is queue authoring. Many requests repeat the same multi-scene or capture-pack combinations:

- topic selection -> publish handoff
- viral teardown -> testing
- competitor monitoring -> publish prep
- audience language -> live support
- real TikTok capture pack -> ranked breakdown or account watch

`scripts/generate_batch_preset.py` turns those repeated patterns into ready-to-run batch JSON files plus a manifest.
It now also emits one human-readable preset report so the operator can inspect the generated queue before running it.

## Script

`scripts/generate_batch_preset.py`

What it does:

- lists available preset slugs
- accepts one reusable JSON config file with `--config`
- can emit one starter config template with `--template-output`
- can emit one starter-template bundle with `--template-bundle-root`
- exports both single-preset starter templates and curated combo-board starter templates
- exports seeded vertical starter boards with business-ready defaults when a reusable operating context is common
- exports launch boards organized by operator outcome such as publish week, competitor review, or localization sprint
- exports manager boards organized by operator role such as content, live, strategy, or growth
- exports cadence boards organized by operating rhythm such as daily, weekly, sprint, or live shift
- generates one batch JSON file for the chosen preset
- can merge several preset slugs into one combined queue
- generates one manifest JSON next to that batch file
- generates one Markdown preset report next to that batch file
- generates one reusable `<name>.input.json` file for regeneration
- assigns output roots for each generated task
- supports both goal-mode presets and capture-pack presets
- supports variable injection such as product, category, audience, and account name
- supports queue ordering strategies for combined preset output

## List Presets

```powershell
python scripts/generate_batch_preset.py --list
```

## Generate From A Saved Config

```powershell
python scripts/generate_batch_preset.py `
  --config "D:\path\beauty-ops-board.input.json"
```

## Generate A Starter Config Template

```powershell
python scripts/generate_batch_preset.py `
  --preset competitor-to-publish,audience-to-live,tiktok-account-watch-capture `
  --ordering mode `
  --template-output "D:\path\beauty-ops-board.template.json"
```

## Generate A Template Bundle

Export one starter template per preset plus curated combo-board templates:

```powershell
python scripts/generate_batch_preset.py `
  --template-bundle-root "D:\path\preset-template-bundle"
```

Export starter templates only for a chosen subset. In subset mode, combo templates are included only when every preset required by that combo is present in the subset:

```powershell
python scripts/generate_batch_preset.py `
  --preset topic-to-publish,competitor-to-publish,tiktok-account-watch-capture `
  --template-bundle-root "D:\path\preset-template-bundle"
```

Fill one generated `*.template.json`, then turn it into a real queue:

```powershell
python scripts/generate_batch_preset.py `
  --config "D:\path\preset-template-bundle\beauty-ops-board.template.json"
```

If you want a mostly ready starter board, use one of the seeded vertical templates from the bundle and generate directly from it:

```powershell
python scripts/generate_batch_preset.py `
  --config "D:\path\preset-template-bundle\beauty-us-ops-starter.template.json"
```

## Generate A Goal Preset

```powershell
python scripts/generate_batch_preset.py `
  --preset topic-to-publish `
  --name spring-lip-launch `
  --project "Spring Lip Launch" `
  --product "Velvet Lip Glaze" `
  --category "Beauty" `
  --output "D:\path\topic-to-publish-batch.json"
```

## Generate A Capture Preset

```powershell
python scripts/generate_batch_preset.py `
  --preset tiktok-ranked-breakdown-capture `
  --name official-account-rank-watch `
  --project "Official Account Rank Watch" `
  --account-name "GlowOfficial" `
  --category "Beauty" `
  --capture-root "D:\path\tiktok-analysis-pack-smoke-20260423f" `
  --output "D:\path\ranked-capture-batch.json"
```

## Generate A Combined Queue

```powershell
python scripts/generate_batch_preset.py `
  --preset competitor-to-publish,audience-to-live,tiktok-account-watch-capture `
  --name beauty-ops-board `
  --project "Beauty Ops Board" `
  --product "Velvet Lip Glaze" `
  --category "Beauty" `
  --audience "Skincare Deal Seekers" `
  --account-name "GlowOfficial" `
  --capture-root "D:\path\tiktok-analysis-pack-smoke-20260423f" `
  --output "D:\path\beauty-ops-board.json"
```

## Ordering Strategies

Use `--ordering` to control the merged queue order:

- `input`: preserve the preset order you typed
- `mode`: group by mode, so goal/scene tasks appear before pack/capture tasks
- `stage`: apply a simple pipeline order across modes and scene ids

Example:

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

## Supported Variables

Current variable flags:

- `--product`
- `--category`
- `--audience`
- `--account-name`

Use `--list` to see which presets expose variables.

If a preset requires one of these variables and you omit it, generation now fails early instead of silently inserting placeholder words.

## Current Presets

- `topic-to-publish`
- `viral-to-testing`
- `category-to-localized-launch`
- `competitor-weekly-and-breakdown`
- `competitor-to-publish`
- `audience-to-live`
- `weekly-monitor-to-next-test`
- `tiktok-ranked-breakdown-capture`
- `tiktok-comment-live-capture`
- `tiktok-account-watch-capture`

## Curated Combo Templates

Current bundle-level combo templates:

- `topic-to-publish-board`
- `viral-testing-board`
- `competitor-to-publish-board`
- `beauty-ops-board`
- `localized-launch-board`
- `weekly-monitor-to-next-test-board`

Each combo template writes:

- one multi-preset `preset` field
- one recommended `ordering`
- the union of required variables
- the union of extra requirements such as `capture_root`

## Vertical Starter Templates

Current seeded vertical starters:

- `beauty-us-ops-starter`
- `beauty-comment-live-starter`
- `douyin-beauty-launch-starter`
- `tiktok-ranked-creator-starter`
- `douyin-competitor-weekly-starter`

Each vertical starter adds:

- one practical `name` and `project`
- one seeded `platform` and `market`
- one seeded business context such as `product`, `category`, `audience`, or `account_name`
- one real local capture fixture when that board depends on `capture_root`

Each vertical starter now also exports one runnable suite under `vertical-suites/<slug>/` with:

- one copied config JSON
- one generate helper script
- one dry-run helper script
- one execute helper script
- one suite README with copy-ready commands

Use vertical starters when you want the fastest path to a runnable board and are comfortable editing from a suggested baseline instead of starting from blank placeholders.

## Launch Boards

Current objective-first launch boards:

- `publish-week-board`
- `comment-to-live-board`
- `competitor-review-board`
- `localization-sprint-board`
- `viral-testing-sprint-board`

Use launch boards when you think in terms of the outcome you need this week rather than which vertical or preset family owns the work.

Like vertical starters, launch boards also export suite directories with copied config, helper scripts, and a suite README.

## Manager Boards

Current role-first manager boards:

- `content-operator-board`
- `live-operator-board`
- `strategy-operator-board`
- `growth-operator-board`

Use manager boards when the most natural entrypoint is the person or responsibility area operating the workflow, not the business vertical or this week's outcome label.

Manager boards also export suite directories with copied config, helper scripts, and a suite README.

## Cadence Boards

Current cadence-first boards:

- `daily-ops-board`
- `weekly-ops-board`
- `launch-sprint-board`
- `live-shift-board`

Use cadence boards when the best entrypoint is the time rhythm of the work rather than the person, the vertical, or the outcome label.

Cadence boards also export suite directories with copied config, helper scripts, and a suite README.

## Output Files

Generating a preset creates:

- one batch JSON file containing the task array
- one `<name>.manifest.json` file describing the preset, defaults, task root, and generated tasks
- one `<name>.report.md` file summarizing presets, variables, mode counts, and the generated task list
- one `<name>.input.json` file capturing the generation inputs for reuse
- optionally one starter config template JSON when you use `--template-output`
- optionally one template bundle directory plus index/report files when you use `--template-bundle-root`
- three helper PowerShell scripts for dry-run, execute, and rerun
- three helper CMD wrappers for the same dry-run, execute, and rerun actions
- one helper PowerShell script to regenerate from the saved input file
- one helper CMD wrapper for regeneration
- one helper PowerShell script to push successful batch results into Feishu after execution
- one helper CMD wrapper for that Feishu push helper

The template bundle index now also records:

- `type: single` or `type: combo`
- `type: vertical`
- `type: launch-board`
- `type: manager-board`
- `type: cadence-board`
- the bundle item slug
- the ordering baked into that starter template
- seeded defaults for vertical starter items
- single/combo/vertical/launch-board/manager-board/cadence-board counts for the whole bundle

The Markdown preset report now also includes:

- a recommended batch artifact directory
- a recommended combined result JSON path
- one ready-to-copy `--dry-run` command
- one ready-to-copy execution command
- one ready-to-copy rerun command for failed or invalid items
- one ready-to-copy `--config` regeneration command
- one ready-to-copy batch-result to Feishu command
- direct script paths for `*.ps1` and `*.cmd` helpers if you do not want to copy commands manually

## Operator Notes

- Presets create queue scaffolding only. They do not bypass evidence requirements.
- Capture presets require a real `--capture-root`.
- Variable-driven presets require their declared variable flags such as `--product`, `--category`, `--audience`, or `--account-name`.
- You can still edit the generated JSON manually before running it through `scripts/batch_run_operator_workflows.py`.

## Feishu Follow-Through Templates

Use these when the queue has already produced one finished scene report JSON and you want a stable Feishu naming pattern.

Recommended rule:

- keep `--feishu-title` and `--feishu-base-name` identical
- include topic or account plus market plus date or week

### Scene 01 Viral Collection

```powershell
python scripts/run_operator_workflow.py `
  --mode scene `
  --scene 01 `
  --project "TikTok Viral Collection" `
  --push-feishu `
  --feishu-app-id $env:FEISHU_APP_ID `
  --feishu-app-secret $env:FEISHU_APP_SECRET `
  --feishu-title "TikTok Viral Collection | Lip Combo | US | 2026-05-08" `
  --feishu-base-name "TikTok Viral Collection | Lip Combo | US | 2026-05-08"
```

### Scene 02 Daily Patrol

Bundle (patrol report + auto-chained Scene 03 on existing capture-pack):

```powershell
python scripts/run_scene0203.py `
  --capture-root "D:\path\your-patrol-capture-pack" `
  --formats md,docx,xlsx
```

Full TikMatrix patrol loop:

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

Then push the generated `scene-02-report.json`:

```powershell
python scripts/push_report_to_feishu_bundle.py `
  --input "D:\path\scene-02-report.json" `
  --app-id $env:FEISHU_APP_ID `
  --app-secret $env:FEISHU_APP_SECRET `
  --title "TikTok Daily Patrol | Beauty | US | 2026-05-08" `
  --base-name "TikTok Daily Patrol | Beauty | US | 2026-05-08"
```

### Scene 03 Viral Deep Teardown

```powershell
python scripts/run_operator_workflow.py `
  --mode scene `
  --scene 03 `
  --project "TikTok Viral Deep Teardown" `
  --push-feishu `
  --feishu-app-id $env:FEISHU_APP_ID `
  --feishu-app-secret $env:FEISHU_APP_SECRET `
  --feishu-title "TikTok Viral Deep Teardown | Lip Combo | US | 2026-05-08" `
  --feishu-base-name "TikTok Viral Deep Teardown | Lip Combo | US | 2026-05-08"
```

### Scene 18 Competitor Weekly

Bundle (Scene 18 + 19 on one multi-week capture-pack):

```powershell
python scripts/run_scene1819.py `
  --capture-root "D:\path\scene18-19-multi-week-account" `
  --preset multiweek `
  --formats md,docx,xlsx
```

Single-scene launcher:

```powershell
python scripts/start_scene_run.py `
  --scene 18 `
  --name tiktok-competitor-weekly `
  --project "TikTok Competitor Weekly" `
  --formats md,docx,xlsx `
  --push-feishu `
  --feishu-app-id $env:FEISHU_APP_ID `
  --feishu-app-secret $env:FEISHU_APP_SECRET `
  --feishu-title "TikTok Competitor Weekly | Beauty | US | 2026-W19" `
  --feishu-base-name "TikTok Competitor Weekly | Beauty | US | 2026-W19"
```

### Scene 19 Account Retro

```powershell
python scripts/start_scene_run.py `
  --scene 19 `
  --name tiktok-account-retro `
  --project "TikTok Account Retro" `
  --formats md,docx,xlsx `
  --push-feishu `
  --feishu-app-id $env:FEISHU_APP_ID `
  --feishu-app-secret $env:FEISHU_APP_SECRET `
  --feishu-title "TikTok Account Retro | GlowOfficial | US | 2026-W19" `
  --feishu-base-name "TikTok Account Retro | GlowOfficial | US | 2026-W19"
```
