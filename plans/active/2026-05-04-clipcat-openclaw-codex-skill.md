# Clipcat OpenClaw Codex Skill

## Goal

Create a durable Codex-native skill package that reproduces the Clipcat/OpenClaw TikTok workflow as closely as possible from the provided docs, report, website, and public skill artifacts.

## Scope

- analyze the three provided DOCX files
- analyze the public Clipcat OpenClaw landing page and install artifacts
- identify feature parity, workflow structure, prompts, and integration boundaries
- create one new durable skill package in the correct workspace zone
- include explicit notes for what can be reproduced natively in Codex vs what still depends on Clipcat or external APIs
- expand the pure Codex package with lightweight reusable automation scripts

- out of scope: reverse engineering private backend APIs, shipping a production TikTok uploader, or claiming full parity where external infrastructure is missing

## Steps

1. inspect repo rules and existing related skill patterns
2. extract source materials and public Clipcat artifacts
3. synthesize a feature map and Codex-native runtime design
4. scaffold and author the new skill package
5. expand into 19 directly callable pure-Codex scenes
6. add reusable automation scripts for scene setup and report generation
7. validate scripts and package references

## Decision Log

- Decision: land this as a new `*.skill` package instead of a temp folder.
- Why: the request is for a reusable durable skill, not a one-off run.
- Decision: optimize for workflow parity and public command parity first, then convert to pure Codex scene parity.
- Why: the source system uses proprietary backend capabilities, but the user explicitly wants a Codex-native replacement.
- Decision: add only the smallest durable automation surface now: scene workspace init, single report scaffold, batch report scaffold.
- Why: these remove repeated setup work without pretending to automate unavailable external systems.

## Validation

- Ran: internal markdown/yaml reference existence check
- Result: passed
- Ran: `python -m py_compile` on skill scripts
- Result: passed
- Ran: JSON parse of `references/scene-catalog.json`
- Result: passed
- Ran: smoke execution of `init_scene_workspace.py`
- Result: passed
- Ran: smoke execution of `generate_scene_report.py`
- Result: passed
- Ran: smoke execution of `batch_generate_scene_reports.py`
- Result: passed after fixing UTF-8 BOM handling

## Follow-up

- optional: add richer export scripts for xlsx/docx after the preferred output format stabilizes
- optional: add browser-assisted collection helpers for scenes 1, 2, 3, 6, 18 when a stable evidence intake flow is chosen

## 2026-05-04 Export Upgrade

- Decision: add one structured scene report contract instead of separate ad hoc exporters per scene.
- Why: all 19 scenes already map to five deliverable families, so one JSON contract keeps renderers reusable and avoids template drift.
- Decision: extend scaffold generation to support both Markdown and JSON.
- Why: Markdown is fast for direct use, while JSON becomes the stable interchange format for DOCX/XLSX rendering.

### Added

- `references/scene-report-contract.md`
- `references/scene-report-example.json`
- `scripts/render_scene_report.py`
- `scripts/start_scene_run.py`
- `scripts/batch_render_scene_reports.py`

### Updated

- `scripts/generate_scene_report.py`
- `scripts/batch_generate_scene_reports.py`
- `references/automation-workflows.md`
- `references/deliverable-contracts.md`
- `tiktok-growth-operator.skill/SKILL.md`

## 2026-05-04 Scene Preset Upgrade

- Decision: add a dedicated scene preset module rather than baking 19 scene branches into one script body.
- Why: the user wants directly usable scene templates, and a standalone preset module keeps the contract readable while allowing deeper scene-specific scaffolds.
- Decision: apply the same scene-aware scaffold behavior to both `generate_scene_report.py` and `run_scene_workflow.py`.
- Why: direct-use entrypoints must not fall behind the main generator.

### Added

- `scripts/scene_report_presets.py`
- `scripts/validate_scene_presets.py`

### Updated

- `scripts/generate_scene_report.py`
- `scripts/run_scene_workflow.py`
- `references/scene-report-contract.md`
- `references/automation-workflows.md`
- `references/direct-use.md`
- `tiktok-growth-operator.skill/SKILL.md`

## 2026-05-04 Intake Upgrade

- Decision: extend `working_context` with `minimum_evidence`, `ideal_evidence`, and `ready_checklist`.
- Why: scene templates should not only describe output shape; they should tell the operator when the scene is actually runnable and what evidence is still missing.

### Updated

- `scripts/scene_report_presets.py`
- `scripts/generate_scene_report.py`
- `scripts/render_scene_report.py`
- `scripts/validate_scene_presets.py`
- `references/scene-report-contract.md`

## 2026-05-04 Scene Chain Recommender

- Decision: add a goal-to-scene-chain recommender instead of making the user manually choose scene numbers for common end-to-end workflows.
- Why: the package now has enough scene coverage that the bigger usability problem is orchestration, not missing atomic templates.

### Added

- `scripts/recommend_scene_chain.py`
- `scripts/start_goal_workflow.py`

### Updated

- `references/direct-use.md`
- `references/automation-workflows.md`
- `references/feature-map.md`
- `scripts/recommend_scene_chain.py`

## 2026-05-04 Goal Template Routing

- Decision: add a built-in workflow-template layer on top of the goal recommender.
- Why: real operator requests are often phrased as multi-stage business workflows, not single-goal slugs.
- Decision: record routing lineage in generated goal workspaces.
- Why: once one free-text request expands into several scene chains, the workspace should show which template and component goals created it.

### Added

- `references/goal-templates.md`

### Updated

- `scripts/start_goal_workflow.py`
- `references/direct-use.md`
- `references/automation-workflows.md`
- `references/feature-map.md`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\recommend_scene_chain.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\recommend_scene_chain.py" --query "我想做一个从选题到素材测试再到发布交付的抖音工作流" --format markdown`
- Result: passed and matched template `topic-to-publish`
- Ran: `python "tiktok-growth-operator.skill\scripts\recommend_scene_chain.py" --query "我想做竞品周报和达人拆解" --format markdown`
- Result: passed and matched template `competitor-weekly-and-breakdown`
- Ran: `python "tiktok-growth-operator.skill\scripts\start_goal_workflow.py" --query "我想做一个从选题到素材测试再到发布交付的抖音工作流" --name douyin-topic-to-publish --project "Douyin Topic To Publish" --formats md --output-root "D:\我的文档\Documents\Playground 4\.codex-tmp\goal-workflow-template-smoke"`
- Result: passed and generated one merged goal workspace plus `publish-prep`

## 2026-05-04 Template Expansion And Unified Entrypoint

- Decision: expand the built-in workflow template library beyond three starter routes.
- Why: once the package reached full 19-scene coverage, the next usability gain was routing common business requests without forcing the operator to translate them into goal slugs manually.
- Decision: add one unified workflow runner instead of asking the operator to remember separate scene, goal, and pack commands.
- Why: this reduces direct-use friction while still keeping the durable underlying scripts separate and inspectable.

### Added

- `scripts/run_operator_workflow.py`

### Updated

- `scripts/recommend_scene_chain.py`
- `scripts/run_scene_workflow.py`
- `scripts/start_goal_workflow.py`
- `references/goal-templates.md`
- `references/direct-use.md`
- `references/automation-workflows.md`
- `references/feature-map.md`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\recommend_scene_chain.py" "tiktok-growth-operator.skill\scripts\run_scene_workflow.py" "tiktok-growth-operator.skill\scripts\start_goal_workflow.py" "tiktok-growth-operator.skill\scripts\run_operator_workflow.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\recommend_scene_chain.py" --query "I want a multi-market workflow from category research to localized launch" --format markdown`
- Result: passed and matched template `category-to-localized-launch`
- Ran: `python "tiktok-growth-operator.skill\scripts\run_operator_workflow.py" --mode scene --scene 03 --project "Morning Makeup Hook Teardown" --name morning-makeup-teardown --output-root "D:\我的文档\Documents\Playground 4\.codex-tmp\operator-scene-smoke"`
- Result: passed and created a direct scene workspace
- Ran: `python "tiktok-growth-operator.skill\scripts\run_operator_workflow.py" --mode goal --query "I want a multi-market workflow from category research to localized launch" --name localized-launch-workflow --project "Localized Launch Workflow" --formats md --output-root "D:\我的文档\Documents\Playground 4\.codex-tmp\operator-goal-smoke"`
- Result: passed and created a merged goal workspace plus `publish-prep`
- Ran: `python "tiktok-growth-operator.skill\scripts\run_operator_workflow.py" --mode pack --type publish-prep --project "Localized Launch Workflow" --output-dir "D:\我的文档\Documents\Playground 4\.codex-tmp\operator-pack-smoke"`
- Result: passed and created a direct pack output

## 2026-05-04 Auto Routing Layer

- Decision: make the unified runner default to auto mode instead of requiring the operator to choose scene, goal, or pack manually.
- Why: the next usability bottleneck after unifying commands was still mode selection. The operator should be able to give one natural-language request and let the package route it.
- Decision: prefer transparent heuristics over a hidden classifier.
- Why: the route should remain debuggable in script output and easy to tune inside the package.

### Updated

- `scripts/run_operator_workflow.py`
- `references/direct-use.md`
- `references/automation-workflows.md`
- `references/feature-map.md`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\run_operator_workflow.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\run_operator_workflow.py" --request "Run scene 03 for morning makeup hooks and output a teardown report" --project "Morning Makeup Hook Teardown" --output-root "D:\我的文档\Documents\Playground 4\.codex-tmp\auto-scene-smoke"`
- Result: passed and auto-routed to `scene`
- Ran: `python "tiktok-growth-operator.skill\scripts\run_operator_workflow.py" --request "I want a multi-market workflow from category research to localized launch" --name localized-launch-auto --project "Localized Launch Auto" --output-root "D:\我的文档\Documents\Playground 4\.codex-tmp\auto-goal-smoke"`
- Result: passed and auto-routed to `goal`, matching template `category-to-localized-launch`
- Ran: `python "tiktok-growth-operator.skill\scripts\run_operator_workflow.py" --request "Create a publish prep pack for a morning makeup sell-through video" --project "Morning Makeup Sell-Through Video" --output-dir "D:\我的文档\Documents\Playground 4\.codex-tmp\auto-pack-smoke"`
- Result: passed and auto-routed to `pack`

## 2026-05-04 Route Explainability

- Decision: make auto routing explainable in the output payload instead of returning only the resolved mode.
- Why: once auto mode exists, operators need to see why one request was interpreted as a scene, goal, or pack without reading the source code.

### Updated

- `scripts/run_operator_workflow.py`
- `references/direct-use.md`
- `references/automation-workflows.md`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\run_operator_workflow.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\run_operator_workflow.py" --request "Run scene 03 for morning makeup hooks and output a teardown report" --project "Morning Makeup Hook Teardown" --output-root "D:\我的文档\Documents\Playground 4\.codex-tmp\explain-scene-smoke"`
- Result: passed and returned route explanation for `scene`
- Ran: `python "tiktok-growth-operator.skill\scripts\run_operator_workflow.py" --request "I want a multi-market workflow from category research to localized launch" --name explain-goal-auto --project "Explain Goal Auto" --output-root "D:\我的文档\Documents\Playground 4\.codex-tmp\explain-goal-smoke"`
- Result: passed and returned route explanation for `goal`
- Ran: `python "tiktok-growth-operator.skill\scripts\run_operator_workflow.py" --request "Create a publish prep pack for a morning makeup sell-through video" --project "Morning Makeup Sell-Through Video" --output-dir "D:\我的文档\Documents\Playground 4\.codex-tmp\explain-pack-smoke"`
- Result: passed and returned route explanation for `pack`

## 2026-05-04 Route Signal Cleanup

- Decision: exclude low-signal stopwords from scene and goal preview scoring.
- Why: explainable routing is only useful if the candidate lists are readable and not dominated by generic words such as `a`, `and`, `for`, or `to`.

### Updated

- `scripts/recommend_scene_chain.py`
- `scripts/run_operator_workflow.py`
- `references/automation-workflows.md`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\recommend_scene_chain.py" "tiktok-growth-operator.skill\scripts\run_operator_workflow.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\run_operator_workflow.py" --request "Run scene 03 for morning makeup hooks and output a teardown report" --project "Morning Makeup Hook Teardown" --output-root "D:\我的文档\Documents\Playground 4\.codex-tmp\explain-scene-smoke-v2"`
- Result: passed and the explainable scene candidates became less noisy
- Ran: `python "tiktok-growth-operator.skill\scripts\run_operator_workflow.py" --request "I want a multi-market workflow from category research to localized launch" --name explain-goal-auto-v2 --project "Explain Goal Auto" --output-root "D:\我的文档\Documents\Playground 4\.codex-tmp\explain-goal-smoke-v2"`
- Result: passed and the explainable goal route still matched `category-to-localized-launch`
- Ran: `python "tiktok-growth-operator.skill\scripts\run_operator_workflow.py" --request "Create a publish prep pack for a morning makeup sell-through video" --project "Morning Makeup Sell-Through Video" --output-dir "D:\我的文档\Documents\Playground 4\.codex-tmp\explain-pack-smoke-v2"`
- Result: passed and the explainable pack route no longer selected a misleading fallback scene

## 2026-05-04 Capture-Pack History And Scene 14 Expansion

- Decision: expose run-history dashboards through the same unified operator entrypoints instead of leaving them as a standalone utility only.
- Why: operators should not need to remember a separate command surface just to inspect recent runs and derived packs.
- Decision: extend real TikTok capture-pack support to scene `14` as a launch asset family blueprint, not as a fabricated finished-asset generator.
- Why: the ranked TikTok reference packs are strong enough to define message logic and production priority, but they do not contain owned product assets needed for scenes `13`, `15`, or `16`.

### Updated

