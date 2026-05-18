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

## 2026-05-09 Chinese-First Cleanup Pass

- Decision: finish the remaining Chinese-first cleanup in durable source instead of patching historical outputs by hand.
- Why: the remaining issues were template/example leakage and naming drift, so the correct fix belonged in preset, renderer, and reference generators.

### Updated

- `tiktok-growth-operator.skill/scripts/scene_report_presets.py`
- `tiktok-growth-operator.skill/scripts/render_scene_report.py`
- `tiktok-growth-operator.skill/scripts/generate_scene_quick_reference.py`
- `tiktok-growth-operator.skill/scripts/generate_creative_brief_quick_reference.py`
- `tiktok-growth-operator.skill/scripts/validate_skill_docs.py`
- `tiktok-growth-operator.skill/references/automation-workflows.md`

### What Changed

- Scene `04/05/17` residual English example values were localized in the durable preset/render path.
- `Brief` naming on the main user-facing reference surfaces was normalized toward `制作简报`.
- file-hint wording now renders as Chinese-first mixed labels such as `summary.json 或 aggregate_summary.json`.
- regenerated `scene-quick-reference.md` and `creative-brief-quick-reference.md` from source generators after naming cleanup.

### Validation

- Ran: `python -m py_compile` on the edited Python scripts
- Result: passed
- Ran: `python tiktok-growth-operator.skill\scripts\generate_scene_quick_reference.py`
- Result: passed
- Ran: `python tiktok-growth-operator.skill\scripts\generate_creative_brief_quick_reference.py`
- Result: passed
- Ran: representative rerender of Scene `04`, `05`, and `17` into `.codex-tmp\scene04-zh-pass-20260509-v12`, `.codex-tmp\scene05-zh-pass-20260509-v12`, and `.codex-tmp\scene17-zh-pass-20260509-v12`
- Result: passed for `md`, `docx`, and `xlsx`
- Ran: residual-English grep across the regenerated reference docs and the rerendered Scene `04/05/17` Markdown outputs
- Result: no remaining targeted residuals on the inspected export surfaces; remaining English hits were non-target internal automation prose in `references/automation-workflows.md`

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

## 2026-05-05 Final Consistency Closure

- Decision: align the capture-pack default operator-pack docs and implementation exactly.
- Why: the package now has enough handoff surfaces that even one stale default-pack line would mislead operators about what the runner actually generates.
- Decision: remove the unreachable scene `10` creative-pack branch from capture-pack defaults.
- Why: capture-pack support does not currently include scene `10`, so keeping that branch only made the implementation and docs harder to trust during review.

### Updated

- `tiktok-growth-operator.skill/scripts/start_capture_pack_run.py`
- `tiktok-growth-operator.skill/references/automation-workflows.md`
- `reports/2026-05-05-tiktok-growth-operator-local-pr-handoff.md`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\start_capture_pack_run.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\validate_skill_docs.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Result: passed with the final doc and default-pack alignment in place
## 2026-05-05 Creative Handoff Owner Deepening

- Decision: deepen `creative-production-handoff` into an owner-facing execution pack instead of leaving it as one generic production section.
- Why: once scenes `09` to `16` started auto-deriving handoff packs, the next usability bottleneck became role clarity. Script, design, localization, and production owners each needed their own next-action block.

### Updated

- `tiktok-growth-operator.skill/scripts/generate_operator_pack.py`
- `tiktok-growth-operator.skill/references/creative-production-handoff-pack.md`

### Added Behavior

- `creative-production-handoff` now includes:
  - `Script And Storyboard Handoff`
  - `Design And Layout Handoff`
  - `Localization And Review Handoff`
  - `Owner Map`
- the pack now carries stronger owner-specific next-step guidance derived from source-scene tables and requested outputs

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\\scripts\\generate_operator_pack.py"`
- Result: passed after fixing one helper-name regression
- Ran: `python "tiktok-growth-operator.skill\\scripts\\generate_operator_pack.py" --type creative-production-handoff --source-report ".\\tiktok-growth-operator.skill\\tmp\\20260504_validation_capture_scene15\\scene-15\\scene-15-validation-scene15-capture.json" --platform TikTok --market US --output-dir ".\\tiktok-growth-operator.skill\\tmp\\20260505_validation_creative_handoff_pack_v2"`
- Result: passed and generated the deeper owner-facing handoff pack
- Ran: `python "tiktok-growth-operator.skill\\scripts\\validate_capture_pack_workflows.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\\scripts\\validate_all_workflows.py"`
- Result: passed with `success: true`

## 2026-05-06 TikMatrix Real-Run Bridge

- Decision: bridge `E:\tiktok\TikMatrix` exports into the operator capture-pack format inside `tiktok-growth-operator.skill` instead of modifying the collector project.
- Why: the user explicitly required real TikTok runs while preserving the existing TikMatrix collection skill and runtime.
- Decision: reuse the existing `start_capture_pack_run.py` flow after writing a local bridge pack.
- Why: this keeps the operator runtime single-path and avoids forking a second import surface just for one collector.

### Added

- `tiktok-growth-operator.skill/scripts/run_tikmatrix_capture_bridge.py`

### Updated

- `tiktok-growth-operator.skill/scripts/validate_all_workflows.py`
- `tiktok-growth-operator.skill/references/automation-workflows.md`
- `tiktok-growth-operator.skill/references/direct-use.md`
- `tiktok-growth-operator.skill/references/final-handoff.md`

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\run_tikmatrix_capture_bridge.py" "tiktok-growth-operator.skill\scripts\start_capture_pack_run.py" "tiktok-growth-operator.skill\scripts\generate_operator_pack.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\run_tikmatrix_capture_bridge.py" --profile-posts-json "E:\tiktok\TikMatrix\tmp\live-profile-posts-browser-batch\mrorangecat555\profile_posts.json" --comments-json "E:\tiktok\TikMatrix\tmp\comments-live-mrorangecat-paged\7624057229930450192\comments.json" --downloads-json "E:\tiktok\TikMatrix\tmp\skill-batch-download\downloads.json" --scene 08 --name mrorangecat-comment-signal --project "Mr Orange Cat Comment Signal" --market US --formats md`
- Result: passed and produced a real scene `08` operator run plus `live-assist` pack from TikMatrix exports
- Ran: `python "tiktok-growth-operator.skill\scripts\run_tikmatrix_capture_bridge.py" --profile-posts-json "E:\tiktok\TikMatrix\tmp\live-profile-posts-browser-batch\mrorangecat555\profile_posts.json" --downloads-json "E:\tiktok\TikMatrix\tmp\skill-batch-download\downloads.json" --scene 17 --name mrorangecat-account-distill --project "Mr Orange Cat Creator Distillation" --market US --formats md`
- Result: passed and produced a real scene `17` operator run plus `publish-prep` pack from TikMatrix exports
- Ran: `python "tiktok-growth-operator.skill\scripts\validate_skill_docs.py"`
- Result: passed

## 2026-05-07 Public Parity Audit And Bridge Validator

- Decision: add one durable parity audit inside the skill package instead of leaving completion status only in chat.
- Why: the user explicitly asked what is already complete, what is still partial, and what remains to be done versus the article, site, and DOCX materials.
- Decision: add one standalone real TikMatrix bridge validator instead of depending only on the broader all-workflows suite.
- Why: the bridge is now a critical integration surface, and it should be verifiable without mentally unpacking the heavier mixed validator.

### Added

- `tiktok-growth-operator.skill/references/clipcat-openclaw-parity-audit.md`
- `tiktok-growth-operator.skill/scripts/validate_tikmatrix_bridge.py`

### Updated

- `tiktok-growth-operator.skill/SKILL.md`
- `tiktok-growth-operator.skill/references/direct-use.md`
- `tiktok-growth-operator.skill/references/final-handoff.md`
- `tiktok-growth-operator.skill/scripts/validate_skill_docs.py`
- `tiktok-growth-operator.skill/scripts/validate_all_workflows.py`

### Intended Validation

- `python -m py_compile ".\tiktok-growth-operator.skill\scripts\validate_tikmatrix_bridge.py" ".\tiktok-growth-operator.skill\scripts\validate_skill_docs.py" ".\tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- `python ".\tiktok-growth-operator.skill\scripts\validate_skill_docs.py"`
- `python ".\tiktok-growth-operator.skill\scripts\validate_tikmatrix_bridge.py"`

## 2026-05-07 Account Ops Bridge And Doc-Only Enterprise Boundaries

- Decision: add one safe operator bridge for TikMatrix logged-in account exports such as newest reply, notice, and following requests.
- Why: the user provided real TikTok inbox and account-operation request surfaces and wants platform-level parity without modifying the proven collector project.
- Decision: record cloud-phone, RPA, `养号`, and anti-detection topics as doc-only boundaries instead of pretending they are implemented.
- Why: the user explicitly allowed those topics to remain documented-only, and they require risky or external infrastructure.

### Added

- `tiktok-growth-operator.skill/references/account-ops-assist-pack.md`
- `tiktok-growth-operator.skill/references/rpa-and-account-farming-doc-only.md`
- `tiktok-growth-operator.skill/scripts/run_tikmatrix_account_ops_bridge.py`
- `tiktok-growth-operator.skill/scripts/validate_tikmatrix_account_ops_bridge.py`

### Updated

- `tiktok-growth-operator.skill/scripts/generate_operator_pack.py`
- `tiktok-growth-operator.skill/scripts/run_operator_workflow.py`
- `tiktok-growth-operator.skill/scripts/start_scene_run.py`
- `tiktok-growth-operator.skill/scripts/start_capture_pack_run.py`
- `tiktok-growth-operator.skill/scripts/validate_skill_docs.py`
- `tiktok-growth-operator.skill/scripts/validate_all_workflows.py`
- `tiktok-growth-operator.skill/SKILL.md`
- `tiktok-growth-operator.skill/references/automation-workflows.md`
- `tiktok-growth-operator.skill/references/direct-use.md`
- `tiktok-growth-operator.skill/references/final-handoff.md`
- `tiktok-growth-operator.skill/references/clipcat-openclaw-parity-audit.md`

### Intended Validation

- `python -m py_compile ".\tiktok-growth-operator.skill\scripts\run_tikmatrix_account_ops_bridge.py" ".\tiktok-growth-operator.skill\scripts\validate_tikmatrix_account_ops_bridge.py" ".\tiktok-growth-operator.skill\scripts\generate_operator_pack.py" ".\tiktok-growth-operator.skill\scripts\run_operator_workflow.py"`
- `python ".\tiktok-growth-operator.skill\scripts\validate_skill_docs.py"`
- `python ".\tiktok-growth-operator.skill\scripts\validate_tikmatrix_account_ops_bridge.py"`

## 2026-05-07 Expanded Real TikMatrix Coverage Sync

- Decision: mark the durable parity and handoff docs from observed real bridge runs instead of leaving them stale at scenes `08` and `17` only.
- Why: the workspace already proved a much wider safe operator surface, and the docs needed to match reality before any further parity work.

### Updated

- `tiktok-growth-operator.skill/references/clipcat-openclaw-parity-audit.md`
- `tiktok-growth-operator.skill/references/final-handoff.md`
- `plans/active/2026-05-04-clipcat-openclaw-codex-skill.md`

### Real Runs Recorded

- Scene `11`
  - output root: `D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260507_002608-tikmatrix-bridge-mrorangecat-scene11`
- Scene `12`
  - output root: `D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260507_002609-tikmatrix-bridge-mrorangecat-scene12`
- Scene `13`
  - output root: `D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260507_002608-tikmatrix-bridge-mrorangecat-scene13`
  - target markets: `US,Japan,Germany`
- Scene `14`
  - output root: `D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260507_002608-tikmatrix-bridge-mrorangecat-scene14`
- Scene `15`
  - output root: `D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260507_002639-tikmatrix-bridge-mrorangecat-scene15`
  - target languages: `English,Japanese,German`
- Scene `16`
  - output root: `D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260507_002639-tikmatrix-bridge-mrorangecat-scene16`
- Scene `18`
  - output root: `D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260507_002639-tikmatrix-bridge-mrorangecat-scene18`
- Scene `19`
  - output root: `D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260507_002641-tikmatrix-bridge-mrorangecat-scene19`
- Account-ops validator
  - output root: `D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260507_validate_tikmatrix_account_ops_bridge`

### Validation

- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\run_tikmatrix_capture_bridge.py" ".\tiktok-growth-operator.skill\scripts\validate_tikmatrix_bridge.py" ".\tiktok-growth-operator.skill\scripts\run_tikmatrix_account_ops_bridge.py" ".\tiktok-growth-operator.skill\scripts\validate_tikmatrix_account_ops_bridge.py" ".\tiktok-growth-operator.skill\scripts\generate_operator_pack.py" ".\tiktok-growth-operator.skill\scripts\run_operator_workflow.py" ".\tiktok-growth-operator.skill\scripts\start_scene_run.py" ".\tiktok-growth-operator.skill\scripts\start_capture_pack_run.py" ".\tiktok-growth-operator.skill\scripts\validate_skill_docs.py" ".\tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_skill_docs.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_tikmatrix_bridge.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_tikmatrix_account_ops_bridge.py"`
- Result: passed

## 2026-05-07 Scene 01 Enrichment And Scene 03 Real Teardown

- Decision: enrich ranked TikMatrix bridge rows with downloaded single-video metadata when available instead of treating `profile_posts.json` alone as the full evidence surface.
- Why: `Scene 01` and `Scene 03` were already runnable, but their shortlist quality degraded whenever `profile_posts.json` lacked caption text or topic hints.
- Decision: keep the enrichment in the bridge layer, not the collector project.
- Why: the user explicitly required preserving `E:\tiktok\TikMatrix` and improving only the Codex-side operator runtime.

### Updated

- `tiktok-growth-operator.skill/scripts/run_tikmatrix_capture_bridge.py`
- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`
- `tiktok-growth-operator.skill/references/clipcat-openclaw-parity-audit.md`
- `plans/active/2026-05-04-clipcat-openclaw-codex-skill.md`

### Added Behavior

- `downloads.json -> metadata_path -> single-video JSON` can now enrich ranked bridge rows with:
  - `caption_text`
  - `hook_text`
  - `core_topic`
  - `hashtags`
  - `author_signature`
  - `author_verified`
  - `music_title`
- `Scene 01` now uses the enriched fields to improve:
  - shortlist `Core Topic`
  - `Why Selected`
  - recovered hook/topic evidence in the report
- `Scene 03` now uses the enriched shortlist as direct teardown input, so the same real run can move from collection into deeper breakdown more cleanly.

### Real Runs Recorded

- Scene `01`
  - output root: `D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260507_004634-tikmatrix-bridge-mrorangecat-scene01-enhanced-v2`
- Scene `03`
  - output root: `D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260507_004634-tikmatrix-bridge-mrorangecat-scene03-real-run-v2`

### Validation

- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\run_tikmatrix_capture_bridge.py" ".\tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\run_tikmatrix_capture_bridge.py" --profile-posts-json "E:\tiktok\TikMatrix\tmp\live-profile-posts-browser-batch\mrorangecat555\profile_posts.json" --downloads-json "E:\tiktok\TikMatrix\tmp\skill-batch-download\downloads.json" --scene 01 --name mrorangecat-scene01-enhanced-v2 --project "Mr Orange Cat Viral Video Collection Enhanced" --market US --formats md,docx,xlsx`
- Result: passed and produced an enhanced real `Scene 01` shortlist with stronger recovered hook/topic evidence where metadata existed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\run_tikmatrix_capture_bridge.py" --profile-posts-json "E:\tiktok\TikMatrix\tmp\live-profile-posts-browser-batch\mrorangecat555\profile_posts.json" --downloads-json "E:\tiktok\TikMatrix\tmp\skill-batch-download\downloads.json" --scene 03 --name mrorangecat-scene03-real-run-v2 --project "Mr Orange Cat Deep Teardown" --market US --formats md,docx,xlsx`
- Result: passed and produced a real `Scene 03` teardown chain from the enhanced shortlist

## 2026-05-07 Richer Real TikTok Account Reruns For Scene 01 And Scene 03

- Decision: rerun the bridge against richer real TikTok accounts instead of continuing to benchmark `Scene 01` and `Scene 03` mostly on `mrorangecat555`.
- Why: the bridge enrichment was now correct, but the older sample still limited output quality whenever upstream caption metadata was sparse.
- Decision: use the available browser-capable runtime first, then restore the original `E:\tiktok\TikMatrix\.venv` as the preferred collector runtime once disk pressure is removed.
- Why: the richer reruns needed to continue immediately, but the durable goal was always to bring the original collector chain back instead of leaving `.venv-api` as the long-term main path.

### Real Runs Recorded

- Browser-authenticated profile-post download:
  - `E:\tiktok\TikMatrix\tmp\codex-mustsharenews-profile-post-downloads-20260507\mustsharenews`
  - `E:\tiktok\TikMatrix\tmp\codex-sherrinandyixi-profile-post-downloads-20260507\sherrinandyixi`
- Scene `01` from `mustsharenews`
  - output root: `D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260507_010741-tikmatrix-bridge-mustsharenews-scene01-real-rerun`
- Scene `03` from `mustsharenews`
  - output root: `D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260507_010740-tikmatrix-bridge-mustsharenews-scene03-real-rerun`
- Scene `01` from `sherrinandyixi`
  - output root: `D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260507_010741-tikmatrix-bridge-sherrinandyixi-scene01-real-rerun`
- Scene `03` from `sherrinandyixi`
  - output root: `D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260507_010741-tikmatrix-bridge-sherrinandyixi-scene03-real-rerun`

### Observed Outcome

- `mustsharenews` is the stronger fixture for authority-led packaging, longer caption recovery, and mixed image/video studies.
- `sherrinandyixi` is the stronger fixture for creator-native hook cadence, episodic caption patterns, and subtitle-rich conversational rows.
- Both reruns materially improved `caption_text`, `hook_text`, and `core_topic` quality relative to the weaker `mrorangecat555` sample.

### Validation

- Ran: `E:\tiktok\TikMatrix\.venv-api\Scripts\python.exe E:\tiktok\TikMatrix\scripts\run_from_skill.py profile-posts-browser-download --url "https://www.tiktok.com/@mustsharenews" --count 12 --max-pages 2 --new-only --output-dir "E:\tiktok\TikMatrix\tmp\codex-mustsharenews-profile-post-downloads-20260507"`
- Result: passed and exported `profile_posts.json`, `downloads.json`, and downloaded media/metadata for 12 posts
- Ran: `E:\tiktok\TikMatrix\.venv-api\Scripts\python.exe E:\tiktok\TikMatrix\scripts\run_from_skill.py profile-posts-browser-download --url "https://www.tiktok.com/@sherrinandyixi" --count 12 --max-pages 2 --new-only --output-dir "E:\tiktok\TikMatrix\tmp\codex-sherrinandyixi-profile-post-downloads-20260507"`
- Result: passed and exported `profile_posts.json`, `downloads.json`, and downloaded media/metadata for 12 posts
- Ran: `python ".\tiktok-growth-operator.skill\scripts\run_tikmatrix_capture_bridge.py" --profile-posts-json "E:\tiktok\TikMatrix\tmp\codex-mustsharenews-profile-post-downloads-20260507\mustsharenews\profile_posts.json" --downloads-json "E:\tiktok\TikMatrix\tmp\codex-mustsharenews-profile-post-downloads-20260507\mustsharenews\downloads.json" --scene 01 --name mustsharenews-scene01-real-rerun --project "MustShareNews Real Runtime Rerun" --market SG --min-likes 1000 --qualified-count 5`
- Result: passed and produced a richer real `Scene 01` shortlist
- Ran: `python ".\tiktok-growth-operator.skill\scripts\run_tikmatrix_capture_bridge.py" --profile-posts-json "E:\tiktok\TikMatrix\tmp\codex-mustsharenews-profile-post-downloads-20260507\mustsharenews\profile_posts.json" --downloads-json "E:\tiktok\TikMatrix\tmp\codex-mustsharenews-profile-post-downloads-20260507\mustsharenews\downloads.json" --scene 03 --name mustsharenews-scene03-real-rerun --project "MustShareNews Real Runtime Rerun" --market SG --min-likes 1000 --qualified-count 5`
- Result: passed and produced a richer real `Scene 03` teardown chain
- Ran: `python ".\tiktok-growth-operator.skill\scripts\run_tikmatrix_capture_bridge.py" --profile-posts-json "E:\tiktok\TikMatrix\tmp\codex-sherrinandyixi-profile-post-downloads-20260507\sherrinandyixi\profile_posts.json" --downloads-json "E:\tiktok\TikMatrix\tmp\codex-sherrinandyixi-profile-post-downloads-20260507\sherrinandyixi\downloads.json" --scene 01 --name sherrinandyixi-scene01-real-rerun --project "SherrinAndYixi Real Runtime Rerun" --market SG --min-likes 1000 --qualified-count 5`
- Result: passed and produced a richer creator-style `Scene 01` shortlist
- Ran: `python ".\tiktok-growth-operator.skill\scripts\run_tikmatrix_capture_bridge.py" --profile-posts-json "E:\tiktok\TikMatrix\tmp\codex-sherrinandyixi-profile-post-downloads-20260507\sherrinandyixi\profile_posts.json" --downloads-json "E:\tiktok\TikMatrix\tmp\codex-sherrinandyixi-profile-post-downloads-20260507\sherrinandyixi\downloads.json" --scene 03 --name sherrinandyixi-scene03-real-rerun --project "SherrinAndYixi Real Runtime Rerun" --market SG --min-likes 1000 --qualified-count 5`
- Result: passed and produced a richer creator-style `Scene 03` teardown chain

## 2026-05-07 TikMatrix Original .venv Runtime Restored

- Decision: switch the preferred real TikTok collector runtime back to `E:\tiktok\TikMatrix\.venv`.
- Why: after the safe `C:` cleanup created enough free space, restoring the original runtime was lower risk than keeping a split `.venv-api` operating path.

### Real Runs Recorded

- Original `.venv` browser smoke export:
  - `E:\tiktok\TikMatrix\tmp\codex-smoke-mustsharenews-browser-venv-20260507`
- Original `.venv` browser download export:
  - `E:\tiktok\TikMatrix\tmp\codex-mustsharenews-profile-post-downloads-venv-20260507\mustsharenews`
- `Scene 01` from restored `.venv` export:
  - `D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260507_014554-tikmatrix-bridge-mustsharenews-scene01-venv-restored`
- `Scene 03` from restored `.venv` export:
  - `D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260507_014554-tikmatrix-bridge-mustsharenews-scene03-venv-restored`

### Observed Outcome

- `playwright==1.52.0` is now installed and callable inside the original `E:\tiktok\TikMatrix\.venv`.
- `profile-posts-browser` now runs successfully in the original runtime against real TikTok browser-authenticated state.
- `profile-posts-browser-download` now runs successfully in the original runtime with mixed image and video posts, `download_count=8`, and `error_count=0`.
- the restored collector output can be bridged directly into `tiktok-growth-operator.skill` for real `Scene 01` and `Scene 03` outputs without changing the collector source.

### Validation

- Ran: `E:\tiktok\TikMatrix\.venv\Scripts\python.exe -m pip show playwright`
- Result: passed and confirmed `playwright==1.52.0` inside the original collector runtime
- Ran: `E:\tiktok\TikMatrix\.venv\Scripts\python.exe -m playwright --help`
- Result: passed
- Ran: `E:\tiktok\TikMatrix\.venv\Scripts\python.exe E:\tiktok\TikMatrix\scripts\run_from_skill.py profile-posts-browser --url "https://www.tiktok.com/@mustsharenews" --count 5 --max-pages 1 --output-dir "E:\tiktok\TikMatrix\tmp\codex-smoke-mustsharenews-browser-venv-20260507"`
- Result: passed and exported `profile_posts.json`, `profile_posts.csv`, and `profile_posts.txt` from the original runtime
- Ran: `E:\tiktok\TikMatrix\.venv\Scripts\python.exe E:\tiktok\TikMatrix\scripts\run_from_skill.py profile-posts-browser-download --url "https://www.tiktok.com/@mustsharenews" --count 8 --max-pages 1 --new-only --output-dir "E:\tiktok\TikMatrix\tmp\codex-mustsharenews-profile-post-downloads-venv-20260507"`
- Result: passed with `download_count=8` and `error_count=0`
- Ran: `python ".\tiktok-growth-operator.skill\scripts\run_tikmatrix_capture_bridge.py" --profile-posts-json "E:\tiktok\TikMatrix\tmp\codex-mustsharenews-profile-post-downloads-venv-20260507\mustsharenews\profile_posts.json" --downloads-json "E:\tiktok\TikMatrix\tmp\codex-mustsharenews-profile-post-downloads-venv-20260507\mustsharenews\downloads.json" --scene 01 --name mustsharenews-scene01-venv-restored --project "MustShareNews Venv Restored Runtime" --market SG --min-likes 1000 --qualified-count 5 --formats md`
- Result: passed and produced a restored-runtime `Scene 01` shortlist
- Ran: `python ".\tiktok-growth-operator.skill\scripts\run_tikmatrix_capture_bridge.py" --profile-posts-json "E:\tiktok\TikMatrix\tmp\codex-mustsharenews-profile-post-downloads-venv-20260507\mustsharenews\profile_posts.json" --downloads-json "E:\tiktok\TikMatrix\tmp\codex-mustsharenews-profile-post-downloads-venv-20260507\mustsharenews\downloads.json" --scene 03 --name mustsharenews-scene03-venv-restored --project "MustShareNews Venv Restored Runtime" --market SG --min-likes 1000 --qualified-count 5 --formats md`
- Result: passed and produced a restored-runtime `Scene 03` teardown chain

## 2026-05-07 Unified Encoding Output Layer And Historical Re-render Repair

- Decision: route the main scene, goal, project, and history entrypoints through one shared text-normalization module instead of leaving mixed direct `write_text` behavior.
- Why: the real runtime was already stable, but mixed local writes still allowed Windows-facing markdown artifacts and old mojibake classes to drift across workflow entrypoints.
- Decision: add one batch historical scene-output re-render script instead of hand-editing old markdown files.
- Why: the canonical repair source is the existing `scene-*.json` report contract, not manual edits to generated markdown.

### Added

- `tiktok-growth-operator.skill/scripts/rerender_scene_outputs.py`

### Updated

- `tiktok-growth-operator.skill/scripts/text_normalization.py`
- `tiktok-growth-operator.skill/scripts/start_scene_run.py`
- `tiktok-growth-operator.skill/scripts/start_goal_workflow.py`
- `tiktok-growth-operator.skill/scripts/start_project_workflow.py`
- `tiktok-growth-operator.skill/scripts/run_scene_workflow.py`
- `tiktok-growth-operator.skill/scripts/run_operator_workflow.py`
- `tiktok-growth-operator.skill/scripts/validate_export_outputs.py`
- `tiktok-growth-operator.skill/references/direct-use.md`
- `tiktok-growth-operator.skill/references/final-handoff.md`
- `tiktok-growth-operator.skill/references/clipcat-openclaw-parity-audit.md`

### Added Behavior

- shared UTF-8 normalization now covers the main scene, goal, project, pack-history, bridge, and renderer write paths
- Markdown/text outputs now consistently use the same Windows-friendly UTF-8 BOM write path
- historical scene exports can be batch-repaired by re-rendering from existing `scene-*.json` files

### Validation

- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\text_normalization.py" ".\tiktok-growth-operator.skill\scripts\start_scene_run.py" ".\tiktok-growth-operator.skill\scripts\start_goal_workflow.py" ".\tiktok-growth-operator.skill\scripts\start_project_workflow.py" ".\tiktok-growth-operator.skill\scripts\run_scene_workflow.py" ".\tiktok-growth-operator.skill\scripts\run_operator_workflow.py" ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py" ".\tiktok-growth-operator.skill\scripts\validate_export_outputs.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\start_scene_run.py" --scene 01 --name encoding-entrypoint-smoke --project "Encoding Entrypoint Smoke" --formats md --output-root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260507_start_scene_encoding_smoke"`
- Result: passed and confirmed the scene entrypoint writes through the unified encoding layer
- Ran: `python ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py" --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp" --formats md --dry-run`
- Result: passed and discovered 648 historical `scene-*.json` candidates
- Ran: `python ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py" --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp" --formats md`
- Result: passed and re-rendered 649 scene Markdown outputs from canonical JSON reports

## 2026-05-07 Encoding Sweep Closure

- Decision: finish the remaining durable script sweep instead of leaving lower-priority template, quick-reference, and validation scripts on mixed local text I/O.
- Why: the main runtime paths were already normalized, but inconsistent helper/template scripts could still reintroduce Windows-facing encoding drift and make later validation noisy.
- Decision: fix the lingering validator false-negative and the account-ops bridge runtime import while closing the sweep.
- Why: the user asked for continuous completion, and leaving one false-red validator plus one missing import would make the package look unfinished even though the core scene runtime was already stable.

### Updated

- `tiktok-growth-operator.skill/scripts/generate_batch_preset.py`
- `tiktok-growth-operator.skill/scripts/recommend_entry_board.py`
- `tiktok-growth-operator.skill/scripts/generate_scene_quick_reference.py`
- `tiktok-growth-operator.skill/scripts/generate_creative_brief_quick_reference.py`
- `tiktok-growth-operator.skill/scripts/load_route_eval_fixtures.py`
- `tiktok-growth-operator.skill/scripts/validate_all_workflows.py`
- `tiktok-growth-operator.skill/scripts/validate_capture_pack_workflows.py`
- `tiktok-growth-operator.skill/scripts/run_tikmatrix_account_ops_bridge.py`

### Added / Confirmed Behavior

- shared `text_normalization.py` helpers now cover the remaining preset/template and quick-reference writers
- bundle-index and route-fixture JSON reads now go through the same normalized read path as the main runtime
- regenerated `scene-quick-reference.md` and `creative-brief-quick-reference.md` no longer show the prior mojibake fragments
- the account-ops TikMatrix bridge now completes end to end again after restoring the missing `json` import
- the dedup check in `validate_capture_pack_workflows.py` now validates the intended project root directly instead of producing a limit-window false failure

### Validation

- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\generate_batch_preset.py" ".\tiktok-growth-operator.skill\scripts\recommend_entry_board.py" ".\tiktok-growth-operator.skill\scripts\generate_scene_quick_reference.py" ".\tiktok-growth-operator.skill\scripts\generate_creative_brief_quick_reference.py" ".\tiktok-growth-operator.skill\scripts\load_route_eval_fixtures.py" ".\tiktok-growth-operator.skill\scripts\validate_all_workflows.py" ".\tiktok-growth-operator.skill\scripts\validate_capture_pack_workflows.py" ".\tiktok-growth-operator.skill\scripts\run_tikmatrix_account_ops_bridge.py" ".\tiktok-growth-operator.skill\scripts\validate_tikmatrix_account_ops_bridge.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\generate_batch_preset.py" --template-bundle-root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260507_batch_preset_encoding_smoke"`
- Result: passed and generated a 34-template bundle plus UTF-8 normalized `README.md` and `template-index.json`
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_skill_docs.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_tikmatrix_account_ops_bridge.py"`
- Result: passed and emitted the account-ops bridge pack under `D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260507_validate_tikmatrix_account_ops_bridge`
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_capture_pack_workflows.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Result: passed

## 2026-05-07 DOCX/XLSX Export Hardening

- Decision: close the parity gap where `execution_template` existed in the report contract and Markdown renderer but did not survive into DOCX/XLSX exports.
- Why: the skill is meant to be directly runnable in Codex, so reusable request scaffolds, runner args, variable inputs, and workflow checklists must remain visible in rich exports instead of disappearing outside Markdown.
- Decision: improve workbook and DOCX readability with content-aware sizing instead of relying only on fixed widths.
- Why: the structure was already green, but long TikTok captions, evidence notes, and section tables were still harder to read than necessary in exported files.

### Updated

- `tiktok-growth-operator.skill/scripts/render_scene_report.py`
- `tiktok-growth-operator.skill/scripts/validate_export_outputs.py`

### Added / Confirmed Behavior

- `execution_template` is now normalized inside the export renderer and can render into:
  - DOCX `Direct-Use Template` section
  - XLSX `Execution Template` sheet
- Summary now links to the `Execution Template` sheet when the payload includes direct-use workflow content.
- DOCX now renders:
  - recommended request
  - Chinese recommended request
  - runner args
  - variable input table
  - Codex prompt scaffold
  - Chinese prompt scaffold
  - workflow steps
  - output checklist
- XLSX now renders the same execution-template surface in a dedicated worksheet with back-link navigation.
- DOCX scene tables now use content-aware width inference instead of only static fallback widths.
- XLSX section and list sheets now use content-aware column widths plus row-height expansion for longer text blocks.
- export validation now checks execution-template parity explicitly instead of only validating navigation and sheet/table presence.
- a new synthetic execution-template fixture now guards against future regressions where rich exports would silently omit direct-use instructions.

### Validation

- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\render_scene_report.py" ".\tiktok-growth-operator.skill\scripts\validate_export_outputs.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_export_outputs.py" --output-root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260507_export_validation_hardening_v2"`
- Result: passed for:
  - `scene15`
  - `scene17`
  - `synthetic_duplicate_heading`
  - `synthetic_sparse_section`
  - `synthetic_execution_template`
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Result: passed and confirmed the broader workflow set still stays green after the export hardening

### Follow-on Tightening

- Added one more guard so Markdown validation now also enforces execution-template section presence whenever the payload actually contains direct-use template content.
- Why: after rich export parity was fixed, the remaining gap was that Markdown validation still only checked the base report skeleton and could miss a future regression inside `Direct-Use Template`.
- Rebuilt `generate_scene_report.py` to remove the lingering historical mojibake labels inside the execution-template Markdown renderer.
- Why: even though the synthetic validation path was already green, those two label strings were still a latent source of future dirty Markdown re-renders if older payloads were regenerated directly from the scaffold path.
- Tightened section-sheet XLSX rendering so only real tabular regions become Excel tables.
- Why: the prior implementation could wrap narrative/merged-cell section sheets into `openpyxl` tables and emit `column headings must be strings` warnings during rich export re-render runs.

### Additional Validation

- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\validate_export_outputs.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_export_outputs.py" --output-root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260507_export_validation_hardening_v3"`
- Result: passed and confirmed Markdown, DOCX, and XLSX all preserve the synthetic execution-template fixture
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Result: passed again after the Markdown execution-template guard was added
- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\generate_scene_report.py" ".\tiktok-growth-operator.skill\scripts\render_scene_report.py" ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py" --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp" --formats md,docx,xlsx --dry-run --summary-path "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\rerender-dryrun-summary-v2.json"`
- Result: passed and discovered `775` historical `scene-*.json` candidates for rich export re-rendering
- Ran: `python ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py" --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_capture_runner_scene15" --formats md,docx,xlsx --summary-path "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260504_capture_runner_scene15\rerender-summary-v3.json"`
- Result: passed and rewrote `md`, `docx`, and `xlsx` for one real historical run with `format_counts` recorded in the summary
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_export_outputs.py" --output-root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260507_export_validation_hardening_v5"`
- Result: passed after the Markdown label cleanup and section-sheet XLSX table fix

## 2026-05-07 Historical Rich Export Batch Controls And Spot Check

- Decision: keep historical rich-export rerendering incremental instead of sweeping all `775` scene JSON files in one pass.
- Why: the user explicitly asked for staged rerenders, and bounded batches make it easier to validate visual quality and catch export regressions without churning the entire history tree.
- Decision: tighten XLSX width heuristics per sheet type instead of leaving one global wide-column rule.
- Why: spot-checking five real scene exports showed the same recurring readability issue: `Summary.B` was effectively fixed at `109`, and `Evidence` / `Assets` detail columns were repeatedly landing at `55`, which made exports feel bloated rather than readable.

### Updated

- `tiktok-growth-operator.skill/scripts/render_scene_report.py`
- `tiktok-growth-operator.skill/scripts/rerender_scene_outputs.py`

### Added / Confirmed Behavior

- `rerender_scene_outputs.py` now supports:
  - `--limit`
  - `--match`
  - `--since`
- rerender summaries now record:
  - `filters`
  - `discovered_count`
  - `batch_counts`
  - `format_counts`
- `Summary` sheet value-column width was reduced from the prior over-wide behavior to a bounded readable width.
- `Evidence` and `Assets` sheets now use sheet-specific width presets and column caps instead of the older generic width inference.
- list-sheet row heights still expand for long text, but now work inside tighter width bounds so the visual tradeoff is cleaner.
- DOCX evidence/assets tables now use slightly rebalanced column ratios so detail/path content gets more room without oversizing the label/note columns.

### Spot Check

- Re-rendered five real scene outputs for manual-rule spot check:
  - `20260504_capture_runner_scene15`
  - `20260504_capture_runner_scene17`
  - `20260507_010741-tikmatrix-bridge-mustsharenews-scene01-real-rerun`
  - `20260507_010740-tikmatrix-bridge-mustsharenews-scene03-real-rerun`
  - `20260504_validation_capture_scene13`
- Before tuning, the sampled XLSX files consistently showed:
  - `Summary.B ~= 109.22`
  - `Evidence.B/C ~= 55.22`
  - `Assets.B/C ~= 55.22`
- After tuning, the same sampled files consistently showed:
  - `Summary.B ~= 77.22`
  - `Evidence.A/B/C ~= 29.22 / 51.22 / 39.22`
  - `Assets.A/B/C ~= 27.22 or 21.22 / 51.22 / 37.22`
- DOCX zip-level structure checks remained intact across the same sample set:
  - `Section Overview` present
  - `Evidence` present
  - `Assets` present
  - execution-template labels present when the source payload actually contained them

### Validation

- Ran: `python ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py" --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp" --formats docx,xlsx --match "*20260504_capture_runner_scene15*" --limit 1 --summary-path "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\rerender-spotcheck-scene15-v1.json"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py" --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp" --formats docx,xlsx --match "*20260504_capture_runner_scene17*" --limit 1 --summary-path "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\rerender-spotcheck-scene17-v1.json"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py" --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp" --formats docx,xlsx --match "*20260507_010741-tikmatrix-bridge-mustsharenews-scene01-real-rerun*" --limit 1 --summary-path "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\rerender-spotcheck-scene01-v1.json"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py" --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp" --formats docx,xlsx --match "*20260507_010740-tikmatrix-bridge-mustsharenews-scene03-real-rerun*" --limit 1 --summary-path "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\rerender-spotcheck-scene03-v1.json"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py" --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp" --formats docx,xlsx --match "*20260504_validation_capture_scene13*" --limit 1 --summary-path "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\rerender-spotcheck-scene13-v1.json"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_export_outputs.py" --output-root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260507_export_validation_hardening_v6"`
- Result: passed and emitted `validation_summary.json`
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py" --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp" --formats md,docx,xlsx --since 20260507 --limit 12 --summary-path "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\rerender-batch-20260507-v2.json"`
- Result: passed and re-rendered `12` bounded historical batches with all three formats written

### Residual Follow-up

- continue staged rerendering of the remaining historical `scene-*.json` population using `--since`, `--match`, and `--limit`
- if later spot checks still show over-tall first rows in `Evidence` or `Assets`, tighten `chars_per_line` or row-height caps one step further instead of widening columns again

## 2026-05-07 Additional Staged Rerender Coverage

- Decision: finish the full `20260504_capture_runner_*` and `20260504_validation_capture_*` families before pushing deeper into the broader `20260507_*` population.
- Why: those two dated families are compact, historically important validation/capture groups, and closing them first gives a clean bounded baseline under the new rich-export sizing rules.
- Decision: keep the broader `20260507_*` rerender bounded to `24` items for this pass.
- Why: the `20260507_*` tree contains many real-runtime and workflow variants, so a bounded pass keeps runtime manageable while still extending real historical coverage.

### Validation

- Ran: `python ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py" --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp" --formats md,docx,xlsx --match "*20260504_capture_runner_*" --limit 20 --summary-path "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\rerender-batch-capture-runner-v2.json"`
- Result: passed and re-rendered the full currently discovered `20260504_capture_runner_*` family with `8` scene JSON files:
  - `scene08`
  - `scene11`
  - `scene12`
  - `scene13`
  - `scene14`
  - `scene15`
  - `scene16`
  - `scene17`
- Ran: `python ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py" --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp" --formats md,docx,xlsx --match "*20260504_validation_capture_*" --limit 20 --summary-path "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\rerender-batch-validation-capture-v2.json"`
- Result: passed and re-rendered the full currently discovered `20260504_validation_capture_*` family with `7` scene JSON files:
  - `scene11`
  - `scene12`
  - `scene13`
  - `scene14`
  - `scene15`
  - `scene16`
  - `scene_auto`
- Ran: `python ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py" --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp" --formats md,docx,xlsx --match "*20260507_*" --limit 24 --summary-path "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\rerender-batch-20260507-v3.json"`
- Result: passed and re-rendered `24` bounded `20260507_*` historical items covering:
  - `mrorangecat` scene `01`, `03`, `11`, `12`, `13`, `14`, `15`, `16`, `18`, `19`
  - `mustsharenews` scene `01`, `03` real-rerun and venv-restored variants
  - `sherrinandyixi` scene `01`, `03` real-rerun variants
  - one direct scene-run workspace
  - one goal-workflow workspace with scene `01` and scene `07`

### Coverage Note

- the rerender dry-run candidate count has now risen from the earlier `775` snapshot to `793`, reflecting additional generated scene JSON history created during ongoing validation/runtime work
- the new rich-export width rules are now confirmed across:
  - all discovered `20260504_capture_runner_*` history
  - all discovered `20260504_validation_capture_*` history
  - three staged `20260507_*` rerender passes

## 2026-05-07 20260505 And 20260506 Historical Coverage Expansion

- Decision: expand staged rerendering into `20260505` and `20260506` by workflow pattern instead of by one mixed date-wide sweep.
- Why: `20260505` contains several repeated families such as `goal-workflow` and repeated `scene-03` direct-run workspaces, while `20260506` contains a small TikMatrix-bridge pair. Grouped rerenders make the resulting summaries auditable instead of noisy.
- Decision: treat `publish-prep` as a non-scene family unless matching `scene-*.json` evidence appears.
- Why: the rerender tool intentionally only consumes canonical `scene-*.json` reports, and the `publish-prep` operator-pack outputs are not represented as scene report JSONs.

### Validation

- Ran: `python ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py" --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp" --formats md,docx,xlsx --match "*20260506_*" --limit 12 --summary-path "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\rerender-batch-20260506-v1.json"`
- Result: passed and re-rendered the full discovered `20260506_*` scene-report family with `2` items:
  - `20260506_232633-tikmatrix-bridge-mrorangecat-account-distill`
  - `20260506_232633-tikmatrix-bridge-mrorangecat-comment-signal`
- Ran: `python ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py" --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp" --formats md,docx,xlsx --match "*20260505_*goal-workflow*" --limit 40 --summary-path "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\rerender-batch-20260505-goal-workflow-v1.json"`
- Result: passed and re-rendered `40` goal-workflow scene reports across these batches:
  - `20260505_020339-goal-workflow` (`9`)
  - `20260505_020552-goal-workflow` (`9`)
  - `20260505_021600-goal-workflow` (`9`)
  - `20260505_021726-goal-workflow` (`9`)
  - `20260505_021915-goal-workflow` (`4` within the current limit window)
- Ran: `python ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py" --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp" --formats md,docx,xlsx --match "*20260505_*run-scene-03*" --limit 20 --summary-path "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\rerender-batch-20260505-scene03-v1.json"`
- Result: passed and re-rendered all currently discovered `20260505` direct `scene-03` run-report batches with `13` items
- Ran: `python ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py" --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp" --formats md,docx,xlsx --match "*20260505_*publish-prep*" --limit 20 --summary-path "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\rerender-batch-20260505-publish-prep-v1.json"`
- Result: passed with `0` matches, confirming there are no canonical `scene-*.json` payloads in that family for the rerender tool to consume

### Coverage Note

- historical rich-export rerender coverage now also includes:
  - the full currently discovered `20260506_*` scene-report family
  - a large first slice of the `20260505_*goal-workflow*` family
  - the full currently discovered `20260505_*run-scene-03*` family
- the `publish-prep` branch remains intentionally outside rerender scope unless it later produces canonical scene-report JSONs

## 2026-05-07 Historical Workflow-Family Rerender Sweep Closure

- Decision: close the remaining `20260505_*` and `20260507_*` workflow-family gaps by rerendering the residual workspace blocks individually instead of widening one more date-level sweep.
- Why: by this point the remaining population was concentrated in a few known workspace slugs, so direct block completion was cleaner than another noisy mixed rerender pass.
- Decision: treat `20260505_014318-goal-build-a-full-douyin-workflow-from-topic-selection-to-publish-handoff` as an expected non-scene special case.
- Why: the workspace exists, but it does not contain canonical `scene-*.json` payloads, so there is nothing for `rerender_scene_outputs.py` to consume.

### Validation

- Ran: `python ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py" --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp" --formats md,docx,xlsx --match "*20260505_043*goal-workflow*" --limit 24 --summary-path "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\rerender-batch-20260505-goal-workflow-043-v1.json"`
- Result: passed and completed:
  - `20260505_043011-goal-workflow`
  - `20260505_043122-goal-workflow`
- Ran: `python ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py" --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp" --formats md,docx,xlsx --match "*20260505_044*goal-workflow*" --limit 24 --summary-path "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\rerender-batch-20260505-goal-workflow-044-v1.json"`
- Result: passed and completed:
  - `20260505_044010-goal-workflow`
  - `20260505_044803-goal-workflow`
- Ran: `python ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py" --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp" --formats md,docx,xlsx --match "*20260505_045*goal-workflow*" --limit 24 --summary-path "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\rerender-batch-20260505-goal-workflow-045-v1.json"`
- Result: passed and completed `20260505_045914-goal-workflow`
- Ran: `python ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py" --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp" --formats md,docx,xlsx --match "*20260505_043*build-a-full-douyin-workflow-from-topic-selectio*" --limit 24 --summary-path "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\rerender-batch-20260505-build-douyin-043-v1.json"`
- Result: passed and completed:
  - `20260505_043015-goal-build-a-full-douyin-workflow-from-topic-selectio`
  - `20260505_043126-goal-build-a-full-douyin-workflow-from-topic-selectio`
- Ran: `python ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py" --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp" --formats md,docx,xlsx --match "*20260505_044*build-a-full-douyin-workflow-from-topic-selectio*" --limit 24 --summary-path "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\rerender-batch-20260505-build-douyin-044-v1.json"`
- Result: passed and completed:
  - `20260505_044014-goal-build-a-full-douyin-workflow-from-topic-selectio`
  - `20260505_044806-goal-build-a-full-douyin-workflow-from-topic-selectio`
- Ran: `python ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py" --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp" --formats md,docx,xlsx --match "*20260505_045*build-a-full-douyin-workflow-from-topic-selectio*" --limit 24 --summary-path "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\rerender-batch-20260505-build-douyin-045-v1.json"`
- Result: passed and completed `20260505_045920-goal-build-a-full-douyin-workflow-from-topic-selectio`
- Ran: `python ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py" --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp" --formats md,docx,xlsx --match "*20260507_*goal-workflow*" --limit 96 --summary-path "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\rerender-batch-20260507-goal-workflow-full-v1.json"`
- Result: passed and completed all discovered `20260507_*goal-workflow` scene-report workspaces with `72` rerendered scene reports across:
  - `20260507_023321-goal-workflow`
  - `20260507_023548-goal-workflow`
  - `20260507_023643-goal-workflow`
  - `20260507_023830-goal-workflow`
  - `20260507_030149-goal-workflow`
  - `20260507_030604-goal-workflow`
  - `20260507_031238-goal-workflow`
  - `20260507_033131-goal-workflow`
- Ran: `python ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py" --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp" --formats md,docx,xlsx --match "*20260507_*build-a-full-douyin-workflow-from-topic-selectio*" --limit 96 --summary-path "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\rerender-batch-20260507-build-douyin-full-v1.json"`
- Result: passed and completed all discovered `20260507_*build-a-full-douyin-workflow-from-topic-selectio` scene-report workspaces with `64` rerendered scene reports across:
  - `20260507_023322-goal-build-a-full-douyin-workflow-from-topic-selectio`
  - `20260507_023549-goal-build-a-full-douyin-workflow-from-topic-selectio`
  - `20260507_023644-goal-build-a-full-douyin-workflow-from-topic-selectio`
  - `20260507_023831-goal-build-a-full-douyin-workflow-from-topic-selectio`
  - `20260507_030151-goal-build-a-full-douyin-workflow-from-topic-selectio`
  - `20260507_030606-goal-build-a-full-douyin-workflow-from-topic-selectio`
  - `20260507_031239-goal-build-a-full-douyin-workflow-from-topic-selectio`
  - `20260507_033133-goal-build-a-full-douyin-workflow-from-topic-selectio`
- Ran additional completion batches:
  - `rerender-batch-20260505-build-douyin-024-v1.json`
  - `rerender-batch-20260505-goal-goal-workflow-033-v1.json`
  - `rerender-batch-20260505-build-douyin-033-v2.json`
  - `rerender-batch-20260505-build-douyin-0339-v1.json`
  - `rerender-batch-20260505-goal-workflow-034-v1.json`
  - `rerender-batch-20260505-build-douyin-034-v1.json`
  - `rerender-batch-20260505-goal-workflow-035-v1.json`
  - `rerender-batch-20260505-build-douyin-035-v1.json`
  - `rerender-batch-20260505-build-douyin-033604-v1.json`
  - `rerender-batch-20260505-goal-goal-workflow-03392-v1.json`
  - `rerender-batch-20260507-04140-v1.json`
- Result: passed and closed the remaining real scene-report gaps across:
  - `20260505_024356-goal-build-a-full-douyin-workflow-from-topic-selectio`
  - `20260505_024605-goal-build-a-full-douyin-workflow-from-topic-selectio`
  - `20260505_033311-goal-goal-workflow`
  - `20260505_033315-goal-goal-workflow`
  - `20260505_033345-goal-goal-workflow`
  - `20260505_033351-goal-goal-workflow`
  - `20260505_033547-goal-goal-workflow`
  - `20260505_033552-goal-goal-workflow`
  - `20260505_033557-goal-goal-workflow`
  - `20260505_033602-goal-goal-workflow`
  - `20260505_033604-goal-build-a-full-douyin-workflow-from-topic-selectio`
  - `20260505_033921-goal-goal-workflow`
  - `20260505_033927-goal-goal-workflow`
  - `20260505_033932-goal-build-a-full-douyin-workflow-from-topic-selectio`
  - `20260505_034925-goal-workflow`
  - `20260505_034928-goal-build-a-full-douyin-workflow-from-topic-selectio`
  - `20260505_035018-goal-workflow`
  - `20260505_035028-goal-build-a-full-douyin-workflow-from-topic-selectio`
  - `20260505_035342-goal-workflow`
  - `20260505_035347-goal-build-a-full-douyin-workflow-from-topic-selectio`
  - `20260505_035811-goal-workflow`
  - `20260505_035812-goal-build-a-full-douyin-workflow-from-topic-selectio`
  - `20260507_041401-goal-workflow`
  - `20260507_041403-goal-build-a-full-douyin-workflow-from-topic-selectio`
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Result: passed after the rerender sweep closure

### Coverage Note

- the rerender dry-run candidate count has now risen again to `811`, reflecting additional generated history produced while validating and rerendering the broader workflow families
- all discovered `20260505_*goal-workflow`, `20260505_*goal-goal-workflow`, `20260505_*build-a-full-douyin-workflow-from-topic-selectio`, `20260506_*`, and `20260507_*` workflow-family scene-report workspaces are now rerender-covered
- the only remaining uncovered workflow-family directory in the reconciliation pass is:
  - `20260505_014318-goal-build-a-full-douyin-workflow-from-topic-selection-to-publish-handoff`
- that remaining directory is not an export gap because it contains `0` canonical `scene-*.json` files

### Residual Follow-up

- historical rerender coverage for the workflow-family backlog is effectively closed unless new historical scene-report workspaces are generated later
- if future spot checks still show overly tall first rows in `Evidence` or `Assets`, tighten row-height caps or `chars_per_line` one step further rather than widening columns
- if needed later, rerender non-workflow historical branches incrementally with the same `--match` / `--since` / `--limit` controls rather than reintroducing whole-tree sweeps

## 2026-05-07 P1-P3 Closure Pass

- Decision: extend the real capture-pack importer from the earlier ranked/comment scenes into scenes `04`, `05`, and `10`.
- Why: these scenes were still below the same real-runtime confidence level as the rest of the operator surface, even though the package already had strong template parity.
- Decision: revalidate scenes `07` and `09` in the same pass instead of leaving them as “runtime supported”.
- Why: once the capture-pack validation surface was open, it was cheaper and cleaner to raise them to the same confirmation grade immediately.
- Decision: close the reference-index debt by promoting `command-map.md` into the operator-facing document flow.
- Why: the package already had the compact command index, but it was not consistently referenced as the first lightweight entry surface.
- Decision: document incremental rerender SOP directly inside the automation reference.
- Why: `rerender_scene_outputs.py` already had the right controls, but the operator-facing repair procedure was still implicit.

### Updated

- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`
- `tiktok-growth-operator.skill/scripts/start_capture_pack_run.py`
- `tiktok-growth-operator.skill/scripts/validate_capture_pack_workflows.py`
- `tiktok-growth-operator.skill/references/automation-workflows.md`
- `tiktok-growth-operator.skill/references/direct-use.md`
- `tiktok-growth-operator.skill/references/final-handoff.md`
- `tiktok-growth-operator.skill/references/route-eval-fixtures.json`
- `tiktok-growth-operator.skill/references/clipcat-openclaw-parity-audit.md`
- `docs/quality/debt-log.md`

### Added Behavior

- real capture-pack runtime now supports scene `04` single-video breakdown
- real capture-pack runtime now supports scene `05` reverse-engineered brief reconstruction
- real capture-pack runtime now supports scene `10` product-image-to-video brief generation at the brief layer
- scenes `07` and `09` are now explicitly revalidated in the capture-pack workflow suite
- scene `10` now auto-generates the same downstream operator packs as the other brief-heavy creative scenes
- `automation-workflows.md` now contains a bounded incremental rerender SOP using `--match`, `--since`, `--limit`, and `--summary-path`
- `direct-use.md` now points operators to `command-map.md` as the shortest command index
- parity documentation now distinguishes real-runtime confirmation from external-platform boundaries more explicitly

### Validation

- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_capture_pack_workflows.py"`
- Result: passed, including real capture-pack runtime validation for scenes `04`, `05`, `07`, `09`, and `10`

