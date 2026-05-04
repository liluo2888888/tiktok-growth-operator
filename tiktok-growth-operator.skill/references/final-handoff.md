# Final Handoff

Use this file as the shortest durable entrypoint for the finished Codex-native TikTok Growth Operator package.

## What Is Finished

This package now provides:

- one unified Codex-native operator surface across 19 scenes
- real TikTok capture-pack ingestion for supported scenes
- durable report rendering to `md`, `docx`, and `xlsx`
- derived `publish-prep` and `live-assist` handoff packs where appropriate
- repeatable validation for scene presets, capture-pack workflows, export quality, and core skill docs

## Reference Roles

Use the reference set by role:

- `final-handoff.md`: shortest finished-state summary and recommended entrypoints
- `direct-use.md`: operator-facing command cookbook
- `automation-workflows.md`: script ownership and automation behavior
- `batch-presets.md`: preset queue generation and suite export
- `command-map.md`: public Clipcat parity notes only

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

## Real Validation Fixtures

The strongest current real TikTok validation inputs are:

- ranked/account pack: `captures/tiktok-analysis-pack-smoke-20260423f`
- comment-bearing pack: `captures/tiktok-download-validated-20260423`

Representative export validation outputs:

- `tiktok-growth-operator.skill/tmp/20260504_validate_all_export_suite`
- `tiktok-growth-operator.skill/tmp/20260504_export_validation_suite_v4`

## Recommended Operator Order

1. Pick `run_operator_workflow.py` for normal use.
2. Use `start_capture_pack_run.py` when a real TikTok capture folder already exists.
3. Use `validate_all_workflows.py` after durable script or rendering changes.
4. Use `validate_export_outputs.py` when the change is export-only.

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
3. broader capture-pack scene coverage only when grounded by real evidence

Do not reopen core exporter structure unless a validation gap or user-visible defect appears.