- `scripts/run_operator_workflow.py`
- `scripts/start_project_workflow.py`
- `scripts/batch_run_operator_workflows.py`
- `scripts/import_tiktok_capture_pack.py`
- `scripts/validate_capture_pack_workflows.py`
- `references/direct-use.md`
- `references/automation-workflows.md`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\run_operator_workflow.py" "tiktok-growth-operator.skill\scripts\start_project_workflow.py" "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" "tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py" "tiktok-growth-operator.skill\scripts\validate_capture_pack_workflows.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\run_operator_workflow.py" --mode history --history-output-json "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_history_unified_smoke.json" --history-output-md "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_history_unified_smoke.md" --history-limit 5`
- Result: passed and emitted unified-entrypoint history JSON + Markdown outputs
- Ran: `python "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" --batch-file "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_history_batch_tasks.json" --output-file "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_history_batch_result.json"`
- Result: passed and executed a batch `history` task successfully
- Ran: `python "tiktok-growth-operator.skill\scripts\start_capture_pack_run.py" --scene 14 --capture-root "D:\我的文档\Documents\Playground 4\captures\tiktok-analysis-pack-smoke-20260423f" --name scene14-capture-run --project "TikTok Launch Asset Family Blueprint" --platform TikTok --market US --output-root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_capture_runner_scene14" --formats md`
- Result: passed and generated a real TikTok scene `14` blueprint run plus derived `publish-prep`

## 2026-05-04 Run-History Dedup Fix

- Decision: when a temp project root contains both `project_manifest.json` and `run_manifest.json`, count only the project manifest in run history.
- Why: both files describe the same launched workflow root, and double-counting distorts dashboard totals.

### Updated

- `scripts/summarize_run_history.py`
- `scripts/validate_capture_pack_workflows.py`

### Validation

- Ran: `python "tiktok-growth-operator.skill\scripts\summarize_run_history.py" --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp" --limit 50`
- Result: project launcher test root is now counted once instead of once as `project` plus once as `run`

## 2026-05-04 Scene 16 Capture-Pack Expansion

- Decision: extend real TikTok capture-pack support to scene `16` only as a competitor main-image benchmark blueprint.
- Why: the ranked TikTok pack provides competitor-side recognition and cover-click cues, but still does not contain an owned main image needed for a true redesign brief.

### Updated

- `scripts/import_tiktok_capture_pack.py`
- `scripts/validate_capture_pack_workflows.py`
- `references/direct-use.md`
- `references/automation-workflows.md`

### Validation

- Ran: `python "tiktok-growth-operator.skill\scripts\start_capture_pack_run.py" --scene 16 --capture-root "D:\我的文档\Documents\Playground 4\captures\tiktok-analysis-pack-smoke-20260423f" --name scene16-capture-run --project "TikTok Main Image Benchmark Blueprint" --platform TikTok --market US --output-root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_capture_runner_scene16" --formats md`
- Result: passed and generated a real TikTok scene `16` benchmark blueprint plus derived `publish-prep`

## 2026-05-04 Scene 13 Capture-Pack Expansion

- Decision: extend real TikTok capture-pack support to scene `13` only as a multi-market localization blueprint with explicit `target_markets`.
- Why: the ranked TikTok pack can support invariant-versus-localizable planning, but it still cannot justify fabricated translated scripts or market-native copy without owned product and local-language evidence.

### Updated

- `scripts/import_tiktok_capture_pack.py`
- `scripts/start_capture_pack_run.py`
- `scripts/run_operator_workflow.py`
- `scripts/start_project_workflow.py`
- `scripts/batch_run_operator_workflows.py`
- `scripts/validate_capture_pack_workflows.py`
- `references/direct-use.md`
- `references/automation-workflows.md`

### Validation

- Ran: `python "tiktok-growth-operator.skill\scripts\start_capture_pack_run.py" --scene 13 --capture-root "D:\我的文档\Documents\Playground 4\captures\tiktok-analysis-pack-smoke-20260423f" --target-markets "US,Japan,Germany" --name scene13-capture-run --project "TikTok Multi-Market Localization Blueprint" --platform TikTok --market US --output-root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_capture_runner_scene13" --formats md`
- Result: passed and generated a real TikTok scene `13` localization blueprint plus derived `publish-prep`

## 2026-05-04 Mixed Batch Runner

- Decision: add one batch entrypoint that can execute mixed `auto`, `scene`, `goal`, and `pack` tasks from one JSON array.
- Why: the next practical step after single-request auto routing is operations batching. The operator should be able to queue a day's or week's workflow requests in one file.

### Added

- `scripts/batch_run_operator_workflows.py`

### Updated

- `references/automation-workflows.md`
- `references/direct-use.md`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" --batch-file "D:\我的文档\Documents\Playground 4\.codex-tmp\operator-batch-smoke.json" --output-file "D:\我的文档\Documents\Playground 4\.codex-tmp\operator-batch-smoke-result.json"`
- Result: passed and executed one mixed batch containing `auto`, `goal`, and `pack` tasks

## 2026-05-04 Resilient Batch Behavior

- Decision: make batch execution resilient by default so one failed task does not abort the rest.
- Why: real operator queues often contain mixed-quality inputs, and the batch runner should still return useful work from the tasks that can complete.
- Decision: add explicit per-item status and top-level summary fields.
- Why: batch users need fast triage instead of manually diffing which outputs were created.

### Updated

- `scripts/batch_run_operator_workflows.py`
- `references/automation-workflows.md`
- `references/direct-use.md`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" --batch-file "D:\我的文档\Documents\Playground 4\.codex-tmp\operator-batch-invalid-smoke.json" --batch-root "D:\我的文档\Documents\Playground 4\.codex-tmp\batch-invalid-suggestions-smoke"`
- Result: passed and attached repair suggestions to both invalid tasks
- Verified: `D:\我的文档\Documents\Playground 4\.codex-tmp\batch-invalid-suggestions-smoke\batch_result.json`
- Result: invalid tasks included concrete suggestions such as adding `type` or `capture_root`
- Ran: `python "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" --batch-file "D:\我的文档\Documents\Playground 4\.codex-tmp\operator-batch-warning-smoke.json" --dry-run --batch-root "D:\我的文档\Documents\Playground 4\.codex-tmp\batch-warning-suggestions-smoke-v2"`
- Result: passed and attached warning-specific suggestions without blocking the tasks
- Verified: `D:\我的文档\Documents\Playground 4\.codex-tmp\batch-warning-suggestions-smoke-v2\batch_report.md`
- Result: report showed warning lines and one concrete remediation suggestion per task

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" --batch-file "D:\我的文档\Documents\Playground 4\.codex-tmp\operator-batch-invalid-smoke.json" --batch-root "D:\我的文档\Documents\Playground 4\.codex-tmp\batch-invalid-smoke-v2"`
- Result: passed and blocked both invalid tasks before execution
- Verified: `D:\我的文档\Documents\Playground 4\.codex-tmp\batch-invalid-smoke-v2\summary.json`
- Result: summary recorded `invalid: 2` and `invalid_indexes: [1, 2]`
- Verified: `D:\我的文档\Documents\Playground 4\.codex-tmp\batch-invalid-smoke-v2\batch_report.md`
- Result: report showed validation errors and explicit blocked-before-execution status
- Ran: `python "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" --batch-file "D:\我的文档\Documents\Playground 4\.codex-tmp\operator-batch-warning-smoke.json" --dry-run --batch-root "D:\我的文档\Documents\Playground 4\.codex-tmp\batch-warning-smoke"`
- Result: passed and recorded preview-only warnings without blocking the tasks
- Verified: `D:\我的文档\Documents\Playground 4\.codex-tmp\batch-warning-smoke\batch_report.md`
- Result: report showed ignored-parameter warnings for scene and pack preview tasks

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" --batch-file "D:\我的文档\Documents\Playground 4\.codex-tmp\operator-batch-smoke.json" --dry-run --batch-root "D:\我的文档\Documents\Playground 4\.codex-tmp\batch-dry-run-smoke"`
- Result: passed and produced preview-only batch artifacts without executing workflows
- Verified: `D:\我的文档\Documents\Playground 4\.codex-tmp\batch-dry-run-smoke\summary.json`
- Result: summary recorded `preview: 3` with `success: 0` and `failed: 0`
- Verified: `D:\我的文档\Documents\Playground 4\.codex-tmp\batch-dry-run-smoke\batch_report.md`
- Result: report showed would-run mode, routed scene preview, and target output locations

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" --batch-file "D:\我的文档\Documents\Playground 4\.codex-tmp\operator-batch-smoke.json" --batch-root "D:\我的文档\Documents\Playground 4\.codex-tmp\batch-report-smoke"`
- Result: passed and created `batch_report.md`
- Verified: `D:\我的文档\Documents\Playground 4\.codex-tmp\batch-report-smoke\batch_report.md`
- Result: report contained overview totals, per-mode summary, per-item status, and output paths

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" --batch-file "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_capture_batch_validation.json" --batch-root "D:\我的文档\Documents\Playground 4\.codex-tmp\capture-batch-rerun-validation"`
- Result: passed with `2/2` success for `capture-pack` batch execution
- Ran: `python "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" --rerun-failed-from "D:\我的文档\Documents\Playground 4\.codex-tmp\operator-batch-smoke-result.json" --rerun-indexes 1,3 --batch-root "D:\我的文档\Documents\Playground 4\.codex-tmp\rerun-selected-indexes-smoke"`
- Result: passed and reran only the selected prior batch items

## 2026-05-04 Batch Markdown Report

- Decision: make every batch run emit one human-readable Markdown report in addition to JSON artifacts.
- Why: operators should be able to review outcomes, key output paths, and failure summaries without opening raw JSON first.

### Updated

- `scripts/batch_run_operator_workflows.py`
- `references/automation-workflows.md`
- `references/direct-use.md`

## 2026-05-04 Batch Dry Run Preview

- Decision: add a `--dry-run` preview mode to the batch runner.
- Why: large mixed queues need one pre-execution pass so the operator can inspect routing, scenes, pack types, and target outputs before actually running the workflows.

### Updated

- `scripts/batch_run_operator_workflows.py`
- `references/automation-workflows.md`
- `references/direct-use.md`

## 2026-05-04 Batch Preflight Validation

- Decision: add task-level validation before batch execution rather than relying only on runtime failures.
- Why: mixed operator queues should surface missing required fields and ignored parameters early, and should block invalid tasks before they consume execution time.
- Decision: include invalid tasks in rerun recovery together with failed tasks.
- Why: once an operator fixes the bad inputs, recovery should not require rebuilding the batch subset by hand.

### Updated

- `scripts/batch_run_operator_workflows.py`
- `references/automation-workflows.md`
- `references/direct-use.md`

## 2026-05-04 Batch Remediation Suggestions

- Decision: add concrete fix suggestions to batch validation results instead of returning only warnings and errors.
- Why: operators should be able to repair invalid or conflicting tasks directly from the report without re-reading the script contract.

### Updated

- `scripts/batch_run_operator_workflows.py`
- `references/automation-workflows.md`
- `references/direct-use.md`

## 2026-05-04 Batch Preset Generator

- Decision: add a preset-based batch generator instead of forcing the operator to hand-write every JSON queue.
- Why: common TikTok and Douyin operating flows now repeat often enough that queue authoring became the next usability bottleneck.

### Added

- `scripts/generate_batch_preset.py`
- `references/batch-presets.md`

### Updated

- `references/automation-workflows.md`
- `references/direct-use.md`
- `tiktok-growth-operator.skill/SKILL.md`

## 2026-05-04 Parameterized Batch Presets

- Decision: extend batch presets from fixed canned queries into variable-driven templates.
- Why: reusable queues are more useful when the operator can inject the current product, category, audience, or account name instead of editing the generated JSON every time.

### Updated

- `scripts/generate_batch_preset.py`
- `references/batch-presets.md`
- `references/automation-workflows.md`
- `references/direct-use.md`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\generate_batch_preset.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_batch_preset.py" --preset topic-to-publish --name missing-product-smoke --project "Missing Product Smoke" --category "Beauty" --output "D:\我的文档\Documents\Playground 4\.codex-tmp\missing-product-smoke.json"`
- Result: failed fast as intended with `Preset topic-to-publish requires --product.`
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_batch_preset.py" --preset audience-to-live --name audience-live-ok --project "Audience Live OK" --product "Velvet Lip Glaze" --audience "Skincare Deal Seekers" --output "D:\我的文档\Documents\Playground 4\.codex-tmp\audience-live-ok.json"`
- Result: passed and generated the expected parameterized preset
- Verified: `D:\我的文档\Documents\Playground 4\.codex-tmp\audience-live-ok.manifest.json`
- Result: manifest recorded the required variable values for the successful run

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\generate_batch_preset.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_batch_preset.py" --preset tiktok-account-watch-capture,competitor-to-publish,audience-to-live --ordering input --name beauty-ops-input-order --project "Beauty Ops Input Order" --product "Velvet Lip Glaze" --category "Beauty" --audience "Skincare Deal Seekers" --account-name "GlowOfficial" --capture-root "D:\我的文档\Documents\Playground 4\captures\tiktok-analysis-pack-smoke-20260423f" --output "D:\我的文档\Documents\Playground 4\.codex-tmp\beauty-ops-input-order.json"`
- Result: passed and preserved the original preset order, with capture-pack tasks first
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_batch_preset.py" --preset tiktok-account-watch-capture,competitor-to-publish,audience-to-live --ordering mode --name beauty-ops-mode-order --project "Beauty Ops Mode Order" --product "Velvet Lip Glaze" --category "Beauty" --audience "Skincare Deal Seekers" --account-name "GlowOfficial" --capture-root "D:\我的文档\Documents\Playground 4\captures\tiktok-analysis-pack-smoke-20260423f" --output "D:\我的文档\Documents\Playground 4\.codex-tmp\beauty-ops-mode-order.json"`
- Result: passed and reordered the queue so goal tasks came before capture-pack tasks
- Verified: `D:\我的文档\Documents\Playground 4\.codex-tmp\beauty-ops-mode-order.manifest.json`
- Result: manifest recorded `ordering_strategy: mode`
- Ran: `python "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" --batch-file "D:\我的文档\Documents\Playground 4\.codex-tmp\beauty-ops-mode-order.json" --dry-run --batch-root "D:\我的文档\Documents\Playground 4\.codex-tmp\beauty-ops-mode-order-dry-run"`
- Result: passed and previewed the ordered combined queue with `preview: 4`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\generate_batch_preset.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_batch_preset.py" --preset competitor-to-publish,audience-to-live,tiktok-account-watch-capture --name beauty-ops-board --project "Beauty Ops Board" --product "Velvet Lip Glaze" --category "Beauty" --audience "Skincare Deal Seekers" --account-name "GlowOfficial" --capture-root "D:\我的文档\Documents\Playground 4\captures\tiktok-analysis-pack-smoke-20260423f" --output "D:\我的文档\Documents\Playground 4\.codex-tmp\beauty-ops-board.json"`
- Result: passed and generated one merged batch queue containing goal and capture-pack tasks
- Verified: `D:\我的文档\Documents\Playground 4\.codex-tmp\beauty-ops-board.manifest.json`
- Result: manifest recorded `presets`, merged variable coverage, and `task_count: 4`
- Ran: `python "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" --batch-file "D:\我的文档\Documents\Playground 4\.codex-tmp\beauty-ops-board.json" --dry-run --batch-root "D:\我的文档\Documents\Playground 4\.codex-tmp\beauty-ops-board-dry-run"`
- Result: passed and previewed the combined queue with `preview: 4`
- Verified: `D:\我的文档\Documents\Playground 4\.codex-tmp\beauty-ops-board-dry-run\batch_report.md`
- Result: report showed two goal tasks plus two capture-pack tasks in one combined ops board

