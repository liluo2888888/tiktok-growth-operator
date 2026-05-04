# Automation Workflows

This file describes the durable automation layer for the pure Codex scene pack.

## What The Scripts Do

### `scripts/init_scene_workspace.py`

Creates a run folder with:

- `inputs/`
- `evidence/`
- `outputs/`
- `notes/`
- `run_manifest.json`
- `README.md`

### `scripts/generate_scene_report.py`

Generates one scene report scaffold for a chosen scene and project.

Supports:

- Markdown scaffold output
- JSON scaffold output
- scene-specific section seeds
- intake-aware working context
- operator checklist and common failure modes

### `scripts/render_scene_report.py`

Renders one structured scene report JSON into:

- `md`
- `docx`
- `xlsx`

Current export quality layer includes:

- DOCX cover page and internal section bookmarks
- DOCX section overview links into section anchors
- XLSX stable section-sheet mapping plus `Section Index`
- XLSX native Excel tables on summary, navigation, and list sheets

### `scripts/validate_export_outputs.py`

Runs a durable export regression suite against representative real TikTok scene reports.

It currently validates:

- render success for `md`, `docx`, and `xlsx`
- presence of `Summary`, `Section Overview`, and `Section Index`
- section navigation links and section-sheet back-links
- native Excel table creation on key navigation sheets
- visible DOCX and XLSX text for common mojibake regressions

Example:

```powershell
python scripts/validate_export_outputs.py `
  --output-root "D:\path\export-validation-suite"
```

### `scripts/validate_all_workflows.py`

Runs the main durable validation surface for this package in one command:

- skill-doc and reference validation
- scene preset validation
- capture-pack workflow validation
- export rendering regression validation

Example:

```powershell
python scripts/validate_all_workflows.py
```

For the shortest finished-state operator summary and recommended command order, see `references/final-handoff.md`.

### `scripts/batch_generate_scene_reports.py`

Generates multiple scene report scaffolds from a JSON batch file.

### `scripts/batch_render_scene_reports.py`

Renders multiple structured scene report JSON files in one pass.

### `scripts/validate_scene_presets.py`

Validates that all 19 scenes have a preset and that required preset sections are present.

### `scripts/run_scene_workflow.py`

Creates a lightweight runnable scene workspace and first report scaffold in one command.

Example:

```powershell
python scripts/run_scene_workflow.py `
  --scene 03 `
  --project "Morning Makeup Hook Teardown" `
  --name zao-ba-zhuang-rundown `
  --context-file "D:\path\brief.txt"
```

### `scripts/generate_operator_pack.py`

Generates one direct-use operator pack outside the numbered scene flow.

Supported pack types:

- `publish-prep`
- `live-assist`

It can work in two modes:

1. blank pack generation from direct parameters
2. derived pack generation from a structured scene report JSON

Example:

```powershell
python scripts/generate_operator_pack.py `
  --type publish-prep `
  --source-report "D:\path\scene-12-report.json" `
  --platform Douyin `
  --market China `
  --output-dir "D:\path\publish-pack"
```

### `scripts/start_scene_run.py`

Creates the full durable scene run workspace:

- scene report JSON
- starter rendered outputs
- run manifest
- optional derived operator packs

Example:

```powershell
python scripts/start_scene_run.py `
  --scene 12 `
  --name lip-liner-style-matrix `
  --project "Lip Liner Style Matrix" `
  --platform Douyin `
  --market China
```

Default derived operator packs:

- scenes `09` to `16` -> `publish-prep`
- scenes `08`, `18`, `19` -> `live-assist`

Override example:

```powershell
python scripts/start_scene_run.py `
  --scene 08 `
  --name user-language-live-pack `
  --project "User Language Live Pack" `
  --operator-packs live-assist `
  --platform Douyin `
  --market China
```

### `scripts/start_capture_pack_run.py`

Creates a full durable run directly from a real TikTok capture pack:

- imports the capture pack into a structured scene report JSON
- renders md/docx/xlsx outputs
- optionally derives `publish-prep` or `live-assist`
- writes a run manifest and README

Example for a ranked/creator pack:

```powershell
python scripts/start_capture_pack_run.py `
  --scene 17 `
  --capture-root "D:\path\tiktok-analysis-pack-smoke-20260423f" `
  --name tiktok-official-capture-run `
  --project "TikTok Official Account Creator Distillation" `
  --platform TikTok `
  --market US