### Outcome

- the safe operator surface is now real-runtime confirmed across scenes `01`, `03`, `04`, `05`, `07`, `08`, `09`, `10`, `11`, `12`, `13`, `14`, `15`, `16`, `17`, `18`, and `19`
- remaining gaps are now cleaner boundary items rather than package ambiguity:
  - scene `02` still depends on a patrol scheduler or equivalent live feed
  - scene `06` still depends on TikTok Shop product/detail/comment data sources
  - final media rendering, delivery pushes, and privileged account mutation remain external

## 2026-05-07 Scene 01 02 03 Encoding And Export Spot Check

- Decision: replace the earlier ad hoc mojibake replacement table with a conservative shared normalization layer that only removes invisible control characters and a few deterministic Latin-encoding artifacts.
- Why: the previous replacement map itself contained dirty source strings and risked reintroducing corruption during future re-renders.
- Decision: treat current 01/02/03 quality review as a representative no-乱码 smoke pass across Markdown, DOCX, and XLSX instead of broad whole-history manual checking.
- Why: the user asked specifically whether the generated documents are currently satisfactory and whether they still contain garbling, so the highest-signal proof is a direct spot check on the latest real-runtime fixtures.

### Updated

- `tiktok-growth-operator.skill/scripts/text_normalization.py`
- `tiktok-growth-operator.skill/references/clipcat-openclaw-parity-audit.md`

### Validation

- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\text_normalization.py" ".\tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py" ".\tiktok-growth-operator.skill\scripts\render_scene_report.py" ".\tiktok-growth-operator.skill\scripts\generate_scene_report.py" ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py" --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp" --formats md,docx,xlsx --match "*20260507_020341-tikmatrix-bridge-mustsharenews-scene01-venv-restored-encoding-fix*" --limit 4 --summary-path "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\rerender-scene01-cleanpass.json"`
- Result: passed and re-rendered the representative real Scene `01` Markdown, DOCX, and XLSX outputs
- Ran: `python ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py" --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp" --formats md,docx,xlsx --match "*20260507_validation_capture_scene02*" --limit 4 --summary-path "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\rerender-scene02-cleanpass.json"`
- Result: passed and re-rendered both representative Scene `02` capture/patrol outputs across Markdown, DOCX, and XLSX
- Ran: `python ".\tiktok-growth-operator.skill\scripts\rerender_scene_outputs.py" --root "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp" --formats md,docx,xlsx --match "*20260507_020341-tikmatrix-bridge-mustsharenews-scene03-venv-restored-encoding-fix*" --limit 4 --summary-path "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\rerender-scene03-cleanpass.json"`
- Result: passed and re-rendered the representative real Scene `03` Markdown, DOCX, and XLSX outputs
- Ran: Python spot checks against the re-rendered 01/02/03 Markdown outputs for `\u200e`, `\u200f`, bidi isolate characters, and raw table-breaking pipe cases
- Result: passed; no invisible direction-control artifacts remain, and the earlier Scene `03` table pipe-break issue stays fixed
- Ran: Python `python-docx` and `openpyxl` spot checks against the re-rendered Scene `02` and Scene `03` rich exports
- Result: passed; DOCX text loads cleanly with expected workspace paths and XLSX still includes the `Execution Template` sheet plus readable `Summary` metadata

### Outcome

- current representative Scene `01`, `02`, and `03` outputs are no longer showing actual encoding corruption in the generated files
- the earlier visible terminal mojibake was confirmed again as console-display noise rather than file corruption
- the remaining output quality issues are now source-text quality issues, not encoding-layer issues:
  - some upstream TikTok caption/prose fragments are naturally terse or inconsistent
  - some English authority-signal strings still contain literal separators such as `|`, but they no longer break Markdown tables

## 2026-05-07 Scene 01 02 03 Source-Text Polish Pass

- Decision: keep the current scene structure and exporter contract stable, and improve only the importer-side text shaping for ranked caption, topic, authority, and patrol-sample fields.
- Why: by this point the remaining defects were not structural or encoding failures; they were presentation-quality issues caused by raw TikTok source text flowing too directly into final report cells.

### Updated

- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`

### Added / Changed Behavior

- ranked caption/topic extraction now runs through a shared caption normalizer before clipping
- concatenated hashtag walls are split into readable tokens instead of being preserved as one raw block
- authority signals now render as readable account summaries such as `mustsharenews (verified) - ...` instead of pipe-heavy fragments
- Scene `01` `Why They Matter` now uses a semantic proof-style label (`Verified account authority`, etc.) instead of dropping raw author signature text into the wrong column
- Scene `02` patrol sample rows now render cleaner hook/topic cues when the source row is hashtag-heavy

### Validation

- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py"`
- Result: passed
- Ran: importer regeneration plus rich-export rerender for the representative real-runtime:
  - `Scene 01` `mustsharenews` restored-runtime fixture
  - `Scene 03` `mustsharenews` restored-runtime fixture
  - `Scene 02` patrol fixture
- Result: passed; regenerated JSON plus Markdown, DOCX, and XLSX outputs all landed successfully

### Outcome

- `Scene 01` and `Scene 03` now present cleaner authority lines and more natural proof-style labeling
- `Scene 02` now shows less raw hashtag concatenation in patrol sample rows, even when the source post is tag-heavy
- the main remaining quality ceiling is now upstream source quality itself, not the package formatting logic

## 2026-05-07 Shared Caption Cleanup Follow-Through

- Decision: finish the remaining importer-side text cleanup in the shared capture-pack cue normalizer instead of patching individual scene outputs.
- Why: the unresolved defects were shared source-text residues showing up across multiple scenes `04`, `05`, `07`, `09`, and `10`, so per-scene fixes would only hide the real ownership point.

### Updated

- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`

### Added / Changed Behavior

- shared caption normalization now repairs the remaining broken phrase residue `sing your out` into `sing your heart out`
- trailing emoji-noise substitutions that previously left naked tail text such as `moments heart` are now collapsed into readable final phrases
- final caption cleanup is applied once at the shared normalizer exit, so all downstream display fields inherit the same repaired text

### Validation

- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_capture_pack_workflows.py"`
- Result: passed, including regenerated real capture-pack outputs for scenes `04`, `05`, `07`, `09`, and `10`
- Ran: Python JSON spot checks against regenerated scene reports for `04`, `05`, `07`, `09`, and `10`
- Result: passed; no residual `sing your out`, no residual `moments heart`, and no file-level Chinese mojibake strings in the regenerated JSON payloads

### Outcome

- the remaining shared capture-pack text residue for scenes `04`, `05`, `07`, `09`, and `10` is now cleaned at source
- current real-runtime validation fixtures for those scenes now read cleanly enough to treat the issue as closed at the importer layer
- remaining polish opportunities are now editorial quality improvements, not broken-text repair

## 2026-05-07 Report-Cue Compression Pass

- Decision: split evidence-grade raw captions from report-grade hook/topic cues inside the shared importer instead of letting the same long source sentence flow into every visible table cell.
- Why: the remaining friction was no longer corruption or parsing; it was that some real TikTok captions still carried long continuation CTAs such as `tune into the full episode...`, which made scene reports read like raw exports instead of operator summaries.

### Updated

- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`

### Added / Changed Behavior

- added a shared tail-marker trim pass for report-facing cue extraction
- report-facing cue text now strips common long-tail CTA fragments such as full-episode or on-page continuation language before clipping
- scenes `04`, `05`, `07`, `09`, and `10` now inherit shorter hook/topic cues while keeping the original evidence rows intact

### Validation

- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_capture_pack_workflows.py"`
- Result: passed, including regenerated real capture-pack outputs for scenes `04`, `05`, `07`, `09`, and `10`
- Ran: Python spot checks against regenerated scene reports for the updated visible cue fields
- Result: passed; representative hook/topic cells now stop at the reusable cue instead of carrying the longer `tune into the full episode...` tail

### Outcome

- the current real-runtime fixtures read more like operator reports and less like raw caption dumps
- source evidence is still preserved, but visible hook/topic cells are now materially tighter for teardown, replication, and briefing workflows

## 2026-05-07 Scene 09 10 Handoff Completion Pass

- Decision: align importer-side Scene `09` output to the current section-table schema instead of relying on older numbered or paragraph fields.
- Why: the real runtime was already producing the right intent, but Scene `09` still rendered blank-looking `Structure`, `Creative Constraints`, and `Production Handoff` tables because the importer was populating obsolete shapes.
- Decision: make Scene `10` production handoff rows more concrete while the same validation surface was open.
- Why: Scene `10` was functional, but its handoff lines still read more like placeholders than a real operator-to-production transfer.

### Updated

- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`

### Added / Changed Behavior

- Scene `09` now fills the current `Message`, `Structure`, `Creative Constraints`, and `Production Handoff` tables with concrete replication-brief content
- Scene `09` now outputs a filmable beat map with owned-asset needs, overlay direction, and blocking risks instead of leaving visible rows empty
- Scene `10` handoff rows now include more explicit proof-asset, overlay, and CTA destination guidance

### Validation

- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_capture_pack_workflows.py"`
- Result: passed, including regenerated real capture-pack outputs for scenes `09` and `10`
- Ran: Python spot checks against regenerated Scene `09` and `10` JSON reports
- Result: passed; Scene `09` no longer leaves the visible handoff/structure tables blank, and Scene `10` handoff rows now carry concrete operator-to-production guidance

### Outcome

- Scene `09` now reads like a usable replication brief instead of a partially wired scaffold
- Scene `10` now gives a stronger production-safe handoff from reference logic into image-only execution planning

## 2026-05-07 Scene 01 03 Operator-Handoff Pass

- Decision: turn Scene `01` and `03` shortlist outputs into explicit study-lane and teardown-handoff boards instead of leaving them as research-style summaries only.
- Why: by this point the main remaining weakness in those scenes was not missing evidence; it was that the outputs still told the operator what was interesting without clearly assigning what should be torn down first and how each candidate should be used.

### Updated

- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`

### Added / Changed Behavior

- Scene `01` shortlist rows now assign each winner to a concrete study lane such as proof/authority, hook/emotional framing, or topic/angle teardown
- Scene `01` `Why They Matter` rows now read as routing guidance rather than passive description
- Scene `03` shortlist and per-video teardown rows now carry explicit handoff actions for the next operator step
- Scene `03` next-action output now distinguishes main control, backup lane, and contrast reference instead of offering only generic follow-up advice

### Validation

- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\start_capture_pack_run.py" --scene 01 ...`
- Result: passed for inspection workspace `20260507_inspect_scene01`
- Ran: `python ".\tiktok-growth-operator.skill\scripts\start_capture_pack_run.py" --scene 03 ...`
- Result: passed for inspection workspace `20260507_inspect_scene03`
- Ran: Python spot checks against regenerated Scene `01` and `03` JSON reports
- Result: passed; both scenes now expose concrete teardown lanes and operator-next-step language in the visible output

### Outcome

- Scene `01` now behaves more like a shortlist dispatch board than a static collection table
- Scene `03` now behaves more like a teardown assignment pack than a generic pattern summary

## 2026-05-07 Scene 11 12 Schema Closure And Dispatch Polish

- Decision: close the remaining Scene `11` and `12` blank-table gaps inside the importer instead of accepting half-upgraded schemas.
- Why: the recent schema expansion had already improved the richer matrices, but `Execution Handoff`, `Expected Effect`, `Next Action`, and part of `Core Invariant` were still rendering as empty shells in real inspection outputs.
- Decision: push scenes `07`, `17`, `18`, and `19` one step further toward operator dispatch boards while the same validation surface was open.
- Why: those scenes were structurally valid, but they still benefited from more explicit watch/test/suppress and follow-up-gap framing to better match the platform-style operating feel.

### Updated

- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`

### Added / Changed Behavior

- Scene `11` now fills the `Core Invariant` rule table with concrete entry-threshold, teardown-lens, and queue-standard rules
- Scene `11` now fills `Execution Handoff` with artifact owner, ready-state, and blocking-risk rows instead of leaving the queue artifacts blank
- Scene `12` now fills `Expected Effect`, `Execution Handoff`, and table-form `Next Action` with variant-specific attention/conversion expectations, asset owners, and launch priority logic
- Scene `07` now labels its recommendation grid more explicitly as a category dispatch board
- Scene `17` now includes a visible operator dispatch table for watch/test/suppress handling
- Scene `18` now includes a concrete next-capture upgrade table instead of leaving the follow-up fields only in bullets
- Scene `19` now includes a visible follow-up data-gap table so the retro reads more like an operating brief than a loose summary

### Validation

- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\start_capture_pack_run.py" --scene 11 ...`
- Result: passed for inspection workspace `20260507_inspect_scene11_v2`
- Ran: `python ".\tiktok-growth-operator.skill\scripts\start_capture_pack_run.py" --scene 12 ...`
- Result: passed for inspection workspace `20260507_inspect_scene12_v2`
- Ran: `python ".\tiktok-growth-operator.skill\scripts\start_capture_pack_run.py" --scene 17 ...`
- Result: passed for inspection workspace `20260507_inspect_scene17_v2`
- Ran: `python ".\tiktok-growth-operator.skill\scripts\start_capture_pack_run.py" --scene 18 ...`
- Result: passed for inspection workspace `20260507_inspect_scene18_v2`
- Ran: `python ".\tiktok-growth-operator.skill\scripts\start_capture_pack_run.py" --scene 19 ...`
- Result: passed for inspection workspace `20260507_inspect_scene19_v2`
- Ran: Python JSON spot checks against regenerated Scene `11`, `12`, `17`, `18`, and `19` reports
- Result: passed; the previously blank `Scene 11/12` tables are now fully populated, and the new dispatch/follow-up tables for `17/18/19` render with non-empty rows

### Outcome

- Scene `11` now reads like a real weekly replication pipeline handoff rather than a partial scaffold
- Scene `12` now reads like a launch-ready multi-style test board instead of a half-filled matrix
- Scenes `07`, `17`, `18`, and `19` now feel more like operator playbooks and less like passive summaries

## 2026-05-08 Scene 02 Patrol Action-Board Upgrade

- Decision: strengthen Scene `02` at the importer layer so a patrol run still produces a concrete operator decision board even when delta files contain `0` live alerts or breakouts.
- Why: the real `Orange Cat` runtime proved that a quiet cycle was rendering too passively; operators still need a ranked Scene `03` handoff, a data-quality backlog, and a stable-watch interpretation instead of a near-empty alert section.

### Updated

- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`

### Added / Changed Behavior

- Scene `02` alert logic now supports a priority column and synthesizes meaningful patrol actions when the runtime delta is quiet
- quiet-cycle patrols now emit a `P1` scheduled teardown lane, a `P2` stable-leaderboard watch rule, and a metadata-enrichment backlog item instead of only saying “no high-priority alert”
- Scene `02` now exposes a visible prioritized Scene `03` queue with candidate reason, teardown lane, metric context, and owner guidance
- Scene `02` next-action content now reads more like a platform patrol action board than a passive monitoring memo

### Validation

- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\start_capture_pack_run.py" --scene 02 ...`
- Result: passed for inspection workspace `20260508_scene02_v2`
- Ran: Python spot checks against the regenerated Scene `02` JSON payload
- Result: passed; `Alert Logic`, `Scene 03` queue bullets, and `Next Action` summary blocks now render populated, actionable rows in the quiet-cycle runtime

### Outcome

- Scene `02` now behaves more like a true patrol console: quiet cycles still hand the operator a ranked next move instead of an empty escalation state

## 2026-05-08 Scene 02 To 03 Patrol Chain And Rich-Export QC

- Decision: wire the real `Scene 02` patrol output directly into a follow-on `Scene 03` teardown run instead of leaving the handoff only as a visible queue inside the patrol report.
- Why: the user explicitly wanted a true patrol-to-teardown closed loop, not just a recommendation board.
- Decision: compact local capture-pack paths at the importer/renderer display layer and suppress visibly dirty template text from rich exports.
- Why: the remaining quality issues were no longer workflow gaps; they were platform-feel issues caused by long absolute workspace paths and previously corrupted Chinese execution-template text leaking into operator-facing outputs.

### Updated

- `tiktok-growth-operator.skill/scripts/start_capture_pack_run.py`
- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`
- `tiktok-growth-operator.skill/scripts/render_scene_report.py`

### Added / Changed Behavior

- running `Scene 02` on a patrol capture pack now auto-launches a nested `Scene 03` teardown run when `scene03_candidates.json` is present
- `Scene 03` now prefers the patrol-generated candidate queue instead of falling back immediately to the generic qualified/ranked pool
- importer-side working-context, source, evidence, and asset references now render with compact display paths such as `tmp/.../capture-pack` or basename-level file references instead of full absolute Windows workspace paths
- `Scene 02` no longer emits low-value placeholder bullets under `Fields To Capture Next Time`; that section now explains the enrichment backlog and alert-governance purpose directly
- author-signature display text is cleaned further so noisy tail artifacts do not leak into `Scene 03` proof rows
- rich-export quality metrics no longer miscount compact display asset references as broken local paths
- current `Scene 02/03` JSON now keeps clean Chinese execution-template fields again, so DOCX/XLSX can keep the bilingual headings without mojibake

### Validation

- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py" ".\tiktok-growth-operator.skill\scripts\render_scene_report.py" ".\tiktok-growth-operator.skill\scripts\start_capture_pack_run.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\start_capture_pack_run.py" --scene 02 --capture-root "...\\20260507_validation_capture_scene02\\capture-pack" --name validation-scene02-chain-qc-v2 --project "TikTok Validation Scene 02 Chain QC V2" --platform TikTok --market US --output-root ".\\tiktok-growth-operator.skill\\tmp\\20260508_scene02_scene03_chain_qc_v2" --formats md,docx,xlsx`
- Result: passed and produced a real chained `scene-03-from-patrol` run
- Ran: JSON spot checks against the regenerated `Scene 02` and chained `Scene 03` reports
- Result: passed; compact display paths are present, `Scene 02` alert/backlog copy is upgraded, and the `Scene 03` authority line is cleaned
- Ran: `python-docx` and `openpyxl` spot checks against the regenerated `Scene 02` and `Scene 03` DOCX/XLSX outputs
- Result: passed; no mojibake markers were found, no absolute workspace paths remain in rich exports, and `Broken Asset Paths` now reports `0`

### Outcome

- `Scene 02 -> Scene 03` is now a real runtime chain, not only a visual handoff note
- current `Scene 02/03` DOCX and XLSX outputs are materially cleaner and read more like platform deliverables than debug exports
- remaining polish opportunities are now editorial density and layout taste improvements, not broken chain, encoding, or path-leak issues

## 2026-05-08 Scene 02 03 Executive-Surface Polish And V4 Chain Confirmation

- Decision: compress importer-generated `Working Context` and `Notes` into operator-summary language instead of field-dump language.
- Why: the chain was already correct, but the visible reports still read too much like internal runtime state rather than platform-facing patrol and teardown deliverables.
- Decision: tighten DOCX/XLSX summary surfaces at the renderer layer instead of hand-editing outputs.
- Why: the durable fix belongs in the package, and future rerenders should inherit the same cleaner executive presentation automatically.

### Updated

- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`
- `tiktok-growth-operator.skill/scripts/render_scene_report.py`

### Added / Changed Behavior

- importer `Working Context` now renders as a short executive summary with source pack, board size, lead candidate, and qualified control instead of a long line-by-line telemetry dump
- `Scene 02` notes now read as a dispatch memo with queue, backlog, and operating rule language
- `Scene 03` notes now read as a teardown memo with primary control, contrast reference, patrol-handoff status, and adaptation rule
- DOCX cover pages now show a shorter metadata block, bulletized working-context preview, and a compact executive snapshot table
- XLSX `Summary` sheets now use cleaner metric labels such as `Evidence Rows`, `Operator Notes`, `Ready Checks`, `Decision`, `Why Now`, and `Next Move`

### Validation

- Ran: `python -m py_compile ".\\tiktok-growth-operator.skill\\scripts\\import_tiktok_capture_pack.py" ".\\tiktok-growth-operator.skill\\scripts\\generate_scene_report.py" ".\\tiktok-growth-operator.skill\\scripts\\render_scene_report.py" ".\\tiktok-growth-operator.skill\\scripts\\start_capture_pack_run.py"`
- Result: passed
- Ran: `python ".\\tiktok-growth-operator.skill\\scripts\\start_capture_pack_run.py" --scene 02 --capture-root ".\\tiktok-growth-operator.skill\\tmp\\20260507_validation_capture_scene02\\capture-pack" --name validation-scene02-chain-qc-v4 --project "TikTok Validation Scene 02 Chain QC V4" --platform TikTok --market US --output-root ".\\tiktok-growth-operator.skill\\tmp\\20260508_scene02_scene03_chain_qc_v4" --formats md,docx,xlsx`
- Result: passed and produced a fresh real chained `scene-03-from-patrol` run
- Ran: Python JSON parse checks against regenerated `Scene 02` and chained `Scene 03` payloads
- Result: passed; both reports parse cleanly and now expose the new four-line operator-note blocks
- Ran: Markdown spot checks plus Excel COM spot checks against regenerated `Scene 02` and `Scene 03` outputs
- Result: passed; summary sheets show the new executive labels, current working-context previews are materially shorter, and no absolute workspace paths were reintroduced

### Outcome

- the latest confirmed chain root is `tiktok-growth-operator.skill/tmp/20260508_scene02_scene03_chain_qc_v4`
- current `Scene 02/03` Markdown, DOCX, and XLSX outputs now feel closer to operator deliverables than engineering exports
- remaining polish is now mostly around bilingual template cleanup and optional layout refinement, not runtime closure or encoding integrity

## 2026-05-08 Historical Rerender Normalization Fix

- Decision: make historical rerenders pass through the same payload-normalization layer as fresh render runs.
- Why: old `scene-*.json` payloads can contain legacy execution-template fields, and `rerender_scene_outputs.py` previously re-emitted them too literally instead of reusing the current display cleanup path.

### Updated

- `tiktok-growth-operator.skill/scripts/rerender_scene_outputs.py`

### Added / Changed Behavior

- rerender now resolves each existing `scene-*.json` through `render_scene_report.resolve_payload(...)` before writing MD, DOCX, or XLSX
- historical rerenders now inherit the current execution-template normalization, path compaction, and display cleanup rules automatically

### Validation

- Ran: `python -m py_compile ".\\tiktok-growth-operator.skill\\scripts\\rerender_scene_outputs.py" ".\\tiktok-growth-operator.skill\\scripts\\render_scene_report.py"`
- Result: passed
- Ran: `python ".\\tiktok-growth-operator.skill\\scripts\\rerender_scene_outputs.py" --root ".\\tiktok-growth-operator.skill\\tmp\\20260508_scene02_scene03_chain_qc_v4" --limit 2`
- Result: passed and rewrote both `Scene 02` and chained `Scene 03` outputs
- Ran: Python literal-content spot checks against regenerated Markdown `Recommended Request (ZH)` lines
- Result: passed; file content is clean Chinese, and no mojibake marker strings remain in the regenerated Markdown files

### Outcome

- historical rerender output now self-heals through the current renderer surface instead of replaying stale display issues
- the latest `Scene 02/03` v4 Markdown files are confirmed clean at file-content level, not only in visual spot checks

## 2026-05-08 Representative Historical Rerender Sweep

- Decision: rerender one representative historical sample for priority scenes `01`, `03`, `11`, `12`, `13`, `14`, `15`, and `16` through the repaired rerender path.
- Why: the current source and latest v4 outputs were already correct, but the visible backlog still included older scene workspaces that needed to inherit the new normalization and export-surface cleanup.
- Decision: extend renderer cleanup to cover embedded local paths inside `working_context.summary` and list items.
- Why: historical payloads stored some absolute Windows paths inside free-text summary and input fields, which still leaked into rerendered Markdown and summary sheets until those scalar/list fields were normalized too.

### Updated

- `tiktok-growth-operator.skill/scripts/render_scene_report.py`

### Added / Changed Behavior

- `working_context.summary` now passes through display cleanup during payload normalization
- `working_context.inputs`, `minimum_evidence`, `ideal_evidence`, `constraints`, `requested_outputs`, and `ready_checklist` now all normalize embedded local paths before rendering
- embedded Windows paths inside free text are compacted to short display paths such as `Playground 4/captures/...`
- representative historical rerenders now preserve clean Chinese execution-template text while also dropping absolute capture-root leakage from Markdown content

### Validation

- Ran: `python -m py_compile ".\\tiktok-growth-operator.skill\\scripts\\render_scene_report.py" ".\\tiktok-growth-operator.skill\\scripts\\rerender_scene_outputs.py"`
- Result: passed
- Ran representative rerenders for:
- `20260507_inspect_scene01`
- `20260507_inspect_scene03`
- `20260507_inspect_scene11_v2`
- `20260507_inspect_scene12_v2`
- `20260504_validation_capture_scene13`
- `20260504_validation_capture_scene14`
- `20260504_validation_capture_scene15`
- `20260504_validation_capture_scene16`
- Result: all passed and rewrote `md/docx/xlsx` outputs in place
- Ran: Python file-content spot checks against regenerated Markdown outputs for scenes `01`, `03`, `11`, and `15`
- Result: passed; `Recommended Request (ZH)` lines are clean Chinese, and `Capture root` now renders as `Playground 4/captures/...` rather than a full `D:\...` path

### Outcome

- the high-value historical sample set for scenes `01`, `03`, `11`, `12`, `13`, `14`, `15`, and `16` has been re-rendered through the current normalization stack
- file-content level checks now confirm both bilingual template cleanliness and local path compaction across the representative backlog slice

## 2026-05-08 Validator Fixture Hardening And Full Green Validation

- Decision: stop binding durable validators to ephemeral historical output roots that may disappear between runs.
- Why: the package logic was healthy, but `validate_export_outputs.py` and `validate_capture_pack_workflows.py` were still depending on older fixture directories and stale Summary-card wording, which created false-negative validation failures.

### Updated

- `tiktok-growth-operator.skill/scripts/validate_export_outputs.py`
- `tiktok-growth-operator.skill/scripts/validate_capture_pack_workflows.py`

### Added / Changed Behavior

- export validation now resolves its representative real fixtures from currently existing validation roots before falling back to older historical paths
- capture-pack validation now creates its own minimal run-history dedup fixture instead of assuming one legacy `project_launcher_test` directory still exists
- sparse-export validation now checks the current Summary quality card wording (`Blank Sections`) instead of the older `Empty Sections` label

### Validation

- Ran: `python -m py_compile ".\\tiktok-growth-operator.skill\\scripts\\validate_export_outputs.py" ".\\tiktok-growth-operator.skill\\scripts\\validate_capture_pack_workflows.py"`
- Result: passed
- Ran: `python ".\\tiktok-growth-operator.skill\\scripts\\validate_skill_docs.py"`
- Result: passed
- Ran: `python ".\\tiktok-growth-operator.skill\\scripts\\validate_scene_presets.py"`
- Result: passed
- Ran: `python ".\\tiktok-growth-operator.skill\\scripts\\validate_export_outputs.py" --output-root ".\\.codex-tmp\\20260508_validate_export_outputs_v3"`
- Result: passed; representative real fixtures and synthetic fixtures all rendered clean Markdown, DOCX, and XLSX outputs with no mojibake findings
- Ran: `python ".\\tiktok-growth-operator.skill\\scripts\\validate_capture_pack_workflows.py"`
- Result: passed; Scene `02 -> 03` patrol chain, capture-pack scenes, operator packs, and run-history dedup fixture all validated successfully
- Ran: `python ".\\tiktok-growth-operator.skill\\scripts\\validate_all_workflows.py"`
- Result: passed; the skill package now returns a full green validation bundle again

### Outcome

- the current durable validator surface is now aligned with the fixtures that actually exist in this workspace
- full package validation is green again without relying on vanished historical run folders
- the remaining work is product-surface expansion and optional external integrations, not validator drift or export-regression ambiguity

## 2026-05-08 Validator External-Root Closure

- Decision: remove the last functional validator dependency on `E:\tiktok\TikMatrix\tmp\...` by routing Scene `02` patrol validation through package-owned TikMatrix fixtures first.
- Why: the package already owned equivalent stable fixture copies under `testdata/validation/tikmatrix`, so keeping the validator pinned to external mutable temp roots no longer had any value and weakened reproducibility.

### Updated

- `tiktok-growth-operator.skill/scripts/validate_capture_pack_workflows.py`
- `docs/quality/debt-log.md`

### Added / Changed Behavior

- Scene `02` patrol validation now resolves `query-root` and `topic-root` from:
  - `tiktok-growth-operator.skill/testdata/validation/tikmatrix/search-live-orange-cat`
  - `tiktok-growth-operator.skill/testdata/validation/tikmatrix/topic-live-orangecat`
- legacy `E:\tiktok\TikMatrix\tmp\...` roots remain only as fallback, not as the primary validation dependency
- the debt item about mutable validation fixtures is now closed as a functional risk; remaining follow-up is documentation polish, not runtime fragility

### Validation

- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\validate_capture_pack_workflows.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_capture_pack_workflows.py"`
- Result: passed; Scene `02 -> 03` patrol validation now uses package-owned TikMatrix fixture roots
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_skill_docs.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Result: passed; full validator suite remains green after removing the last primary external patrol-root dependency

