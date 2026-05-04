# Scene Report Contract

Use this contract when a scene should become a durable deliverable instead of an ad hoc chat answer.

## Goal

Keep one structured report shape that can be:

- filled directly by Codex
- reviewed by a human
- rendered into `md`, `docx`, or `xlsx`

The scaffold can also start with scene-specific structure instead of a blank generic shell.

That can include:

- scene-specific working-context prompts
- evidence placeholders
- starter tables or comparison grids
- starter numbered workflows

## Canonical Fields

The canonical payload is JSON with these top-level keys:

```json
{
  "metadata": {},
  "working_context": {},
  "executive_summary": {},
  "evidence": [],
  "sections": [],
  "assets": [],
  "notes": [],
  "sources": []
}
```

## Field Rules

### `metadata`

Required practical fields:

- `scene`
- `project`
- `title`
- `deliverable_type`

Recommended fields:

- `scene_slug`
- `scene_title`
- `generated_at`
- `scenario_file`
- `status`

### `working_context`

Use this block to preserve the operator brief and boundaries.

- `summary`: one short project brief
- `inputs`: list of supplied materials
- `minimum_evidence`: smallest acceptable evidence set to proceed
- `ideal_evidence`: stronger evidence set for better output quality
- `constraints`: list of missing data, market limits, or platform limits
- `requested_outputs`: list of what the user explicitly wants
- `ready_checklist`: quick operator checklist before treating the scene as runnable

### `executive_summary`

Always keep this block short and decisive.

- `conclusion`
- `why_it_matters`
- `next_action`
- `confidence`

### `operator_guide`

Use this block to make the scene executable for a human operator.

- `operator_checklist`: flat list of must-do operating actions
- `common_failure_modes`: flat list of ways this scene often goes wrong

### `evidence`

Use for links, screenshots, exports, observations, or quoted user evidence.

Each item:

```json
{
  "label": "Top candidate 1",
  "detail": "1.2M views in 3 days with product demo in first 2 seconds",
  "source": "https://example.com/video-1"
}
```

### `sections`

Each section is the main reusable delivery unit.

```json
{
  "heading": "Shared Pattern Summary",
  "instruction": "Optional fill guidance",
  "paragraphs": [],
  "bullets": [],
  "numbered": [],
  "table": {
    "title": "",
    "headers": [],
    "rows": []
  }
}
```

Use:

- `paragraphs` for explanation
- `bullets` for scan-friendly conclusions
- `numbered` for workflows or ordered logic
- `table` for shortlist, matrix, dashboard, or benchmarking output

### `assets`

Use for local files that support the report.

```json
{
  "label": "Hook screenshot",
  "path": "D:\\path\\frame-001.png",
  "note": "First-frame product reveal"
}
```

### `notes`

Use for reviewer notes, caveats, or follow-up items that do not belong in the main narrative.

### `sources`

Use for compact source provenance such as:

- user docx name
- website page name
- live browser search
- local export filename

## Deliverable-Type Mapping

Use the default seeded sections from `scripts/generate_scene_report.py`.

- `collection_board`: collection and tracking oriented sections
- `breakdown_report`: teardown and formula extraction sections
- `insight_report`: market judgment and recommendation sections
- `creation_brief`: creation target, audience, message, and constraints
- `testing_matrix`: invariant, variables, expected effects, and learning agenda

## Scene-Specific Presets

Scene-aware starter structures live in:

- `scripts/scene_report_presets.py`
- `scripts/validate_scene_presets.py`

Use this file when you want to make one scene more directly usable without changing the top-level contract.

## Example

Reference example:

- [scene-report-example.json](scene-report-example.json)

## Rendering Workflow

1. Generate a scaffold JSON:

```powershell
python scripts/generate_scene_report.py `
  --scene 03 `
  --project "lip combo US" `
  --output ".\tmp\scene-03-lip-combo-us.json" `
  --format json
```

2. Fill the JSON with real evidence and conclusions.

3. Render deliverables:

```powershell
python scripts/render_scene_report.py `
  --input ".\tmp\scene-03-lip-combo-us.json" `
  --output-dir ".\tmp\rendered" `
  --formats md,docx,xlsx
```