```

Example for the hot-video replication pipeline:

```powershell
python scripts/start_capture_pack_run.py `
  --scene 11 `
  --capture-root "D:\path\tiktok-analysis-pack-smoke-20260423f" `
  --name tiktok-hot-video-pipeline `
  --project "TikTok Hot Video Replication Pipeline" `
  --platform TikTok `
  --market US
```

Example for the one-product multi-style matrix:

```powershell
python scripts/start_capture_pack_run.py `
  --scene 12 `
  --capture-root "D:\path\tiktok-analysis-pack-smoke-20260423f" `
  --name tiktok-style-matrix `
  --project "TikTok One Product Multi Style Matrix" `
  --platform TikTok `
  --market US
```

Example for the multi-market localization blueprint:

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

Example for the launch asset family blueprint:

```powershell
python scripts/start_capture_pack_run.py `
  --scene 14 `
  --capture-root "D:\path\tiktok-analysis-pack-smoke-20260423f" `
  --name tiktok-launch-asset-blueprint `
  --project "TikTok Launch Asset Family Blueprint" `
  --platform TikTok `
  --market US
```

Example for the image-translation blueprint:

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

Example for the main-image benchmark blueprint:

```powershell
python scripts/start_capture_pack_run.py `
  --scene 16 `
  --capture-root "D:\path\tiktok-analysis-pack-smoke-20260423f" `
  --name tiktok-main-image-benchmark-blueprint `
  --project "TikTok Main Image Benchmark Blueprint" `
  --platform TikTok `
  --market US
```

Example for a comment/live pack:

```powershell
python scripts/start_capture_pack_run.py `
  --scene 08 `
  --capture-root "D:\path\tiktok-download-validated-20260423" `
  --name tiktok-comment-capture-run `
  --project "TikTok Comment Signal Synthesis" `
  --platform TikTok `
  --market US
```

Default derived operator packs:

- scene `08` -> `live-assist`
- scenes `11`, `12`, `13`, `14`, `15`, `16`, and `17` -> `publish-prep`

The current capture-pack importer supports:

- scene `01`
- scene `03`
- scene `07`
- scene `08`
- scene `09`
- scene `11`
- scene `12`
- scene `13`
- scene `14`
- scene `15`
- scene `16`
- scene `17`
- scene `18`
- scene `19`

Scene `15` remains blueprint-only:

- requires explicit `--target-languages`
- assumes source image text still needs OCR or manual recovery
- outputs hierarchy and localization-risk planning, not final translated image copy

### `scripts/summarize_run_history.py`

Scans `tmp/` manifests and emits a lightweight run dashboard in JSON and Markdown.

Example:

```powershell
python scripts/summarize_run_history.py `
  --output-json "D:\path\run-history.json" `
  --output-md "D:\path\run-history.md" `
  --limit 25
```

### `scripts/run_operator_workflow.py`

Now supports dedicated `board`, `capture-pack`, and `history` modes in addition to `auto`, `scene`, `goal`, and `pack`.

Use this as the preferred operator-facing entrypoint when you already have a real TikTok capture directory:

### `scripts/recommend_entry_board.py`

Provides a transparent board-family recommender on top of the batch preset system.

It does not generate queues by itself. It helps the operator choose the right entry surface across:

- `single`
- `combo`
- `vertical`
- `launch-board`
- `manager-board`
- `cadence-board`

It returns:

- one recommended family
- top board slug suggestions
- matched language signals
- fallback families and board slugs
- one family score breakdown for tuning

Example:

```powershell
python scripts/recommend_entry_board.py `
  --query "I'm the live operator for tonight's session" `
  --format markdown
```

### `scripts/start_entry_board.py`

Turns one natural-language request into one local starter folder for the selected board.

It currently:

- chooses the best entry family
- chooses the top board slug
- copies the selected template and suite config into a local starter directory
- copies local `generate`, `dry-run`, and `run` helper scripts when they exist
- writes one `README.md` plus one `entry-board-recommendation.json`
- can optionally generate the local queue immediately
- can optionally run a local dry-run or full run from the starter directory

Example:

```powershell
python scripts/start_entry_board.py `
  --query "Give me a daily board for TikTok beauty ops" `
  --bundle-root "D:\path\preset-template-bundle"
```

Immediate preview example:

```powershell
python scripts/start_entry_board.py `
  --query "Give me a daily board for TikTok beauty ops" `
  --bundle-root "D:\path\preset-template-bundle" `
  --generate `
  --dry-run
```

Unified-router equivalent:

```powershell
python scripts/run_operator_workflow.py `
  --mode board `
  --query "Give me a daily board for TikTok beauty ops" `
  --bundle-root "D:\path\preset-template-bundle" `
  --generate `
  --dry-run
```

Bundle-aware example:

```powershell
python scripts/recommend_entry_board.py `
  --query "Give me the fastest beauty TikTok ops starter" `
  --bundle-root "D:\path\preset-template-bundle" `
  --format markdown
```

When `--bundle-root` points to a generated preset bundle, the output also includes:

- the resolved starter `template_file`
- the suite root when one exists
- the next `generate`, `dry-run`, and `run` commands

```powershell
python scripts/run_operator_workflow.py `
  --mode capture-pack `
  --scene 08 `
  --capture-root "D:\path\tiktok-download-validated-20260423" `
  --name tiktok-comment-capture-run `
  --project "TikTok Comment Signal Synthesis" `
  --platform TikTok `
  --market US
```

Auto mode now respects `--capture-root` and routes to `capture-pack` before normal scene mode.

History mode exposes the run dashboard from the same unified entrypoint:

```powershell
python scripts/run_operator_workflow.py `
  --mode history `
  --history-output-json "D:\path\run-history.json" `
  --history-output-md "D:\path\run-history.md" `
  --history-limit 25
```

### `scripts/recommend_scene_chain.py`

Maps a goal slug or free-text business goal into a recommended multi-scene sequence.

Example:

```powershell
python scripts/recommend_scene_chain.py `
  --goal competitor-monitoring `
  --format markdown
```

Free-text example:

```powershell
python scripts/recommend_scene_chain.py `
  --query "I want competitor weekly monitoring and creator breakdown" `
  --format markdown
```

The recommender supports two routing modes:

- single-goal recommendation
- built-in multi-goal workflow template matching

### `scripts/start_goal_workflow.py`

Creates a goal-level workspace that expands into multiple scene workspaces.

Example:

```powershell
python scripts/start_goal_workflow.py `
  --goal creative-testing `
  --name creative-testing-run `
  --project "Creative Testing Run" `
  --formats md
```

Free-text template example:

```powershell
python scripts/start_goal_workflow.py `
  --query "I want a Douyin workflow from topic selection to creative testing to publish handoff" `
  --name douyin-topic-to-publish `
  --project "Douyin Topic To Publish" `
  --formats md
