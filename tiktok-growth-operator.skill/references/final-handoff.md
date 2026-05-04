# Final Handoff

Use this file as the shortest durable entrypoint for the finished Codex-native TikTok Growth Operator package.

## What Is Finished

This package now provides:

- one unified Codex-native operator surface across 19 scenes
- real TikTok capture-pack ingestion for supported scenes
- durable report rendering to `md`, `docx`, and `xlsx`
- derived `publish-prep` and `live-assist` handoff packs where appropriate
- repeatable validation for scene presets, capture-pack workflows, export quality, and core skill docs
- one transparent entry selector for choosing among single/combo/vertical/launch/manager/cadence boards
- one unified `board` entry mode that can scaffold a local starter folder from the main operator router

## Reference Roles

Use the reference set by role:

- `final-handoff.md`: shortest finished-state summary and recommended entrypoints
- `direct-use.md`: operator-facing command cookbook
- `automation-workflows.md`: script ownership and automation behavior
- `batch-presets.md`: preset queue generation and suite export
- `entry-selector.md`: which board family and slug to use before queue generation
- `command-map.md`: public Clipcat parity notes only

Use `direct-use.md` for copy-ready commands first. Use `automation-workflows.md` only when you need the batch JSON contract, rerun semantics, or validator behavior behind those commands.

## Best Entrypoints

Use these first.

### One-shot real TikTok capture run

```powershell
python scripts/start_capture_pack_run.py `
  --scene 17 `
  --capture-root "D:\path\tiktok-analysis-pack-smoke-20260423f" `
  --name tiktok-official-capture-run `
  --project "TikTok Official Account Creator Distillation" `
  --platform TikTok `
  --market US
```

### Unified operator router

```powershell
python scripts/run_operator_workflow.py `
  --request "Run scene 03 for morning makeup hooks and output a teardown report" `
  --project "Morning Makeup Hook Teardown"
```

### Board selector

```powershell
python scripts/recommend_entry_board.py `
  --query "Set up my weekly competitor review" `
  --format markdown
```

### One-step starter scaffold

```powershell
python scripts/start_entry_board.py `
  --query "Give me a daily board for TikTok beauty ops"
```

Unified-router version:

```powershell
python scripts/run_operator_workflow.py `
  --mode board `
  --query "Give me a daily board for TikTok beauty ops"
```

Preview-ready version:

```powershell
python scripts/start_entry_board.py `
  --query "Give me a daily board for TikTok beauty ops" `
  --generate `
  --dry-run
```

Pinned-bundle version when you do not want auto-discovery:

```powershell
python scripts/recommend_entry_board.py `
  --query "Give me a daily board" `
  --bundle-root "D:\path\preset-template-bundle" `
  --format markdown
```

For more board-family examples and selector rules, see [entry-selector.md](entry-selector.md).

### Full durable validation

```powershell
python scripts/validate_all_workflows.py
```

## Export Quality Status

Current `docx` export quality includes:

- cover page with deliverable banner and metadata block
- table of contents field
- section overview with internal links
- explicit section return links back to contents and overview
- repeated table headers for long tables
- image captions for embedded asset previews

Current `xlsx` export quality includes:

- `Summary`, `Section Overview`, and `Section Index`
- stable section-sheet naming even when headings repeat
- native Excel tables on key sheets
- top-line volume dashboard cards
- second-line quality status cards for empty sections and missing evidence/assets
- section-to-index and index-to-section navigation links

## Validation Surface

The durable validation layer is:

- `scripts/validate_skill_docs.py`
- `scripts/validate_scene_presets.py`
- `scripts/validate_capture_pack_workflows.py`
- `scripts/validate_export_outputs.py`
- `scripts/validate_all_workflows.py`

`validate_export_outputs.py` covers both:

- representative real TikTok reports
- synthetic duplicate-heading and sparse-section edge cases

`validate_all_workflows.py` now covers both:

- board preview routing and preview-field assertions inside batch mode
- one hermetic board execute smoke that scaffolds a starter, generates a queue, and performs board-local dry-run output checks
- route regressions for weekly-review, Chinese cadence-board, hybrid vertical-cadence-board, and multi-stage goal requests
- long free-text goal routing with bounded `run_name` output for safer Windows path lengths

## Real Validation Fixtures

The strongest current real TikTok validation inputs are:

- ranked/account pack: `captures/tiktok-analysis-pack-smoke-20260423f`
- comment-bearing pack: `captures/tiktok-download-validated-20260423`

Representative export validation outputs:

- `tiktok-growth-operator.skill/tmp/20260504_validate_all_export_suite`
- `tiktok-growth-operator.skill/tmp/20260504_export_validation_suite_v4`

## Recommended Operator Order

1. Pick `run_operator_workflow.py` for normal use.
2. Use `run_operator_workflow.py --mode board` when the request is role-first, cadence-first, outcome-first, or vertical-first.
3. Use `start_capture_pack_run.py` when a real TikTok capture folder already exists.
4. Use `validate_all_workflows.py` after durable script or rendering changes.
5. Use `validate_export_outputs.py` when the change is export-only.

## Current Boundaries

This package still does not claim:

- platform API automation without credentials
- direct publishing
- fake engagement or account-farming behavior
- fabricated OCR or translated image copy in scene `15`
- unsupported data extraction from capture packs that do not contain the needed evidence

## If Work Continues Later

Prefer this order:

1. docs and operator guidance cleanup
2. visual-only export polish
3. route-eval expansion and fixture hardening
4. broader capture-pack scene coverage only when grounded by real evidence

Do not reopen core exporter structure unless a validation gap or user-visible defect appears.