## 2026-05-04 Combined Preset Queues

- Decision: allow one batch preset output to merge multiple preset slugs into a single queue.
- Why: daily operations often span several recurring workflows at once, and generating them separately creates unnecessary queue assembly work.

### Updated

- `scripts/generate_batch_preset.py`
- `references/batch-presets.md`
- `references/automation-workflows.md`
- `references/direct-use.md`

## 2026-05-04 Preset Queue Ordering

- Decision: add explicit ordering strategies for combined preset queues instead of relying only on raw preset concatenation.
- Why: operators often want analysis and planning tasks first, with capture-pack and downstream tasks later, while still preserving the option to keep manual input order.

### Updated

- `scripts/generate_batch_preset.py`
- `references/batch-presets.md`
- `references/automation-workflows.md`
- `references/direct-use.md`

## 2026-05-04 Preset Variable Validation

- Decision: make preset variables fail-fast requirements instead of optional placeholders.
- Why: generated queues should never silently fall back to generic `Product`, `Category`, `Audience`, or `Account` values because that weakens direct usability and hides bad operator input.

### Updated

- `scripts/generate_batch_preset.py`
- `references/batch-presets.md`
- `references/automation-workflows.md`
- `references/direct-use.md`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\generate_batch_preset.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_batch_preset.py" --list`
- Result: passed and exposed preset variable lists together with preset metadata
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_batch_preset.py" --preset topic-to-publish --name spring-lip-launch --project "Spring Lip Launch" --product "Velvet Lip Glaze" --category "Beauty" --output "D:\我的文档\Documents\Playground 4\.codex-tmp\topic-to-publish-parameterized.json"`
- Result: passed and injected product/category variables into the generated goal query, task name, and project title
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_batch_preset.py" --preset tiktok-ranked-breakdown-capture --name official-account-rank-watch --project "Official Account Rank Watch" --account-name "GlowOfficial" --category "Beauty" --capture-root "D:\我的文档\Documents\Playground 4\captures\tiktok-analysis-pack-smoke-20260423f" --output "D:\我的文档\Documents\Playground 4\.codex-tmp\tiktok-ranked-capture-parameterized.json"`
- Result: passed and injected account-name variables into the generated capture-pack task names and project titles
- Ran: `python "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" --batch-file "D:\我的文档\Documents\Playground 4\.codex-tmp\topic-to-publish-parameterized.json" --dry-run --batch-root "D:\我的文档\Documents\Playground 4\.codex-tmp\topic-to-publish-parameterized-dry-run"`
- Result: passed and previewed the parameterized goal preset queue
- Ran: `python "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" --batch-file "D:\我的文档\Documents\Playground 4\.codex-tmp\tiktok-ranked-capture-parameterized.json" --dry-run --batch-root "D:\我的文档\Documents\Playground 4\.codex-tmp\tiktok-ranked-capture-parameterized-dry-run"`
- Result: passed and previewed the parameterized capture-pack preset queue

## 2026-05-04 Preset Report Artifact

- Decision: add one Markdown preset report artifact next to each generated preset queue.
- Why: operators should be able to inspect preset composition, injected variables, mode distribution, and exact generated tasks without opening raw JSON or manifest files.
- Decision: turn the preset report into an execution handoff surface instead of a passive summary only.
- Why: once the queue is generated, the next operator step should be obvious and copy-ready without manually composing dry-run, execution, or rerun commands.
- Decision: emit runnable helper scripts next to each preset queue instead of stopping at report-only handoff.
- Why: some operators want to execute the next step immediately from the filesystem without copying commands out of Markdown.
- Decision: emit one reusable preset input file and support `--config` regeneration.
- Why: once a good operator queue exists, regenerating variants should not require retyping every variable and output parameter.
- Decision: add a starter config template mode before real queue generation.
- Why: operators should be able to begin from a field-complete template instead of remembering config keys or cloning an old input file by hand.
- Decision: add a template-bundle export mode on top of the single starter template.
- Why: once the preset catalog is broad enough, operators benefit from receiving a whole board of starter configs in one pass rather than generating them one by one.

### Updated

- `scripts/generate_batch_preset.py`
- `references/batch-presets.md`
- `references/automation-workflows.md`
- `references/direct-use.md`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\generate_batch_preset.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_batch_preset.py" --preset topic-to-publish --name spring-lip-launch-report --project "Spring Lip Launch Report" --product "Velvet Lip Glaze" --category "Beauty" --output "D:\我的文档\Documents\Playground 4\.codex-tmp\spring-lip-launch-report.json"`
- Result: passed and generated JSON, manifest, and Markdown preset report for a single goal preset
- Verified: `D:\我的文档\Documents\Playground 4\.codex-tmp\spring-lip-launch-report.report.md`
- Result: report captured preset overview, variable values, mode summary, and generated task details
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_batch_preset.py" --preset competitor-to-publish,audience-to-live,tiktok-account-watch-capture --ordering mode --name beauty-ops-report-board --project "Beauty Ops Report Board" --product "Velvet Lip Glaze" --category "Beauty" --audience "Skincare Deal Seekers" --account-name "GlowOfficial" --capture-root "D:\我的文档\Documents\Playground 4\captures\tiktok-analysis-pack-smoke-20260423f" --output "D:\我的文档\Documents\Playground 4\.codex-tmp\beauty-ops-report-board.json"`
- Result: passed and generated JSON, manifest, and Markdown preset report for a combined ordered queue
- Verified: `D:\我的文档\Documents\Playground 4\.codex-tmp\beauty-ops-report-board.report.md`
- Result: combined report captured all selected presets, injected variables, mode counts, and four ordered tasks
- Verified: preset reports now include recommended batch root, recommended result file, and copy-ready dry-run, execute, and rerun commands
- Result: report can now be used directly as the next-step operator handoff
- Verified: helper `*.ps1` and `*.cmd` runner files are generated next to the preset queue
- Result: preset generation now hands off both command text and runnable script surfaces
- Verified: one `.input.json` file and regenerate helper scripts are generated next to the preset queue
- Result: preset generation now supports durable config-based regeneration instead of command-only repetition
- Verified: `--template-output` writes one starter config template keyed to the selected preset set
- Result: the preset flow now supports blank-template -> filled config -> queue generation without manual schema recall
- Verified: `--template-bundle-root` writes one starter-template bundle with an index JSON and Markdown summary
- Result: the preset input layer now supports catalog-scale scaffold export, not only single-template generation

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\generate_batch_preset.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_batch_preset.py" --list`
- Result: passed and listed all current goal and capture-pack preset slugs
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_batch_preset.py" --preset topic-to-publish --name spring-lip-launch --project "Spring Lip Launch" --output "D:\我的文档\Documents\Playground 4\.codex-tmp\topic-to-publish-preset.json"`
- Result: passed and generated a goal-mode preset batch plus manifest
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_batch_preset.py" --preset tiktok-ranked-breakdown-capture --name official-account-rank-watch --project "Official Account Rank Watch" --capture-root "D:\我的文档\Documents\Playground 4\captures\tiktok-analysis-pack-smoke-20260423f" --output "D:\我的文档\Documents\Playground 4\.codex-tmp\tiktok-ranked-capture-preset.json"`
- Result: passed and generated a capture-pack preset batch plus manifest
- Ran: `python "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" --batch-file "D:\我的文档\Documents\Playground 4\.codex-tmp\topic-to-publish-preset.json" --dry-run --batch-root "D:\我的文档\Documents\Playground 4\.codex-tmp\topic-to-publish-preset-dry-run"`
- Result: passed and previewed the generated goal preset queue
- Ran: `python "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" --batch-file "D:\我的文档\Documents\Playground 4\.codex-tmp\tiktok-ranked-capture-preset.json" --dry-run --batch-root "D:\我的文档\Documents\Playground 4\.codex-tmp\tiktok-ranked-capture-preset-dry-run"`
- Result: passed and previewed the generated capture-pack preset queue

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" --batch-file "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_capture_batch_validation.json" --batch-root "D:\我的文档\Documents\Playground 4\.codex-tmp\capture-batch-rerun-validation"`
- Result: passed with `2/2` success for `capture-pack` batch execution
- Ran: `python "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" --rerun-failed-from "D:\我的文档\Documents\Playground 4\.codex-tmp\operator-batch-smoke-result.json" --rerun-indexes 1,3 --batch-root "D:\我的文档\Documents\Playground 4\.codex-tmp\rerun-selected-indexes-smoke"`
- Result: passed and reran only the selected prior batch items

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" --batch-file "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_capture_batch_validation.json" --batch-root "D:\我的文档\Documents\Playground 4\.codex-tmp\capture-batch-rerun-validation"`
- Result: passed with `2/2` success for mixed batch `capture-pack` execution
- Ran: `python "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" --rerun-failed-from "D:\我的文档\Documents\Playground 4\.codex-tmp\operator-batch-smoke-result.json" --rerun-indexes 1,3 --batch-root "D:\我的文档\Documents\Playground 4\.codex-tmp\rerun-selected-indexes-smoke"`
- Result: passed and reran only the selected prior batch items

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" --batch-file "D:\我的文档\Documents\Playground 4\.codex-tmp\operator-batch-failure-smoke.json" --output-file "D:\我的文档\Documents\Playground 4\.codex-tmp\operator-batch-failure-smoke-result.json"`
- Result: passed with resilient behavior; one `pack` task failed, while the following `goal` task still completed

## 2026-05-04 Batch Artifact Directory

- Decision: always materialize a batch artifact directory instead of relying only on terminal output or one combined JSON file.
- Why: large batch runs need a stable on-disk structure for review, rerun, and debugging.

### Updated

- `scripts/batch_run_operator_workflows.py`
- `references/automation-workflows.md`
- `references/direct-use.md`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" --batch-file "D:\我的文档\Documents\Playground 4\.codex-tmp\operator-batch-smoke.json" --batch-root "D:\我的文档\Documents\Playground 4\.codex-tmp\batch-artifact-smoke"`
- Result: passed and created a batch artifact directory
- Verified: `batch_input.json`, `summary.json`, `batch_result.json`, and per-item files under `items/`
- Result: passed

## 2026-05-04 Failed-Item Rerun

- Decision: allow batch reruns to read a previous `batch_result.json` or batch artifact directory and automatically requeue only failed tasks.
- Why: once resilient batch exists, the next natural step is recovery. Operators should not have to manually rebuild a failed subset.
- Decision: allow one override JSON object to be merged into every rerun task.
- Why: failed tasks often need one corrected field such as `project`, `type`, or `source_report`.

### Updated

- `scripts/batch_run_operator_workflows.py`
- `references/automation-workflows.md`
- `references/direct-use.md`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" --rerun-failed-from "D:\我的文档\Documents\Playground 4\.codex-tmp\operator-batch-failure-smoke-result.json" --batch-root "D:\我的文档\Documents\Playground 4\.codex-tmp\rerun-failed-smoke"`
- Result: passed and recreated only the previously failed task
- Verified: `D:\我的文档\Documents\Playground 4\.codex-tmp\rerun-failed-smoke\summary.json`
- Result: rerun payload remained failed as expected because no override was applied
- Ran: `python "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" --rerun-failed-from "D:\我的文档\Documents\Playground 4\.codex-tmp\operator-batch-failure-smoke-result.json" --override-file "D:\我的文档\Documents\Playground 4\.codex-tmp\rerun-override-pack-fix.json" --batch-root "D:\我的文档\Documents\Playground 4\.codex-tmp\rerun-failed-fixed-smoke"`
- Result: passed and repaired the prior failed pack task
- Verified: `D:\我的文档\Documents\Playground 4\.codex-tmp\rerun-failed-fixed-smoke\summary.json`
- Result: rerun payload completed with `1/1` success

## 2026-05-04 Batch Recovery Hardening

- Decision: restore `capture-pack` support inside the mixed batch runner instead of leaving it available only through single-run entrypoints.
- Why: the package already treats real TikTok capture folders as first-class inputs, so batch mode must preserve that same operator surface.
- Decision: allow reruns by explicit prior batch indexes, not only failed items.
- Why: operators often need to reprocess a selected subset after changing one template, pack rule, or capture input.

### Updated

- `scripts/batch_run_operator_workflows.py`
- `references/automation-workflows.md`
- `references/direct-use.md`

## 2026-05-04 Direct-Use Hardening

- Decision: add a direct-use guide and a Tencent article parity map.
- Why: the user asked for a Codex-first replacement of the Douyin article workflow, not only a Clipcat-scene documentation pack.
- Decision: add one command that creates both a scene workspace and its first report scaffold.
- Why: direct use in Codex needs a shorter path than separately initializing the workspace and generating the report.
- Decision: explicitly exclude fake engagement, anti-detection, cloud-phone control, and comment hijacking.
- Why: these are high-risk automation behaviors and do not belong in a safe durable package.

### Added

- `references/direct-use.md`
- `references/article-2640429-feature-parity.md`
- `scripts/run_scene_workflow.py`

### Updated

- `references/assistant-spec.md`
- `references/feature-map.md`
- `references/automation-workflows.md`
- `agents/openai.yaml`
- `tiktok-growth-operator.skill/SKILL.md`