```

When a workflow template matches:

- scenes from all component goals are merged into one ordered chain
- duplicate scenes are removed automatically
- derived packs are still generated when any component goal includes them
- the goal `README.md` and `goal_manifest.json` record the matched template and component goals

### `scripts/run_operator_workflow.py`

Provides one unified entrypoint for:

- `scene` mode
- `goal` mode
- `board` mode
- `pack` mode
- `auto` mode

`auto` is the default and routes a natural-language request into scene, goal, board, or pack execution.

The auto-mode result includes a `route` object with explanation fields so the operator can inspect:

- why the request was classified the way it was
- which pack keywords matched
- which scene candidates scored highest
- which board family and board slugs scored highest
- whether multi-stage markers were detected
- which goal or template would win on the goal layer

The scorer now ignores low-signal stopwords so scene and goal previews are less noisy.

### `scripts/batch_run_operator_workflows.py`

Runs a JSON array of mixed workflow tasks in one pass.

Each task can be any of:

- `auto`
- `scene`
- `goal`
- `board`
- `pack`
- `capture-pack`

For the fastest operator-facing command set, keep [direct-use.md](direct-use.md) as the cookbook and [command-map.md](command-map.md) as the short command index. This file is the ownership and behavior reference for how those commands compose.

Example batch file:

```json
[
  {
    "mode": "auto",
    "request": "Run scene 03 for morning makeup hooks and output a teardown report",
    "project": "Morning Makeup Hook Teardown",
    "output_root": "D:\\path\\scene-run"
  },
  {
    "mode": "goal",
    "query": "I want a multi-market workflow from category research to localized launch",
    "name": "localized-launch-workflow",
    "project": "Localized Launch Workflow",
    "output_root": "D:\\path\\goal-run"
  },
  {
    "mode": "board",
    "query": "I'm the live operator for tonight's session",
    "bundle_root": "D:\\path\\preset-template-bundle",
    "name": "live-operator-board-batch-item",
    "output_root": "D:\\path\\board-run"
  },
  {
    "mode": "pack",
    "type": "publish-prep",
    "project": "Morning Makeup Sell-Through Video",
    "output_dir": "D:\\path\\pack-run"
  },
  {
    "mode": "capture-pack",
    "scene": "15",
    "capture_root": "D:\\path\\tiktok-analysis-pack-smoke-20260423f",
    "target_languages": "English,Japanese,German",
    "name": "batch-scene15-capture",
    "project": "TikTok Image Translation Blueprint",
    "platform": "TikTok",
    "market": "US",
    "output_root": "D:\\path\\capture-pack-run-scene15"
  },
  {
    "mode": "capture-pack",
    "scene": "08",
    "capture_root": "D:\\path\\tiktok-download-validated-20260423",
    "name": "batch-scene08-capture",
    "project": "TikTok Comment Signal Synthesis",
    "platform": "TikTok",
    "market": "US",
    "output_root": "D:\\path\\capture-pack-run"
  }
]
```

Run it with:

```powershell
python scripts/batch_run_operator_workflows.py `
  --batch-file "D:\path\operator-batch.json" `
  --output-file "D:\path\operator-batch-result.json"
```

Preview the batch without executing the tasks:

```powershell
python scripts/batch_run_operator_workflows.py `
  --batch-file "D:\path\operator-batch.json" `
  --dry-run `
  --batch-root "D:\path\operator-batch-preview"
```

It also creates a batch artifact directory.

Default layout:

```text
<batch-root>/
  batch_input.json
  summary.json
  batch_result.json
  batch_report.md
  items/
    001-success.json
    002-failed.json
    ...
```

You can control the directory with:

- `--batch-root`
- `--batch-name`

By default the batch runner is resilient:

- one failed task does not stop the whole batch
- each item gets `status: success` or `status: failed`
- failed items include `error.type`, `error.message`, and a short `error.trace`
- the top-level payload includes `summary.total`, `summary.success`, `summary.failed`, `summary.by_mode`, and `summary.failed_indexes`

The runner now also performs task-level preflight validation:

- invalid tasks are recorded with `status: invalid`
- invalid tasks are blocked before execution
- warnings are attached when a field is present but would be ignored in the chosen mode
- invalid indexes are recorded in `summary.invalid_indexes`
- validation payloads now include `suggestions` with concrete next-step fixes

The batch artifact directory also includes `batch_report.md`, a human-readable summary that lists:

- top-level success and failure counts
- per-mode counts
- one section per batch item
- key output paths for successful tasks
- short error summaries for failed tasks
- validation warnings and blocked-task errors
- actionable fix suggestions for invalid and warning-bearing tasks

When `--dry-run` is enabled:

- tasks are not executed
- each item is recorded with `status: preview`
- auto-mode items still include route explanation
- board-mode items still show bundle root, top-k, and starter-run flags in preview
- `batch_report.md` shows the would-run mode and intended outputs instead of real generated paths

When rerunning from a prior batch result or directory, the runner now requeues both:

- `failed` tasks
- `invalid` tasks

### `scripts/generate_batch_preset.py`

Generates ready-to-run batch JSON queues for common operator workflows.

Use this when you want a durable preset instead of writing the batch array by hand.

Examples:

```powershell
python scripts/generate_batch_preset.py `
  --preset topic-to-publish `
  --name spring-lip-launch `
  --project "Spring Lip Launch" `
  --product "Velvet Lip Glaze" `
  --category "Beauty" `
  --output "D:\path\topic-to-publish-batch.json"
```

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

See `references/batch-presets.md` for the preset catalog.

You can also merge multiple presets into one operator queue:

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

If a preset declares `product`, `category`, `audience`, or `account_name` as required variables, the generator now blocks output until the corresponding flag is provided.