### Outcome

- the validator stack is now package-first for both export and patrol fixtures
- no remaining functional validation blocker depends on `E:\tiktok\TikMatrix\tmp\...`

## 2026-05-08 Validation Fixture README And Ephemeral Write Roots

- Decision: document the package-owned validation fixture inventory in place and move validator write-heavy runtimes onto workspace-local ephemeral roots.
- Why: the remaining friction was operational, not functional. Fixtures were no longer ambiguous, but they still lacked a local ownership note, and several validators were still defaulting to long-lived `tiktok-growth-operator.skill/tmp/...` output trees for transient verification work.

### Updated

- `tiktok-growth-operator.skill/testdata/validation/README.md`
- `tiktok-growth-operator.skill/scripts/validate_export_outputs.py`
- `tiktok-growth-operator.skill/scripts/validate_capture_pack_workflows.py`
- `tiktok-growth-operator.skill/scripts/validate_tikmatrix_bridge.py`
- `tiktok-growth-operator.skill/scripts/validate_tikmatrix_account_ops_bridge.py`
- `tiktok-growth-operator.skill/scripts/validate_all_workflows.py`

### Added / Changed Behavior

- `testdata/validation/README.md` now documents the purpose and ownership of:
  - `capture-packs/`
  - `captures/`
  - `reports/`
  - `tikmatrix/`
- export, capture-pack, TikMatrix bridge, account-ops bridge, and full-suite validators now default to ephemeral runtime roots under `.codex-tmp/` instead of writing their transient outputs into durable package `tmp/` folders
- validator fixture inputs remain package-owned and durable, but validator execution artifacts are now treated as disposable again

### Validation

- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\validate_all_workflows.py" ".\tiktok-growth-operator.skill\scripts\validate_export_outputs.py" ".\tiktok-growth-operator.skill\scripts\validate_capture_pack_workflows.py" ".\tiktok-growth-operator.skill\scripts\validate_tikmatrix_bridge.py" ".\tiktok-growth-operator.skill\scripts\validate_tikmatrix_account_ops_bridge.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_export_outputs.py"`
- Result: passed and wrote only to `.codex-tmp\tgo-validate-export-*`
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_capture_pack_workflows.py"`
- Result: passed and wrote runtime artifacts to `.codex-tmp\tgo-validate-capture-*`
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_tikmatrix_bridge.py"`
- Result: passed and wrote runtime artifacts to `.codex-tmp\tgo-validate-tikmatrix-bridge-*`
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_tikmatrix_account_ops_bridge.py"`
- Result: passed and wrote runtime artifacts to `.codex-tmp\tgo-validate-account-ops-bridge-*`
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Result: passed and now stages its bundle/export/board validation artifacts under `.codex-tmp\tgo-validate-all-*`

### Outcome

- validation fixtures are now self-documented at the point of use
- validator runtime writes are materially more read-only from the package perspective, with disposable outputs redirected away from durable skill-owned `tmp/` paths

## 2026-05-08 Validator Isolation, Reference Slimming, And Historical Tmp Policy

- Decision: isolate validator runtimes and history scan rules one layer more clearly from historical operator evidence roots.
- Why: the functional validator work was already green, but the package still needed a cleaner maintenance story so future validation does not silently drift back toward `tmp/*` archaeology.
- Decision: compress the reference split again instead of letting `direct-use.md`, `automation-workflows.md`, and `command-map.md` keep re-explaining the same entry surface.
- Why: operators need a shorter mental model: cookbook, behavior reference, or parity index.

### Updated

- `tiktok-growth-operator.skill/references/direct-use.md`
- `tiktok-growth-operator.skill/references/automation-workflows.md`
- `tiktok-growth-operator.skill/references/command-map.md`
- `tiktok-growth-operator.skill/references/final-handoff.md`
- `tiktok-growth-operator.skill/references/clipcat-openclaw-parity-audit.md`
- `tiktok-growth-operator.skill/testdata/validation/README.md`

### Added

- `tiktok-growth-operator.skill/references/tmp-retention-policy.md`

### Added / Changed Behavior

- the reference set now has a clearer role split:
  - `direct-use.md` = operator cookbook
  - `automation-workflows.md` = script ownership and validator semantics
  - `command-map.md` = shortest Clipcat parity command index
- package docs now explicitly distinguish:
  - durable validator fixtures under `testdata/validation/`
  - disposable validator runtimes under `.codex-tmp/tgo-validate-*`
  - historical parity evidence under `tiktok-growth-operator.skill/tmp/2026050*_...`
- `final-handoff.md` now records the hermetic Scene `04` single-video validator smoke and points readers to the tmp-retention policy
- parity audit now records the May 8, 2026 Scene `04` re-smoke via the frozen single-video fixture plus the centralized validator-runtime cleanup/isolation rule

### Validation

- planned next: rerun `validate_skill_docs.py`, `validate_capture_pack_workflows.py`, and `validate_all_workflows.py`
- planned next: rerun Scene `04` single-video and capture-pack smokes, then spot-check rich exports for selected high-value scenes

## 2026-05-08 Real-Runtime Scene Optimization Backlog

- Decision: add a durable optimization backlog for the scenes that already have real-runtime confirmation.
- Why: the package has reached broad public-scene parity, so the highest-value next work is report quality, evidence traceability, stronger ranking logic, and cleaner operator outputs rather than more scene count.
- Decision: keep this backlog inside the owning skill package under `references/`.
- Why: these upgrade ideas belong next to the scene contracts and parity audit, not only in chat or in a temp folder.

### Added

- `tiktok-growth-operator.skill/references/scene-optimization-backlog.md`

### Focus

- prioritize scenes `01`, `02`, `03`, `04`, `05`, `07`, `08`, `17`, `18`, and `19`
- compare the current package against public TikTok analysis tooling patterns
- convert external benchmarking into concrete file-owner suggestions plus validation paths

### Validation

- Ran: doc existence check for `tiktok-growth-operator.skill/references/scene-optimization-backlog.md`
- Result: passed
- Ran: manual consistency review against `tiktok-growth-operator.skill/references/clipcat-openclaw-parity-audit.md`
- Result: passed

### Follow-up

- implement `P1` evidence-reference and shortlist-quality upgrades first
- add one reusable scene-quality eval after the first report-quality upgrades land

## 2026-05-08 Public Parity And Scene 04 05 17 Structure Upgrade

- Decision: fold the latest public Clipcat surfaces and the reviewed DOCX bundle directly into the durable scene-optimization backlog.
- Why: the remaining parity gap is no longer scene count; it is output contract quality and platform-style operator structure.
- Decision: upgrade Scenes `04`, `05`, and `17` first.
- Why: these three scenes have the clearest document-backed output schemas and therefore offer the fastest quality lift with the lowest ambiguity.

### Updated

- `tiktok-growth-operator.skill/references/scene-optimization-backlog.md`
- `tiktok-growth-operator.skill/references/scene-report-contract.md`
- `tiktok-growth-operator.skill/scripts/scene_report_presets.py`
- `tiktok-growth-operator.skill/scripts/validate_scene_presets.py`
- `tiktok-growth-operator.skill/scenarios/04-single-video-breakdown.md`
- `tiktok-growth-operator.skill/scenarios/05-reverse-engineer-video-prompt.md`
- `tiktok-growth-operator.skill/scenarios/17-creator-distillation.md`

### Added / Changed Behavior

- Scene `04` now standardizes beat-by-beat timeline reconstruction, BGM analysis, no-voiceover handling, three-part viral interpretation, and explicit video-type classification
- Scene `05` now standardizes a generator-ready brief schema, shot-level rows, original-versus-adapted split, and field-level confidence handling
- Scene `17` now standardizes account overview, high-vs-low interaction comparison, formula extraction, visual/BGM/hashtag/posting-time surface, and a new-script bridge
- the durable backlog now explicitly captures the latest public parity expectations for scenes `01`, `02`, `03`, `04`, `05`, `07`, `08`, `17`, `18`, and `19`

### Validation

- planned next: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\scene_report_presets.py" ".\tiktok-growth-operator.skill\scripts\validate_scene_presets.py"`
- planned next: `python ".\tiktok-growth-operator.skill\scripts\validate_scene_presets.py"`
- planned next: `python ".\tiktok-growth-operator.skill\scripts\validate_skill_docs.py"`

## 2026-05-08 Scene 01 02 03 07 08 18 19 Product-Surface Upgrade

- Decision: upgrade the remaining highest-value runtime-confirmed analysis scenes before expanding any new scene family.
- Why: after the Scene `04/05/17` pass, the biggest parity gap was still operator surface quality across collection, patrol, batch teardown, market judgment, comment mining, competitor weekly review, and self retro.

### Updated

- `tiktok-growth-operator.skill/scripts/scene_report_presets.py`
- `tiktok-growth-operator.skill/scripts/validate_scene_presets.py`
- `tiktok-growth-operator.skill/scenarios/01-viral-video-collection.md`
- `tiktok-growth-operator.skill/scenarios/02-daily-category-patrol.md`
- `tiktok-growth-operator.skill/scenarios/03-batch-viral-search-plus-deep-teardown.md`
- `tiktok-growth-operator.skill/scenarios/07-category-market-insight.md`
- `tiktok-growth-operator.skill/scenarios/08-multi-product-comment-mining-and-persona-report.md`
- `tiktok-growth-operator.skill/scenarios/18-competitor-account-weekly-report.md`
- `tiktok-growth-operator.skill/scenarios/19-self-account-retro-and-optimization.md`

### Added / Changed Behavior

- Scene `01` now hardens search-window, region, sort, and cart-video semantics, plus explicit commerce-confidence and Scene `03` handoff fields
- Scene `02` now hardens append strategy, capture-date schema, change-first patrol logic, and Scene `03` escalation structure
- Scene `03` now hardens shortlist-rule, per-video script and rhythm capture, common-pattern synthesis, and creator-guidance blocks
- Scene `07` now adds keyword-level decisioning and separates content heat from product performance
- Scene `08` now keeps source-product labels through the merge and adds purchase-factor, praise, complaint, and price-band structure
- Scene `18` now emphasizes matrix comparison, breakout attribution, and strategy-change detection
- Scene `19` now emphasizes high-vs-low group comparison, content-mode clustering, and next-cycle testing

### Validation

- planned next: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\scene_report_presets.py" ".\tiktok-growth-operator.skill\scripts\validate_scene_presets.py"`
- planned next: `python ".\tiktok-growth-operator.skill\scripts\validate_scene_presets.py"`
- planned next: `python ".\tiktok-growth-operator.skill\scripts\validate_skill_docs.py"`

## 2026-05-08 Rich Export Validation Expansion

- Decision: extend rich-export validation from the older `Scene 15/17` pair to the real runtime-confirmed `Scene 02/03/08/18` sample set.
- Why: the export layer had already been upgraded for the higher-value analysis scenes, but the durable validator surface was still too narrow to protect those newer layouts.
- Decision: add explicit regression checks for wide section tables and visible local-path leakage.
- Why: the current parity gap is mostly deliverable polish. Two failure modes mattered most now: section sheets collapsing richer tables, and historical/local evidence roots leaking as raw absolute Windows paths.

### Updated

- `tiktok-growth-operator.skill/scripts/validate_export_outputs.py`

### Added / Changed Behavior

- export validation now renders and checks representative real fixtures for:
  - `Scene 02` patrol
  - `Scene 03` patrol-to-teardown handoff
  - `Scene 08` multi-product comment mining
  - `Scene 18` competitor weekly report
- Markdown, DOCX, and XLSX validation now all fail if visible absolute local paths such as `D:\...` leak into user-facing text
- workbook validation now verifies that each section sheet exists for every indexed section and that section-table headers keep the exact source width instead of silently collapsing back to a 4-column layout
- added a synthetic wide-table export fixture to keep section-sheet width regression coverage durable

### Spot Check Notes

- representative rerender spot checks against `.codex-tmp/20260508_scene_export_surface_real/` confirmed:
  - `Scene 02/03/08` rich exports render with clean UTF-8 visible text
  - local evidence roots are compacted to display-safe relative paths such as `tmp/...` or `validation/...`, not raw `D:\...`
  - `Scene 18` still shows `Blank Sections` quality flags because the source payload is intentionally sparse draft content, not because of export corruption

### Validation

- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\validate_export_outputs.py" ".\tiktok-growth-operator.skill\scripts\render_scene_report.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_export_outputs.py" --output-root ".\.codex-tmp\20260508_validate_export_outputs_scene_surface"`
- Result: passed; real fixtures `02/03/08/18` plus synthetic duplicate-heading, sparse, execution-template, and wide-table fixtures all rendered clean `md/docx/xlsx`
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Result: passed; full skill validator bundle remains green after export-surface coverage expansion

### Outcome

- the durable export validator surface now protects the upgraded platform-style analysis scenes instead of only the older `15/17` slice
- the remaining work is scene-content enrichment and optional renderer aesthetics, not basic rich-export integrity or path/encoding regressions

## 2026-05-08 Section-Level Evidence References

- Decision: promote section-local evidence references into the canonical scene-report contract instead of leaving them as ad hoc table columns only.
- Why: the main remaining `P1` quality gap for real-runtime scenes was reviewability. High-level claims and reusable formulas needed durable source linkage that survives `JSON`, `Markdown`, `DOCX`, and `XLSX`, not only human memory or one-off `Evidence Ref` cells.
- Decision: land the first structured evidence-ref pass on the highest-value analysis scenes first.
- Why: scenes `03`, `04`, `08`, `17`, `18`, and `19` are the places where pattern claims, clustered insights, and strategic conclusions most need explicit traceability.

### Updated

- `tiktok-growth-operator.skill/scripts/scene_report_presets.py`
- `tiktok-growth-operator.skill/scripts/generate_scene_report.py`
- `tiktok-growth-operator.skill/scripts/render_scene_report.py`
- `tiktok-growth-operator.skill/scripts/validate_scene_presets.py`
- `tiktok-growth-operator.skill/references/scene-report-contract.md`

### Added / Changed Behavior

- each section can now carry a formal `evidence_refs` list in the report contract
- each evidence-ref row uses a stable schema:
  - `source_type`
  - `source_id`
  - `source_url`
  - `time_range`
  - `excerpt`
  - `supports`
- `Scene 03`, `04`, `08`, `17`, `18`, and `19` starter presets now ship with section-level evidence-ref placeholders tied to their most important analytical claims
- Markdown rendering now emits a `### Evidence References` block beneath any section that includes those refs
- DOCX rendering now emits an `Evidence References` subtable per relevant section
- XLSX section sheets now emit a second native table for section-local evidence refs instead of forcing all provenance into the top-level `Evidence` sheet only
- preset validation now checks the new field so future scene edits do not silently drop the structure

### Spot Check Notes

- scaffold smoke for `Scene 04` at `.codex-tmp/20260508_scene04_evidence_ref_rendered/` confirmed:
  - Markdown now shows an `Evidence References` table directly under `Structure Logic` and `Risks And Adaptation Notes`
  - XLSX `02-Structure Logic` now contains both the main timeline table and a second evidence-reference table
  - DOCX now includes section-local `Evidence References` headings/tables rather than forcing all provenance into one global block

### Validation

- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\scene_report_presets.py" ".\tiktok-growth-operator.skill\scripts\generate_scene_report.py" ".\tiktok-growth-operator.skill\scripts\render_scene_report.py" ".\tiktok-growth-operator.skill\scripts\validate_scene_presets.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_scene_presets.py"`
- Result: passed with no warnings after filling placeholder `source_url/time_range` fields
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_export_outputs.py" --output-root ".\.codex-tmp\20260508_validate_export_outputs_evidence_refs"`
- Result: passed; export validation remained green after section-level evidence-ref rendering was added
- Ran: `python ".\tiktok-growth-operator.skill\scripts\generate_scene_report.py" --scene 04 --project "Evidence Ref Smoke" --output ".\.codex-tmp\20260508_scene04_evidence_ref_smoke.json" --format json`
- Result: passed and emitted a scaffold containing section-local `evidence_refs`
- Ran: `python ".\tiktok-growth-operator.skill\scripts\render_scene_report.py" --input ".\.codex-tmp\20260508_scene04_evidence_ref_smoke.json" --output-dir ".\.codex-tmp\20260508_scene04_evidence_ref_rendered" --formats md,docx,xlsx`
- Result: passed; section-level evidence refs render cleanly in all three export surfaces
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Result: passed; full package validation remains green with the new contract field

### Outcome

- evidence traceability is now part of the durable scene contract rather than a prompt habit
- the upgraded analysis scenes can now carry section-local provenance in a platform-style way across all export types
- the next high-value work should build on this by enriching real scene payloads and scoring logic, not by reworking the exporter again

## 2026-05-08 Scene 01 03 Reuse-Value Shortlist Scoring

- Decision: upgrade the TikMatrix capture bridge from popularity-first ranking to reuse-value-first ranking while keeping TikMatrix core untouched.
- Why: the next quality lift for Scene `01` and Scene `03` comes from choosing better teardown candidates, not from adding more output templates. The bridge already had richer metadata than it was using.
- Decision: keep the new ranking fully explainable and consumable by existing downstream scene fillers.
- Why: shortlist upgrades only help if the ranked rows carry stable rationale fields that Scene `02/03` reports can surface directly.

### Updated

- `tiktok-growth-operator.skill/scripts/run_tikmatrix_capture_bridge.py`
- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`
- `tiktok-growth-operator.skill/scripts/validate_tikmatrix_bridge.py`

### Added / Changed Behavior

- bridge ranking now computes multi-factor `reuse_value_score` instead of relying on one blended popularity count
- each ranked row now carries explicit scoring and handoff fields:
  - `reuse_value_score`
  - `popularity_score`
  - `score_breakdown`
  - `score_breakdown_text`
  - `why_selected`
  - `reuse_value_label`
  - `reuse_purpose`
  - `shopping_intent`
  - `tkshop_signal`
  - `commerce_confidence`
- shortlist selection for `aggregate_qualified_videos.json` now uses reuse-value thresholds plus fallback popularity, then tags each winner with:
  - `shortlist_priority`
  - `shortlist_bucket`
  - `shortlist_decision`
  - `scene03_reason`
- downstream capture-pack import helpers now prefer bridge-provided rationale fields before falling back to older heuristic text, so Scene `03` can surface the new explanations without rewriting the whole scene filler

### Validation

- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\run_tikmatrix_capture_bridge.py" ".\tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py" ".\tiktok-growth-operator.skill\scripts\validate_tikmatrix_bridge.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_tikmatrix_bridge.py"`
- Result: passed; bridge outputs now include the new reuse-value ranking and shortlist fields
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Result: passed; full validator bundle remained green after the shortlist-scoring upgrade

### Spot Check

- Checked `.codex-tmp/tgo-validate-tikmatrix-bridge-8_fch86t/capture-pack/aggregate_qualified_videos.json`
- confirmed top shortlist rows now include:
  - scored quality dimensions
  - explicit `why_selected`
  - direct Scene `03` handoff metadata

### Outcome

- Scene `01` and Scene `03` now select teardown candidates with better emphasis on reusable hook quality, enrichment quality, authority/proof, and portability
- the bridge has shifted from "viral list sorter" toward "platform-style candidate triage" without touching `E:\tiktok\TikMatrix`

## 2026-05-08 Scene 01 Export Surfacing, Comment Cleaning, And Scene 05 Handoff Upgrade

- Decision: expose the new Scene `01` shortlist-quality and commerce fields directly in operator-facing tables instead of keeping them mostly inside bridge JSON.
- Why: the reuse-value ranking only improves platform parity if the exported report itself makes the selection logic obvious to a human operator choosing what to study next.
- Decision: add deterministic comment cleaning and reply-chain synthesis inside the capture-pack importer.
- Why: Scenes `08`, `18`, and `19` were already structurally strong, but the current real runtime needed cleaner buyer-language clusters and some reply-awareness before the outputs could feel platform-grade.
- Decision: expand Scene `05` handoff columns around asset needs and generator-ready adaptation fields.
- Why: this closes more of the gap between analysis output and downstream video-generation brief quality without claiming a final renderer backend.

### Updated

- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`
- `tiktok-growth-operator.skill/scripts/scene_report_presets.py`
- `tiktok-growth-operator.skill/scripts/validate_scene_presets.py`
- `tiktok-growth-operator.skill/references/scene-report-contract.md`

### Added / Changed Behavior

- Scene `01` export tables now surface reuse-value and commerce fields more directly, including:
  - publish-window visibility
  - TikTok Shop signal
  - commerce confidence
  - reuse label / reuse purpose
  - why-selected rationale
  - best-next-scene handoff
- capture-pack comment intake now adds deterministic cleaning, low-signal filtering support, cluster typing, price-band estimation, and lightweight reply-chain synthesis
- Scene `08` now summarizes cleaner comment clusters, reply cues, product-direction implications, and price-band evidence more clearly in runtime-filled outputs
- Scene `17` now carries account-overview metrics, breakout-rate estimate, formula-library rows, fuller visual/distribution signature blocks, and a stronger new-script bridge
- Scene `18` now fills comparison-oriented capture-next rows with hook, proof, and posting-pattern deltas instead of leaving the section generic
- Scene `05` presets and contract now require generator-handoff aware columns such as `Asset Need` and `Generator Handoff Field`

### Validation

- Ran: `python "tiktok-growth-operator.skill\scripts\validate_scene_presets.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\validate_capture_pack_workflows.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Result: passed

### Follow-up

- run representative rich-export spot checks for Scenes `01`, `08`, and `17`
- continue strengthening runtime-filled Scene `04/05/17` output quality and handoff completeness

## 2026-05-08 Scene 04 05 17 Runtime Filler Upgrade And Spot Check

- Decision: strengthen the real-runtime filler logic for Scenes `04`, `05`, and `17` instead of relying only on prettier preset scaffolds.
- Why: these scenes already had better contracts, but the imported capture-pack outputs still needed more platform-style structure in the filled rows before they truly matched the intended operator surface.
- Decision: treat the recent DOCX encoding check as a validation-method issue, not an export corruption bug.
- Why: the initial grep-like check was falsely matching the XML declaration `<?xml`; stricter replacement-char and mojibake inspection showed no UTF-8 replacement-character corruption in the sampled DOCX exports.

### Updated

- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`

### Added / Changed Behavior

- Scene `04` runtime import now fills:
  - beat-level timeline rows with time ranges and evidence refs
  - explicit video-type classification
  - no-voiceover interpretation guidance
  - BGM / sensory layer rows
  - practical three-lens viral interpretation rows
  - safer vs more aggressive adaptation table output
- Scene `05` runtime import now fills:
  - generator-ready schema rows across style/environment/tone/camera/lighting/character/audio/editing
  - shot-level breakdown rows with `Asset Need`
  - stronger product-adaptation rows with `Generator Handoff Field`
  - clearer recovered proof-lane and adaptation-lane cues in the executive section
- Scene `17` runtime import now fills:
  - stronger account-overview positioning text
  - high-vs-low interaction comparison rows, including video-type contrast
  - richer formula-library and new-script bridge rows tied to the top sampled post
  - fuller visual/distribution surface with BGM and hashtag signals

### Spot Check

- rerendered representative rich outputs under `.codex-tmp/20260508_scene_spotcheck_v2/`
- confirmed Scene `04/05/17` Markdown exports now show the strengthened runtime rows instead of mostly generic fallback copy
- confirmed sampled `DOCX` exports do not contain Unicode replacement characters; the earlier `?` hit was the XML declaration opener, not a garbling defect
- confirmed sampled `XLSX` exports still render cleanly with no visible encoding regression in shared strings

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\validate_scene_presets.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\validate_capture_pack_workflows.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Result: passed

## 2026-05-08 Scene 18 19 Runtime Upgrade And Scene 18 Text-Clean Repair

- Decision: keep pushing runtime-filled report quality for Scenes `18` and `19` instead of stopping at preset parity.
- Why: these two scenes are only useful at platform level when the imported real-capture outputs already read like operator-ready weekly reports and retros, not generic templates.
- Decision: fix the remaining Scene `18` main-table mojibake leak at the importer layer rather than masking it in exports.
- Why: the output surface was already mostly clean, so the remaining bad row had to be eliminated where `desc` text was still being passed through too directly.

### Updated

- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`

### Added / Changed Behavior

- Scene `18` runtime import now fills:
  - clearer winning-lane and breakout-cue framing in the executive section
  - stronger weekly-shift rows with strategy-change phrasing tied to ranking evidence
  - better weekly operator-response actions with cleaner urgency and action-area structure
  - safer main-theme text in the per-account summary table by routing through normalized cue text instead of raw `desc`
- Scene `19` runtime import now fills:
  - explicit high-vs-low comparison rows
  - stronger content-mode-first clustering
  - growth / ROI relevance framing per pattern
  - clearer do-more / do-less / stop / test-next operating rules
  - a real next-cycle test-plan table rather than only retrospective notes
- caption/display cleaning now strips a few more TikTok-specific mojibake fragments so recovered hook text stays usable in final report tables

### Spot Check

- rerendered representative Scene `18` and Scene `19` outputs under `.codex-tmp/20260508_scene_spotcheck_v2/`
- confirmed Scene `18` now renders the per-account `Main Theme` row with clean text:
  - `PSA: always sing your heart out, you'll never know who's going to listen`
- confirmed Scene `18` weekly operator-response rows render with the intended 4-column structure
- confirmed Scene `19` Markdown export shows the upgraded:
  - high-vs-low judgment table
  - performance clusters
  - do-more / do-less / stop / test-next action table
  - next-cycle test plan