## 2026-05-04 Publish And Live Packs

- Decision: implement publish preparation and live assist as operator packs rather than new numbered scenes.
- Why: they are cross-scene handoff layers that sit on top of existing research and creation scenes.
- Decision: keep them outside risky automation and generate only ready-to-use briefs, checklists, and prompt banks.
- Why: the user asked for direct Codex use, not cloud-phone or anti-detection infrastructure.

### Added

- `references/publish-prep-pack.md`
- `references/live-assist-pack.md`
- `scripts/generate_operator_pack.py`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\generate_operator_pack.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_operator_pack.py" --type publish-prep --project "早八妆容带货视频" --platform Douyin --market China --output-dir "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_publish_prep_smoke"`
- Result: passed and created a publish prep smoke pack
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_operator_pack.py" --type live-assist --project "晚间护肤专场直播" --platform Douyin --market China --output-dir "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_live_assist_smoke"`
- Result: passed and created a live assist smoke pack
- Ran: reference existence check for the new pack docs and generator script
- Result: passed

## 2026-05-04 Derived Pack Autofill

- Decision: teach the operator-pack generator to consume structured scene report JSON.
- Why: the next useful step after blank pack generation is turning real scene analysis into a first-draft publish pack or live pack.

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\generate_operator_pack.py"`
- Result: passed after adding source-report autofill and UTF-8 BOM output for PowerShell compatibility
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_operator_pack.py" --type publish-prep --source-report "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\references\scene-report-example.json" --platform Douyin --market China --output-dir "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_publish_derived_smoke_bom"`
- Result: passed and produced a non-empty derived publish prep pack
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_operator_pack.py" --type live-assist --source-report "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\references\scene-report-example.json" --platform Douyin --market China --output-dir "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_live_derived_smoke_bom"`
- Result: passed and produced a non-empty derived live assist pack

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\run_scene_workflow.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\run_scene_workflow.py" --scene 03 --project "早八妆容批量深拆" --name "zao-ba-zhuang-rundown"`
- Result: passed and created a smoke workspace under `tiktok-growth-operator.skill\tmp\20260504_045454-scene-03-zao-ba-zhuang-rundown`
- Ran: reference existence check for the new docs and runner script
- Result: passed

## 2026-05-04 End-To-End Integration

- Decision: wire `start_scene_run.py` directly to operator-pack generation.
- Why: the durable workflow should not require a separate manual command after every scene run.
- Decision: auto-route `publish-prep` for creation scenes and `live-assist` for comment or account scenes.
- Why: this captures the most useful default handoff behavior without inventing a parallel router layer.
- Decision: add scene-specific derivation rules inside `generate_operator_pack.py`.
- Why: generic autofill was not enough for high-signal publish and live handoff packs.

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\generate_operator_pack.py"`
- Result: passed
- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\start_scene_run.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\start_scene_run.py" --scene 12 --name "lip-liner-style-matrix" --project "Lip Liner Style Matrix" --platform Douyin --market China --output-root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_scene12_full_run"`
- Result: passed and auto-generated `publish-prep`
- Ran: `python "tiktok-growth-operator.skill\scripts\start_scene_run.py" --scene 08 --name "user-language-live-pack" --project "User Language Live Pack" --platform Douyin --market China --output-root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_scene08_full_run"`
- Result: passed and auto-generated `live-assist`
- Ran: recursive file existence checks for `publish-prep-pack.md` and `live-assist-pack.md` inside the generated full-run workspaces
- Result: passed

## 2026-05-04 Real Project Import Run

- Decision: add a durable historical-case importer instead of manually editing one real project into scene JSON.
- Why: the workspace already contains older high-value Douyin evidence packs, and a reusable importer makes those immediately runnable through the new Codex-native scene/report pipeline.
- Decision: use `reports/2026-04-29-douyin-anxiansheng-viral-analysis` as the first real project.
- Why: it has the strongest existing bundle across prior curated analysis, source manifest, transcript manifest, frames, storyboard, and workbook outputs.
- Decision: run both scene `04` and scene `17` from the same real case, then derive publish and live packs from the imported creator-distillation report.
- Why: scene `04` proves single-video deep teardown, scene `17` proves creator-formula distillation, and the derived packs prove downstream handoff usefulness from a real imported case.

### Added

- `tiktok-growth-operator.skill/scripts/import_historical_case.py`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\import_historical_case.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\import_historical_case.py" --scene 04 --case-json "D:\我的文档\Documents\Playground 4\reports\2026-04-29-douyin-anxiansheng-viral-analysis\case_data_v3.json" --source-manifest "D:\我的文档\Documents\Playground 4\captures\2026-04-29-douyin-anxiansheng-viral-analysis\source_manifest.json" --transcript-manifest "D:\我的文档\Documents\Playground 4\captures\2026-04-29-douyin-anxiansheng-viral-analysis\transcript_manifest.json" --project "Anxiansheng Single Video Breakdown" --output "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_anxiansheng_real_project\scene-04\scene-04-anxiansheng-single-video-breakdown.json"`
- Result: passed and created a filled scene-04 report JSON from the historical project
- Ran: `python "tiktok-growth-operator.skill\scripts\import_historical_case.py" --scene 17 --case-json "D:\我的文档\Documents\Playground 4\reports\2026-04-29-douyin-anxiansheng-viral-analysis\case_data_v3.json" --source-manifest "D:\我的文档\Documents\Playground 4\captures\2026-04-29-douyin-anxiansheng-viral-analysis\source_manifest.json" --transcript-manifest "D:\我的文档\Documents\Playground 4\captures\2026-04-29-douyin-anxiansheng-viral-analysis\transcript_manifest.json" --project "Anxiansheng Creator Distillation" --output "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_anxiansheng_real_project\scene-17\scene-17-anxiansheng-creator-distillation.json"`
- Result: passed and created a filled scene-17 report JSON from the historical project
- Ran: `python "tiktok-growth-operator.skill\scripts\render_scene_report.py" --input "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_anxiansheng_real_project\scene-04\scene-04-anxiansheng-single-video-breakdown.json" --output-dir "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_anxiansheng_real_project\scene-04\outputs" --formats md,docx,xlsx"`
- Result: passed and rendered markdown, docx, and xlsx outputs for scene 04
- Ran: `python "tiktok-growth-operator.skill\scripts\render_scene_report.py" --input "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_anxiansheng_real_project\scene-17\scene-17-anxiansheng-creator-distillation.json" --output-dir "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_anxiansheng_real_project\scene-17\outputs" --formats md,docx,xlsx"`
- Result: passed and rendered markdown, docx, and xlsx outputs for scene 17
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_operator_pack.py" --type publish-prep --source-report "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_anxiansheng_real_project\scene-17\scene-17-anxiansheng-creator-distillation.json" --platform Douyin --market China --output-dir "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_anxiansheng_real_project\operator-packs\publish-prep"`
- Result: passed and created a derived publish-prep pack from the real imported project
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_operator_pack.py" --type live-assist --source-report "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_anxiansheng_real_project\scene-17\scene-17-anxiansheng-creator-distillation.json" --platform Douyin --market China --output-dir "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_anxiansheng_real_project\operator-packs\live-assist"`
- Result: passed and created a derived live-assist pack from the real imported project

## 2026-05-04 TikTok Real Project Correction

- Decision: correct the platform mismatch by running a real TikTok capture-pack project instead of the prior Douyin case.
- Why: the user explicitly asked for a TikTok project, and the reusable package must prove it can operate on real TikTok artifacts, not only Douyin evidence packs.
- Decision: use `captures/tiktok-analysis-pack-smoke-20260423f` as the first real TikTok project.
- Why: it includes aggregated ranked and qualified video outputs, profile summary, ranked workbooks, and a profile-specific capture folder under `01-tiktok/`, making it the strongest directly runnable TikTok capture pack in the workspace.
- Decision: run scene `03` and scene `17`, then derive `publish-prep` only.
- Why: the pack has enough evidence for ranked-video teardown and creator/account distillation, but its comment sampling is empty, so generating a live-assist handoff from this specific pack would overclaim missing audience-language evidence.

### Added

- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py" --scene 03 --capture-root "D:\我的文档\Documents\Playground 4\captures\tiktok-analysis-pack-smoke-20260423f" --project "TikTok Official Account Ranked Breakdown" --output "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_tiktok_real_project\scene-03\scene-03-tiktok-official-ranked-breakdown.json"`
- Result: passed and created a filled scene-03 report JSON from the real TikTok capture pack
- Ran: `python "tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py" --scene 17 --capture-root "D:\我的文档\Documents\Playground 4\captures\tiktok-analysis-pack-smoke-20260423f" --project "TikTok Official Account Creator Distillation" --output "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_tiktok_real_project\scene-17\scene-17-tiktok-official-creator-distillation.json"`
- Result: passed and created a filled scene-17 report JSON from the real TikTok capture pack
- Ran: `python "tiktok-growth-operator.skill\scripts\render_scene_report.py" --input "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_tiktok_real_project\scene-03\scene-03-tiktok-official-ranked-breakdown.json" --output-dir "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_tiktok_real_project\scene-03\outputs" --formats md,docx,xlsx"`
- Result: passed and rendered markdown, docx, and xlsx outputs for TikTok scene 03
- Ran: `python "tiktok-growth-operator.skill\scripts\render_scene_report.py" --input "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_tiktok_real_project\scene-17\scene-17-tiktok-official-creator-distillation.json" --output-dir "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_tiktok_real_project\scene-17\outputs" --formats md,docx,xlsx"`
- Result: passed and rendered markdown, docx, and xlsx outputs for TikTok scene 17
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_operator_pack.py" --type publish-prep --source-report "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_tiktok_real_project\scene-17\scene-17-tiktok-official-creator-distillation.json" --platform TikTok --market US --output-dir "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_tiktok_real_project\operator-packs\publish-prep"`
- Result: passed and created a derived TikTok publish-prep pack from the real imported project

## 2026-05-04 TikTok Comment And Live Extension

- Decision: extend the TikTok importer to support scene `08` from a comment-bearing capture pack.
- Why: the earlier TikTok ranked/creator pack had no sampled comments, which was enough for scene `03` and `17` but not enough to prove comment-mining and live-assist behavior.
- Decision: use `captures/tiktok-download-validated-20260423` as the second TikTok real project.
- Why: it includes `ranked_videos.json`, `comments_sampled.json`, `comments_summary.json`, and enough direct comment evidence across three videos to produce a real scene `08` report and a grounded `live-assist` pack.
- Decision: broaden the TikTok capture importer to support both aggregate-style packs and single-run packs.
- Why: the workspace contains both shapes, and the durable package should not force separate one-off import scripts per capture layout.

### Updated

- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py"`
- Result: passed after adding scene `08` support and single-pack compatibility
- Ran: `python "tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py" --scene 08 --capture-root "D:\我的文档\Documents\Playground 4\captures\tiktok-download-validated-20260423" --project "TikTok Comment Signal Synthesis" --output "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_tiktok_comment_project\scene-08\scene-08-tiktok-comment-signal-synthesis.json"`
- Result: passed and created a filled scene-08 report JSON from the real TikTok comment pack
- Ran: `python "tiktok-growth-operator.skill\scripts\render_scene_report.py" --input "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_tiktok_comment_project\scene-08\scene-08-tiktok-comment-signal-synthesis.json" --output-dir "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_tiktok_comment_project\scene-08\outputs" --formats md,docx,xlsx"`
- Result: passed and rendered markdown, docx, and xlsx outputs for TikTok scene 08
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_operator_pack.py" --type live-assist --source-report "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_tiktok_comment_project\scene-08\scene-08-tiktok-comment-signal-synthesis.json" --platform TikTok --market US --output-dir "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_tiktok_comment_project\operator-packs\live-assist"`
- Result: passed and created a derived TikTok live-assist pack from the real comment-bearing project

## 2026-05-04 Unified Capture Pack Runner

- Decision: add one durable runner that consumes a real TikTok capture-pack directory and completes import, render, and derived-pack steps in one command.
- Why: the real TikTok validations proved the importer path works, but it still required several manual commands. The user asked to keep going and finish the work, so the durable path should be one-shot runnable.

### Added

- `tiktok-growth-operator.skill/scripts/start_capture_pack_run.py`

### Updated

- `tiktok-growth-operator.skill/references/automation-workflows.md`
- `tiktok-growth-operator.skill/references/direct-use.md`
- `tiktok-growth-operator.skill/SKILL.md`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\start_capture_pack_run.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\start_capture_pack_run.py" --scene 17 --capture-root "D:\我的文档\Documents\Playground 4\captures\tiktok-analysis-pack-smoke-20260423f" --name tiktok-official-capture-run --project "TikTok Official Account Creator Distillation" --platform TikTok --market US --output-root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_capture_runner_scene17"`
- Result: passed and created a one-command scene-17 + publish-prep run from the real TikTok capture pack
- Ran: `python "tiktok-growth-operator.skill\scripts\start_capture_pack_run.py" --scene 08 --capture-root "D:\我的文档\Documents\Playground 4\captures\tiktok-download-validated-20260423" --name tiktok-comment-capture-run --project "TikTok Comment Signal Synthesis" --platform TikTok --market US --output-root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_capture_runner_scene08"`
- Result: passed and created a one-command scene-08 + live-assist run from the real TikTok comment-bearing capture pack

## 2026-05-04 Capture Pack Routing And Batch Completion

- Decision: promote `capture-pack` into the unified operator router and batch runner instead of leaving it as a standalone script only.
- Why: the remaining A-class work was mainly about finishing the operator surface, not about adding more isolated scripts.
- Decision: extend the TikTok capture importer to support scene `18` and `19` in addition to `03`, `08`, and `17`.
- Why: these scenes are the next most natural fits for ranked/account-style capture packs and materially expand real-project coverage without inventing unsupported data.

### Updated

