---
name: tiktok-growth-operator
description: Pure Codex TikTok and Douyin growth operating system. Use this when the user wants to run one of the 19 Clipcat-style scenarios without relying on Clipcat CLI, by using direct prompt and workflow templates for collection, teardown, selection, scripting, localization, and account review.
---

# TikTok Growth Operator

Use this skill when the user wants a pure Codex version of the Clipcat/OpenClaw TikTok or Douyin growth workflow.

This package is organized as:

1. one main router
2. one scenario index
3. 19 directly callable scenario playbooks
4. shared prompt and deliverable templates
5. lightweight automation scripts for scene workspace and report generation
6. direct-use guides for Codex-first execution without Clipcat/OpenClaw runtime

## What This Skill Owns

- direct routing across 19 TikTok growth scenarios
- Codex-native prompt and workflow templates for each scenario
- report structures for teardown, market insight, creator distillation, and optimization
- scene-specific starter tables and evidence slots for all 19 scenarios
- intake-aware working context blocks with minimum evidence, ideal evidence, and ready checklist
- explicit input and output contracts
- pure Codex fallback rules when no platform API or automation connector exists
- a safe replacement map for the Tencent Cloud Douyin article feature set
- a direct runner script that creates a workspace and report scaffold in one command
- a starter-board launcher that converts a natural-language request into one local runnable board folder
- a starter-board launcher that can also generate and preview the queue directly from that local folder
- a capture-pack runner that turns real TikTok capture folders into scene outputs and handoff packs
- unified operator routing that can treat real TikTok capture folders as first-class workflow inputs

## What This Skill Does Not Own

- guaranteed access to TikTok, Douyin, TikTok Shop, or Feishu when the runtime lacks credentials
- proprietary Clipcat generation backends
- pretending a scenario is fully automated when it still needs human-provided links, exports, screenshots, or browser evidence

## Hard Rules

- Default to pure Codex workflows. Do not assume `clipcat` exists.
- When freshness matters, use browsing or the user's supplied live exports instead of guessing.
- Distinguish evidence-backed conclusions, inferences, and pending validation.
- For generation-oriented scenarios, produce briefs, prompts, storyboards, and testing matrices even if actual rendering must happen elsewhere.
- Prefer scenario-specific outputs over generic advice.
- Do not implement fake engagement, comment hijacking, anti-detection, or account farming tactics.

## Invocation Model

If the user names a scenario number or describes one of the source use cases, route into that scenario file directly.

Examples:

- `跑场景 3，关键词=lip combo，市场=US`
- `按场景 12 做一个一品多风格测试矩阵`
- `帮我做场景 8，把这些评论整理成人群画像`
- `按文章 2640429 的思路直接用 Codex 跑一个 Douyin 工作区`

## Execution Order

### Step 1: Read the scenario index

Read [references/scenario-index.md](references/scenario-index.md) to map the request to the right scenario.

### Step 2: Read the scenario file

Open the corresponding file under `scenarios/`.

Each scenario file contains:

- trigger conditions
- minimum inputs
- ideal inputs
- exact workflow
- output contract
- direct prompt template
- fallback path when live data is missing

### Step 3: Reuse shared templates only as needed

- prompt blocks: [references/prompt-library.md](references/prompt-library.md)
- output formats: [references/deliverable-contracts.md](references/deliverable-contracts.md)
- structured report contract: [references/scene-report-contract.md](references/scene-report-contract.md)
- reproduction boundaries: [references/codex-replication-blueprint.md](references/codex-replication-blueprint.md)
- automation helpers: [references/automation-workflows.md](references/automation-workflows.md)
- direct Codex usage: [references/direct-use.md](references/direct-use.md)
- final operator handoff: [references/final-handoff.md](references/final-handoff.md)
- batch preset catalog: [references/batch-presets.md](references/batch-presets.md)
  Use it for single starter templates, template bundles, config-driven regeneration, and the generated preset `.report.md` handoff into dry-run, execute, or rerun flows.
- entry board selection: [references/entry-selector.md](references/entry-selector.md)
  Use it when the operator knows the desired outcome, role, cadence, or vertical context but does not know which board family or slug to start with.
- Tencent article parity map: [references/article-2640429-feature-parity.md](references/article-2640429-feature-parity.md)
- publish prep pack: [references/publish-prep-pack.md](references/publish-prep-pack.md)
- live assist pack: [references/live-assist-pack.md](references/live-assist-pack.md)

## Scenario List

1. viral video collection
2. daily category patrol
3. batch viral search plus deep teardown
4. single video breakdown
5. reverse-engineer video prompt
6. competitor product dashboard
7. category market insight
8. multi-product comment mining and persona report
9. reference-video replication brief
10. product-image-to-video brief
11. hot-video replication pipeline
12. one-product multi-style testing matrix
13. multi-market localization pack
14. launch asset family pack
15. image translation brief
16. competitor main-image benchmark
17. creator distillation
18. competitor account weekly report
19. self-account retro and optimization

## When To Read References

- Read [references/assistant-spec.md](references/assistant-spec.md) for scope and truthfulness rules.
- Read [references/scenario-index.md](references/scenario-index.md) first for routing.
- Read [references/prompt-runtime-design.md](references/prompt-runtime-design.md) for the pure Codex runtime model.
- Read [references/feature-map.md](references/feature-map.md) for the source-derived capability map.
- Read [references/direct-use.md](references/direct-use.md) when the user wants Codex to run the workflow directly.
- Read [references/final-handoff.md](references/final-handoff.md) when you want the shortest durable summary of what is finished, how to run it, and how to validate it.
- Read [references/batch-presets.md](references/batch-presets.md) when the user wants a ready-made reusable batch queue.
  Prefer the generated preset `.report.md` before execution because it includes copy-ready batch commands, suggested artifact paths, reusable input config, and generated helper scripts.
- Read [references/entry-selector.md](references/entry-selector.md) when the user needs a recommendation across `single`, `combo`, `vertical`, `launch-board`, `manager-board`, or `cadence-board`.
- Read [references/article-2640429-feature-parity.md](references/article-2640429-feature-parity.md) when the user refers to the Tencent Cloud Douyin article.
- Read [references/publish-prep-pack.md](references/publish-prep-pack.md) when the user wants a publish-ready handoff pack.
- Read [references/live-assist-pack.md](references/live-assist-pack.md) when the user wants a live-room operator pack.
- Read [references/prompt-library.md](references/prompt-library.md) for reusable prompt blocks.
- Read [references/deliverable-contracts.md](references/deliverable-contracts.md) for output formats.
- Read [references/scene-report-contract.md](references/scene-report-contract.md) when the output should become a durable JSON, Markdown, DOCX, or XLSX deliverable.
- Read [references/automation-workflows.md](references/automation-workflows.md) when you want reusable run folders or report skeletons.
- Read [references/evaluation-pack.md](references/evaluation-pack.md) before changing behavior.