- confirmed the earlier DOCX/XLSX encoding concern remains closed; this pass exposed a runtime text-cleaning issue in one Markdown/JSON path, not a document-export encoding regression

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\validate_capture_pack_workflows.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- Result: passed

## 2026-05-08 Feishu Bitable First-Step Adapter

- Decision: start Feishu integration with a zero-extra-install Bitable bridge instead of waiting for a richer Docs/message adapter stack.
- Why: the public Clipcat docs repeatedly frame Feishu table/doc delivery as a core operator surface, and the fastest safe parity gain is to push structured scene outputs into Feishu with the Python environment that already exists here.
- Decision: optimize the first pass for Feishu beginners.
- Why: the user explicitly said they are a Feishu novice, so the first deliverable has to be a minimal, setup-friendly path rather than a broad but fragile integration.

### Added

- `tiktok-growth-operator.skill/scripts/push_report_to_feishu.py`
- `tiktok-growth-operator.skill/references/feishu-setup.md`

### Updated

- `tiktok-growth-operator.skill/references/direct-use.md`

### Added / Changed Behavior

- new Feishu push script now supports:
  - `App ID` + `App Secret` auth through Feishu Open Platform
  - create-or-reuse Feishu Bitable app
  - create-or-reuse table
  - batch insert beginner-friendly report slices:
    - `summary`
    - `section_overview`
    - `evidence`
    - `assets`
- direct-use docs now include copy-ready Feishu push commands
- Feishu setup doc now gives a beginner-first path:
  - create app
  - enable permissions
  - set env vars
  - push `summary` first
  - reuse returned `app_token` for later tables

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\push_report_to_feishu.py"`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\push_report_to_feishu.py" --help`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill\scripts\validate_skill_docs.py"`
- Result: passed

## 2026-05-08 Official lark-cli Feishu Doc Bridge

- Decision: add an official `lark-cli` document-delivery bridge alongside the existing Python Bitable adapter instead of replacing the beginner path.
- Why: the user wants Feishu integration but is a beginner. The current Python adapter is the fastest route to first success, while `lark-cli` is the better long-term platform-grade delivery layer for full report docs.
- Decision: install the official Windows binary directly under `E:\飞书` instead of relying on the local `npm` or `go` toolchain.
- Why: this machine currently has a broken `npm` resolution path and a broken `go` runtime, but the release binary is sufficient for real CLI usage.

### Added

- `tiktok-growth-operator.skill/scripts/push_report_to_feishu_doc.py`

### Updated

- `tiktok-growth-operator.skill/references/feishu-setup.md`
- `tiktok-growth-operator.skill/references/direct-use.md`

### Local Environment Notes

- downloaded official repo snapshot to `E:\飞书\larksuite-cli`
- downloaded official Windows binary release archive to `E:\飞书\lark-cli-bin\lark-cli-1.0.25-windows-amd64.zip`
- extracted runnable binary to `E:\飞书\lark-cli-bin\v1.0.25\lark-cli.exe`
- verified:
  - `lark-cli version 1.0.25`
- observed current blocker before real auth:
  - `lark-cli auth status` returns `hermes context detected but lark-cli is not bound to it`
- interpretation:
  - the binary works
  - the current Codex desktop environment needs one-time `config bind` before user/bot auth flows can proceed

### Added / Changed Behavior

- new Feishu doc push script now supports:
  - structured scene report JSON input
  - Markdown handoff rendering from the existing scene-report contract
  - official `lark-cli docs +create`
  - official `lark-cli docs +update --mode append|overwrite`
  - explicit `bot` or `user` identity selection
  - beginner-facing next-step hints when the CLI blocks on `config bind` or `auth login`
- direct-use docs now expose both Feishu delivery paths:
  - `push_report_to_feishu.py` for Bitable
  - `push_report_to_feishu_doc.py` for full Feishu docs
- Feishu setup docs now explain the current agent-workspace binding requirement and the safest first command:
  - `lark-cli config bind --identity bot-only`

## 2026-05-08 Hermes Feishu Credential Sync Helper

- Decision: add a small helper that writes Feishu app credentials into `D:\hermes\.env` instead of leaving the user to hand-edit Hermes internals.
- Why: the real blocker after installing `lark-cli` was not the CLI binary but the missing Hermes-side `FEISHU_APP_ID` / `FEISHU_APP_SECRET` values required by `config bind`.

### Added

- `tiktok-growth-operator.skill/scripts/setup_hermes_feishu_env.py`

### Updated

- `tiktok-growth-operator.skill/references/feishu-setup.md`
- `tiktok-growth-operator.skill/references/direct-use.md`

### Added / Changed Behavior

- new helper now:
  - reads `FEISHU_APP_ID` / `FEISHU_APP_SECRET` from flags or environment
  - writes or updates those values inside `D:\hermes\.env`
  - ensures `FEISHU_DOMAIN=feishu`
  - prints the exact next commands for:
    - `lark-cli config bind --identity bot-only`
    - `lark-cli doctor --offline`
- docs now explain the two-stage official Feishu setup path more concretely:
  - sync Hermes `.env`
  - bind current Hermes workspace

## 2026-05-08 Feishu Direct OpenAPI Runtime And Scope Diagnosis

- Decision: stop treating `lark-cli` as the primary Feishu doc runtime in this workspace and switch the durable doc push path to direct Feishu OpenAPI.
- Why: real credential verification succeeded, but `lark-cli` continued to fail through the Hermes-backed tenant token path with a false `app secret invalid`, while direct OpenAPI calls reached the real Feishu endpoints reliably.
- Decision: make the scripts fail with explicit scope diagnostics instead of raw HTTP tracebacks.
- Why: the remaining blocker is now operator-side app permission setup, so the output must tell the user exactly which Feishu scopes are missing and where to enable them.

### Updated

- `tiktok-growth-operator.skill/scripts/push_report_to_feishu_doc.py`
- `tiktok-growth-operator.skill/scripts/push_report_to_feishu.py`
- `tiktok-growth-operator.skill/references/feishu-setup.md`
- `tiktok-growth-operator.skill/references/direct-use.md`

### Real Runtime Findings

- direct auth succeeded with the current app credentials
- direct Docs API create reached `POST /open-apis/docs_ai/v1/documents`
- direct Bitable app create reached `POST /open-apis/bitable/v1/apps`
- Docs runtime blocker returned:
  - missing scopes `docx:document`, `docx:document:create`
- Bitable runtime blocker returned:
  - missing scopes `bitable:app`, `base:app:create`
- conclusion:
  - code path is now live and correct
  - remaining work is Feishu Open Platform scope enablement

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill\scripts\push_report_to_feishu.py" "tiktok-growth-operator.skill\scripts\push_report_to_feishu_doc.py"`
- Ran: real direct Docs API create against the current app credentials
- Result: reached real Feishu endpoint and returned precise missing-scope error instead of auth failure
- Ran: real direct Bitable app create against the current app credentials
- Result: reached real Feishu endpoint and returned precise missing-scope error instead of auth failure

## 2026-05-08 Feishu Auto-Push Integration Into Native Workflow Entrypoints

- Decision: push Feishu delivery down into the native workflow launchers instead of keeping it only in `run_operator_workflow.py`.
- Why: operators also run `start_scene_run.py` and `start_capture_pack_run.py` directly, so Feishu delivery must not depend on one wrapper only.
- Decision: add one shared Feishu runtime helper and one retry for transient Feishu `10071` doc-create failures.
- Why: this keeps the push behavior consistent across entrypoints and removes a real transient edge observed during native Scene 18 smoke.

### Added

- `tiktok-growth-operator.skill/scripts/feishu_push_runtime.py`

### Updated

- `tiktok-growth-operator.skill/scripts/run_operator_workflow.py`
- `tiktok-growth-operator.skill/scripts/start_scene_run.py`
- `tiktok-growth-operator.skill/scripts/start_capture_pack_run.py`

### Real Runtime Validation

- `run_operator_workflow.py --push-feishu` real smoke succeeded for Scene 18
- `start_capture_pack_run.py --push-feishu` real smoke succeeded for Scene 04 capture fixture
- `start_scene_run.py --push-feishu` hit one transient Feishu `code=10071` on first doc create, then succeeded on retry with the same payload
- conclusion:
  - auto Feishu push now works from all three main workflow entrypoints
  - transient Feishu doc-create instability is now absorbed by one built-in retry

## 2026-05-08 Feishu Scene 04 05 17 Finished-Doc Polish And Confirmed Input List

- Decision: do one more polish pass on Scene `04`, `05`, and `17` instead of treating the first high-value push as done.
- Why: these three scenes still had the most visible mixed-language residue in structure labels, adaptation blocks, and action headers, while the runtime path was already stable.
- Decision: add one durable confirmed-input list for all currently real-confirmed Feishu repush scenes.
- Why: after repeated real pushes, the bigger operator risk is path drift and manual re-entry, not missing runtime capability.

### Added

- `tiktok-growth-operator.skill/references/feishu-confirmed-scene-inputs.txt`

### Updated

- `tiktok-growth-operator.skill/scripts/push_report_to_feishu_doc.py`

### Added / Changed Behavior

- additional Chinese replacements now cover more mixed-language residue in Scene `04/05/17`, especially around:
  - section titles such as `Next Action`, `Structure Map`, and risk/adaptation blocks
  - creator-pattern and brief-schema table headers
  - creator-distillation and reverse-brief action rows that were still half English
- added one reusable input list containing the currently real-confirmed report JSON paths for scenes:
  - `01`, `04`, `05`, `08`, `17`, `18`, `19`

### Real Runtime Validation

- Ran: `python tiktok-growth-operator.skill/scripts/push_scene_reports_to_feishu_doc.py --inputs <scene04> <scene05> <scene17> --app-id ... --app-secret ... --title-prefix "??????-v2"`
- Result: passed and created three new real Feishu Docs
- Scene `04`: https://pizvgz6mvgi.feishu.cn/docx/O0PdddjZvo9awWxKUCAcLq0CnUe
- Scene `05`: https://pizvgz6mvgi.feishu.cn/docx/JqsSd1hqgoA3RyxFpflcPdnangd
- Scene `17`: https://pizvgz6mvgi.feishu.cn/docx/IhBCdYMhnou46zxSGSPcjZzqndb
- Ran: `python -m py_compile` on the touched Feishu scripts
- Result: passed
- Ran: `python tiktok-growth-operator.skill/scripts/validate_skill_docs.py`
- Result: passed

## 2026-05-08 Feishu High-Value Scene 04 05 17 18 19 Chinese Finished-Doc Batch Pass

- Decision: extend the Chinese finished-doc renderer pass from Scene `01/08` to the higher-value analysis and reporting scenes `04`, `05`, `17`, `18`, and `19`.
- Why: these scenes are the ones most likely to be handed directly to operators or used as platform-grade deliverables, so the Feishu delivery surface needed stronger scene-specific Chinese localization beyond the first Scene `01/08` pass.

### Updated

- `tiktok-growth-operator.skill/scripts/push_report_to_feishu_doc.py`

### Added / Changed Behavior

- strengthened Chinese replacements for scene-specific runtime phrases and table structures across:
  - Scene `04` single-video breakdown
  - Scene `05` reverse-prompt / brief reconstruction
  - Scene `17` creator formula distillation
  - Scene `18` competitor account weekly report
  - Scene `19` self-account retro and optimization
- expanded Feishu markdown cleanup to reduce English leakage in:
  - executive summary action lines
  - structure / formula / adaptation section headers
  - common table headers for breakdown, generator handoff, creator pattern, and weekly dispatch blocks

### Real Runtime Validation

- Ran: `python tiktok-growth-operator.skill/scripts/push_scene_reports_to_feishu_doc.py --inputs <scene04> <scene05> <scene17> <scene18> <scene19> --app-id ... --app-secret ... --title-prefix "??????-v1"`
- Result: passed and created five new real Feishu Docs
- Scene `04`: https://pizvgz6mvgi.feishu.cn/docx/UmDqdThItoU5hjxy4YkcjYTIncc
- Scene `05`: https://pizvgz6mvgi.feishu.cn/docx/CXSUdqeakoPFTMxvSE5cBYzRn2g
- Scene `17`: https://pizvgz6mvgi.feishu.cn/docx/QZILd8CKiob7yAxpvMccKR3Bnfw
- Scene `18`: https://pizvgz6mvgi.feishu.cn/docx/RVCzdZmrMokdqBxNptwcXKs6nUb
- Scene `19`: https://pizvgz6mvgi.feishu.cn/docx/Vb6wdJ2UHoV2VXx6mpfc4cAfnBd
- Ran: `python -m py_compile` on the touched Feishu scripts
- Result: passed
- Ran: `python tiktok-growth-operator.skill/scripts/validate_skill_docs.py`
- Result: passed

## 2026-05-08 Feishu Scene 01 08 Chinese Finished-Doc Batch Re-Push

- Decision: add one direct scene-report batch Feishu Doc repush entrypoint instead of relying only on `batch_result.json` payloads.
- Why: real scene spot checks often live as standalone scene JSON files, so the fastest operator loop is to repush selected reports directly into Chinese finished docs without rebuilding a prior batch wrapper.
- Decision: strengthen the Feishu doc localizer around scene-id inference and Scene `01` / `08` English-template leakage.
- Why: the real OpenAPI path was already working, but standalone spot-check reports with missing `metadata.scene` were falling back to a generic scene label and still leaking too many English scaffold fragments into the final delivery surface.

### Added

- `tiktok-growth-operator.skill/scripts/push_scene_reports_to_feishu_doc.py`

### Updated

- `tiktok-growth-operator.skill/scripts/push_report_to_feishu_doc.py`

### Added / Changed Behavior

- Feishu doc renderer now infers `scene_id` from `scenario_file` / `scene_slug` when `metadata.scene` is missing
- Scene `01` and `08` standalone JSON reports now resolve to the correct Chinese scene labels in finished Feishu doc titles
- Feishu markdown localization now strips more scaffold-only italic helper lines and translates more runtime English copy for:
  - Scene `01` shortlist / collection-board output
  - Scene `08` comment-mining / persona output
- new direct batch repush helper now accepts one or more scene JSON files and pushes each through the Chinese finished-doc renderer

### Real Runtime Validation

- Ran: `python tiktok-growth-operator.skill/scripts/push_scene_reports_to_feishu_doc.py --inputs <scene01-json> <scene08-json> --app-id ... --app-secret ... --title-prefix "??????"`
- Result: passed and created two new real Feishu Docs
- Scene `01` real doc: `?????? | Spotcheck Scene 01 Rich - ?? 01 - ??????`
  - https://pizvgz6mvgi.feishu.cn/docx/CzMddvGbjoPdoSxSHhVcajYbnYf
- Scene `08` real doc: `?????? | Spotcheck Scene 08 Rich - ?? 08 - ?????????`
  - https://pizvgz6mvgi.feishu.cn/docx/IJ7Ld6CeWowPojxj5tgc7welnid
- Ran: `python -m py_compile` on the touched Feishu scripts
- Result: passed
- Ran: `python tiktok-growth-operator.skill/scripts/validate_skill_docs.py`
- Result: passed

## 2026-05-08 Feishu Chinese Naming Surface

- Decision: translate the default Feishu delivery surface to Chinese through one shared naming helper instead of patching titles independently in each script.
- Why: the user explicitly wants everything pushed to Feishu to be Chinese, and a shared helper prevents the Doc title, Bitable Base name, table name, and batch preset recommendations from drifting apart again.

### Added

- `tiktok-growth-operator.skill/scripts/feishu_naming.py`

### Updated

- `tiktok-growth-operator.skill/scripts/push_report_to_feishu.py`
- `tiktok-growth-operator.skill/scripts/push_report_to_feishu_doc.py`
- `tiktok-growth-operator.skill/scripts/push_batch_results_to_feishu.py`
- `tiktok-growth-operator.skill/scripts/generate_batch_preset.py`
- `tiktok-growth-operator.skill/references/feishu-setup.md`
- `tiktok-growth-operator.skill/references/direct-use.md`

### Added / Changed Behavior

- Feishu Doc 默认标题现在使用中文场景名和中文报告名。
- Feishu Bitable 默认 Base 名、表名、字段名现在全部使用中文。
- 批量预设报告里的飞书后续推送说明与推荐命名现在改成中文。
- Feishu 脚本返回的 `next_steps` 说明改成中文，适合直接给飞书新手看。
- Feishu Doc 正文不再直接复用英文 Markdown，而是走一层飞书专用中文渲染后处理，已覆盖目录、元数据行、常见章节标题与提示块。
- Feishu 命名层开始把常见市场码转换成中文展示，例如 `US -> 美国`。
- 同一套中文成品渲染已确认不只适用于 Scene `18`，也已真实跑通 Scene `19`。
- 中文成品渲染已进一步扩展到 Scene `04` 与 Scene `17` 的真实飞书文档推送。

### Validation

- Ran: `python -m py_compile` on the touched Feishu scripts
- Ran: `python "tiktok-growth-operator.skill\scripts\validate_skill_docs.py"`
- Ran: real Feishu bundle push against an existing Scene `18` report after the Chinese naming change
- Ran: second real Feishu Doc push after adding the Chinese body renderer
- Ran: additional real Feishu Doc pushes for Scene `18` and Scene `19` after the delivery-surface cleanup and market-label localization
- Ran: additional real Feishu Doc pushes for Scene `04` and Scene `17` using representative rich spot-check reports
- Result: passed; new Feishu Doc body and new Bitable table surfaces now render in Chinese by default, with Scenes `04`, `17`, `18`, and `19` all confirmed on the real path

## 2026-05-09 Feishu Chinese Finished-Doc Acceptance Pass

- Decision: force Feishu doc titles to rebuild from the shared Chinese naming layer instead of trusting scene JSON `metadata.title`.
- Why: several real scene reports still carried legacy English titles such as `Scene 04 Report - ...`, which leaked into the final Feishu delivery surface even after the body localizer improved.
- Decision: treat remaining English in real doc bodies as two categories: must-localize structure text versus allowed raw evidence text.
- Why: the user requirement is a Chinese product-grade deliverable, but source captions, usernames, quoted comments, and reference post text must remain intact as evidence instead of being falsely translated.

### Updated

- `tiktok-growth-operator.skill/scripts/feishu_naming.py`
- `tiktok-growth-operator.skill/scripts/push_report_to_feishu_doc.py`

### Added / Changed Behavior

- Feishu doc default titles now always rebuild from localized `project + scene` naming, even when the source JSON still contains old English report titles.
- The doc-body localizer now covers more real residue from Scenes `04`, `05`, `08`, `17`, and `19`, including:
  - structure-table labels
  - brief-schema labels
  - creator-pattern labels
  - retro / next-cycle planning labels
  - weekly / performance action wording
- Scene `19` retro docs now render Chinese action and test-plan sections instead of mixed English operator scaffolds.
- The acceptance rule is now explicit:
  - all product framing, headings, section names, table labels, recommendations, and action text should be Chinese
  - raw TikTok evidence such as usernames, source captions, comment quotes, URLs, and file names may remain in source language

### Real Runtime Validation

- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\feishu_naming.py" ".\tiktok-growth-operator.skill\scripts\push_report_to_feishu_doc.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_skill_docs.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\push_scene_reports_to_feishu_doc.py" --confirmed --app-id ... --app-secret ... --title-prefix "中文成品确认集-v7"`
- Result: passed; 7/7 real Feishu docs created successfully

### v7 Real Feishu Docs

- Scene `01`: https://pizvgz6mvgi.feishu.cn/docx/D6pud8CAXo793uxfEs0c1xO9nje
- Scene `04`: https://pizvgz6mvgi.feishu.cn/docx/VEeidiCKyoEDCHxX9BLcgKWKndc
- Scene `05`: https://pizvgz6mvgi.feishu.cn/docx/XBXDdD8pno5sW1xmqSucEwdDnfg
- Scene `08`: https://pizvgz6mvgi.feishu.cn/docx/AInldzd56ohkLOxIsoJcUZodnVe
- Scene `17`: https://pizvgz6mvgi.feishu.cn/docx/IosqdKUIgoUPJrxWjeicWYLjnFc
- Scene `18`: https://pizvgz6mvgi.feishu.cn/docx/KbNcda8Kvo0sasxHJtScJSTRnbb
- Scene `19`: https://pizvgz6mvgi.feishu.cn/docx/TNaIdb7oGonLd7xrpB6cPkR0nuc

### Acceptance Verdict

- Passed for the current requirement of:
  - Chinese Feishu titles
  - Chinese operator-facing sections
  - Chinese table headers and action areas
  - product-grade direct delivery surface for the currently confirmed scenes
- Remaining English is now primarily source evidence:
  - TikTok captions
  - usernames
  - raw comments
  - URLs
  - file names
- If a later pass is needed, the next highest-value improvement is not more generic translation; it is scene-specific richer layout and stronger card-like doc composition for the Feishu body.

## 2026-05-09 Scene 04 05 Production-Spec Upgrade

- Decision: push Scene `04` and Scene `05` further from analysis-only output into production-spec handoff output.
- Why: the current breakdowns were already useful as study notes, but the next parity gain is making them directly usable by editors, prompt operators, or generation backends without another rewrite pass.

### Updated

- `tiktok-growth-operator.skill/scripts/scene_report_presets.py`
- `tiktok-growth-operator.skill/references/scene-report-contract.md`
- `tiktok-growth-operator.skill/scripts/validate_scene_presets.py`

### Added / Changed Behavior

- Scene `04` now carries stronger production-spec structure:
  - timeline rows now include `Asset / Talent Needed`
  - new `Mechanism Breakdown` table replaces purely narrative-only mechanism notes
  - `BGM And Sensory Layer` now includes strategic role plus evidence ref support
  - new `Production-Spec Handoff` table turns the teardown into a replication shot order
  - next-action paths now include explicit asset need and primary risk
- Scene `05` now carries stronger generator and editor handoff structure:
  - inferred-original schema now includes `Generator Handoff`
  - core mechanism now records `Asset Dependency`
  - generator-ready brief rows now include `Generator Handoff Field`
  - shot-level breakdown now includes `Generator Handoff`
  - product-adapted brief now includes `Asset / Talent Dependency`
  - new `Production-Spec Handoff` section summarizes what is ready for generator/editor handoff versus what is still blocked
- Contract documentation now explicitly describes these stronger Scene `04` and Scene `05` expectations so future preset changes do not drift from the intended production-spec surface.

### Validation

- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\scene_report_presets.py" ".\tiktok-growth-operator.skill\scripts\generate_scene_report.py" ".\tiktok-growth-operator.skill\scripts\render_scene_report.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_scene_presets.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\generate_scene_report.py" --scene 04 --project "Scene04 Production Spec Smoke" --output ".\.codex-tmp\scene04-prod-spec-smoke.json" --format json`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\generate_scene_report.py" --scene 05 --project "Scene05 Production Spec Smoke" --output ".\.codex-tmp\scene05-prod-spec-smoke.json" --format json`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\render_scene_report.py" --input ".\.codex-tmp\scene04-prod-spec-smoke.json" --output-dir ".\.codex-tmp\scene04-prod-spec-render" --formats md,xlsx`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\render_scene_report.py" --input ".\.codex-tmp\scene05-prod-spec-smoke.json" --output-dir ".\.codex-tmp\scene05-prod-spec-render" --formats md,xlsx`
- Result: passed

## 2026-05-09 Scene 08 Comment Cleaning And Reply-Chain Synthesis

- Decision: upgrade Scene `08` comment intake from a flat sampled-comment list into a cleaner, duplicate-collapsed, reply-aware synthesis layer, then surface the strongest comment-side signal into Scenes `18` and `19`.
- Why: the next quality bottleneck was not scene scaffolding but noisy comment evidence. Real TikTok comment captures contain emoji-only rows, repeated viral-thread reactions, and shallow engagement bait that flatten persona and operator outputs unless cleaned first.

### Updated

- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`

### Added / Changed Behavior

- comment intake now reads both:
  - `comments_sampled.json`
  - `comments.json`
- duplicate comments are now collapsed by canonicalized text instead of naively keeping the first visible row only
- cleaned entries now preserve:
  - strongest raw quote text
  - duplicate count
  - source product list
  - comment language list
  - sample kind list
  - reply pressure
- reply-chain synthesis is stronger:
  - high reply volume now promotes a stronger objection / trust cue
  - cluster-level reply pressure is accumulated instead of shown as one-off comment text only
- Scene `08` now outputs a more stable structure on real runtime data:
  - source-product summary rows
  - quote-level clustered evidence with repeated-mention counts
  - price-band difference rows generated from cleaned evidence
  - recommendations that adapt when complaint or purchase clusters are genuinely weak instead of fabricating them
- Scenes `18` and `19` now surface the strongest available comment-side cue when the capture root includes comments, so weekly and retro reports are less blind to trust / objection pressure.

### Validation

- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_scene_presets.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_skill_docs.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py" --scene 08 --capture-root ".\tiktok-growth-operator.skill\testdata\validation\tikmatrix\comments-live-mrorangecat-paged\7624057229930450192" --project "Scene08 Comment Cleaning Real Check" --output ".\.codex-tmp\scene08-comment-cleaning-check.json"`
- Result: passed; real Scene `08` import now produces duplicate-collapsed quotes, reply-pressure-aware clusters, and non-fabricated weak-signal recommendations on an entertainment-heavy comment set
- Ran: `python ".\tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py" --scene 18 --capture-root ".\tiktok-growth-operator.skill\testdata\validation\captures\tiktok-download-validated-20260423" --project "Scene18 Comment Signal Check" --output ".\.codex-tmp\scene18-comment-signal-check.json"`
- Result: passed; Scene `18` now surfaces comment-side trust / objection cues in the weekly-shift layer
- Ran: `python ".\tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py" --scene 19 --capture-root ".\tiktok-growth-operator.skill\testdata\validation\captures\tiktok-download-validated-20260423" --project "Scene19 Comment Signal Check" --output ".\.codex-tmp\scene19-comment-signal-check.json"`
- Result: passed; Scene `19` now carries comment-side friction / trust context into the retro surface

### Remaining Follow-Up

- carry the richer Scene `08` comment signal fields more explicitly into DOCX/XLSX rich export layouts
- when a future fixture contains multiple real source products, revalidate the source-product summary and price-band rows on a more category-complete pack

## 2026-05-09 Scene 08 18 19 Rich Export Layout Pass

- Decision: push the new comment/reply synthesis through the rich export layer instead of stopping at JSON quality only.
- Why: the user requirement is not just correct scene JSON. The DOCX/XLSX deliverables must also feel usable and readable, especially for Scene `08`, `18`, and `19`.

### Updated

- `tiktok-growth-operator.skill/scripts/render_scene_report.py`

### Added / Changed Behavior

- added scene-and-section-specific DOCX width presets for:
  - Scene `08`
    - `High-Level Judgment`
    - `Evidence Clusters`
    - `Recommended Action`
    - `Open Questions`
  - Scene `18`
    - `Objects To Track`
    - `Why They Matter`
    - `Fields To Capture Next Time`
    - `Next Action`
  - Scene `19`
    - `High-Level Judgment`
    - `Evidence Clusters`
    - `Recommended Action`
    - `Open Questions`
- added matching XLSX preferred column widths, per-column max widths, and row-wrap heuristics for those same sections
- result:
  - long quote and implication columns now receive more width
  - narrow label columns no longer waste as much space
  - weekly/retro tables read less like evenly split raw exports and more like operator-ready boards