- `tiktok-growth-operator.skill/scripts/run_operator_workflow.py`
- `tiktok-growth-operator.skill/scripts/batch_run_operator_workflows.py`
- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`
- `tiktok-growth-operator.skill/references/direct-use.md`
- `tiktok-growth-operator.skill/references/automation-workflows.md`
- `tiktok-growth-operator.skill/SKILL.md`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\run_operator_workflow.py"`
- Result: passed
- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py"`
- Result: passed
- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py"`
- Result: passed
- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\start_capture_pack_run.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\run_operator_workflow.py" --mode capture-pack --scene 17 --capture-root "D:\我的文档\Documents\Playground 4\captures\tiktok-analysis-pack-smoke-20260423f" --name routed-capture-scene17 --project "TikTok Official Account Creator Distillation" --platform TikTok --market US --output-root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_routed_capture_scene17" --formats md,docx,xlsx"`
- Result: passed and produced a routed capture-pack run with derived `publish-prep`
- Ran: `python "tiktok-growth-operator.skill\scripts\run_operator_workflow.py" --mode auto --request "run a real TikTok capture pack scene 08 comment signal workflow" --scene 08 --capture-root "D:\我的文档\Documents\Playground 4\captures\tiktok-download-validated-20260423" --name routed-auto-capture-scene08 --project "TikTok Comment Signal Synthesis" --platform TikTok --market US --output-root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_routed_capture_scene08_auto_fixed" --formats md,docx,xlsx"`
- Result: passed after fixing routing priority and confirmed `auto -> capture-pack -> live-assist`
- Ran: `python "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" --batch-file "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_capture_batch_validation.json" --output-file "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_capture_batch_validation_result.json"`
- Result: passed with 2/2 success for batch `capture-pack` tasks

## 2026-05-04 Capture-Pack Testing Matrix And Run Dashboard

- Decision: extend the real TikTok capture-pack importer into scenes `11` and `12`.
- Why: creative-testing parity was the next real gap after creator, comment, and account-review coverage.
- Decision: keep scene `11` and `12` grounded in ranked/qualified TikTok evidence and explicitly mark missing product-specific inputs rather than fabricating them.
- Why: this preserves truthfulness while still producing directly useful testing structures.
- Decision: add a lightweight run-history dashboard over manifests under `tmp/`.
- Why: the operator surface now creates enough scene, capture-pack, project, and pack artifacts that a durable summary view is useful.

### Added

- `tiktok-growth-operator.skill/scripts/summarize_run_history.py`

### Updated

- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`
- `tiktok-growth-operator.skill/scripts/start_capture_pack_run.py`
- `tiktok-growth-operator.skill/scripts/validate_capture_pack_workflows.py`
- `tiktok-growth-operator.skill/references/direct-use.md`
- `tiktok-growth-operator.skill/references/automation-workflows.md`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py" "tiktok-growth-operator.skill\scripts\start_capture_pack_run.py" "tiktok-growth-operator.skill\scripts\summarize_run_history.py" "tiktok-growth-operator.skill\scripts\validate_capture_pack_workflows.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\start_capture_pack_run.py" --scene auto --capture-root "D:\我的文档\Documents\Playground 4\captures\tiktok-analysis-pack-smoke-20260423f" --name auto-regression-check --project "TikTok Auto Regression Check" --platform TikTok --market US --output-root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_auto_regression_check" --formats md"`
- Result: passed and preserved `auto -> scene 17` for the ranked TikTok pack
- Ran: `python "tiktok-growth-operator.skill\scripts\start_capture_pack_run.py" --scene 11 --capture-root "D:\我的文档\Documents\Playground 4\captures\tiktok-analysis-pack-smoke-20260423f" --name scene11-capture-run --project "TikTok Hot Video Replication Pipeline" --platform TikTok --market US --output-root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_capture_runner_scene11" --formats md,docx,xlsx"`
- Result: passed and produced a real TikTok scene-11 testing-pipeline run plus derived `publish-prep`
- Ran: `python "tiktok-growth-operator.skill\scripts\start_capture_pack_run.py" --scene 12 --capture-root "D:\我的文档\Documents\Playground 4\captures\tiktok-analysis-pack-smoke-20260423f" --name scene12-capture-run --project "TikTok One Product Multi Style Matrix" --platform TikTok --market US --output-root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_capture_runner_scene12" --formats md,docx,xlsx"`
- Result: passed and produced a real TikTok scene-12 testing-matrix run plus derived `publish-prep`
- Ran: `python "tiktok-growth-operator.skill\scripts\summarize_run_history.py" --output-json "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_run_history_dashboard.json" --output-md "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_run_history_dashboard.md" --limit 25`
- Result: passed and generated a recent-run dashboard across capture-pack, scene, project, and operator-pack manifests

## 2026-05-04 Scene 15 Capture-Pack Expansion

- Decision: extend real TikTok capture-pack support to scene `15` only as an image-translation blueprint with explicit `target_languages`.
- Why: the ranked TikTok pack can support hierarchy and localization-planning output, but it still cannot justify fabricated OCR text or final translated image copy without source-image text recovery and native-language review.

### Updated

- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`
- `tiktok-growth-operator.skill/scripts/start_capture_pack_run.py`
- `tiktok-growth-operator.skill/scripts/run_operator_workflow.py`
- `tiktok-growth-operator.skill/scripts/start_project_workflow.py`
- `tiktok-growth-operator.skill/scripts/batch_run_operator_workflows.py`
- `tiktok-growth-operator.skill/scripts/validate_capture_pack_workflows.py`
- `tiktok-growth-operator.skill/references/direct-use.md`
- `tiktok-growth-operator.skill/references/automation-workflows.md`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py" "tiktok-growth-operator.skill\scripts\start_capture_pack_run.py" "tiktok-growth-operator.skill\scripts\run_operator_workflow.py" "tiktok-growth-operator.skill\scripts\start_project_workflow.py" "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" "tiktok-growth-operator.skill\scripts\validate_capture_pack_workflows.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\start_capture_pack_run.py" --scene 15 --capture-root "D:\我的文档\Documents\Playground 4\captures\tiktok-analysis-pack-smoke-20260423f" --target-languages "English,Japanese,German" --name scene15-capture-run --project "TikTok Image Translation Blueprint" --platform TikTok --market US --output-root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_capture_runner_scene15" --formats md`
- Result: passed and generated a real TikTok scene `15` blueprint run plus derived `publish-prep`
- Ran: `python "tiktok-growth-operator.skill\scripts\validate_capture_pack_workflows.py"`
- Result: passed and preserved full capture-pack validation coverage including scene `15`

## 2026-05-04 Export Quality Round 3

- Decision: keep the scene report JSON contract unchanged and improve only the shared renderer output quality.
- Why: the reports are already being produced by multiple durable workflows, so layout upgrades should not fork or destabilize the contract.
- Decision: generate one stable section-sheet map for XLSX navigation and expose it through a dedicated `Section Index` sheet.
- Why: recomputing sheet names independently in overview and section writers risks broken links when headings collide or truncate differently.
- Decision: add a DOCX cover page and explicit table width control.
- Why: the previous renderer content was structurally complete, but the front page and wide-table behavior were still too raw for handoff-quality exports.

### Updated

- `tiktok-growth-operator.skill/scripts/render_scene_report.py`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\render_scene_report.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\render_scene_report.py" --input "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_capture_runner_scene15\scene-15\scene-15-scene15-capture-run.json" --output-dir "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_export_quality_scene15_v3" --formats md,docx,xlsx"`
- Result: passed and rendered upgraded scene `15` Markdown, DOCX, and XLSX outputs
- Ran: `python "tiktok-growth-operator.skill\scripts\render_scene_report.py" --input "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_capture_runner_scene17\scene-17\scene-17-tiktok-official-capture-run.json" --output-dir "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_export_quality_scene17_v3" --formats md,docx,xlsx"`
- Result: passed and rendered upgraded scene `17` Markdown, DOCX, and XLSX outputs
- Ran: workbook navigation smoke check against both new XLSX outputs
- Result: passed and confirmed `Section Overview -> section sheet`, `Section Index -> section sheet`, and section-sheet back-links to `Section Index`

## 2026-05-04 Export Quality Round 4

- Decision: add internal DOCX section anchors and link the section overview into them.
- Why: the report already had a TOC field, but operators still needed one-click navigation from the overview grid into the exact body section.
- Decision: convert key XLSX sheets into native Excel tables.
- Why: filters and styling on plain cell ranges were workable, but true table objects are a more durable handoff format for sorting, copying, and downstream editing.
- Decision: add a dedicated export regression validator.
- Why: exporter quality is now a maintained workflow surface, so future changes need a one-command representative check instead of ad hoc manual inspection.

### Added

- `tiktok-growth-operator.skill/scripts/validate_export_outputs.py`

### Updated

- `tiktok-growth-operator.skill/scripts/render_scene_report.py`
- `tiktok-growth-operator.skill/references/direct-use.md`
- `tiktok-growth-operator.skill/references/automation-workflows.md`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\render_scene_report.py" "tiktok-growth-operator.skill\scripts\validate_export_outputs.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\validate_export_outputs.py" --output-root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_export_validation_suite_v2"`
- Result: passed and re-rendered representative real TikTok scene `15` and `17` reports while confirming workbook navigation links and Excel table creation

## 2026-05-04 Export Quality Round 5

- Decision: improve DOCX long-report readability with repeated table headers, figure captions, and keep-with-next heading behavior.
- Why: exporter quality is now good enough that pagination polish affects real handoff usability more than basic structure completeness.
- Decision: turn the Summary sheet into a lightweight dashboard with top-row metrics.
- Why: operators opening the workbook should get report scale and readiness signals immediately instead of reading line-by-line metadata first.
- Decision: expand export regression coverage with synthetic duplicate-heading and sparse-section fixtures.
- Why: these are the most likely places for future navigation and table regressions after the new sheet-map and dashboard work.

### Updated

- `tiktok-growth-operator.skill/scripts/render_scene_report.py`
- `tiktok-growth-operator.skill/scripts/validate_export_outputs.py`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\render_scene_report.py" "tiktok-growth-operator.skill\scripts\validate_export_outputs.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\validate_export_outputs.py" --output-root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_export_validation_suite_v3"`
- Result: passed and validated real TikTok scene `15`/`17` exports plus synthetic duplicate-heading and sparse-section fixtures

## 2026-05-04 Validation And Navigation Finish

- Decision: add explicit DOCX navigation links back to contents and section overview from each main section.
- Why: internal bookmarks existed, but the report still benefited from visible operator-facing return paths instead of relying only on Word's navigation pane.
- Decision: add second-row Summary quality metrics in XLSX.
- Why: dashboard counts are more useful when they include hygiene signals such as empty sections or broken local asset paths, not only volume metrics.
- Decision: add one unified validation entrypoint for the durable package.
- Why: the package now has enough validation surface that operators and future agents need one command to run the main checks end to end.

### Added

- `tiktok-growth-operator.skill/scripts/validate_all_workflows.py`

### Updated

- `tiktok-growth-operator.skill/scripts/render_scene_report.py`
- `tiktok-growth-operator.skill/references/direct-use.md`
- `tiktok-growth-operator.skill/references/automation-workflows.md`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\render_scene_report.py" "tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Result: passed and completed scene preset validation, capture-pack workflow validation, and export regression validation in one command

## 2026-05-04 Export Polish Finish

- Decision: promote Summary quality metrics from neutral counters to status-colored health cards.
- Why: once the workbook is used as a handoff artifact, problem signals should be scannable immediately instead of requiring the operator to interpret raw counts.
- Decision: strengthen the DOCX cover page with a deliverable banner and a compact metadata panel.
- Why: the report is now close enough to final handoff quality that the cover page should read like a finished deliverable rather than a plain scaffold.

### Updated

- `tiktok-growth-operator.skill/scripts/render_scene_report.py`
- `tiktok-growth-operator.skill/scripts/validate_export_outputs.py`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\render_scene_report.py" "tiktok-growth-operator.skill\scripts\validate_export_outputs.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\validate_export_outputs.py" --output-root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_export_validation_suite_v4"`
- Result: passed and confirmed the new Summary quality cards across real and synthetic export regression fixtures

## 2026-05-04 Combo Template Bundle Upgrade

- Decision: extend preset template-bundle export from single-preset starters to curated multi-preset combo boards.
- Why: the batch preset surface had already matured into a real operator board system, so bundle export needed to cover the most common multi-scene operating boards instead of only atomic presets.
- Decision: keep combo bundles declarative in one explicit catalog.
- Why: curated board templates should be inspectable and easy to extend without burying workflow logic in the `main()` branch.
- Decision: make bundle templates suggest one sibling queue output path instead of pointing `output` back at the template file itself.
- Why: config-driven regeneration should not overwrite the starter template a user is filling in.

### Updated

- `tiktok-growth-operator.skill/scripts/generate_batch_preset.py`
- `tiktok-growth-operator.skill/references/batch-presets.md`
- `tiktok-growth-operator.skill/references/direct-use.md`
- `tiktok-growth-operator.skill/references/automation-workflows.md`

### Added Behavior

- bundle export now emits `single` and `combo` template items
- bundle index now records item `slug`, `type`, `ordering`, and `suggested_output_file`
- bundle README now explains fill-and-run flow for template-driven queue generation
- curated combo templates now include:
  - `topic-to-publish-board`
  - `viral-testing-board`
  - `competitor-to-publish-board`
  - `beauty-ops-board`
  - `localized-launch-board`
  - `weekly-monitor-to-next-test-board`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\generate_batch_preset.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_batch_preset.py" --template-bundle-root "D:\我的文档\Documents\Playground 4\.codex-tmp\preset-template-bundle-v3"`
- Result: passed and exported `10` single templates plus `6` combo templates with updated bundle index and README
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_batch_preset.py" --config "D:\我的文档\Documents\Playground 4\.codex-tmp\beauty-ops-board-filled-v3.json"`
- Result: passed and generated one real combined queue plus manifest, report, helper scripts, and reusable input file from the filled combo template

## 2026-05-04 Final Handoff Cleanup

- Decision: add one durable final-handoff reference instead of leaving the finished state scattered across several references and chat history.
- Why: the package now has enough surface area that future operators need one short file for best entrypoints, validation commands, real fixtures, and current boundaries.

### Added

- `tiktok-growth-operator.skill/references/final-handoff.md`

### Updated

- `tiktok-growth-operator.skill/SKILL.md`
- `tiktok-growth-operator.skill/references/direct-use.md`

### Validation

