# Direct Use

Use this file when the user wants Codex to run the TikTok or Douyin workflow directly instead of relying on Clipcat or OpenClaw.

If you only need the finished-state summary, preferred commands, validation entrypoints, and real fixture paths, read [final-handoff.md](final-handoff.md) first.

## Default Rule

Treat this package as:

- a Codex-native router for the 19 scenes
- a report and workspace generator
- a planning and evidence-synthesis system
- a handoff-pack generator for publish preparation and live assist
- a goal-workflow expander for multi-scene business requests
- a unified workflow runner for scene, goal, and pack modes
- an auto router that can infer scene, goal, or pack from one natural-language request
- a board selector that can recommend the best preset family and board slug before generation

Do not pretend the workspace already has:

- Douyin official API credentials
- cloud-phone clusters
- RPA templates that can safely publish, comment, or message users

## Fastest Invocation Paths

If you do not know which board family to start with, run the transparent selector first:

```powershell
python scripts/recommend_entry_board.py `
  --query "I need a publish plan for this week" `
  --format markdown
```

If you already generated a template bundle and want the selector to return real local template and suite paths:

```powershell
python scripts/recommend_entry_board.py `
  --query "Give me a daily board" `
  --bundle-root "D:\path\preset-template-bundle" `
  --format markdown
```

If you skip `--bundle-root`, the selector will try to auto-discover the latest local `preset-template-bundle*` export.

Use [entry-selector.md](entry-selector.md) for the family-level rule of thumb across `single`, `combo`, `vertical`, `launch-board`, `manager-board`, and `cadence-board`.

If you want the package to choose a board and scaffold one local starter folder in one step:

```powershell
python scripts/start_entry_board.py `
  --query "Give me a daily board for TikTok beauty ops" `
  --bundle-root "D:\path\preset-template-bundle"
```

One-step starter plus queue generation and preview:

```powershell
python scripts/start_entry_board.py `
  --query "Give me a daily board for TikTok beauty ops" `
  --bundle-root "D:\path\preset-template-bundle" `
  --generate `
  --dry-run
```

### In Codex chat

Examples:

- `Run scene 03 for morning makeup hooks and output a teardown report`
- `Run scene 08 and summarize audience pain points from four competitor comment sets`
- `Build a full Douyin workflow from topic selection to publish handoff`

### In the local shell

Create a lightweight scene workspace and report:

```powershell
python scripts/run_operator_workflow.py `
  --request "Run scene 03 for morning makeup hooks and output a teardown report" `
  --project "Morning Makeup Hook Teardown"
```

Create the full durable scene run with starter outputs:

```powershell
python scripts/start_scene_run.py `
  --scene 12 `
  --name lip-liner-style-matrix `
  --project "Lip Liner Style Matrix" `
  --platform Douyin `
  --market China
```

Create a full durable run directly from a real TikTok capture pack:

```powershell
python scripts/start_capture_pack_run.py `
  --scene 17 `
  --capture-root "D:\path\tiktok-analysis-pack-smoke-20260423f" `
  --name tiktok-official-capture-run `
  --project "TikTok Official Account Creator Distillation" `
  --platform TikTok `
  --market US
```

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

Batch version:

```powershell
python scripts/batch_run_operator_workflows.py `
  --batch-file "D:\path\capture-batch.json" `
  --output-file "D:\path\capture-batch-result.json"
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

Run the full durable validation surface after broader workflow changes:

```powershell
python scripts/validate_all_workflows.py
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

Current templates:

- `topic-to-publish` -> `category-entry + creative-testing + publish-handoff`
- `competitor-weekly-and-breakdown` -> `competitor-monitoring`
- `account-retro-to-next-test` -> `account-improvement`
- `viral-to-testing` -> `viral-discovery + creative-testing`
- `category-to-localized-launch` -> `category-entry + localization + publish-handoff`
- `competitor-to-publish` -> `competitor-monitoring + creative-testing + publish-handoff`
- `audience-to-live` -> `category-entry + live-support`
- `weekly-monitor-to-next-test` -> `competitor-monitoring + account-improvement`

Current higher-level board families:

- `combo` -> reusable multi-preset bundles such as `beauty-ops-board`
- `vertical` -> seeded starters such as `beauty-us-ops-starter`
- `launch-board` -> outcome-first boards such as `publish-week-board`
- `manager-board` -> role-first boards such as `growth-operator-board`
- `cadence-board` -> rhythm-first boards such as `weekly-ops-board`

Create a full multi-scene goal workspace:

```powershell
python scripts/run_operator_workflow.py `
  --request "I want a Douyin workflow from topic selection to creative testing to publish handoff" `
  --name douyin-growth-workflow `
  --project "Douyin Growth Workflow" `
  --formats md
```

When a query matches a workflow template:

- scenes from all component goals are merged into one ordered chain
- duplicate scenes are removed automatically
- derived packs such as `publish-prep` or `live-assist` still generate from the merged workflow
- the generated `README.md` and `goal_manifest.json` record the matched template and component goals

The current built-in goal templates are documented in `references/goal-templates.md`.

## Article-Derived Safe Replacements

When the user refers to the Tencent Cloud article about OpenClaw and Douyin, translate it into these Codex-native paths:

- intelligent topic selection -> scenes `01`, `02`, `03`, `07`
- AI video brief generation -> scenes `09`, `10`, `11`, `12`, `13`, `14`, `15`, `16`
- competitor monitoring and review -> scenes `06`, `17`, `18`
- comment mining and audience language extraction -> scene `08`
- account retro and next-step planning -> scene `19`
- publish preparation -> workspace generation plus title, hook, cover, and checklist outputs
- live assist -> monitoring templates, moderator reply prompts, and anomaly checklists

## Direct Pack Generation

Generate a publish prep pack:

```powershell
python scripts/run_operator_workflow.py `
  --request "Create a publish prep pack for a morning makeup sell-through video" `
  --project "Morning Makeup Sell-Through Video" `
  --platform Douyin `
  --market China `
  --output-dir "D:\path\publish-pack"
```

Generate a publish prep pack from an existing scene report JSON:

```powershell
python scripts/generate_operator_pack.py `
  --type publish-prep `
  --source-report "D:\path\scene-03-report.json" `
  --platform Douyin `
  --market China `
  --output-dir "D:\path\publish-pack"
```

Generate a live assist pack:

```powershell
python scripts/run_operator_workflow.py `
  --request "Create a live assist pack for an evening skincare live session" `
  --project "Evening Skincare Live Session" `
  --platform Douyin `
  --market China `
  --output-dir "D:\path\live-pack"
```

## Auto Routing Rules

`scripts/run_operator_workflow.py` now defaults to `--mode auto`.

Routing priority:

- explicit `--scene`, `--goal`, or `--type` always wins
- pack-like requests are routed to `pack` when the request is clearly about publish or live packs
- single-scene requests are routed to `scene` when the request names a scene number or strongly matches one scene
- everything else is routed to `goal`, then matched against built-in workflow templates or single-goal chains

The auto result now includes route explanation fields:

- `route.reason`
- `route.explanation.reasons`
- `route.explanation.pack_scores`
- `route.explanation.scene_preview`
- `route.explanation.goal_preview`
- `route.explanation.multi_stage`

Use these when you want to inspect why the request was routed into `scene`, `goal`, or `pack`.

Recommended pattern:

- use `--request` for natural-language routing
- add `--type` only when you want to force a specific pack type instead of relying on auto detection
- add `--project` when you want a cleaner workspace name
- add `--name` only when you need an exact run folder slug

## Batch Execution

When you want to queue multiple mixed tasks at once, use:

```powershell
python scripts/batch_run_operator_workflows.py `
  --batch-file "D:\path\operator-batch.json" `
  --output-file "D:\path\operator-batch-result.json"
```

If you do not want to hand-write the batch JSON, generate one from a preset first:

```powershell
python scripts/generate_batch_preset.py `
  --preset topic-to-publish `
  --name spring-lip-launch `
  --project "Spring Lip Launch" `
  --product "Velvet Lip Glaze" `
  --category "Beauty" `
  --output "D:\path\topic-to-publish-batch.json"
```

If you want a fill-in template before generating the real queue, create a starter config first:

```powershell
python scripts/generate_batch_preset.py `
  --preset competitor-to-publish,audience-to-live,tiktok-account-watch-capture `
  --ordering mode `
  --template-output "D:\path\beauty-ops-board.template.json"
```

If you want a whole preset-template board up front, export a template bundle:

```powershell
python scripts/generate_batch_preset.py `
  --template-bundle-root "D:\path\preset-template-bundle"
```

That bundle now includes:

- one template per single preset
- curated combo templates such as `beauty-ops-board` and `topic-to-publish-board`
- seeded vertical starters such as `beauty-us-ops-starter`
- one `template-index.json` file marking each item as `single`, `combo`, or `vertical`
- one `README.md` with fill-and-run instructions

Use vertical starters when you want a near-runnable baseline with seeded platform, market, naming, and capture fixture values already filled.

If the bundle includes `vertical-suites/`, you can skip manual command assembly and use the suite-level scripts directly.

The same suite pattern now applies to `launch-board` items when you want an outcome-first entry such as `publish-week-board` or `competitor-review-board`.

It now also applies to `manager-board` items when you want a role-first entry such as `content-operator-board` or `growth-operator-board`.

It also applies to `cadence-board` items when you want a rhythm-first entry such as `daily-ops-board` or `weekly-ops-board`.

To turn one combo template into a real queue, fill the generated JSON and run:

```powershell
python scripts/generate_batch_preset.py `
  --config "D:\path\preset-template-bundle\beauty-ops-board.template.json"
```

To turn one seeded vertical starter into a queue, you can often run it directly and then adjust from the generated board:

```powershell
python scripts/generate_batch_preset.py `
  --config "D:\path\preset-template-bundle\beauty-us-ops-starter.template.json"
```

Or use the exported suite scripts:

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

## Evidence Modes

Choose one mode before execution:

- `live-analysis`: current links, URLs, or public data can be checked now
- `evidence-pack-analysis`: the user has screenshots, spreadsheets, exports, or notes
- `planning-only`: the user wants the exact workflow and deliverable shape first

## Not Supported As Direct Automation

This package intentionally does not implement:

- simulated view, like, comment, or share chains for cold-start boosting
- competitor comment hijacking
- mass private-message conversion workflows
- device fingerprint spoofing, anti-detection tuning, or account farming
- cloud-phone fleet control

If the user asks for one of those, downgrade the output to:

- risk explanation
- safe alternative workflow
- manual checklist
- prompt pack for human review