### Validation

- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\render_scene_report.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\render_scene_report.py" --input ".\.codex-tmp\scene08-comment-cleaning-check.json" --output-dir ".\.codex-tmp\scene08-comment-cleaning-render" --formats md,docx,xlsx`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\render_scene_report.py" --input ".\.codex-tmp\scene18-comment-signal-check.json" --output-dir ".\.codex-tmp\scene18-comment-signal-render" --formats md,docx,xlsx`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\render_scene_report.py" --input ".\.codex-tmp\scene19-comment-signal-check.json" --output-dir ".\.codex-tmp\scene19-comment-signal-render" --formats md,docx,xlsx`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_export_outputs.py" --output-root ".\.codex-tmp\validate-export-post-comment-pass"`
- Result: passed

### Manual Acceptance Check

- Checked representative rendered outputs:
  - `scene08-comment-cleaning-render`
  - `scene18-comment-signal-render`
  - `scene19-comment-signal-render`
- Result:
  - no visible mojibake found in Markdown, DOCX, or XLSX
  - no visible absolute local path leakage found in rendered surfaces
  - column allocation is improved and materially more readable for quote-heavy and implication-heavy tables
- Still not final-perfect:
  - top-level DOCX framing is still generic English-first in some headings such as `Executive Snapshot` / `Working Context`
  - Scene `08` still needs a stronger multi-product fixture before the product-summary and price-band table can be judged as platform-grade
- DOCX body composition is more readable now, but still not yet at the richest “project card / premium report” level


## 2026-05-09 Markdown Chinese Surface Pass And Export Spot Check

- Decision: keep Markdown localization in the export layer instead of rewriting the scene preset contract.
- Why: the remaining user-facing quality gap had shifted from scene logic to delivery surface. The package already localized DOCX/XLSX headings, but Markdown still leaked too much English template scaffolding.
- Decision: expand the shared export-time header mapping instead of adding scene-specific one-off post-processors.
- Why: Scene 04/05/08/17 exposed the same pattern family: English metadata labels, execution-template labels, reusable-table headers, and a few common placeholder sentences.

### Updated

- `tiktok-growth-operator.skill/scripts/render_scene_report.py`

### Added / Changed Behavior

- Markdown export now goes through a dedicated localized render wrapper instead of writing the raw `render_markdown_from_payload(...)` output directly.
- The wrapper now localizes:
  - metadata lines such as scene / project / deliverable type / generated time / status / scenario file
  - execution-summary labels such as conclusion / why it matters / next action / confidence
  - direct-use template labels such as recommended request / runner args / variable inputs / output checklist
  - common placeholder lines such as `_Fill this field._`, `_Optional._`, and the generic context scaffold sentence
- Common table-header localization was expanded for real high-value scene surfaces, including:
  - Scene 04 production-spec tables
  - Scene 05 brief / generator handoff tables
  - Scene 08 multi-product comment-mining tables
  - Scene 17 creator-formula extraction tables
- XLSX historical mojibake leftovers in the simple evidence / assets / notes / sources tabs were cleaned to stable Chinese labels.
- DOCX section-overview table no longer leaks `Yes / No`; it now uses Chinese structured-status phrasing.

### Validation

- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\render_scene_report.py"`
- Result: passed
- Ran: rich rerender for:
  - `scene04-prod-spec-smoke.json` -> `scene04-card-pass-render-v4`
  - `scene05-prod-spec-smoke.json` -> `scene05-card-pass-render-v4`
  - `scene08-multi-product-check.json` -> `scene08-multi-product-render-v4`
  - `scene17-card-pass.json` -> `scene17-card-pass-render-v4`
- Result: passed; renderer returned Markdown / DOCX / XLSX paths for all four scenes
- Ran: focused English-residue scan for common template leakage such as:
  - `Recommended Request`
  - `Deliverable Type`
  - `Operator Checklist`
  - `Common Failure Modes`
  - `Source Product`
  - `Cluster Type`
  - `Mechanism Layer`
  - `Observed Pattern`
  - `Reusable?`
  - `Decision Area`
  - `Price Band`
  - `Scene Type`
  - `What Must Happen`
  - `Confidence`
- Result: the targeted residue set dropped to zero on the rerendered outputs

### Manual Acceptance Check

- Spot-checked rerendered Scene 04 and Scene 08 Markdown outputs after the localization pass.
- Result:
  - section titles are now Chinese
  - template labels and many reusable headers are now Chinese
  - raw source evidence remains in source language where appropriate
- Remaining gap:
  - some preset-authored body copy and fixture-specific content can still remain English if it is not part of the shared export mapping or if it is source evidence
  - next highest-value pass is now DOCX visual composition and richer scene-specific body-card layout, not another broad generic heading translation pass

## 2026-05-09 Scene Surface Localization, Multi-Product Scene 08 Fixture, And DOCX Card Pass

- Decision: localize scene section display names at export time instead of rewriting the underlying scene payload contract.
- Why: this preserves workflow compatibility while making DOCX/XLSX outputs feel more like a Chinese operator platform deliverable.
- Decision: add one stronger Scene `08` multi-product fixture under durable validation testdata.
- Why: the prior real comment pack validated cleaning and reply-chain synthesis well, but was too single-thread and entertainment-heavy to judge category-level comment mining quality.
- Decision: push the DOCX surface one step further toward a platform-report feel with overview cards and section cards.
- Why: the previous exporter was already clean, but still felt too much like a local document dump instead of a structured project/report artifact.

### Updated

- `tiktok-growth-operator.skill/scripts/render_scene_report.py`
- `tiktok-growth-operator.skill/scripts/validate_export_outputs.py`

### Added

- `tiktok-growth-operator.skill/testdata/validation/captures/scene08-multi-product-comments/comments_sampled.json`
- `tiktok-growth-operator.skill/testdata/validation/captures/scene08-multi-product-comments/README.md`

### Added / Changed Behavior

- more residual section names now localize in DOCX/XLSX export, including:
  - `Structure`
  - `Production-Spec Handoff`
  - `Execution Handoff`
  - `BGM And Sensory Layer`
  - `Visual And Distribution Signature`
  - `Core Invariant`
  - `Variable Matrix`
  - `What To Learn`
  - `Expected Effect`
  - `Fallback Mode`
- section sheet names in XLSX now localize as well, not only the workbook top-level tabs
- Scene `08` now has a stronger category-style multi-product validation fixture that exercises:
  - source-product summary
  - merged cluster synthesis
  - complaint / trust / control-language interpretation
- DOCX output now includes:
  - a top overview card on the cover page
  - a clearer section-overview intro
  - a small section card at the top of each chapter

### Validation

- Ran: `python -m py_compile` on:
  - `tiktok-growth-operator.skill/scripts/render_scene_report.py`
  - `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`
  - `tiktok-growth-operator.skill/scripts/validate_export_outputs.py`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py" --scene 08 --capture-root ".\tiktok-growth-operator.skill\testdata\validation\captures\scene08-multi-product-comments" --project "Scene08 Multi Product Comment Check" --output ".\.codex-tmp\scene08-multi-product-check.json"`
- Result: passed
- Ran: rich rerender for:
  - `scene08-multi-product-check.json`
  - `scene08-comment-cleaning-check.json`
  - `scene18-comment-signal-check.json`
  - `scene19-comment-signal-check.json`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_export_outputs.py" --output-root ".\.codex-tmp\validate-export-chinese-surface-v3"`
- Result: passed

## 2026-05-09 DOCX Project-Card Pass, Commerce Scene 08 Fixture, And Export QA Checklist

- Decision: keep pushing the rich export layer from “clean local report” toward “platform project card” without rewriting scene preset contracts.
- Why: the current parity gap has moved from workflow coverage into delivery surface quality, especially DOCX chapter feel and category-level Scene `08` comment realism.
- Decision: replace the old Scene `08` multi-product validation pack with a purchase-oriented commerce-language replay fixture.
- Why: the previous fixture was too announcement / platform-reaction heavy to properly judge category-level comment mining quality.

### Updated

- `tiktok-growth-operator.skill/scripts/render_scene_report.py`

### Added

- `tiktok-growth-operator.skill/references/scene-export-qa-checklist.md`
- `tiktok-growth-operator.skill/testdata/validation/captures/scene08-multi-product-comments/README.md`
- `tiktok-growth-operator.skill/testdata/validation/captures/scene08-multi-product-comments/comments_sampled.json`

### Added / Changed Behavior

- export-time shared template localization now also flows through payload normalization for:
  - `working_context`
  - `executive_summary`
  - `operator_guide`
  - execution-template fields
  - section instructions / paragraphs / bullets / numbered text
- DOCX cover now includes stronger project-card metrics beyond the badge row:
  - structured chapter count
  - evidence chapter count
  - asset / evidence / notes totals
  - execution-template presence
- chapter entry cards now also expose:
  - paragraph / bullet / numbered counts
  - evidence-ref count
  - table row count
- chapter rendering now page-breaks between sections for a stronger “chapter card” feel.
- Scene `08` validation fixture is now purchase-oriented around:
  - shade / fit questions
  - shipping / packaging problems
  - value / price framing
  - repurchase intent
  - before / after proof language
  - refund / damage / trust pressure

### Validation

- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\render_scene_report.py" ".\tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py"`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py" --scene 08 --capture-root ".\tiktok-growth-operator.skill\testdata\validation\captures\scene08-multi-product-comments" --project "Scene08 Commerce Comment Check" --output ".\.codex-tmp\scene08-commerce-comment-check.json"`
- Result: passed
- Ran: rich rerender for:
  - `scene-01-spotcheck-scene-01-rich.json` -> `.codex-tmp\scene01-card-pass-v5`
  - `scene-04-spotcheck-scene-04-capture-rich.json` -> `.codex-tmp\scene04-card-pass-v5`
  - `scene-05-validation-scene05-capture.json` -> `.codex-tmp\scene05-card-pass-v5`
  - `scene08-commerce-comment-check.json` -> `.codex-tmp\scene08-card-pass-v5`
  - `scene-17-spotcheck-scene-17-rich.json` -> `.codex-tmp\scene17-card-pass-v5`
  - `scene-18-feishu-batch-smoke-glowofficial-account-weekly.json` -> `.codex-tmp\scene18-card-pass-v5`
  - `scene-19-feishu-batch-smoke-glowofficial-account-retro.json` -> `.codex-tmp\scene19-card-pass-v5`
- Result: passed; Markdown / DOCX / XLSX files were emitted for all seven spot-check scenes.

### Manual Acceptance Check

- Added a durable QA checklist at:
  - `tiktok-growth-operator.skill/references/scene-export-qa-checklist.md`
- Real spot-check batch prepared for:
  - `01 / 04 / 05 / 08 / 17 / 18 / 19`
- Current acceptance result:
  - DOCX / XLSX rich outputs exist for all seven priority scenes
  - Scene `08` fixture is now meaningfully more purchase-oriented than the prior platform-reaction pack
  - DOCX chapter structure is materially closer to a platform project-card report
- Remaining known gap:
  - Markdown still has a small residue path for some scene-authored runtime strings in Scene `08` and a few direct-use-template lines; the rich exports were the primary priority in this pass, but Markdown residue cleanup still remains as a follow-up if full surface parity is required

## 2026-05-09 Export Surface Localization Closure And V6 Acceptance

- Decision: close the remaining rich-export parity gap by fixing durable template sources and validator expectations instead of patching generated outputs.
- Why: the remaining issues had shifted from workflow coverage into export-surface consistency, especially Scene `04 / 05 / 17` preset wording, workbook header localization, and validator drift.

### Updated

- `tiktok-growth-operator.skill/scripts/scene_report_presets.py`
- `tiktok-growth-operator.skill/scripts/render_scene_report.py`
- `tiktok-growth-operator.skill/scripts/validate_export_outputs.py`

### Added / Changed Behavior

- Scene `04 / 05 / 17` preset-level operator request, checklist, and failure-mode text is now Chinese-first at the durable template layer.
- Scene `08` purchase-comment workflow guidance is now Chinese-first in the durable operator guide layer.
- Shared export localization now additionally covers more generator / handoff / formula / shot-level labels so DOCX and XLSX surfaces no longer depend on raw English preset wording.
- Workbook validator now accepts localized exported headers instead of assuming source-language headers only.
- Rich export surface for the current priority set was rerendered again after the durable template updates:
  - `01`
  - `04`
  - `05`
  - `08`
  - `17`
  - `18`
  - `19`

### Validation

- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\scene_report_presets.py" ".\tiktok-growth-operator.skill\scripts\render_scene_report.py" ".\tiktok-growth-operator.skill\scripts\validate_export_outputs.py"`
- Result: passed
- Ran: real rerender batch into:
  - `.codex-tmp\scene01-card-pass-v6`
  - `.codex-tmp\scene04-card-pass-v6`
  - `.codex-tmp\scene05-card-pass-v6`
  - `.codex-tmp\scene08-card-pass-v6`
  - `.codex-tmp\scene17-card-pass-v6`
  - `.codex-tmp\scene18-card-pass-v6`
  - `.codex-tmp\scene19-card-pass-v6`
- Result: passed
- Ran: `python ".\tiktok-growth-operator.skill\scripts\validate_export_outputs.py" --output-root ".\.codex-tmp\validate-export-v6"`
- Result: passed

### Current Acceptance Result

- DOCX / XLSX export validator is green again after header-localization alignment.
- Scene `04 / 17 / 18 / 19` rich outputs are now clean on the checked product-surface strings and did not show mojibake or local absolute-path leakage.
- Scene `05` durable template wording has been pushed much closer to full Chinese operator surface while preserving generator-facing terms like `Brief`, `hook`, and `CTA` where they still read naturally for the target operator.
- Scene `08` commerce-comment fixture remains purchase-oriented and suitable for category-level comment-mining spot checks.

### Remaining Light Risk

- Some raw source evidence in Scene `08` still naturally contains English question marks or original-language buyer phrasing; this is expected evidence retention, not product-surface leakage.
- If stricter full-Chinese surface is required later, the next pass should focus on scene-authored evidence-adjacent strings and a few scenario-file metadata displays, not on the exporter core.

## 2026-05-09 Metadata And Legacy-JSON Surface Cleanup

- Decision: continue the export-surface cleanup by translating legacy input JSON display strings at render time instead of forcing every historical fixture to be regenerated first.
- Why: a small amount of remaining English was coming from older scene JSON payloads, not from the current durable preset source.

### Updated

- `tiktok-growth-operator.skill/scripts/render_scene_report.py`
- `tiktok-growth-operator.skill/scripts/scene_report_presets.py`

### Added / Changed Behavior

- Added more shared display replacements for legacy Scene `05` requested-output strings so older input JSON files render a Chinese-first surface without mutating the evidence payloads.
- Added more header-level localization coverage for generic fields such as:
  - `Field`
  - `Fields`
  - `Why It Matters`
- Confirmed Scene `18` surface no longer leaves those generic English headers visible in rich exports.

### Validation

- Ran: rerender of Scene `05` into `.codex-tmp\scene05-card-pass-v9`
- Result: passed
- Ran: rerender of Scene `18` into `.codex-tmp\scene18-card-pass-v7`
- Result: passed

### Current Acceptance Result

- Scene `18` product-surface English header residue was cleared.
- Scene `05` legacy requested-output residue from older JSON inputs is now suppressed at render time.
- Remaining visible English is now largely intentional operator-domain vocabulary such as `Brief`, `hook`, or preserved source evidence, not uncontrolled platform-surface leakage.

## 2026-05-09 High-Value Scene Surface Cleanup Pass

- Decision: stop optimizing around tiny isolated labels and instead target the high-value scene surface where older imported JSON still leaked English checklist, summary, and constraint sentences.
- Why: the remaining readability gap was no longer in table headers alone; it had shifted into imported `working_context`, `executive_summary`, and `operator_guide` strings on real scene outputs.

### Updated

- `tiktok-growth-operator.skill/scripts/render_scene_report.py`

### Added / Changed Behavior

- Added a larger compatibility localization layer for older imported scene JSON strings commonly seen in:
  - `working_context.minimum_evidence`
  - `working_context.ideal_evidence`
  - `working_context.constraints`
  - `working_context.requested_outputs`
  - `working_context.ready_checklist`
  - `executive_summary`
  - `operator_guide`
- Explicitly removed the overly aggressive short-token replacements that had started to corrupt words like `screenshots`.
- Re-ran high-value surface spot checks for:
  - `01`
  - `04`
  - `08`
  - `17`
  - `18`
  - `19`

### Validation

- Ran: `python -m py_compile ".\tiktok-growth-operator.skill\scripts\render_scene_report.py"`
- Result: passed
- Ran: rich rerender batch into:
  - `.codex-tmp\scene01-card-pass-v11`
  - `.codex-tmp\scene04-card-pass-v11`
  - `.codex-tmp\scene08-card-pass-v11`
  - `.codex-tmp\scene17-card-pass-v11`
  - `.codex-tmp\scene18-card-pass-v11`
  - `.codex-tmp\scene19-card-pass-v11`
- Result: passed

### Current Acceptance Result

- The strongest leftover English summaries, checklist items, and constraint lines on the checked real scenes were reduced again.
- Product-surface readability is now materially better across the imported real-scene outputs without mutating evidence payloads.
- Remaining English is now mostly one of:
  - real file names such as `summary.json`
  - real source evidence strings
  - intentional operator-domain terms such as `TikTok`, `Brief`, `hook`, `ROI`


## 2026-05-09 Runtime Logic Recovery And Preset Repair

- Decision: repair the durable preset source instead of working around broken exported artifacts.
- Why: `scene_report_presets.py` had legacy mojibake string corruption severe enough to break Python parsing, which blocked all downstream validation and rerender work.
- Decision: keep the current P1/P2 runtime improvements in source scripts and only repair the preset / operator-guide layer needed to restore execution.
- Why: this preserves the already-improved Scene 01 / 02 / 03 / 04 / 08 / 18 / 19 logic while unblocking validation.

### Updated

- `tiktok-growth-operator.skill/scripts/scene_report_presets.py`
- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`
- `tiktok-growth-operator.skill/scripts/run_scene02_patrol.py`

### Added / Changed Behavior

- repaired Scene `04 / 05 / 17` execution-template request, prompt-line, and checklist text to stable Chinese-first operator wording
- repaired `SCENE_INTAKE` entries for Scene `04 / 05 / 09 / 10 / 13 / 17 / 19`
- repaired high-value `SCENE_OPERATOR_GUIDE` blocks for Scene `01 / 04 / 05 / 08 / 17` so operator-facing guidance is readable again and no longer breaks parsing
- preserved this round's runtime enhancements already landed in capture-pack import and patrol logic:
  - Scene `01` shortlist reasoning / reuse-purpose / next-scene surfacing
  - Scene `02` append-to-same-board patrol semantics
  - Scene `03` explicit shortlist-rule and deeper script / timeline carry-through
  - Scene `04` stronger timeline labels and no-voiceover support line
  - Scene `08` stronger commerce comment theme detection
  - Scene `18 / 19` latest-two-weeks comparison helpers and weekly shift summaries

### Validation

- Ran: `python -m py_compile` on:
  - `tiktok-growth-operator.skill/scripts/scene_report_presets.py`
  - `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`
  - `tiktok-growth-operator.skill/scripts/run_scene02_patrol.py`
- Result: passed
- Ran: `python tiktok-growth-operator.skill/scripts/validate_scene_presets.py`
- Result: passed with `ok: true`, `errors: []`, `warnings: []`
- Ran: `python .\tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py --scene 08 --capture-root .\tiktok-growth-operator.skill\testdata\validation\captures\scene08-multi-product-comments --project "Scene08 Commerce Comment Check 20260509" --output .\.codex-tmp\scene08-commerce-comment-check-20260509.json`
- Result: passed
- Ran: rich rerender for:
  - Scene `01` -> `.codex-tmp\scene01-card-pass-20260509`
  - Scene `08` -> `.codex-tmp\scene08-card-pass-20260509`
  - Scene `17` -> `.codex-tmp\scene17-card-pass-20260509`
  - Scene `18` -> `.codex-tmp\scene18-card-pass-20260509`
- Result: passed and emitted Markdown / DOCX / XLSX outputs

### Current Acceptance Result

- The durable preset layer compiles again.
- Scene preset validation is green again.
- Real Scene `08` capture import and representative Scene `01 / 08 / 17 / 18` rich exports are runnable again after the preset repair.
- This round restored the validation path without touching `E:	iktok\TikMatrix` or hand-patching generated artifacts.

### Remaining Follow-up

- `validate_export_outputs.py` still contains older localized-string residue and fixture-path fragility; it should be cleaned as a separate validator-hardening pass.
- More operator-guide / metadata Chinese-surface cleanup can still be done for lower-priority scenes, but the current blocker is removed.


## 2026-05-09 Export Validator Recovery And Scene 08 Residue Check

- Decision: treat the latest Scene `08` residue report as a validator/probe issue first, not as proof of export corruption.
- Why: the quick scan was incorrectly treating normal `?` punctuation inside preserved user-language evidence as mojibake.
- Decision: re-point `validate_export_outputs.py` at current real fixtures instead of keeping one broken legacy Scene `18` temp path.
- Why: the validator had become partially stale even though the renderer and real outputs were healthy.

### Updated

- `tiktok-growth-operator.skill/scripts/validate_export_outputs.py`

### Added / Changed Behavior

- Scene `08` real export check now prefers the current runtime JSON fixture:
  - `.codex-tmp\scene08-commerce-comment-check-20260509.json`
- Scene `18` real export check now uses the current stable real report fixture:
  - `.codex-tmp\spotcheck-scene18-rich\operator-run\scene-18\scene-18-spotcheck-scene18-rich.json`
- confirmed the latest Scene `08` Markdown did not contain actual mojibake tokens; the remaining visible `?` characters were ordinary punctuation inside preserved comment evidence

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill/scripts/validate_export_outputs.py"`
- Result: passed
- Ran: `python .\tiktok-growth-operator.skill\scripts\validate_export_outputs.py --output-root .\.codex-tmp\validate-export-20260509-runtime-fix`
- Result: passed with `status: ok`
- Covered fixtures in that validation run:
  - scene `02`
  - scene `03`
  - scene `08`
  - scene `15`
  - scene `17`
  - scene `18`
  - synthetic duplicate-heading / sparse-section / execution-template / wide-table checks

### Current Acceptance Result

- export validator is runnable again and green
- Scene `08` latest rich export is acceptable; no real mojibake was found in the checked Markdown surface
- the validation chain is back to durable-script state instead of depending on a broken legacy temp path

### Remaining Follow-up

- `validate_export_outputs.py` still carries a few old detection literals and mixed-language synthetic strings, but they no longer block execution
- next highest-value work remains broader scene parity and product-surface polish, not validator triage


## 2026-05-09 P1 Scene Runtime Quality Pass

- Decision: prioritize runtime-output upgrades that improve real operator deliverables immediately instead of only polishing docs or preset wording.
- Why: the largest remaining gap for Scene `01 / 02 / 03 / 04 / 18 / 19` is now report quality and handoff quality, not raw syntax stability.

### Updated

- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`

### Added / Changed Behavior

- Scene `02`
  - added a change-first patrol digest layer so `Why They Matter` prioritizes:
    - ????
    - ????
    - ????
    - ?? hook
  - preserved tracked sample rows, but demoted them out of the main operator table into dispatch bullets / notes
- Scene `03`
  - replaced the placeholder-style reusable-formula rows with evidence-ready rows that match the target table width
  - filled the risk table instead of leaving only bullets
  - filled the next-action handoff table with concrete teardown rows and owners
- Scene `04`
  - added real `Production-Spec Handoff` rows so the scene now exports an actual beat-level handoff instead of leaving the chapter scaffold empty
- Scene `19`
  - replaced the flat per-post evidence-cluster list with actual content-mode clustering rows so the retro reads more like grouped operating insight than ranked inventory

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py"`
- Result: passed
- Ran: rich rerender for:
  - Scene `01` -> `.codex-tmp\scene01-card-pass-20260509-v2`
  - Scene `03` -> `.codex-tmp\scene03-card-pass-20260509-v2`
  - Scene `18` -> `.codex-tmp\scene18-card-pass-20260509-v2`
- Result: passed
- Ran: `python .\tiktok-growth-operator.skill\scripts\validate_export_outputs.py --output-root .\.codex-tmp\validate-export-20260509-post-p1-pass`
- Result: passed with `status: ok`

### Current Acceptance Result

- the exporter and validator stayed green after the runtime-quality changes
- Scene `03` now has filled handoff / risk structures instead of partially empty creation-ready sections
- Scene `04` now exports a real production-spec beat handoff
- Scene `19` now groups by content mode instead of reading like a raw ranked-post list
- Scene `02` patrol output is more change-first and closer to daily operator digest behavior

### Remaining Follow-up

- Scene `01` still deserves a stronger board-first configuration surface in the main table, not only in working-context inputs
- Scene `18` and `19` still have room for richer multi-week dispatch logic when more true weekly slices are available
- Scene `04` can still be pushed closer to the lipstick teardown artifact with denser visual-scene / spoken-line reconstruction when richer evidence exists


## 2026-05-09 Scene 01 Board-First Config Pass And Scene 18/19 Weekly Dispatch Upgrade

- Decision: raise Scene `01` patrol configuration into the main candidate board instead of hiding it only in `working_context`.
- Why: the parity gap had shifted from raw collection into board usability; operators need to see market, cadence, queries, threshold, shortlist size, and shop-only intent directly in the exported main table.
- Decision: rewrite Scene `18 / 19` week-dispatch output toward explicit Chinese-first `本周继续追 / 本周值得借鉴 / 本周应忽略 / 本周多做 / 本周少做 / 本周停止 / 下轮测试` actions.
- Why: the user wants platform-style weekly operating output, not generic English recap tables.

### Updated

- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`

### Added / Changed Behavior

- Scene `01`
  - added a durable board-config snapshot layer backed by `patrol_config.json` / aggregate summary fields
  - main table now surfaces:
    - category
    - market
    - cadence
    - queries
    - topics
    - publish window
    - sort rule
    - min-like threshold
    - shortlist count
    - shop-only intent
  - executive conclusion is now Chinese-first and closer to an operator intake board instead of a generic summary
- Scene `18`
  - executive summary and weekly-dispatch language is now Chinese-first
  - next-action table now expresses week-level operator routing as:
    - `本周继续追`
    - `本周值得借鉴`
    - `本周应忽略`
- Scene `19`
  - retro summary language is now Chinese-first
  - recommended-action table now dispatches as:
    - `本周多做`
    - `本周少做`
    - `本周停止`
    - `下轮测试`
- shared runtime helper cleanup
  - localized proof / strategy / cue fallback helper text to reduce English residue in real Scene `18 / 19` outputs

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py"`
- Result: passed
- Ran: real importer reruns for:
  - Scene `01` -> `.codex-tmp/scene01-p1-20260509.json`
  - Scene `18` -> `.codex-tmp/scene18-p1-20260509.json`
  - Scene `19` -> `.codex-tmp/scene19-p1-20260509.json`
- Result: passed
- Ran: rich rerender for:
  - `.codex-tmp/scene01-p1-20260509-export`
  - `.codex-tmp/scene18-p1-20260509-export`
  - `.codex-tmp/scene19-p1-20260509-export`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py" --scene 01 --capture-root "tiktok-growth-operator.skill/tmp/20260507_validation_capture_scene02/capture-pack" --project "Scene01 Patrol Config Check" --output ".codex-tmp/scene01-config-check-20260509.json"`