- Ran: shell read of `references/final-handoff.md`
- Result: passed
- Ran: link-reference presence check in `SKILL.md` and `references/direct-use.md`
- Result: content updated; a direct Python path-based check hit a Windows console encoding issue on the Chinese workspace path, but the files themselves were written successfully

## 2026-05-04 Vertical Starter Bundle Upgrade

- Decision: add a third bundle item family, `vertical`, on top of `single` and `combo`.
- Why: combo templates solve structure reuse, but operators still lose time refilling the same platform, market, product, audience, and capture fixture values for repeated business contexts.
- Decision: seed only real local capture roots that already exist in the workspace.
- Why: vertical starters should be close to runnable, not another fake convenience layer that points at nonexistent evidence packs.
- Decision: keep vertical starters declarative beside combo templates in the same generator.
- Why: starter-board evolution should remain inspectable and low-friction instead of scattering config across separate ad hoc files.

### Updated

- `tiktok-growth-operator.skill/scripts/generate_batch_preset.py`
- `tiktok-growth-operator.skill/references/batch-presets.md`
- `tiktok-growth-operator.skill/references/direct-use.md`
- `tiktok-growth-operator.skill/references/automation-workflows.md`

### Added Behavior

- template bundles now emit `vertical` items in addition to `single` and `combo`
- bundle index now records `vertical_template_count`
- vertical items now record `seeded_defaults`
- bundle README now explains when to use seeded vertical starters
- current vertical starters now include:
  - `beauty-us-ops-starter`
  - `beauty-comment-live-starter`
  - `douyin-beauty-launch-starter`
  - `tiktok-ranked-creator-starter`
  - `douyin-competitor-weekly-starter`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\generate_batch_preset.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_batch_preset.py" --template-bundle-root "D:\我的文档\Documents\Playground 4\.codex-tmp\preset-template-bundle-v4"`
- Result: passed and exported `10` single templates, `6` combo templates, and `5` vertical starters
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_batch_preset.py" --config "D:\我的文档\Documents\Playground 4\.codex-tmp\beauty-us-ops-starter-v4-config.json"`
- Result: passed and generated one zero-edit beauty vertical queue with manifest, report, helper scripts, and reusable input file

## 2026-05-04 Vertical Suite Upgrade

- Decision: promote each `vertical` starter into a suite directory with its own config, helper scripts, and README.
- Why: seeded starter templates reduce variable-entry time, but the operator still had to remember generation and dry-run commands manually. A suite directory makes each starter closer to a runnable product surface.
- Decision: keep suite queue output inside the suite directory instead of the bundle root.
- Why: generate, dry-run, and execute should work as one local chain without cross-directory path confusion.
- Decision: reuse the existing preset generator and batch runner instead of creating a second suite-specific runtime.
- Why: the durable operator surface should stay inspectable and maintain one execution path.

### Updated

- `tiktok-growth-operator.skill/scripts/generate_batch_preset.py`
- `tiktok-growth-operator.skill/references/batch-presets.md`
- `tiktok-growth-operator.skill/references/direct-use.md`
- `tiktok-growth-operator.skill/references/automation-workflows.md`

### Added Behavior

- bundle export now creates `vertical-suites/<slug>/` for each vertical starter
- each suite now contains:
  - copied config JSON
  - `generate.ps1/.cmd`
  - `dry-run.ps1/.cmd`
  - `run.ps1/.cmd`
  - suite README
- bundle index now records `vertical_suite_root`
- vertical item metadata now records suite script paths

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\generate_batch_preset.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_batch_preset.py" --template-bundle-root "D:\我的文档\Documents\Playground 4\.codex-tmp\preset-template-bundle-v6"`
- Result: passed and exported bundle plus suite directories for all vertical starters
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_batch_preset.py" --config "D:\我的文档\Documents\Playground 4\.codex-tmp\preset-template-bundle-v6\vertical-suites\beauty-us-ops-starter\beauty-us-ops-starter.config.json"`
- Result: passed and generated suite-local queue, manifest, report, and helper scripts
- Ran: `python "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" --batch-file "D:\我的文档\Documents\Playground 4\.codex-tmp\preset-template-bundle-v6\vertical-suites\beauty-us-ops-starter\beauty-us-ops-starter.json" --dry-run --batch-root "D:\我的文档\Documents\Playground 4\.codex-tmp\preset-template-bundle-v6\vertical-suites\beauty-us-ops-starter\batch-run"`
- Result: passed and produced one suite-local dry-run batch artifact set with `4` preview tasks

## 2026-05-04 Docs Validation Finish

- Decision: add an executable skill-doc validator and wire it into the unified validation entrypoint.
- Why: the package handoff surface is now durable enough that broken internal references should fail validation instead of being caught only by manual reading.

### Added

- `tiktok-growth-operator.skill/scripts/validate_skill_docs.py`

### Updated

- `tiktok-growth-operator.skill/scripts/validate_all_workflows.py`
- `tiktok-growth-operator.skill/references/automation-workflows.md`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\validate_skill_docs.py" "tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Result: passed and now includes skill-doc/reference validation in the unified validation surface

## 2026-05-04 Launch Board Upgrade

- Decision: add `launch-board` as a fourth preset-bundle item family beside `single`, `combo`, and `vertical`.
- Why: many operators think in desired weekly outcomes such as publish week, competitor review, localization sprint, or comment-to-live conversion rather than in preset ownership or vertical grouping.
- Decision: reuse the same suite export path as vertical starters.
- Why: objective-first boards should remain as runnable as vertical starters instead of introducing a parallel command surface.

### Updated

- `tiktok-growth-operator.skill/scripts/generate_batch_preset.py`
- `tiktok-growth-operator.skill/references/batch-presets.md`
- `tiktok-growth-operator.skill/references/direct-use.md`
- `tiktok-growth-operator.skill/references/automation-workflows.md`

### Added Behavior

- bundle export now emits `launch-board` items
- current launch boards now include:
  - `publish-week-board`
  - `comment-to-live-board`
  - `competitor-review-board`
  - `localization-sprint-board`
  - `viral-testing-sprint-board`
- launch boards are seeded and exported into suite directories the same way as vertical starters
- bundle index now records `launch_board_count`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\generate_batch_preset.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_batch_preset.py" --template-bundle-root "D:\我的文档\Documents\Playground 4\.codex-tmp\preset-template-bundle-v7"`
- Result: passed and exported `5` launch boards in addition to existing single/combo/vertical items
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_batch_preset.py" --config "D:\我的文档\Documents\Playground 4\.codex-tmp\preset-template-bundle-v7\vertical-suites\publish-week-board\publish-week-board.config.json"`
- Result: passed and generated suite-local queue, manifest, report, and helper scripts for `publish-week-board`
- Ran: `python "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" --batch-file "D:\我的文档\Documents\Playground 4\.codex-tmp\preset-template-bundle-v7\vertical-suites\publish-week-board\publish-week-board.json" --dry-run --batch-root "D:\我的文档\Documents\Playground 4\.codex-tmp\preset-template-bundle-v7\vertical-suites\publish-week-board\batch-run"`
- Result: passed and produced `4` preview tasks for the objective-first publish-week suite

## 2026-05-04 Manager Board Upgrade

- Decision: add `manager-board` as a fifth preset-bundle item family.
- Why: some users think in roles and responsibilities first, such as content operator, live operator, strategy operator, or growth operator. That mental model should map to runnable entrypoints directly.
- Decision: keep manager boards on the same suite-export mechanism as vertical and launch boards.
- Why: the outer entry model can change without forking execution behavior or maintenance cost.

### Updated

- `tiktok-growth-operator.skill/scripts/generate_batch_preset.py`
- `tiktok-growth-operator.skill/references/batch-presets.md`
- `tiktok-growth-operator.skill/references/direct-use.md`
- `tiktok-growth-operator.skill/references/automation-workflows.md`

### Added Behavior

- bundle export now emits `manager-board` items
- current manager boards now include:
  - `content-operator-board`
  - `live-operator-board`
  - `strategy-operator-board`
  - `growth-operator-board`
- manager boards are seeded and exported into suite directories the same way as vertical and launch boards
- bundle index now records `manager_board_count`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\generate_batch_preset.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_batch_preset.py" --template-bundle-root "D:\我的文档\Documents\Playground 4\.codex-tmp\preset-template-bundle-v8"`
- Result: passed and exported `4` manager boards in addition to existing single/combo/vertical/launch-board items
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_batch_preset.py" --config "D:\我的文档\Documents\Playground 4\.codex-tmp\preset-template-bundle-v8\vertical-suites\growth-operator-board\growth-operator-board.config.json"`
- Result: passed and generated suite-local queue, manifest, report, and helper scripts for `growth-operator-board`
- Ran: `python "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" --batch-file "D:\我的文档\Documents\Playground 4\.codex-tmp\preset-template-bundle-v8\vertical-suites\growth-operator-board\growth-operator-board.json" --dry-run --batch-root "D:\我的文档\Documents\Playground 4\.codex-tmp\preset-template-bundle-v8\vertical-suites\growth-operator-board\batch-run"`
- Result: passed and produced `5` preview tasks for the role-first growth-operator suite

## 2026-05-04 Review, Docs, And Git Closure

- Decision: convert the late review findings into durable validators instead of leaving them as manual checks.
- Why: both doc mojibake and DOCX structure regressions are easy to miss in chat review but cheap to enforce automatically.
- Decision: keep reference-set overlap small but intentional, and document the role of each top-level reference instead of forcing one oversized catch-all file.
- Why: operators enter the package from different paths, so complete de-duplication would hurt usability more than it helps.

### Updated

- `tiktok-growth-operator.skill/SKILL.md`
- `tiktok-growth-operator.skill/references/article-2640429-feature-parity.md`
- `tiktok-growth-operator.skill/references/command-map.md`
- `tiktok-growth-operator.skill/references/final-handoff.md`
- `tiktok-growth-operator.skill/references/prompt-library.md`
- `tiktok-growth-operator.skill/references/source-map.md`
- `tiktok-growth-operator.skill/scripts/validate_skill_docs.py`
- `tiktok-growth-operator.skill/scripts/validate_export_outputs.py`
- `docs/quality/debt-log.md`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\validate_skill_docs.py" "tiktok-growth-operator.skill\scripts\validate_export_outputs.py" "tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\validate_skill_docs.py"`
- Result: passed and confirmed core operator docs are free of broken links and known mojibake markers
- Ran: `python "tiktok-growth-operator.skill\scripts\validate_export_outputs.py" --output-root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_export_validation_suite_v5"`
- Result: passed and now checks DOCX navigation text, bookmarks, and conditional figure-caption behavior in addition to XLSX structure
- Ran: `python "tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Result: passed after the validator upgrades

### Git Closure

- Local branch: `codex/tiktok-growth-operator-finish`
- Local commit: pending after this update block
- Push/PR status: blocked because the workspace still has no `remote` and no prior `HEAD`

## 2026-05-05 Cadence Board Upgrade

- Decision: add `cadence-board` as a sixth preset-bundle item family.
- Why: some operators think first in operating rhythm, such as daily loops, weekly reviews, launch sprints, or one live-session shift. That should map to runnable entrypoints directly.
- Decision: keep cadence boards on the same suite-export mechanism as vertical, launch, and manager boards.
- Why: changing the entry abstraction should not create a second execution system.

### Updated

- `tiktok-growth-operator.skill/scripts/generate_batch_preset.py`
- `tiktok-growth-operator.skill/references/batch-presets.md`
- `tiktok-growth-operator.skill/references/direct-use.md`
- `tiktok-growth-operator.skill/references/automation-workflows.md`

### Added Behavior

- bundle export now emits `cadence-board` items
- current cadence boards now include:
  - `daily-ops-board`
  - `weekly-ops-board`
  - `launch-sprint-board`
  - `live-shift-board`
- cadence boards are seeded and exported into suite directories the same way as other higher-level board types
- bundle index now records `cadence_board_count`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\generate_batch_preset.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_batch_preset.py" --template-bundle-root "D:\我的文档\Documents\Playground 4\.codex-tmp\preset-template-bundle-v9"`
- Result: passed and exported `4` cadence boards in addition to existing single/combo/vertical/launch-board/manager-board items
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_batch_preset.py" --config "D:\我的文档\Documents\Playground 4\.codex-tmp\preset-template-bundle-v9\vertical-suites\weekly-ops-board\weekly-ops-board.config.json"`
- Result: passed and generated suite-local queue, manifest, report, and helper scripts for `weekly-ops-board`
- Ran: `python "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" --batch-file "D:\我的文档\Documents\Playground 4\.codex-tmp\preset-template-bundle-v9\vertical-suites\weekly-ops-board\weekly-ops-board.json" --dry-run --batch-root "D:\我的文档\Documents\Playground 4\.codex-tmp\preset-template-bundle-v9\vertical-suites\weekly-ops-board\batch-run"`
- Result: passed and produced `4` preview tasks for the cadence-first weekly-ops suite

## 2026-05-05 Entry Selector Layer

- Decision: add a transparent entry-board selector instead of forcing operators to inspect batch docs manually before choosing a board family.
- Why: the package now has enough entry surfaces that the next usability bottleneck is selection, not missing workflows.
- Decision: keep the selector heuristic and explainable.
- Why: the operator should be able to see which outcome, role, cadence, or vertical signals caused one recommendation.

### Added

- `tiktok-growth-operator.skill/scripts/recommend_entry_board.py`
- `tiktok-growth-operator.skill/references/entry-selector.md`

### Updated