Each preset generation now creates three operator-facing artifacts:

- the batch JSON queue
- one `.manifest.json` metadata file
- one `.report.md` human-readable queue summary
- one `.input.json` reusable generation-input file
- optionally one starter config template JSON from `--template-output`
- optionally one starter-template bundle directory from `--template-bundle-root`
- three `.ps1` helper scripts for dry-run, execute, and rerun
- three `.cmd` wrappers for the same helper actions
- one `.ps1` regenerate script plus one `.cmd` regenerate wrapper

The template-bundle mode now exports two families:

- `single` templates for each individual preset
- `combo` templates for curated multi-preset boards
- `vertical` templates for seeded business-ready starter boards
- `launch-board` templates for objective-first weekly operator boards
- `manager-board` templates for role-first operator boards
- `cadence-board` templates for rhythm-first operator boards

The bundle index and README record:

- the item slug
- the item type
- the preset list
- the baked ordering
- the required variables and requirements
- optional seeded defaults such as product, market, or capture fixture path

For `vertical` items, bundle export now also creates one suite directory with:

- a copied config JSON for stable reruns
- `generate.ps1/.cmd`
- `dry-run.ps1/.cmd`
- `run.ps1/.cmd`
- a suite-level `README.md`

The preset report is also the execution handoff surface:

- it recommends a `--batch-root`
- it recommends an `--output-file`
- it includes copy-ready dry-run, execute, and rerun commands
- it includes one copy-ready `--config` regeneration command
- it points to runnable helper scripts in both PowerShell and CMD wrapper form

Use `--fail-fast` only when you want the batch to stop on the first failure.

You can also rerun only failed items from a previous batch:

```powershell
python scripts/batch_run_operator_workflows.py `
  --rerun-failed-from "D:\path\previous-batch\batch_result.json"
```

Or rerun from the whole batch artifact directory:

```powershell
python scripts/batch_run_operator_workflows.py `
  --rerun-failed-from "D:\path\previous-batch"
```

If the failed items need corrected fields, provide one override object:

```json
{
  "project": "Recovered Batch Pack",
  "type": "publish-prep"
}
```

Then rerun with:

```powershell
python scripts/batch_run_operator_workflows.py `
  --rerun-failed-from "D:\path\previous-batch" `
  --override-file "D:\path\rerun-override.json"
```

You can also rerun specific prior batch indexes, even if they were not failed:

```powershell
python scripts/batch_run_operator_workflows.py `
  --rerun-failed-from "D:\path\previous-batch" `
  --rerun-indexes 1,3
```

Auto example:

```powershell
python scripts/run_operator_workflow.py `
  --request "I want a multi-market workflow from category research to localized launch" `
  --name localized-launch-workflow `
  --project "Localized Launch Workflow"
```

Scene example:

```powershell
python scripts/run_operator_workflow.py `
  --mode scene `
  --scene 03 `
  --project "Morning Makeup Hook Teardown" `
  --name morning-makeup-teardown
```

Goal example:

```powershell
python scripts/run_operator_workflow.py `
  --mode goal `
  --query "I want a Douyin workflow from topic selection to creative testing to publish handoff" `
  --name douyin-topic-to-publish `
  --project "Douyin Topic To Publish" `
  --formats md
```

Board example:

```powershell
python scripts/run_operator_workflow.py `
  --mode board `
  --query "I'm the live operator for tonight's session" `
  --bundle-root "D:\path\preset-template-bundle"
```

Pack example:

```powershell
python scripts/run_operator_workflow.py `
  --mode pack `
  --type publish-prep `
  --project "Morning Makeup Sell-Through Video" `
  --output-dir "D:\path\publish-pack"
```

## Why This Layer Exists

It removes repeated setup work without pretending to automate the whole business workflow.

The scripts automate:

- scene workspace initialization
- report skeleton generation
- report rendering
- preset validation
- one-command scene workspace plus report setup
- direct operator-pack generation
- goal-level multi-scene workflow expansion
- end-to-end scene-run plus pack generation

They do not automate:

- live TikTok or Douyin crawling
- TikTok Shop or Douyin API calls
- final video or image rendering
- filling the report with conclusions when no evidence was supplied
- cloud-phone publishing
- fake engagement or account-growth manipulation
