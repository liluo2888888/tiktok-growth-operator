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
  "operator_guide": {},
  "execution_template": {},
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

When a major finding must remain reviewable, prefer adding a compact `evidence_ref` inside the relevant table row or paragraph. Recommended fields:

```json
{
  "source_type": "video | comment | creator | account_week | transcript | screenshot",
  "source_id": "video id, comment id, or local fixture key",
  "source_url": "https://example.com/video-1",
  "time_range": "00:00-00:03",
  "excerpt": "short quoted or paraphrased supporting evidence"
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
  "evidence_refs": [],
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
- `evidence_refs` for section-local proof objects that must survive review and export
- `table` for shortlist, matrix, dashboard, or benchmarking output

Recommended `evidence_refs` row shape:

```json
{
  "source_type": "video | comment | creator | account_week | transcript | screenshot",
  "source_id": "video id, comment id, or local fixture key",
  "source_url": "https://example.com/video-1",
  "time_range": "00:00-00:03",
  "excerpt": "short quoted or paraphrased supporting evidence",
  "supports": "which section claim, row, or finding this evidence supports"
}
```

### `execution_template`

Use this block when the scene should be directly runnable as a Codex prompt or workflow template instead of only a report scaffold.

- `recommended_request`: one natural-language request the operator can reuse directly
- `recommended_request_zh`: one Chinese natural-language request the operator can reuse directly
- `recommended_runner_args`: concrete local script entrypoints for this scene
- `variable_inputs`: named inputs with meaning, example, and whether they are required
- `codex_prompt_scaffold`: flat lines that can be copied into a Codex request
- `codex_prompt_scaffold_zh`: flat Chinese lines that can be copied into a Codex request
- `workflow_steps`: ordered execution steps for the operator
- `output_checklist`: what must be true before the operator treats the scene output as complete

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

## Public-Parity Notes For High-Value Scenes

The May 8, 2026 parity pass tightened several scene-specific expectations using the reviewed DOCX bundle plus public Clipcat surfaces.

### Scene `04` expected blocks

- timeline table should be close to:
  - `Time Range | Scene Type | Visual Content | Spoken / On-Screen Script | Role In Conversion | Asset / Talent Needed | Evidence Ref`
- add one mechanism breakdown table, not only freeform bullets:
  - `Mechanism Layer | Observed Pattern | Why It Works | Failure Mode If Removed | Evidence Ref`
- include BGM analysis
- include a three-part viral interpretation:
  - opening hook
  - conversion rhythm
  - visual style
- support no-voiceover videos explicitly
- label the video type for downstream reuse
- include one production-spec handoff table close to:
  - `Beat / Shot | What Must Happen | Purpose | Subtitle / VO Beat | Proof Block | Asset / Talent Needed | Confidence`

### Scene `05` expected blocks

- keep a generator-ready brief schema with:
  - `Style`
  - `Environment`
  - `Tone & Pacing`
  - `Camera`
  - `Lighting`
  - `Character`
  - `Shots`
  - `Background Sound`
  - `Transition / Editing`
- include shot-level rows, not only one top-level prompt
- shot-level rows may also include an `Asset Need` column when the scene is intended to hand off into production or render planning
- generator-ready brief rows may also include a `Generator Handoff Field` column so the output can map more directly into downstream render or editing systems
- include both:
  - inferred original brief
  - adapted brief for the user's product
- preserve field-level low-confidence marking
- adapted brief tables may include an explicit generator-handoff field when the output is meant for downstream model or production routing
- include one direct production handoff block close to:
  - `Delivery Block | What Must Be Finalized | Who Uses It | Blocking Gap | Next Owner`

### Scene `17` expected blocks

- include an account overview layer before formula distillation
- compare high-interaction and low-interaction samples
- output reusable hook formulas and pacing models
- keep visual style, BGM, hashtag, and posting-time sections visible
- end with a new-script bridge or adaptation path

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