- `tiktok-growth-operator.skill/references/direct-use.md`
- `tiktok-growth-operator.skill/references/automation-workflows.md`
- `tiktok-growth-operator.skill/references/final-handoff.md`
- `tiktok-growth-operator.skill/SKILL.md`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\recommend_entry_board.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\recommend_entry_board.py" --query "I need a publish plan for this week" --format markdown`
- Result: passed and recommended `launch-board` with top slug `publish-week-board`
- Ran: `python "tiktok-growth-operator.skill\scripts\recommend_entry_board.py" --query "I'm the live operator for tonight's session" --format markdown`
- Result: passed and recommended `manager-board` with top slug `live-operator-board`
- Ran: `python "tiktok-growth-operator.skill\scripts\recommend_entry_board.py" --query "Set up my weekly competitor review" --format markdown`
- Result: passed and recommended `launch-board` with top slug `competitor-review-board`, while exposing `weekly-ops-board` as the cadence fallback
- Ran: `python "tiktok-growth-operator.skill\scripts\recommend_entry_board.py" --query "Give me the fastest beauty TikTok ops starter" --format markdown`
- Result: passed and recommended `vertical` with top slug `beauty-us-ops-starter`
- Ran: `python "tiktok-growth-operator.skill\scripts\recommend_entry_board.py" --query "Give me a daily board" --format markdown`
- Result: passed and recommended `cadence-board` with top slug `daily-ops-board`
- Ran: `python "tiktok-growth-operator.skill\scripts\recommend_entry_board.py" --query "Give me the fastest beauty TikTok ops starter" --bundle-root "D:\我的文档\Documents\Playground 4\.codex-tmp\preset-template-bundle-v9" --format markdown`
- Result: passed and returned the real `template_file`, `suite_root`, and `generate/dry-run/run` helper commands for `beauty-us-ops-starter`
- Ran: `python "tiktok-growth-operator.skill\scripts\recommend_entry_board.py" --query "Give me a daily board" --bundle-root "D:\我的文档\Documents\Playground 4\.codex-tmp\preset-template-bundle-v9" --format markdown`
- Result: passed and returned the real `template_file`, `suite_root`, and `generate/dry-run/run` helper commands for `daily-ops-board`
- Ran: `python "tiktok-growth-operator.skill\scripts\recommend_entry_board.py" --query "Give me a daily board" --format markdown`
- Result: passed and auto-discovered `D:\我的文档\Documents\Playground 4\.codex-tmp\preset-template-bundle-v9`, then returned the same bundle-aware path guidance without needing `--bundle-root`
- Ran: `python "tiktok-growth-operator.skill\scripts\recommend_entry_board.py" --query "I need a publish plan for this week" --format json`
- Result: passed and returned `resolved_bundle_root`, `recommended_boards`, and path-aware fallback payload in JSON

## 2026-05-05 Starter Launcher Layer

- Decision: add a one-step starter-board launcher on top of the entry selector.
- Why: after board selection became explainable, the next friction point was still manual copying of template paths and helper scripts.
- Decision: copy starter-local helper scripts into the generated folder instead of only referencing the original bundle suite.
- Why: the generated starter should remain locally runnable and portable inside the workspace.

### Added

- `tiktok-growth-operator.skill/scripts/start_entry_board.py`

### Updated

- `tiktok-growth-operator.skill/scripts/recommend_entry_board.py`
- `tiktok-growth-operator.skill/references/direct-use.md`
- `tiktok-growth-operator.skill/references/automation-workflows.md`
- `tiktok-growth-operator.skill/references/final-handoff.md`
- `tiktok-growth-operator.skill/SKILL.md`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\start_entry_board.py" "tiktok-growth-operator.skill\scripts\recommend_entry_board.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\start_entry_board.py" --query "Give me a daily board for TikTok beauty ops" --bundle-root "D:\我的文档\Documents\Playground 4\.codex-tmp\preset-template-bundle-v9" --output-root "D:\我的文档\Documents\Playground 4\.codex-tmp\entry-board-starter-smoke-v3"`
- Result: passed and scaffolded a local starter folder for `daily-ops-board` with copied config, template, local helper scripts, README, and recommendation manifest
- Ran: `python "tiktok-growth-operator.skill\scripts\recommend_entry_board.py" --query "Give me a daily board for TikTok beauty ops" --format markdown`
- Result: passed and now prioritizes `cadence-board` over `vertical` when strong daily cadence signals are present
- Ran: `python "tiktok-growth-operator.skill\scripts\start_entry_board.py" --query "Give me a daily board for TikTok beauty ops" --bundle-root "D:\我的文档\Documents\Playground 4\.codex-tmp\preset-template-bundle-v9" --output-root "D:\我的文档\Documents\Playground 4\.codex-tmp\entry-board-starter-smoke-v4" --generate --dry-run`
- Result: passed and created a fully local starter for `daily-ops-board`, generated the local queue, and produced a successful dry-run preview with `4` tasks

## 2026-05-05 Unified Board Routing And Doc Stabilization

- Decision: promote starter-board generation into the main operator router as a first-class `board` mode.
- Why: once `recommend_entry_board.py` and `start_entry_board.py` existed, the remaining usability gap was that broad board-style requests still had to bypass the main router manually.
- Decision: rewrite `references/entry-selector.md` cleanly instead of trying to preserve mixed-encoding fragments.
- Why: the entry-selector document had stale mojibake examples and had become less trustworthy than the script layer.

### Updated

- `tiktok-growth-operator.skill/scripts/run_operator_workflow.py`
- `tiktok-growth-operator.skill/scripts/start_project_workflow.py`
- `tiktok-growth-operator.skill/scripts/start_entry_board.py`
- `tiktok-growth-operator.skill/references/direct-use.md`
- `tiktok-growth-operator.skill/references/automation-workflows.md`
- `tiktok-growth-operator.skill/references/final-handoff.md`
- `tiktok-growth-operator.skill/references/entry-selector.md`

### Added Behavior

- unified router now supports explicit `--mode board`
- auto routing can now resolve role-first, cadence-first, outcome-first, and seeded-vertical requests into `board`
- route explanation payload now includes `board_preview`
- project launcher now supports `board` mode too
- entry-selector reference examples were rewritten into clean Chinese/English text and updated to document unified-router board usage

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\run_operator_workflow.py" "tiktok-growth-operator.skill\scripts\start_project_workflow.py" "tiktok-growth-operator.skill\scripts\start_entry_board.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\run_operator_workflow.py" --request "Give me a daily board for TikTok beauty ops" --output-root "D:\我的文档\Documents\Playground 4\.codex-tmp\auto-board-route-smoke-v2"`
- Result: passed and auto-routed the request to `board`
- Ran: `python "tiktok-growth-operator.skill\scripts\start_project_workflow.py" --request "Give me a daily board for TikTok beauty ops" --name project-board-route-smoke-v2 --output-root "D:\我的文档\Documents\Playground 4\.codex-tmp\project-board-route-smoke-v2"`
- Result: passed and preserved `board` routing through the project launcher

## 2026-05-05 Starter Auto-Discovery And Closure

- Decision: make `start_entry_board.py` auto-discover the latest local `preset-template-bundle*` when `--bundle-root` is omitted.
- Why: the one-step starter should stay low-friction by default, while still allowing explicit bundle pinning when reproducibility matters.
- Decision: extend durable validation to reject common visible-text mojibake in exported `docx` and `xlsx` outputs.
- Why: export quality is not complete if navigation and structure pass but operator-facing text is visibly garbled.

### Updated

- `tiktok-growth-operator.skill/scripts/start_entry_board.py`
- `tiktok-growth-operator.skill/scripts/validate_skill_docs.py`
- `tiktok-growth-operator.skill/scripts/validate_export_outputs.py`
- `tiktok-growth-operator.skill/references/direct-use.md`
- `tiktok-growth-operator.skill/references/automation-workflows.md`
- `tiktok-growth-operator.skill/references/entry-selector.md`
- `tiktok-growth-operator.skill/references/final-handoff.md`
- `tiktok-growth-operator.skill/SKILL.md`

## 2026-05-05 Batch Board Surface Upgrade

- Decision: extend the batch runner to understand `board` as a first-class task mode.
- Why: once the main operator router and project launcher could create starter boards, batch orchestration became the next inconsistent surface.
- Decision: keep batch-level `--dry-run` separate from board-task `generate/dry_run/run` flags.
- Why: batch preview should not accidentally execute starter-local queue generation or runs.

### Updated

- `tiktok-growth-operator.skill/scripts/batch_run_operator_workflows.py`
- `tiktok-growth-operator.skill/scripts/validate_all_workflows.py`
- `tiktok-growth-operator.skill/references/automation-workflows.md`

### Added Behavior

- batch tasks can now use `mode: board`
- batch preview now exposes board-specific preview fields such as `bundle_root`, `top_k`, and starter-run flags
- task validation now understands board-mode requirements and board-only field warnings
- full validation now includes one board-mode batch preview smoke check

## 2026-05-05 Board Handoff Surface Cleanup

- Decision: align board starter README, preset report, and batch report around one explicit operator handoff chain.
- Why: the package already had the right files and helper scripts, but the last-mile usability problem was that each artifact explained the next step differently.

### Updated

- `tiktok-growth-operator.skill/scripts/start_entry_board.py`
- `tiktok-growth-operator.skill/scripts/batch_run_operator_workflows.py`

### Added Behavior

- starter README now lists expected generated preset and batch artifact paths before execution
- starter README now documents one explicit operator order from scaffold to rerun
- batch report now shows richer board-specific success and preview handoff details

## 2026-05-05 Board Status Surface

- Decision: add a compact board status and handoff payload on top of the raw starter JSON.
- Why: the system already generated the correct files, but the main return payload still made the operator scan too much low-level path detail to know what to open next.

### Updated

- `tiktok-growth-operator.skill/scripts/start_entry_board.py`

### Added Behavior

- board starter results now include `status_summary`
- board starter results now include `operator_handoff`
- the next recommended file to open is now explicitly surfaced in the result payload

### Review Notes

- Correctness: filled the remaining gap where batch preview JSON already contained board metadata but `batch_report.md` did not render it.
- Readability: kept board handling in the existing mode-switch path instead of adding a parallel batch-specific abstraction.
- Architecture: stayed inside the owning package and validator surface; no new cross-package dependency edges.
- Security: no new external execution path was added beyond existing local script orchestration.
- Performance: validation still uses one-item board smoke only; no broad rerun cost increase.

### Remaining Follow-up

- fixed: added one hermetic batch board execution smoke against the stable local `preset-template-bundle-v9` bundle with board-local `generate` plus `dry_run`

## 2026-05-05 Route Quality And Long-Name Hardening

- Decision: treat explicit board phrasing, Chinese cadence phrases, and role-first board requests as stronger than incidental single-scene matches.
- Why: board-style requests such as weekly review boards and daily ops boards were being stolen by scene or goal routing, which made the unified router feel unreliable.
- Decision: truncate auto-generated goal run names, scene-run folder suffixes, and report base names.
- Why: long free-text workflow requests could exceed practical Windows path limits and fail during goal workspace creation.
- Decision: convert the discovered ambiguous-route probes into durable validation cases.
- Why: these were concrete regressions and should stay locked by `validate_all_workflows.py`, not by ad hoc chat memory.

### Updated

- `tiktok-growth-operator.skill/scripts/recommend_entry_board.py`
- `tiktok-growth-operator.skill/scripts/run_operator_workflow.py`
- `tiktok-growth-operator.skill/scripts/start_goal_workflow.py`
- `tiktok-growth-operator.skill/scripts/validate_all_workflows.py`

### Added Behavior

- Chinese board phrases such as `日常运营板` and `日更运营板` now resolve cleanly to `board`
- weekly competitor review requests now resolve to `board` instead of being stolen by scene `18`
- multi-stage workflow/process requests without board intent now stay in `goal`
- long workflow requests now generate shortened safe run names and shortened per-scene folder/file names
- validation now includes:
  - weekly competitor review -> `board`
  - `给我一个日常运营板` -> `board`
  - `我想做一个美妆TikTok日更运营板` -> `board`
  - `帮我做一个多市场本地化发布流程` -> `goal`
  - long English workflow request -> `goal` with bounded `run_name`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\recommend_entry_board.py" "tiktok-growth-operator.skill\scripts\run_operator_workflow.py" "tiktok-growth-operator.skill\scripts\start_goal_workflow.py" "tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\run_operator_workflow.py" --request "Set up my weekly competitor review"`