- Result: passed and confirmed real patrol-config fields render into the Scene `01` main board
- Ran: `python "tiktok-growth-operator.skill/scripts/validate_export_outputs.py" --output-root ".codex-tmp/validate-export-20260509-scene01-18-19-p1"`
- Result: passed with `status: ok`

### Current Acceptance Result

- Scene `01` now exposes board-first configuration fields in the exported main table instead of hiding them only in context metadata.
- Scene `18 / 19` now read more like real operator dispatch documents and less like generic English analytics notes.
- Export validation stayed green after the runtime changes.

### Remaining Follow-up

- Scene `01` still cannot always surface a real publish-window or shop-only flag unless the capture pack actually records those fields.
- Scene `18 / 19` will become materially stronger once true multi-account, multi-week real fixtures exist instead of one-account sparse packs.
- Scene `04` remains the next best candidate for another parity push against the lipstick teardown report.


## 2026-05-09 Scene 04 Timeline / Mechanism Upgrade And Qualified-Video Loader Fix

- Decision: push Scene `04` closer to the lipstick-style teardown artifact by strengthening the runtime timeline and mechanism tables instead of only polishing exporter visuals.
- Why: the next parity gap for Scene `04` was not syntax or rendering, but the structure of the actual single-video breakdown.
- Decision: normalize single-record `aggregate_qualified_videos.json` files into a one-item list at load time.
- Why: one real validation capture stored the qualified payload as a dict, which caused Scene `04` and other reference-driven scenes to silently lose their strongest source reference.

### Updated

- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`

### Added / Changed Behavior

- loader fix
  - `load_pack_files(...)` now converts dict-shaped `aggregate_qualified_videos.json` into a one-item qualified list
  - this stabilizes reference selection for Scene `04 / 05 / 09 / 10 / 11 / 12 / 13 / 14 / 15 / 16`
- Scene `04`
  - added a dedicated `scene04_structure_rows(...)` helper
  - timeline table is now explicitly shaped as:
    - time range
    - scene type
    - visual content
    - spoken / on-screen script
    - role in conversion
    - evidence ref
  - added a dedicated `scene04_mechanism_rows(...)` helper
  - mechanism table now explicitly covers:
    - video type
    - attention tension
    - proof device
    - no-voiceover fallback
  - rewrote Scene `04` executive summary, bullets, reusable formula, risk notes, and next action into a Chinese-first operator surface
  - kept the output evidence-grounded instead of fabricating transcript detail that does not exist in the capture pack

### Validation

- Ran: `python -m py_compile "tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py"`
- Result: passed
- Ran: real Scene `04` importer rerun against:
  - `tiktok-growth-operator.skill/testdata/validation/captures/tiktok-analysis-pack-smoke-20260423f`
  - output: `.codex-tmp/scene04-p1-20260509.json`
- Result: passed
- Ran: rich rerender for:
  - `.codex-tmp/scene04-p1-20260509-export`
- Result: passed
- Ran: `python "tiktok-growth-operator.skill/scripts/validate_export_outputs.py" --output-root ".codex-tmp/validate-export-20260509-scene04-pass"`
- Result: passed with `status: ok`

### Current Acceptance Result

- Scene `04` now exports a much more platform-like single-video teardown with explicit timeline and mechanism tables.
- The real validation capture now correctly uses its qualified reference video instead of silently dropping it because of dict-vs-list shape drift.
- Export validation stayed green after both the runtime breakdown upgrade and the loader fix.

### Remaining Follow-up

- The current real Scene `04` fixture is still weak on transcript / subtitle / frame-level evidence, so some rows necessarily remain reconstruction-grade rather than fully granular shot notes.
- The next best Scene `04` parity upgrade is to feed it a richer real pack with downloaded video JSON, subtitle text, or OCR frames so the table can move from “structure reconstruction” to denser “shot script reconstruction.”


## 2026-05-09 Scene 18/19 Weekly Evidence Grading And Chinese Surface Cleanup

- Decision: make Scene `18 / 19` explicitly show evidence strength and sparse-fixture limits instead of pretending a one-account, low-volume pack is a full matrix-level verdict.
- Why: the real available TikTok fixture is still thin, but it is useful if the report clearly separates what is observed from what still needs another week, more accounts, or more comments.
- Decision: continue pushing Scene `18 / 19` preset, intake, operator-guide, and capture-import summary surfaces into Chinese-first wording.
- Why: rich exports were still carrying template-layer English in several high-visibility places even after the prior runtime pass.

### Updated

- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`
- `tiktok-growth-operator.skill/scripts/scene_report_presets.py`
- `tiktok-growth-operator.skill/scripts/validate_scene_presets.py`

### Added / Changed Behavior

- Scene `18 / 19`
  - added weekly evidence coverage summaries:
    - account count
    - natural-week count
    - post count
    - cleaned comment count
    - download success count
  - added explicit evidence grades:
    - `可直接周对比`
    - `可做轻周对比`
    - `仅基线周`
    - `样本不足`
  - made single-account / sparse-comment / baseline-only limits explicit in executive summaries and action logic
  - strengthened weekly action rows so they stay action-oriented without over-claiming trend certainty
- Chinese-surface cleanup
  - localized Scene `18 / 19` preset intake inputs, requested outputs, evidence labels, section descriptions, blank-table headers, operator checklist lines, and common failure modes
  - localized capture-pack import summary lead lines such as source profile and board-size summary
  - localized reply-chain synthesis strings such as `Reply chain active` into Chinese operator wording
  - synchronized preset validator header expectations with the newer Chinese-first Scene `18 / 19` tables

### Validation

- Ran: `python -m py_compile` on:
  - `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`
  - `tiktok-growth-operator.skill/scripts/scene_report_presets.py`
  - `tiktok-growth-operator.skill/scripts/validate_scene_presets.py`
- Result: passed
- Ran: `python tiktok-growth-operator.skill/scripts/validate_scene_presets.py`
- Result: passed with `ok: true`, `errors: []`, `warnings: []`
- Ran: real importer reruns for:
  - Scene `18` -> `.codex-tmp/scene18-weekly-evidence-20260509-v3.json`
  - Scene `19` -> `.codex-tmp/scene19-weekly-evidence-20260509-v3.json`
- Result: passed
- Ran: rich rerender for:
  - `.codex-tmp/scene18-weekly-evidence-20260509-v3-export`
  - `.codex-tmp/scene19-weekly-evidence-20260509-v3-export`
- Result: passed
- Ran: markdown spot checks for:
  - evidence-grade lines
  - Scene `18` Chinese table headers and operator checklist
  - Scene `19` Chinese table headers and `下轮测试计划`
- Result: passed

### Current Acceptance Result

- Scene `18 / 19` now state evidence strength directly instead of implying full matrix confidence from a sparse pack.
- The high-visibility preset and runtime surfaces for Scene `18 / 19` are more consistently Chinese-first.
- Real v3 exports preserve the stronger weekly-action framing while exposing the real limits of the current fixture.

### Remaining Follow-up

- The best next upgrade for Scene `18 / 19` is still a stronger real fixture:
  - more than one account
  - more than two weekly slices
  - broader comment capture
  - richer cover / first-frame evidence
- Some preserved evidence rows still naturally contain English because they reflect original-source text, not template leakage.


## 2026-05-09 Scene 04/05/17 Chinese Surface And Export Cleanup

- Decision: prioritize Scene `04 / 05 / 17` user-facing wording in both runtime fill logic and rich-export localization instead of only patching generated artifacts.
- Why: the remaining parity gap was no longer workflow structure; it was mixed Chinese/English report surface leaking through markdown, DOCX, and XLSX outputs.
- Decision: use real existing JSON fixtures for rerender passes instead of synthetic smoke payloads.
- Why: the user asked for real chain quality, so the cleanup needed to prove itself against actual imported TikTok scene payloads.

### Updated

- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`
- `tiktok-growth-operator.skill/scripts/render_scene_report.py`
- `tiktok-growth-operator.skill/scripts/scene_report_presets.py`

### Added / Changed Behavior

- Scene `04`
  - localized executive-summary carry-through when rerendering historical JSON
  - upgraded several visible runtime strings:
    - `已恢复主题 cue` -> `已恢复主题线索`
    - `Hook 逻辑` -> `钩子逻辑`
    - `Hook -> setup -> proof -> soft continuation` -> `钩子 -> 铺垫 -> 证明 -> 轻收口`
    - `Silence / pause usage` -> `留白 / 停顿使用`
  - localized risk / adaptation rows so safer vs aggressive paths read more like operator action guidance
- Scene `05`
  - localized runtime executive summary into Chinese-first wording
  - localized runtime structure / mechanism / handoff table rows:
    - `Style / Environment / Camera / Lighting / Character / Background Sound / Transition / Editing`
    - to Chinese-first dimensions in the scene fill path
  - changed export-layer labels from `Brief` wording toward `制作简报` on the high-visibility report surface
  - updated renderer to localize executive summary, working-context strings, section paragraphs, bullets, and numbered steps during markdown rerender
- Scene `17`
  - localized runtime executive summary, account overview, formula rows, and next-action grid into stronger Chinese-first wording
  - localized creator-formula carry-through strings such as:
    - `Hook formula`
    - `Trust-building`
    - `Conversion move`
    - `New hook draft`
    - `Publishing experiment`
  - localized rich-export replacement layer for creator-report phrases such as:
    - `Official-account authority`
    - `Featured-talent lift`
    - `Operator Dispatch`
    - `Watch / Suppress / Test`
- Shared export localization
  - renderer now applies template-text localization to:
    - executive summary fields
    - working-context summary and checklist lists
    - section instructions
    - section paragraphs / bullets / numbered items
  - added more phrase-level replacement coverage for real historical JSON rows, especially around:
    - `Source account baseline`
    - `Lead candidate`
    - `Qualified control`
    - `creator brief`
    - `production brief`
    - creator-formula report table labels

### Validation

- Ran: `python -m py_compile` on:
  - `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`
  - `tiktok-growth-operator.skill/scripts/render_scene_report.py`
  - `tiktok-growth-operator.skill/scripts/scene_report_presets.py`
- Result: passed
- Ran: real rich rerenders for:
  - Scene `04` -> `.codex-tmp/scene04-zh-pass-20260509-v4`
  - Scene `05` -> `.codex-tmp/scene05-zh-pass-20260509-v4`
  - Scene `17` -> `.codex-tmp/scene17-zh-pass-20260509-v4`
- Result: passed and regenerated `md/docx/xlsx`
- Ran: markdown spot checks against rerendered outputs for:
  - executive-summary language
  - section-title language
  - brief / handoff table labels
  - creator-formula table labels
- Result: improved substantially; major template leakage reduced

### Current Acceptance Result

- Scene `05` now reads much more like a Chinese-first production-brief report instead of a half-localized reverse-engineering worksheet.
- Scene `17` now has a significantly stronger Chinese operator surface across executive summary, formula blocks, and dispatch rows.
- Scene `04` runtime wording improved in the durable source path, and rerender output is materially closer to the desired Chinese platform-report feel.

### Remaining Follow-up

- Scene `04 / 05 / 17` still retain some English in rerendered historical outputs where the original JSON itself contains:
  - old preset-language scaffold lines
  - old table-cell prose
  - preserved source-evidence wording
- The next highest-value cleanup is a targeted second pass that rewrites only non-evidence historical JSON English carry-through for:
  - Scene `04` explanatory rows
  - Scene `05` old prompt-scaffold lines and table prose
  - Scene `17` old markdown section instructions and a few table values
- DOCX / XLSX layout quality was preserved through rerender, but the next platform-feel gain will come from:
  - stronger chapter-card copy tightening
  - fewer English example project names in visible headers
  - cleaner Chinese default examples for scene direct-use templates

## 2026-05-09 Residual Localization Pass

### Updated

- `tiktok-growth-operator.skill/scripts/render_scene_report.py`
- `tiktok-growth-operator.skill/scripts/scene_report_presets.py`
- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`
- `tiktok-growth-operator.skill/scripts/feishu_naming.py`

### What Changed

- Scene `04`
  - localized more historical-rerender carry-through strings in the renderer, including:
    - `Recovered hook`
    - `The proof layer works because ...`
    - `Portable logic: first-frame clarity plus compressed proof.`
    - safer / aggressive adaptation-row wording
  - localized import-runtime baseline lines such as `来源账号基线：...`
- Scene `05`
  - switched scene display name from `反推提示词与 Brief` to `反推提示词与制作简报`
  - localized more residual prompt-brief strings:
    - `反向推断这条视频背后的提示词或制作 brief...`
    - `反推原始 Brief / 产品适配 Brief`
  - made `recommended_request_zh` and `variable_inputs.example` pass through the same localization layer
- Scene `17`
  - localized residual Chinese-template leakage:
    - `转写稿s`
    - `Creator playbook`
    - `Adaptation path`
    - `Operator Dispatch`
  - localized several historical table-cell values for creator-formula rows and next-action rows
- Shared
  - updated `feishu_naming.py` scene labels so visible report titles use `制作简报` naming for Scene `05/09/10`
  - applied extra markdown post-render replacement for `### Operator Dispatch`

### Validation

- Ran: `python -m py_compile` on:
  - `tiktok-growth-operator.skill/scripts/render_scene_report.py`
  - `tiktok-growth-operator.skill/scripts/scene_report_presets.py`
  - `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`
  - `tiktok-growth-operator.skill/scripts/feishu_naming.py`
- Result: passed
- Ran: real rerenders for:
  - Scene `04` -> `.codex-tmp/scene04-zh-pass-20260509-v7`
  - Scene `05` -> `.codex-tmp/scene05-zh-pass-20260509-v9`
  - Scene `17` -> `.codex-tmp/scene17-zh-pass-20260509-v8`
- Result: passed and regenerated `md/docx/xlsx`

### Current Status

- Scene `04 / 05 / 17` are now largely Chinese-first at the template and report-surface layer.
- Remaining English is now mostly concentrated in:
  - raw evidence text
  - example placeholder values such as project-name examples or success-goal examples
  - a few intentionally preserved source captions / source descriptions
- This means the durable localization layer is now doing the right job; the next cleanup, if needed, is example-data tightening rather than another broad renderer rewrite.

## 2026-05-09 Final Doc Tail, Scene 08 Purchase Fixture, and Scene 18/19 Multi-Week Closure

### Updated

- `tiktok-growth-operator.skill/references/direct-use.md`
- `tiktok-growth-operator.skill/scripts/validate_skill_docs.py`
- `tiktok-growth-operator.skill/scripts/scene_report_presets.py`
- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`
- `tiktok-growth-operator.skill/scripts/render_scene_report.py`
- `tiktok-growth-operator.skill/testdata/validation/captures/scene08-multi-product-comments/README.md`
- `tiktok-growth-operator.skill/testdata/validation/captures/scene08-multi-product-comments/comments_sampled.json`

### What Changed

- docs tail
  - changed `direct-use.md` first-line title to Chinese-first `# 直接使用（Direct Use）`
  - changed the high-visibility section titles to Chinese-first:
    - `一句话中文起步`
    - `可直接复制的中文命令`
  - synchronized `validate_skill_docs.py` so docs validation follows the same section names
- Scene `08`
  - fixed cluster-type lookup drift in `comment_signal_snapshot()` so runtime now matches Chinese cluster labels:
    - `购买因素`
    - `差评痛点`
    - `信任信号`
  - localized Scene `08` runtime decision rows and open-question bullets in durable source
  - expanded theme detection for more purchase-friction language:
    - logistics / packaging
    - authenticity
    - refund / exchange
    - before-after proof
    - shade / undertone / oxidation
  - strengthened `reply_signal` synthesis so reply samples read like real objection-handling evidence instead of generic reply activity
  - upgraded the package-owned purchase fixture with reply-like commerce samples across:
    - leak / replacement handling
    - shade / daylight proof
    - oxidation / exchange
    - gift packaging
    - layered-hair before-after proof
- Scene `18 / 19`
  - fixed `parse_video_datetime()` so real fixture timestamps now resolve from `created_at_utc` and `create_time`
  - restored real natural-week labels from the validation pack:
    - `2026-W14`
    - `2026-W15`
    - `2026-W16`
    - `2026-W17`
  - added multi-week pattern rows that distinguish:
    - current baseline week
    - repeated pattern
    - rising new pattern
    - same-pattern fallback
    - pattern switch without scale lift
  - pushed the multi-week context into Scene `18` weekly-watch and Scene `19` retro tables so both scenes now read as real week-over-week operating outputs instead of single-week recaps
- rich export localization
  - extended `render_scene_report.py` so markdown rerender now localizes:
    - execution template fields
    - variable-input examples
    - evidence labels / details
    - asset notes
    - notes and sources
    - section table titles / headers / rows
    - evidence-reference rows
  - added explicit replacement coverage for visible carry-through labels such as:
    - `可下载视频源`
    - `下轮补采升级`
    - `价格带差异`
    - `以场景 18/19 作为本次工作的主流程`

### Validation

- Ran: `python -m py_compile` on:
  - `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`
  - `tiktok-growth-operator.skill/scripts/scene_report_presets.py`
  - `tiktok-growth-operator.skill/scripts/render_scene_report.py`
  - `tiktok-growth-operator.skill/scripts/validate_skill_docs.py`
- Result: passed
- Ran: `python tiktok-growth-operator.skill/scripts/validate_skill_docs.py`
- Result: passed
- Ran: JSON parse for the upgraded Scene `08` purchase fixture
- Result: passed
- Ran: real importer reruns for:
  - Scene `08` -> `.codex-tmp/20260509_final_spotcheck/scene08/scene-08-scene08-commerce-comment-check.json`
  - Scene `18` -> `.codex-tmp/20260509_final_spotcheck/scene18/scene-18-scene18-weekly-review.json`
  - Scene `19` -> `.codex-tmp/20260509_final_spotcheck/scene19/scene-19-scene19-account-retro.json`
  - Scene `04` -> `.codex-tmp/20260509_final_spotcheck/scene04/scene-04-scene04-single-video-breakdown.json`
- Result: passed
- Ran: rich rerenders for:
  - Scene `01` -> `.codex-tmp/20260509_final_spotcheck/scene01/outputs`
  - Scene `05` -> `.codex-tmp/20260509_final_spotcheck/scene05/outputs`
  - Scene `08` -> `.codex-tmp/20260509_final_spotcheck/scene08/outputs`
  - Scene `17` -> `.codex-tmp/20260509_final_spotcheck/scene17/outputs`
  - Scene `18` -> `.codex-tmp/20260509_final_spotcheck/scene18/outputs`
  - Scene `19` -> `.codex-tmp/20260509_final_spotcheck/scene19/outputs`
- Result: passed

### Spot-Check Result

- Scene `08`
  - markdown is now Chinese-first on decision rows, open-question notes, and most report-surface labels
  - purchase-language is materially stronger and now includes reply-chain commerce evidence
  - remaining English in this scene is mostly true source evidence or preserved public user wording
- Scene `18`
  - real multi-week view is restored and visible in markdown
  - weekly action board now references actual week slices instead of `week unknown`
  - DOCX / XLSX structure stayed intact after the multi-week upgrade
- Scene `19`
  - high-vs-low and next-test output now sits on top of real multi-week slices
  - the retro report now behaves more like a real operator dispatch than a static ranked-post recap
- Scene `01 / 04 / 05 / 17`
  - rerendered into the same spot-check batch so their current report surfaces can be compared with the latest localization layer
  - no new exporter breakage was introduced by the final Scene `08 / 18 / 19` changes

### Remaining Non-Blocking Gaps

- some preserved example values in older JSON still stay English when they are treated as historical data rather than regenerated preset content
- some source-evidence rows remain English by design because they preserve public source captions, comments, or URLs
- DOCX visual quality is now stable and platform-like at the current layer, but future polish can still tighten:
  - cover metadata copy
  - example project names
  - asset-card wording

## 2026-05-09 Final Spot-Check Localization Closure

### Updated

- `tiktok-growth-operator.skill/scripts/scene_report_presets.py`
- `tiktok-growth-operator.skill/scripts/render_scene_report.py`
- `tiktok-growth-operator.skill/scripts/feishu_naming.py`

### What Changed

- execution-template default path
  - moved `scene_report_presets.py` further to Chinese-first defaults for:
    - Scene `01` execution examples and success-goal wording
    - Scene `08 / 18 / 19` visible project examples and success-goal wording
  - changed default execution-template field metadata to Chinese-first:
    - `project_name`
    - `market`
    - `evidence_pack`
    - `success_goal`
    - `required`
  - changed fallback prompt scaffold and fallback workflow-check wording to Chinese-first so future scene renders do not keep leaking English template prose
- historical rerender localization
  - extended `render_scene_report.py` replacements to cover the remaining user-visible variable-input and Scene `01 / 08 / 18 / 19` template strings
  - added exact-string handling for the Scene `19` mixed-form example:
    - `Recent post table with metrics, hooks, and content-type labels`
    - `Recent post table with metrics, 钩子s, and content-type labels`
  - removed the broad `medium -> 中` replacement so real source comments such as `medium skin` are preserved correctly as evidence instead of being corrupted by template localization
- project title cleanup
  - extended `feishu_naming.py` project-text localization so final markdown/docx/xlsx report titles and `项目` fields use Chinese project labels for the final spot-check scenes:
    - Scene `08`
    - Scene `18`
    - Scene `19`

### Validation

- Ran: `python -m py_compile`
  - `tiktok-growth-operator.skill/scripts/scene_report_presets.py`
  - `tiktok-growth-operator.skill/scripts/render_scene_report.py`
  - `tiktok-growth-operator.skill/scripts/feishu_naming.py`
- Result: passed
- Ran: real rerenders for final spot-check outputs:
  - Scene `08` -> `.codex-tmp/20260509_final_spotcheck/scene08/outputs`
  - Scene `18` -> `.codex-tmp/20260509_final_spotcheck/scene18/outputs`
  - Scene `19` -> `.codex-tmp/20260509_final_spotcheck/scene19/outputs`
- Result: passed
- Ran: direct UTF-8 spot checks over rerendered markdown using Python file reads
- Result: passed for:
  - no remaining target template-English strings in Scene `08 / 18 / 19` variable-input tables
  - no remaining `with one week's`, `pain-language synthesis`, or `performance retro` leakage
  - Scene `08` preserved real evidence text as `medium skin` instead of corrupting it

### Spot-Check Result

- Scene `08`
  - variable-input examples are now Chinese-first
  - preserved buyer-language evidence stays in source English where appropriate
  - the earlier `中 skin` corruption is gone
- Scene `18`
  - report title and project label now render as Chinese-first
  - variable-input examples now show Chinese operator examples instead of mixed English carry-through
  - multi-week real-runtime framing remains intact
- Scene `19`
  - report title and project label now render as Chinese-first
  - `evidence_pack` and `success_goal` example rows are now Chinese-first
  - no remaining target template-English leakage in the visible markdown surface

### Remaining Non-Blocking Gaps

- PowerShell console `Get-Content` can still display mojibake for some UTF-8 Chinese lines depending on shell encoding, but Python UTF-8 reads confirm the markdown files themselves are correctly encoded
- source-evidence rows can still remain English by design when they preserve public captions, comments, URLs, or original TikTok text

## 2026-05-09 Final Spot-Check Completion Pass

### Updated

- `tiktok-growth-operator.skill/scripts/render_scene_report.py`
- `tiktok-growth-operator.skill/scripts/feishu_naming.py`

### What Changed

- project-title cleanup
  - expanded `feishu_naming.py` spot-check project matching so historical project names like:
    - `Scene 01 Spot Check`
    - `Scene 17 Spot Check`
    - `Scene 04 Spot Check V2`
    - `Scene 05 Spot Check V2`
  - now normalize into Chinese-first project labels instead of only supporting the older `Spotcheck Scene 01` shape
- historical rerender cleanup
  - extended `render_scene_report.py` to localize a few remaining high-visibility Scene `01` carry-through strings that were still leaking from older JSON payloads, including:
    - `Scene 01 Spot Check`
    - `Structured collection board`
    - `Scene-03 shortlist handoff`
    - `Video link`
    - `Traceability into later teardown`
    - two final deliverable summary sentences that still referenced the older English phrasing
- final spot-check batch completion
  - rerendered Scene `01` again from the real historical JSON source so the current durable localization layer fully applies
  - rerendered Scene `17` again from the real historical JSON source so title and project labels are now Chinese-first
  - added the missing Scene `04` export set into `.codex-tmp/20260509_final_spotcheck/scene04/outputs`

### Validation

- Ran: `python -m py_compile`
  - `tiktok-growth-operator.skill/scripts/render_scene_report.py`
  - `tiktok-growth-operator.skill/scripts/feishu_naming.py`
- Result: passed
- Ran: real rerenders for:
  - Scene `01` -> `.codex-tmp/20260509_final_spotcheck/scene01/outputs`
  - Scene `17` -> `.codex-tmp/20260509_final_spotcheck/scene17/outputs`
  - Scene `04` -> `.codex-tmp/20260509_final_spotcheck/scene04/outputs`
- Result: passed
- Ran: direct UTF-8 spot checks over the rerendered markdown for Scene `01 / 04 / 17`
- Result: passed for:
  - Scene `01` no longer leaking:
    - `Scene 01 Spot Check`
    - `Structured collection board`
    - `Scene-03 shortlist handoff`
    - `Lock publish-time window`
    - `Video link`
  - Scene `17` title now renders as `# 场景 17 成品质检`
  - Scene `04` final spot-check batch now includes `md/docx/xlsx`

### Current Acceptance Result

- The final spot-check batch now contains current rerender outputs for `01 / 04 / 05 / 08 / 17 / 18 / 19`.
- Scene `01` and Scene `17` no longer expose the earlier high-visibility English spot-check project labels.
- Scene `04` is now present in the same final comparison batch instead of being the one scene left as JSON-only.

### Remaining Non-Blocking Gaps

- some source-evidence rows remain English by design because they preserve public captions, comments, URLs, or original TikTok text

## 2026-05-09 Scene 04 Final Title Normalization

### Updated

- `tiktok-growth-operator.skill/scripts/feishu_naming.py`

### What Changed

- added historical project-name normalization for older Scene `04 / 05` fixture naming variants such as:
  - `Scene04 Single Video Breakdown`
  - `Scene05 Validation Capture`
- rerendered the final spot-check Scene `04` outputs after the naming-layer update so the visible title and project field are now Chinese-first

### Validation

- Ran: `python -m py_compile tiktok-growth-operator.skill/scripts/feishu_naming.py tiktok-growth-operator.skill/scripts/render_scene_report.py`
- Result: passed
- Ran: `python tiktok-growth-operator.skill/scripts/render_scene_report.py --input .codex-tmp/20260509_final_spotcheck/scene04/scene-04-scene04-single-video-breakdown.json --output-dir .codex-tmp/20260509_final_spotcheck/scene04/outputs`
- Result: passed
- Ran: direct UTF-8 read of `.codex-tmp/20260509_final_spotcheck/scene04/outputs/scene-04-scene04-single-video-breakdown.md`
- Result: title now renders as `# 场景 04 单视频拆解`, project line now renders as `- 项目：场景 04 单视频拆解`

## 2026-05-09 Final Visible-Surface Cleanup Pass

### Updated

- `tiktok-growth-operator.skill/scripts/render_scene_report.py`

### What Changed

- tightened the final markdown rerender layer for high-visibility non-evidence template text, especially in the first screen of the report surface
- localized the remaining mixed helper strings such as:
  - `排序视频 count`
  - `summary.json or aggregate_summary.json`
  - `profile_summary.json or summary.json`
  - `ranked_videos.json or aggregate_ranked_videos.json`
  - `aggregate_qualified_videos.json or qualified_video_links.txt`
  - `aggregate_report.md`
  - `video_details.json`
  - `1 条视频链接或一份分镜摘要 summary`
  - `市场 context`
  - `排序方式 and shop-cart filter state`
  - `TikTok Validation Scene 05 Capture`
- normalized visible `capture-pack` wording on the final report surface toward `采集包` where it was template copy rather than real evidence

### Validation

- Ran: `python -m py_compile tiktok-growth-operator.skill/scripts/render_scene_report.py`
- Result: passed
- Ran: rich rerenders for final spot-check outputs:
  - Scene `01`
  - Scene `04`
  - Scene `05`
  - Scene `08`
  - Scene `17`
  - Scene `18`
  - Scene `19`
- Result: passed
- Ran: direct UTF-8 scan of the first-screen markdown surface for the exact residual targets above
- Result: no remaining hits on the inspected final spot-check outputs

### Current Acceptance Result

- The final spot-check set now reads more consistently Chinese-first on the visible report surface.
- Remaining English in the inspected outputs is now primarily:
  - real TikTok titles, captions, usernames, sound labels, and public-source wording
  - a few preserved metric or system values that belong to source evidence rather than template scaffolding

## 2026-05-10 Display-Value Localization Pass

### Updated

- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`
- `tiktok-growth-operator.skill/scripts/render_scene_report.py`

### What Changed

- localized display-only system values that were still too raw on the first visible screen of the final reports
- importer-side display cleanup
  - added display helpers for session quality and optional empty lists
  - normalized importer metric snapshots from English-style comma joins into Chinese punctuation
  - mapped session-quality codes such as:
    - `browser_same_origin_api_ok`
    - `tikmatrix_profile_posts_export`
    - `unknown`
  - into Chinese operator-facing labels
- renderer-side display cleanup
  - added exact visible-surface replacements for:
    - `会话质量：browser_same_origin_api_ok`
    - `会话质量：tikmatrix_profile_posts_export`
    - `会话质量：unknown`
    - `查询词：none`
    - `主题：none`
    - English metric fragments such as `likes / plays / shares / comments` when they were part of template-style visible summary rows

### Validation

- Ran: `python -m py_compile`
  - `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`
  - `tiktok-growth-operator.skill/scripts/render_scene_report.py`
- Result: passed
- Ran: rerenders for final spot-check outputs:
  - Scene `01`
  - Scene `04`
  - Scene `05`
  - Scene `08`
  - Scene `17`
  - Scene `18`
  - Scene `19`
- Result: passed
- Ran: UTF-8 first-screen checks over the final markdown surfaces
- Result: no remaining hits for:
  - `会话质量：browser_same_origin_api_ok`
  - `会话质量：tikmatrix_profile_posts_export`
  - `会话质量：unknown`
  - `查询词：none`
  - `主题：none`
  - `排序视频 count`

### Current Acceptance Result

- The first-screen operator surface is now cleaner and less technical.
- Remaining English on the inspected final outputs is now mostly real TikTok source evidence:
  - public titles
  - usernames
  - sound labels
  - original captions / comments / URLs

## 2026-05-10 Source-Text Cleanup Guard Pass

### Updated

- `tiktok-growth-operator.skill/scripts/render_scene_report.py`

### What Changed

- added one more narrow post-render cleanup layer for obviously broken or machine-placeholder visible strings on the final report surface
- targeted only the high-confidence bad cases, including:
  - `Topic text missing`
  - `Hook text missing`
  - `not_detected`
  - broken residual text variants such as `sing your ️ out`
  - broken tail markers such as `little moments ️` and `proud of you ️`
- deliberately did not broad-brush normal English source evidence, so real titles, audio names, and public captions still remain intact where they are valid

### Validation

- Ran: `python -m py_compile tiktok-growth-operator.skill/scripts/render_scene_report.py`
- Result: passed
- Ran: rerenders for final spot-check outputs:
  - Scene `01`
  - Scene `18`
  - Scene `19`
- Result: passed
- Ran: UTF-8 checks on final markdown outputs for:
  - `Topic text missing`
  - `not_detected`
  - `sing your ️ out`
  - `little moments ️`
  - `proud of you ️`
- Result: no remaining hits on the inspected final outputs

## 2026-05-10 Final Export Surface Localization Pass

### Updated

- `tiktok-growth-operator.skill/scripts/render_scene_report.py`

### What Changed

- extended the shared export display layer so `md / docx / xlsx` now use the same Chinese-first visible-surface cleanup instead of only fixing markdown
- added exact display mappings for remaining template-field labels and placeholder values, including:
  - `Style / Environment / Camera / Lighting / Character`
  - `Hero cue / hook frame`
  - `Support frame or subtitle`
  - `Continuation CTA`
  - `continuation close`
  - `editorial / social-native`
  - `packaging study`
  - `download enrichment`
  - `portable format`
  - `creator-top-1`
  - `creator-low-1`
  - `paste-video-link`
  - `paste-screenshot-path-or-link`
- localized display-only metric and summary fragments for the export layer:
  - `likes / plays / shares / comments`
  - `ranked / qualified / min_likes`
  - `profile= / session=`
  - `session quality: ...`
  - `queries: none`
  - `topics: none`
- added Chinese status mapping for imported historical runs:
  - `imported` -> `已导入`
- pushed the same localization into evidence rows, asset rows, source rows, note rows, table cells, and section evidence references so final deliverables stay aligned across all export formats

### Validation

- Ran: `python -m py_compile tiktok-growth-operator.skill/scripts/render_scene_report.py`
- Result: passed
- Ran: rerenders for final spot-check outputs:
  - Scene `01`
  - Scene `04`
  - Scene `05`
  - Scene `17`
  - Scene `18`
  - Scene `19`
- Result: passed
- Ran: UTF-8 scans across rerendered markdown outputs for:
  - `Style`
  - `Environment`
  - `Camera`
  - `Lighting`
  - `Character`
  - `Hero cue`
  - `Support frame`
  - `Continuation CTA`
  - `packaging study`
  - `download enrichment`
  - `portable format`
  - `creator-low-1`
  - `likes=`
  - `comments=`
  - `shares=`
- Result: no remaining hits on the inspected final spot-check markdown outputs except preserved file-name references such as `aggregate_summary.json`
- Ran: payload-level unicode-escape verification for Scene `01`
- Result: working-context summary now resolves as Chinese-first text with localized session labels, query/topic empties, and metric labels

### Current Acceptance Result

- Scene `01 / 04 / 05 / 17 / 18 / 19` final spot-check markdown surfaces are now Chinese-first at the template / display layer.
- Remaining English on inspected outputs is intentionally preserved source evidence:
  - public TikTok titles
  - usernames
  - audio labels
  - original captions / comments / URLs
- Preserved file names such as `aggregate_summary.json` remain visible where they function as provenance, not UI copy.

## 2026-05-10 P1 Scene-Definition Tightening Pass

### Updated

- `tiktok-growth-operator.skill/scenarios/02-daily-category-patrol.md`
- `tiktok-growth-operator.skill/scenarios/04-single-video-breakdown.md`
- `tiktok-growth-operator.skill/scenarios/05-reverse-engineer-video-prompt.md`
- `tiktok-growth-operator.skill/scenarios/08-multi-product-comment-mining-and-persona-report.md`
- `tiktok-growth-operator.skill/scenarios/18-competitor-account-weekly-report.md`
- `tiktok-growth-operator.skill/scenarios/19-self-account-retro-and-optimization.md`
- `tiktok-growth-operator.skill/references/scene-quick-reference.md`

### What Changed

- tightened the highest-value P1 scenes to better match the Clipcat reference docs without changing the already-working capture bridge
- Scene `02`
  - added fixed patrol-time, append-into-one-sheet, row-level patrol-date, and weak-signal archive semantics
  - clarified that daily patrol should highlight new / rising / abnormal changes instead of repeating old winners
- Scene `04`
  - added download-JSON / capture-detail as an ideal input
  - strengthened no-voiceover handling and made the standard timeline view more explicit
- Scene `05`
  - separated inferred-original brief from product-adapted brief more explicitly
  - added generator-ready handoff requirements beyond simple prompt analysis
- Scene `08`
  - raised purchase-oriented comment language as a first-class input target
  - added repeated user-language evidence and category base-value vs improvement-opportunity output expectations
- Scene `18`
  - clarified baseline-week vs multi-week trend handling
  - added breakout-cause view and multi-week snapshot expectations
- Scene `19`
  - clarified one-window observation vs repeated pattern handling
  - added do-more / do-less / stop rules and ROI-linked interpretation to the output contract
- aligned `scene-quick-reference.md` with the same upgraded input/output contracts so operator quick-call docs no longer lag behind scenario definitions

### Validation

- Ran: UTF-8 reads over all updated scenario files and `scene-quick-reference.md`
- Result: passed
- Verified: updated scene definitions now exist for `02 / 04 / 05 / 08 / 18 / 19`
- Verified: quick-reference sections for the same scenes now reflect the tightened input and output expectations

### Current Acceptance Result

- The P1 scenes most directly tied to operator value now describe stronger platform-like behavior without changing the stable runtime bridge.
- This raises downstream report quality by improving the requested structure before rendering, not only cleaning outputs afterward.

## 2026-05-10 Preset Propagation And Fixture-Surface Cleanup

### Updated

- `tiktok-growth-operator.skill/scripts/scene_report_presets.py`
- `tiktok-growth-operator.skill/testdata/validation/README.md`
- `tiktok-growth-operator.skill/testdata/validation/captures/scene08-multi-product-comments/README.md`

### What Changed

- validated that the P1 scene-definition tightening really propagates into freshly generated scene JSON, not only into scenario docs
- generated fresh scaffold payloads for Scene `02 / 04 / 05 / 08 / 18 / 19` and verified that the upgraded:
  - `working_context`
  - `operator_guide`
  - `execution_template`
  now flow into new scene outputs
- found one remaining durable gap: several high-visibility scaffold defaults inside `scene_report_presets.py` were still English-first even on newly generated payloads
- localized the remaining first-screen scaffold surfaces for the highest-value operator scenes, especially:
  - Scene `02` patrol checklist / patrol table / alert logic / daily summary table
  - Scene `04` timeline / mechanism / BGM / replication-handoff tables
  - Scene `05` inferred-brief / shot-level / product-adapted / generator-handoff tables
  - Scene `17` account overview / high-vs-low comparison / formula library / bridge tables
- also localized several remaining example values that could still leak into new JSON scaffolds:
  - Scene `03` project and evidence examples
  - Scene `05` evidence example
  - Scene `09` evidence example
- converted the validation-fixture documentation surfaces to Chinese-first so package-maintenance references now match the operator-facing package tone
- kept real public-source evidence, usernames, captions, and comments untouched; only durable scaffold / fixture-explanation copy was normalized

### Validation

- Ran: `python -m py_compile tiktok-growth-operator.skill/scripts/scene_report_presets.py`
- Result: passed
- Ran: fresh scene scaffold generation for:
  - Scene `02` -> `.codex-tmp/20260510_preset_propagation/scene02.json`
  - Scene `04` -> `.codex-tmp/20260510_preset_propagation/scene04.json`
  - Scene `05` -> `.codex-tmp/20260510_preset_propagation/scene05.json`
  - Scene `08` -> `.codex-tmp/20260510_preset_propagation/scene08.json`
  - Scene `17` -> `.codex-tmp/20260510_preset_propagation/scene17.json`
  - Scene `18` -> `.codex-tmp/20260510_preset_propagation/scene18.json`
  - Scene `19` -> `.codex-tmp/20260510_preset_propagation/scene19.json`
- Result: passed
- Ran: targeted scans against generated scene JSON for prior residual scaffold strings such as:
  - `Daily patrol checklist`
  - `Patrol Table Schema`
  - `Timeline Breakdown`
  - `Structure Logic`
  - `Account Overview`
  - `High Vs Low Interaction Comparison`
  - `Formula Library`
  - `Generator / Editor Handoff`
- Result: no remaining hits on the regenerated Scene `02 / 04 / 05 / 17` scaffolds
- Ran: fixture-surface inspection for:
  - `testdata/validation/README.md`
  - `testdata/validation/captures/scene08-multi-product-comments/README.md`
- Result: package-owned validation instructions are now Chinese-first while keeping technical file names intact

### Current Acceptance Result

- the strengthened Scene `02 / 04 / 05 / 08 / 18 / 19` contracts are now confirmed at the real scaffold-generation layer, not only in docs
- newly generated operator scaffolds read more like the intended platform product surface and less like mixed internal templates
- Scene `08` validation fixtures remain commerce-oriented and now have clearer durable documentation about what they are meant to stress-test

### Remaining Non-Blocking Gaps

- a few lower-priority scene presets outside the current P1 focus still contain English-first examples or helper copy
- Scene `18 / 19` already support baseline-vs-multi-week framing in the contract layer, but stronger reusable multi-week durable fixtures would still improve regression confidence
- Scene `08` already has a stronger purchase-language fixture, but a second parallel fixture in another category would further reduce overfitting to one commerce language profile

## 2026-05-10 Scene 18/19 Multi-Week Durable Fixture Pass

### Updated

- `tiktok-growth-operator.skill/testdata/validation/captures/scene18-19-multi-week-account/ranked_videos.json`
- `tiktok-growth-operator.skill/testdata/validation/captures/scene18-19-multi-week-account/summary.json`
- `tiktok-growth-operator.skill/testdata/validation/captures/scene18-19-multi-week-account/profile_summary.json`
- `tiktok-growth-operator.skill/testdata/validation/captures/scene18-19-multi-week-account/comments_sampled.json`
- `tiktok-growth-operator.skill/testdata/validation/captures/scene18-19-multi-week-account/README.md`
- `tiktok-growth-operator.skill/testdata/validation/README.md`
- `tiktok-growth-operator.skill/scripts/validate_capture_pack_workflows.py`

### What Changed

- added one package-owned multi-week account fixture specifically to stress Scene `18` and Scene `19`
- the fixture is intentionally small but structured to trigger real week-compare behavior:
  - one account
  - two natural weeks (`2026-W16` and `2026-W17`)
  - weaker explanation-heavy baseline week
  - stronger recognition-first / proof-first second week
  - comment samples that reinforce the same week-shift story through trust, daylight-proof, wear-test, and hook-speed language
- documented the fixture’s purpose so future agents can distinguish:
  - baseline-only pack behavior
  - true multi-week compare behavior
  - comment-layer trust-pressure behavior
- extended `validate_capture_pack_workflows.py` so Scene `18` and Scene `19` now have direct multi-week validation smoke runs instead of piggybacking only on generic capture fixtures

### Validation

- Ran: `python -m py_compile tiktok-growth-operator.skill/scripts/validate_capture_pack_workflows.py`
- Result: passed
- Ran: `import_tiktok_capture_pack.py` directly on the new fixture for Scene `18`
- Result: passed and executive summary entered the two-week compare framing
- Ran: `import_tiktok_capture_pack.py` directly on the new fixture for Scene `19`
- Result: passed and executive summary entered the two-week retro framing
- Ran: `start_capture_pack_run.py` on the new fixture for:
  - Scene `18`
  - Scene `19`
- Result: passed and produced real run roots plus `md/docx/xlsx` renderable scene JSON outputs under `.codex-tmp/`

### Current Acceptance Result

- Scene `18` no longer relies only on baseline-week or generic account fixtures to prove week-compare logic
- Scene `19` now has a durable package-owned fixture that triggers:
  - high-vs-low pattern comparison
  - multi-week interpretation
  - do-more / do-less / stop style dispatch behavior
- the validation surface for weekly competitor review and self-account retro is materially stronger than before without touching the TikMatrix runtime bridge

### Remaining Non-Blocking Gaps

- Scene `18` still uses a single-account multi-week fixture, so it strengthens week-comparison confidence more than true competitor-matrix confidence
- a future upgrade could add a `3-5 account / 2-week` fixture family for fuller cross-account matrix validation

## 2026-05-10 Scene 18 Matrix Runtime Upgrade

### Updated

- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`
- `tiktok-growth-operator.skill/testdata/validation/captures/scene18-matrix-multi-account/ranked_videos.json`
- `tiktok-growth-operator.skill/testdata/validation/captures/scene18-matrix-multi-account/summary.json`
- `tiktok-growth-operator.skill/testdata/validation/captures/scene18-matrix-multi-account/profile_summary.json`
- `tiktok-growth-operator.skill/testdata/validation/captures/scene18-matrix-multi-account/comments_sampled.json`
- `tiktok-growth-operator.skill/testdata/validation/captures/scene18-matrix-multi-account/README.md`
- `tiktok-growth-operator.skill/testdata/validation/README.md`
- `tiktok-growth-operator.skill/scripts/validate_capture_pack_workflows.py`

### What Changed

- upgraded Scene `18` runtime behavior so it can detect and use a true competitor-matrix view when one capture pack contains multiple accounts
- added account-aware helpers to:
  - group ranked videos by account
  - compute distinct account count from real video rows
  - label each account row with a more readable operator-facing account label
- changed Scene `18` fill behavior so matrix-mode now affects:
  - executive summary framing
  - per-account weekly summary rows
  - per-account week-over-week change rows
  - matrix-level action dispatch rows
- kept Scene `19` untouched so self-account retro remains single-account oriented
- added one durable `3 accounts x 2 weeks` fixture family for Scene `18`:
  - all three accounts move from slower explanation-led packaging in week 16
  - toward faster proof-led packaging in week 17
  - with comment samples that reinforce the same shift
- extended capture-pack validation so Scene `18` now has:
  - single-account multi-week validation
  - multi-account matrix validation

### Validation

- Ran: `python -m py_compile`
  - `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`
  - `tiktok-growth-operator.skill/scripts/validate_capture_pack_workflows.py`
- Result: passed
- Ran: direct Scene `18` import on `captures/scene18-matrix-multi-account/`
- Result: passed and executive summary entered explicit matrix framing
- Ran: `start_capture_pack_run.py --scene 18` on the matrix fixture
- Result: passed and produced a real run root plus scene output bundle under `.codex-tmp/scene18_matrix_validation`
- Verified in the generated report JSON:
  - `Objects To Track` rows are now account-split
  - `Why They Matter` rows are now account-by-account weekly shifts
  - `Next Action` uses matrix dispatch semantics instead of single-account weekly recap language

### Current Acceptance Result

- Scene `18` is no longer only “documented as a matrix workflow”; it now behaves like one when the capture pack truly contains multiple accounts
- package-owned validation now covers both:
  - single-account multi-week compare mode
  - multi-account multi-week matrix mode

### Remaining Non-Blocking Gaps

- the new matrix fixture still uses one category family and one simplified synthetic shift pattern
- a future pass can add a second matrix fixture where different accounts move in different directions instead of all three accounts converging toward the same proof-first trend

## 2026-05-10 Scene 18 Divergent-Matrix Validation Pass

### Updated

- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`
- `tiktok-growth-operator.skill/testdata/validation/captures/scene18-matrix-divergent-account/ranked_videos.json`
- `tiktok-growth-operator.skill/testdata/validation/captures/scene18-matrix-divergent-account/summary.json`
- `tiktok-growth-operator.skill/testdata/validation/captures/scene18-matrix-divergent-account/profile_summary.json`
- `tiktok-growth-operator.skill/testdata/validation/captures/scene18-matrix-divergent-account/comments_sampled.json`
- `tiktok-growth-operator.skill/testdata/validation/captures/scene18-matrix-divergent-account/README.md`
- `tiktok-growth-operator.skill/testdata/validation/README.md`

### What Changed

- strengthened Scene `18` matrix behavior beyond the earlier “all accounts move in the same direction” case
- added a second matrix fixture where the three competitor accounts diverge:
  - one account clearly strengthens
  - one account clearly declines
  - one account only lightly fluctuates and behaves more like event-noise
- upgraded Scene `18` matrix runtime summaries so per-account rows now expose:
  - `本周明显增强`
  - `本周明显回落`
  - `本周相对持平`
- tightened matrix dispatch logic so `减少跟进` is selected from the account with the strongest real decline signal, not simply the lowest absolute top score

### Validation

- Ran: `python -m py_compile tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`
- Result: passed
- Ran: direct Scene `18` import on `captures/scene18-matrix-divergent-account/`
- Result: passed
- Verified in generated Scene `18` JSON:
  - `proofboostlab` marked as clearly strengthened
  - `slowstoryroom` marked as clearly declined
  - `eventspikelab` marked as light fluctuation / likely-noise
  - `Next Action -> 减少跟进` now points at `slowstoryroom` rather than the event-noise account

### Current Acceptance Result

- Scene `18` now has two durable matrix validation patterns:
  - convergence pattern
  - divergence pattern
- this is enough to prove the weekly competitor report can distinguish:
  - broad strategy shifts
  - account-specific decline
  - likely noise

## 2026-05-10 Scene 08 Second-Category Comment Fixture Pass

### Updated

- `tiktok-growth-operator.skill/testdata/validation/captures/scene08-multi-product-home-goods-comments/comments_sampled.json`
- `tiktok-growth-operator.skill/testdata/validation/captures/scene08-multi-product-home-goods-comments/README.md`
- `tiktok-growth-operator.skill/testdata/validation/README.md`
- `tiktok-growth-operator.skill/scripts/validate_capture_pack_workflows.py`

### What Changed

- added a second Scene `08` purchase-language fixture outside the beauty category
- the new fixture focuses on home-goods / pet / travel-pack products instead of shade / wear-test / cosmetic proof language
- it stresses a different family of buyer-language signals:
  - sizing / fit / compatibility
  - packaging quality
  - return / refund friction
  - authenticity / dropship suspicion
  - durability / zipper / handle / load-test trust
  - before-after realism in non-beauty contexts
- extended validation wiring so Scene `08` can now be run directly against this second category fixture instead of only relying on the beauty-oriented commerce pack

### Validation

- Ran: `python -m py_compile`
  - `tiktok-growth-operator.skill/scripts/validate_capture_pack_workflows.py`
  - `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`
- Result: passed
- Ran: direct Scene `08` import on `captures/scene08-multi-product-home-goods-comments/`
- Result: passed
- Ran: `start_capture_pack_run.py --scene 08` on the same fixture
- Result: passed and produced:
  - scene report JSON
  - exportable scene outputs
  - `live-assist` operator pack
- Verified in the generated Scene `08` report:
  - non-beauty purchase language is now visible in the core evidence rows
  - repeated signals include packaging damage, dimension mismatch, authenticity suspicion, durability pressure, and return language

### Current Acceptance Result

- Scene `08` no longer validates only against one beauty-language commerce profile
- package-owned validation now covers at least two distinct comment-language families:
  - beauty / shade / wear-test / before-after
  - home-goods / fit / packaging / authenticity / durability / return

### Remaining Non-Blocking Gaps

- the current non-beauty fixture is still mostly English-language user wording
- a future pass can add:
  - a more cross-border / bilingual purchase-language fixture
  - a lower-price impulse-buy fixture where comments skew toward shipping speed and authenticity rather than fit / durability

## 2026-05-10 Scene 19 ROI / 时间窗上屏补强

### Updated

- `tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`
- `tiktok-growth-operator.skill/references/direct-use.md`
- `tiktok-growth-operator.skill/references/creative-brief-quick-reference.md`
- `tiktok-growth-operator.skill/references/automation-workflows.md`

### What Changed

- 把 Scene `19` 夹具里原本只存在于原始行数据中的字段，真正抬到了报告成品层：
  - `publish_window`
  - `conversion_proxy`
  - `roi_proxy`
- 为 Scene `19` 新增了几组运行时聚合：
  - 时间窗信号汇总
  - ROI / 转化 proxy 聚类
  - 高低表现组对照
  - 下轮测试计划生成
- 修正了 Scene `19` 的高 / 低表现取样方式，改为按 `score + digg_count + comment_count` 排序后再抽高低组，不再依赖输入顺序。
- 把 Scene `19` 常见内容模式名压成中文可读标签：
  - `founder-proof` -> `创始人出镜证明型`
  - `proof-object-demo` -> `证明物直给演示型`
  - `aesthetic-montage` -> `审美拼贴型`
  - `slow-explainer` -> `慢解释型`
- 顺手收了 references 的高可见残留：
  - `direct-use.md` 标题改为中文优先
  - `creative-brief-quick-reference.md` 首屏说明与部分 `Brief` 命名改为中文优先
  - `automation-workflows.md` 里与制作简报相关的示例命名改为中文口径更强的 run name / context file

### Validation

- Ran: `python -m py_compile tiktok-growth-operator.skill/scripts/import_tiktok_capture_pack.py`
- Result: passed
- Ran: direct Scene `19` import on `testdata/validation/captures/scene19-roi-multiwindow-account/`
- Result: passed and generated fresh JSON at:
  - `.codex-tmp/scene19-roi-check/scene19.json`
- Ran: `start_capture_pack_run.py --scene 19 --formats md`
- Result: passed and regenerated:
  - `.codex-tmp/scene19_roi_multiwindow_validation/`
- Ran: rich export spot check with `md/docx/xlsx`
- Result: passed and generated:
  - `.codex-tmp/spotcheck-scene19-roi-rich-20260510/scene-19/outputs/scene-19-tiktok-scene-19-roi-rich-spotcheck.md`
  - `.codex-tmp/spotcheck-scene19-roi-rich-20260510/scene-19/outputs/scene-19-tiktok-scene-19-roi-rich-spotcheck.docx`
  - `.codex-tmp/spotcheck-scene19-roi-rich-20260510/scene-19/outputs/scene-19-tiktok-scene-19-roi-rich-spotcheck.xlsx`

### Verified Outcome

- Scene `19` 现在会在可见表格中直接显示：
  - 高表现窗口 / 低表现窗口
  - 转化 proxy / ROI proxy
  - 高低表现模式差异
  - 时间窗级别的强弱差异
  - 基于窗口稳定复测的下轮测试计划
- Markdown 文件本身 UTF-8 正常；此前 PowerShell `Get-Content` 出现的中文乱码，属于控制台显示层，不是导出文件编码本体损坏。

### Current Practical State

- Scene `19` 已从“fixture 有 ROI 字段，但成品不显式使用”升级为“真实运行时可直接读出窗口 + proxy + 下轮测试动作”。
- 这已经足够支撑“半平台级真实闭环”里的自家账号复盘层，不再只是泛复盘笔记。

### Remaining Non-Blocking Gaps

- Scene `19` 里的原始 TikTok 文本证据仍可能保留英文，这是刻意保留真实 source evidence，不应为了表面中文化而误改原证据。
- `High-Level Judgment / Evidence Clusters / Recommended Action / Open Questions` 这些 section heading 仍保留英文 canonical id；当前 renderer 已有中文显示映射，但历史 md 产物不会自动回写。
- 如果后续还要更强平台感，可以继续：
  - 给 Scene `19` 单独补一版“周报 / 复盘卡片”封面副标题
  - 把 `conversion proxy / ROI proxy` 再压成更中文化的展示短语，同时保留原字段名作为括注