- Result: passed and now auto-routes to `board` with `weekly-ops-board`
- Ran: `python "tiktok-growth-operator.skill\scripts\run_operator_workflow.py" --request "给我一个日常运营板"`
- Result: passed and now auto-routes to `board` with `daily-ops-board`
- Ran: `python "tiktok-growth-operator.skill\scripts\run_operator_workflow.py" --request "我想做一个美妆TikTok日更运营板"`
- Result: passed and now auto-routes to `board` with `daily-ops-board`
- Ran: `python "tiktok-growth-operator.skill\scripts\run_operator_workflow.py" --request "帮我做一个多市场本地化发布流程"`
- Result: passed and now auto-routes to `goal`
- Ran: `python "tiktok-growth-operator.skill\scripts\run_operator_workflow.py" --request "Build a full Douyin workflow from topic selection to publish handoff"`
- Result: passed and now auto-routes to `goal` while generating a bounded safe `run_name`
- Ran: `python "tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Result: passed with the new route-quality and long-name regression checks

## 2026-05-05 Hybrid Board Ranking Upgrade

- Decision: when one request mixes vertical context, cadence intent, and explicit board phrasing, allow seeded vertical starters to outrank generic cadence boards.
- Why: requests such as `美妆 TikTok 日更运营板` are better served by a niche-ready starter than by a generic `daily-ops-board`, even though cadence is still important.

### Updated

- `tiktok-growth-operator.skill/scripts/recommend_entry_board.py`
- `tiktok-growth-operator.skill/scripts/validate_all_workflows.py`

### Added Behavior

- mixed `vertical + cadence + board` requests now boost `vertical` family ranking
- `recommend_entry_board.py`, `start_entry_board.py`, and unified `run_operator_workflow.py` now consistently pick `beauty-us-ops-starter` for `我想做一个美妆TikTok日更运营板`
- batch execute validation now expects the higher-signal vertical starter instead of the previous generic cadence board

### Validation

- Ran: `python "tiktok-growth-operator.skill\scripts\recommend_entry_board.py" --query "我想做一个美妆TikTok日更运营板" --format json`
- Result: passed and now recommends `vertical` with top slug `beauty-us-ops-starter`
- Ran: `python "tiktok-growth-operator.skill\scripts\start_entry_board.py" --query "我想做一个美妆TikTok日更运营板" --output-root ".\tiktok-growth-operator.skill\tmp\20260505_hybrid_vertical_cadence_smoke"`
- Result: passed and scaffolded `beauty-us-ops-starter`
- Ran: `python "tiktok-growth-operator.skill\scripts\run_operator_workflow.py" --request "我想做一个美妆TikTok日更运营板" --output-root ".\tiktok-growth-operator.skill\tmp\20260505_hybrid_vertical_cadence_route"`
- Result: passed and unified auto-routing also selected `beauty-us-ops-starter`

## 2026-05-05 Review, Debt, And Reference Cleanup

- Decision: slim the reference set by keeping `direct-use.md` as the command cookbook and pushing `automation-workflows.md` back toward ownership, behavior, and validation semantics.
- Why: the package had reached the point where `direct-use.md`, `automation-workflows.md`, and `final-handoff.md` were all repeating the same command examples, which made future updates noisier and easier to desync.
- Decision: update the local PR handoff with the latest route-quality hardening commit and residual review risks.
- Why: the handoff document should reflect the actual local branch state, not stop one commit early.
- Decision: record the remaining route-eval and bundle-fixture gaps explicitly in the workspace debt log.
- Why: these are now the main non-remote technical debts left after board routing, export quality, and validation closure.

### Updated

- `tiktok-growth-operator.skill/references/automation-workflows.md`
- `tiktok-growth-operator.skill/references/final-handoff.md`
- `reports/2026-05-05-tiktok-growth-operator-local-pr-handoff.md`
- `docs/quality/debt-log.md`

### Added Behavior

- `automation-workflows.md` now points operators back to `direct-use.md` for copy-ready commands instead of repeating the unified-router command set
- `final-handoff.md` now documents route-regression and long-name validation coverage more explicitly
- the local PR handoff now includes the latest route-hardening commit and updated residual-risk notes
- the workspace debt log now captures:
  - local bundle-fixture dependence in board validation
  - heuristic-first routing that still wants a broader saved eval corpus

### Validation

- Pending: `python "tiktok-growth-operator.skill\scripts\validate_skill_docs.py"`
- Pending: `python "tiktok-growth-operator.skill\scripts\validate_export_outputs.py" --output-root ".\tiktok-growth-operator.skill\tmp\20260505_export_validation_suite_doc_cleanup"`

## 2026-05-05 Direct-Use Template Unification

- Decision: make `execution_template` a required part of every scene scaffold instead of an optional generic add-on.
- Why: the user wants all 19 scenes to be directly callable in pure Codex, not just structurally documented.
- Decision: specialize execution templates per scene instead of using one shared generic request shell.
- Why: collection, teardown, insight, brief, and matrix scenes need different request language, variable examples, workflow emphasis, and completion criteria to be genuinely usable.
- Decision: turn execution-template completeness into a validator-enforced contract.
- Why: without hard validation, the direct-use layer would drift back toward partial or empty scaffolds over time.

### Updated

- `tiktok-growth-operator.skill/scripts/scene_report_presets.py`
- `tiktok-growth-operator.skill/scripts/validate_scene_presets.py`
- `tiktok-growth-operator.skill/scripts/generate_scene_report.py`
- `tiktok-growth-operator.skill/references/scene-report-contract.md`

### Added Behavior

- every scene payload now includes a populated `execution_template`
- direct-use templates now expose:
  - scene-specific `recommended_request`
  - scene-specific `recommended_runner_args`
  - variable inputs with realistic per-scene examples
  - scene-specific Codex prompt scaffold lines
  - operator workflow steps
  - completion-oriented output checklist
- `generate_scene_report.py` now renders the direct-use layer into Markdown under `## Direct-Use Template`
- `validate_scene_presets.py` now fails if any scene is missing:
  - `recommended_request`
  - `recommended_runner_args`
  - `variable_inputs`
  - `codex_prompt_scaffold`
  - `workflow_steps`
  - `output_checklist`

### Validation

- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\scene_report_presets.py" ".\tiktok-growth-operator.skill\scripts\generate_scene_report.py" ".\tiktok-growth-operator.skill\scripts\validate_scene_presets.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_scene_presets.py"`
- Result: passed with `19` scenes, `19` presets, `0` errors, `0` warnings
- Ran: `python ".\tiktok-growth-operator.skill\scripts\generate_scene_report.py" --scene 03 --project "Template Audit" --output ".\tiktok-growth-operator.skill\tmp\20260505_scene03_template_audit_v2.json" --format json`
- Result: passed and the generated payload showed the new scene-specific execution template
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Result: passed with `success: true` after the execution-template changes

## 2026-05-05 Bilingual Direct-Use Layer And Scene Quick Reference

- Decision: add a Chinese direct-call layer alongside the English execution template fields.
- Why: the user is operating in Chinese and wants the 19 scenes to be directly callable without having to translate intent into English first.
- Decision: generate one durable 19-scene quick-reference file from the scene catalog and execution-template payloads.
- Why: a manually maintained cheat sheet would drift quickly once scene templates continue to evolve.
- Decision: include quick-reference generation inside the full workflow validation surface.
- Why: the durable direct-use docs should be regenerated and checked as part of the package, not treated as a side artifact.

### Added

- `tiktok-growth-operator.skill/scripts/generate_scene_quick_reference.py`
- `tiktok-growth-operator.skill/references/scene-quick-reference.md`

### Updated

- `tiktok-growth-operator.skill/scripts/scene_report_presets.py`
- `tiktok-growth-operator.skill/scripts/generate_scene_report.py`
- `tiktok-growth-operator.skill/scripts/validate_scene_presets.py`
- `tiktok-growth-operator.skill/scripts/validate_skill_docs.py`
- `tiktok-growth-operator.skill/scripts/validate_all_workflows.py`
- `tiktok-growth-operator.skill/references/scene-report-contract.md`
- `tiktok-growth-operator.skill/references/scene-report-example.json`
- `tiktok-growth-operator.skill/references/direct-use.md`
- `tiktok-growth-operator.skill/SKILL.md`

### Added Behavior

- every scene now includes:
  - `recommended_request_zh`
  - `codex_prompt_scaffold_zh`
- Markdown scene reports now render both:
  - English direct-use request
  - Chinese direct-use request
  - English prompt scaffold
  - Chinese prompt scaffold
- the new `scene-quick-reference.md` now provides one scan-friendly page for all 19 scenes with:
  - scene title
  - deliverable family
  - English request
  - Chinese request
  - key inputs
  - expected outputs
  - main runner command
- full validation now recompiles and executes `generate_scene_quick_reference.py`

### Validation

- Ran: `python ".\tiktok-growth-operator.skill\scripts\generate_scene_quick_reference.py"`
- Result: passed and regenerated `references/scene-quick-reference.md`
- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\scene_report_presets.py" ".\tiktok-growth-operator.skill\scripts\generate_scene_report.py" ".\tiktok-growth-operator.skill\scripts\generate_scene_quick_reference.py" ".\tiktok-growth-operator.skill\scripts\validate_scene_presets.py" ".\tiktok-growth-operator.skill\scripts\validate_skill_docs.py" ".\tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_skill_docs.py"`
- Result: passed and now includes `references/scene-quick-reference.md`
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_scene_presets.py"`
- Result: passed with `19` scenes, `19` presets, `0` errors, `0` warnings after adding bilingual execution-template fields
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Result: passed with `success: true` after adding quick-reference generation into the validation chain

## 2026-05-05 Validation Fixture Self-Generation

- Decision: make `validate_all_workflows.py` generate its own preset-template fixture before board routing and batch smokes run.
- Why: durable validation should not depend on one preexisting `.codex-tmp/preset-template-bundle-v9` tree outside the package-owned validation flow.
- Decision: keep the generated fixture inside `tiktok-growth-operator.skill/tmp/` instead of checking a static bundle into references.
- Why: this keeps the validator hermetic enough for local reruns without expanding the durable reference set.

### Updated

- `tiktok-growth-operator.skill/scripts/validate_all_workflows.py`

### Added Behavior

- `validate_all_workflows.py` now builds `tiktok-growth-operator.skill/tmp/20260505_validate_bundle_fixture`
- board starter smoke uses the generated fixture instead of a preexisting `.codex-tmp` bundle
- batch board preview and execute smokes both consume the same generated validation bundle root

### Validation

- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Result: passed and created the self-generated validation bundle fixture plus successful board preview/execute smoke outputs

## 2026-05-05 Creative Brief Quick Reference

- Decision: add one dedicated quick-reference generator for scenes `09` to `16`.
- Why: the most Clipcat-like value is concentrated in the creative-brief, localization, asset-family, and benchmark scenes, so operators should have one shorter cookbook for those outputs instead of scanning the full 19-scene index.

### Added

- `tiktok-growth-operator.skill/scripts/generate_creative_brief_quick_reference.py`
- `tiktok-growth-operator.skill/references/creative-brief-quick-reference.md`

### Updated

- `tiktok-growth-operator.skill/scripts/validate_skill_docs.py`
- `tiktok-growth-operator.skill/scripts/validate_all_workflows.py`
- `tiktok-growth-operator.skill/references/direct-use.md`
- `tiktok-growth-operator.skill/SKILL.md`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\generate_creative_brief_quick_reference.py" "tiktok-growth-operator.skill\scripts\load_route_eval_fixtures.py" "tiktok-growth-operator.skill\scripts\validate_skill_docs.py" "tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_creative_brief_quick_reference.py"`
- Ran: `python "tiktok-growth-operator.skill\scripts\validate_skill_docs.py"`
- Ran: `python "tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Result: passed after aligning the validator contract and rerunning the full workflow suite

## 2026-05-05 Route Eval Fixtures

- Decision: move natural-language routing expectations into one versioned fixture file instead of leaving them as hard-coded validator cases only.
- Why: the package now has enough board, scene, goal, and pack routing behavior that regression expectations should be inspectable, extensible, and reusable across validators.

### Added

- `tiktok-growth-operator.skill/references/route-eval-fixtures.json`
- `tiktok-growth-operator.skill/scripts/load_route_eval_fixtures.py`

### Updated

- `tiktok-growth-operator.skill/scripts/validate_skill_docs.py`
- `tiktok-growth-operator.skill/scripts/validate_all_workflows.py`
- `docs/quality/debt-log.md`

## 2026-05-05 Chinese Operator Entry Tightening

- Decision: add a first-screen Chinese copy-ready starter block to `references/direct-use.md`.
- Why: the skill already had full routing and scene coverage, but the user-facing friction was still the first command or first sentence an operator should copy.
- Decision: add a fast chooser and common-missing-evidence section to the creative quick reference.
- Why: scenes `09` to `16` are the highest-value creative workflows, and operators need quicker scene selection plus a clearer view of what input gaps usually break output quality.

### Updated

- `tiktok-growth-operator.skill/references/direct-use.md`
- `tiktok-growth-operator.skill/references/creative-brief-quick-reference.md`
- `tiktok-growth-operator.skill/scripts/validate_skill_docs.py`

### Validation

- Ran: `python "tiktok-growth-operator.skill\\scripts\\validate_skill_docs.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\\scripts\\validate_all_workflows.py"`
- Result: passed

## 2026-05-05 Creative Scene Handoff Hardening

- Decision: extend scenes `09` to `16` with explicit production-handoff style sections instead of stopping at strategy-only outputs.
- Why: the creative half of the package is most useful when it can hand one board, brief, or benchmark directly into scripting, design, rendering, or production without another translation pass.
- Decision: make `validate_scene_presets.py` assert exact section headers for the creative-scene tables.
- Why: these scenes now have a stronger deliverable contract, so broad “table exists” checks are no longer sufficient to prevent drift.

### Updated

- `tiktok-growth-operator.skill/scripts/scene_report_presets.py`
- `tiktok-growth-operator.skill/scripts/validate_scene_presets.py`
- `tiktok-growth-operator.skill/references/scene-quick-reference.md`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\scene_report_presets.py" "tiktok-growth-operator.skill\scripts\validate_scene_presets.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\generate_scene_quick_reference.py"`
- Result: passed and regenerated the 19-scene quick reference with the stronger creative-scene output contracts
- Ran: `python "tiktok-growth-operator.skill\scripts\validate_scene_presets.py"`
- Result: passed with exact creative-scene header assertions
- Ran: `python "tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Result: passed with `success: true`

## 2026-05-05 Creative Production Handoff Pack

- Decision: add one third operator-pack type, `creative-production-handoff`, for scenes `09` to `16`.
- Why: `publish-prep` is useful for distribution readiness, but the creative scenes now also need a direct bridge into scripting, editing, design, rendering, and localization execution.
- Decision: auto-derive the new pack for creative scenes in both scene-run and capture-pack workflows.
- Why: if the source scene already exists to structure the brief, operators should not need a second manual command just to produce a production-facing handoff.

### Added

- `tiktok-growth-operator.skill/references/creative-production-handoff-pack.md`

### Updated

- `tiktok-growth-operator.skill/SKILL.md`
- `tiktok-growth-operator.skill/references/direct-use.md`
- `tiktok-growth-operator.skill/references/automation-workflows.md`
- `tiktok-growth-operator.skill/references/final-handoff.md`
- `tiktok-growth-operator.skill/scripts/generate_operator_pack.py`
- `tiktok-growth-operator.skill/scripts/recommend_scene_chain.py`
- `tiktok-growth-operator.skill/scripts/run_operator_workflow.py`
- `tiktok-growth-operator.skill/scripts/start_scene_run.py`
- `tiktok-growth-operator.skill/scripts/start_capture_pack_run.py`
- `tiktok-growth-operator.skill/scripts/validate_capture_pack_workflows.py`
- `tiktok-growth-operator.skill/scripts/validate_skill_docs.py`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\generate_operator_pack.py" "tiktok-growth-operator.skill\scripts\recommend_scene_chain.py" "tiktok-growth-operator.skill\scripts\run_operator_workflow.py" "tiktok-growth-operator.skill\scripts\start_capture_pack_run.py" "tiktok-growth-operator.skill\scripts\start_scene_run.py" "tiktok-growth-operator.skill\scripts\validate_capture_pack_workflows.py" "tiktok-growth-operator.skill\scripts\validate_skill_docs.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\validate_skill_docs.py"`
- Result: passed with the new creative-production handoff reference included
- Ran: `python "tiktok-growth-operator.skill\scripts\validate_capture_pack_workflows.py"`
- Result: passed and generated a `creative-production-handoff` pack from the validated scene `15` capture workflow
