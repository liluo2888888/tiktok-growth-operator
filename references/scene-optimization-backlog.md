# Scene Optimization Backlog

This file tracks the highest-value next improvements for the scenes that already have real TikTok runtime confirmation:

- `01` Viral Video Collection
- `02` Daily Category Patrol
- `03` Batch Viral Search Plus Deep Teardown
- `04` Single Video Breakdown
- `05` Reverse-Engineer Video Prompt
- `07` Category Market Insight
- `08` Multi-Product Comment Mining And Persona Report
- `17` Creator Distillation
- `18` Competitor Account Weekly Report
- `19` Self-Account Retro And Optimization

The goal is not feature count. The goal is better operator outputs, stronger evidence traceability, and more reusable downstream handoff packs.

## External Reference Set

These open-source projects informed the backlog below:

- `davidteather/TikTok-Api`
- `fmd-labs/viral-app-mcp`
- `Seym0n/tiktok-mcp`
- `kodi-leith/TikTok-Trend-Detection`
- `ezedinff/TikTok-Forge`

Use them as design references, not as hard dependencies.

## Priority Bands

- `P1`: directly improves report quality or evidence quality for current real-runtime scenes
- `P2`: improves repeatability, explainability, or trend detection quality
- `P3`: improves resilience, maintainability, or downstream reuse

## Cross-Scene Priorities

### P1. Expand evidence intake from a flat candidate list into a content graph

Target scenes:

- `01`
- `03`
- `07`
- `17`
- `18`
- `19`

Why:

- current scene quality is strongest when ranked candidates already contain rich caption, subtitle, and metadata fields
- external TikTok tooling commonly expands from one post into related posts, hashtag neighborhoods, creator history, and sound-level clusters

Recommended change:

- add a graph-expansion helper that can normalize:
  - source video
  - creator
  - sound
  - hashtag
  - related or follow-up video
- store graph edges in the scene workspace so reports can explain why a candidate entered the shortlist

Likely file owners:

- `scripts/run_tikmatrix_capture_bridge.py`
- `scripts/run_scene_workflow.py`
- `scripts/scene_report_presets.py`
- `references/scene-report-contract.md`

Validation:

- real rerun on one `Scene 01` and one `Scene 03` fixture
- verify richer shortlist provenance in JSON and Markdown outputs

### P1. Upgrade shortlist scoring from popularity-first to reuse-value-first

Target scenes:

- `01`
- `03`
- `07`

Why:

- the current reports already rank well, but the next quality jump comes from better ranking logic, not more templates
- the best open-source TikTok stacks separate "found content" from "actionable content"

Recommended scoring dimensions:

- caption completeness
- subtitle availability
- comment density
- signaled authority or proof strength
- series potential
- adaptation distance
- repeated hook pattern frequency
- sound or topic spread

Likely file owners:

- `scripts/run_tikmatrix_capture_bridge.py`
- `scripts/scene_report_presets.py`
- `references/scene-report-contract.md`

Validation:

- compare old and new ranked order for one rich collector fixture
- verify the top picks are better justified in the exported report

### P1. Make every high-level insight traceable to source evidence

Target scenes:

- `03`
- `04`
- `05`
- `08`
- `17`
- `18`
- `19`

Why:

- operator outputs are strongest when each claim points back to a source clip, comment, creator, or week bucket
- this is the most important remaining quality gap for reviewability

Recommended change:

- add structured evidence refs under each major finding:
  - source type
  - source id or url
  - time range when relevant
  - excerpt or summary

Likely file owners:

- `scripts/scene_report_presets.py`
- `references/scene-report-contract.md`
- `scripts/render_scene_report.py`

Validation:

- rerender one report each from `Scene 04`, `Scene 08`, and `Scene 18`
- confirm evidence refs survive Markdown, DOCX, and XLSX exports

### P1. Add comment cleaning and reply-chain synthesis

Target scenes:

- `08`
- `18`
- `19`

Why:

- raw comment mining quality degrades quickly when spam, duplicate comments, emoji-only noise, and shallow repeats are mixed in
- open-source TikTok comment tooling often exposes reply trees and comment-level engagement that can improve persona quality

Recommended change:

- normalize comments and replies separately
- deduplicate near-identical comments
- label low-signal rows
- preserve high-value original phrasing
- promote repeated reply patterns into trust or objection signals

Likely file owners:

- `scripts/import_tiktok_capture_pack.py`
- `scripts/run_tikmatrix_account_ops_bridge.py`
- `scripts/scene_report_presets.py`

Validation:

- rerun `Scene 08` on the strongest real comments fixture
- compare quote quality and persona outputs before and after cleaning

## Secondary Priorities

### P2. Add baseline-shift and anomaly logic for patrol and weekly scenes

Target scenes:

- `02`
- `18`
- `19`

Why:

- current outputs can summarize well, but true operator value increases when the report detects change instead of just listing observations

Recommended change:

- persist scene history in a more analysis-ready format
- compute:
  - week-over-week changes
  - recent-baseline deltas
  - new hook-pattern appearance
  - sound rotation
  - posting-time shifts
  - creator cluster movement

Likely file owners:

- `scripts/run_scene02_patrol.py`
- `scripts/run_scene_workflow.py`
- `scripts/scene_report_presets.py`

Validation:

- rerun the existing `Scene 02 -> Scene 03` patrol chain
- verify alerts become "change-first" instead of "inventory-first"

### P2. Turn scene 04 and scene 05 into production-spec outputs

Target scenes:

- `04`
- `05`

Why:

- current breakdowns are analytically useful
- the next jump is to make them immediately usable by downstream video generators or human editors

Recommended change:

- output:
  - shot list
  - pacing map
  - subtitle beat map
  - proof block map
  - likely asset requirements
  - confidence-bounded inferred brief fields

Likely file owners:

- `scripts/scene_report_presets.py`
- `references/creative-brief-quick-reference.md`
- `references/scene-report-contract.md`

Validation:

- rerun one `Scene 04` and one `Scene 05` fixture
- confirm the output reads like a generator-ready handoff, not only a study note

### P2. Add supply saturation signals to category opportunity judgments

Target scenes:

- `07`

Why:

- hot topics are not always good opportunities
- opportunity quality improves when demand and supply are evaluated separately

Recommended change:

- estimate:
  - similar-hook density
  - creator count concentration
  - repetitive sound reuse
  - comment-language homogeneity
  - packaging fatigue

Likely file owners:

- `scripts/scene_report_presets.py`
- `references/scene-quick-reference.md`

Validation:

- rerun one `Scene 07` fixture with the stronger reasoning template
- verify the report distinguishes heat from white-space opportunity

## Resilience And Reuse Priorities

### P3. Add stable fallback ordering for transcript recovery

Target scenes:

- `01`
- `03`
- `04`
- `05`
- `17`

Why:

- many real TikTok rows have inconsistent text fields
- current outputs improve substantially when transcript or subtitle recovery succeeds

Recommended fallback order:

1. native caption or subtitle fields from capture
2. downloaded sidecar metadata from single-video download
3. bridge-enriched transcript fields
4. optional external transcript adapter

Likely file owners:

- `scripts/run_tikmatrix_capture_bridge.py`
- `scripts/run_tikmatrix_single_video_scene.py`

Validation:

- replay one sparse-caption fixture and verify more complete hook/topic extraction

### P3. Add series clustering before creator or account summarization

Target scenes:

- `17`
- `18`
- `19`

Why:

- creator and account analysis gets distorted when multiple series or formats are collapsed into one persona

Recommended change:

- cluster videos by recurring format, phrase pattern, proof style, or topic family before computing the final summary

Likely file owners:

- `scripts/scene_report_presets.py`
- `scripts/run_scene_workflow.py`

Validation:

- rerun one creator fixture and one account fixture
- confirm the report distinguishes cross-series patterns from whole-account patterns

### P3. Add one reusable "scene quality comparison" eval

Target scenes:

- `01`
- `03`
- `04`
- `08`
- `17`
- `18`
- `19`

Why:

- once ranking, evidence refs, and anomaly logic evolve, qualitative regressions become easy to miss

Recommended change:

- define one eval sheet or JSON rubric that scores:
  - evidence traceability
  - actionability
  - redundancy
  - operator readability
  - downstream handoff usefulness

Likely file owners:

- `testdata/validation/`
- `scripts/validate_export_outputs.py`
- `references/scene-report-contract.md`

Validation:

- run on 3 to 5 representative real scenes after each report-quality upgrade

## Suggested Implementation Order

1. evidence refs in scene contracts and renderers
2. richer shortlist scoring for scenes `01` and `03`
3. comment cleaning plus reply synthesis for scene `08`
4. anomaly and baseline logic for scenes `02`, `18`, and `19`
5. production-spec upgrade for scenes `04` and `05`
6. series clustering for scenes `17`, `18`, and `19`

## Not In Scope For This Backlog

These belong to other roadmap tracks:

- final video render backends for scenes `09` to `13`
- final image generation backends for scenes `14` to `16`
- TikTok Shop data source work for scene `06`
- risky account mutation or account-farming automation

## 2026-05-08 Clipcat Public-Surface Parity Backlog

This section folds in the latest public parity references directly:

- Tencent article mirror baseline: [cloud.tencent.com/developer/article/2640429](https://cloud.tencent.com/developer/article/2640429)
- ClawHub public skill page: [clawhub.ai/a2888409/clipcat](https://clawhub.ai/a2888409/clipcat)
- Public GitHub skill repo: [github.com/Clipcat-ai/clipcat-skill](https://github.com/Clipcat-ai/clipcat-skill)
- local DOCX bundle already extracted and reviewed on 2026-05-08:
  - `Clipcat 使用手册🔥.docx`
  - `ClipcatSkill - 让 OpenClaw 创作Tiktok爆款短视频.docx`
  - `口红爆款视频拆解报告.docx`

The gap is no longer scene count. The gap is product-surface fidelity: stronger table-first deliverables, richer scene-specific schemas, and more direct handoff into the next workflow.

### Scene 01 - Viral Video Collection

Priority: `P1`

Required parity upgrades:

- make `publish_time_window`, `market`, `sort_by`, and `only_tkshop_cart_videos` first-class required inputs instead of weak optional hints
- strengthen XLSX-first collection output so the main artifact behaves like a board, not only a Markdown note
- add per-row explanation columns:
  - why worth studying
  - best reuse category
  - suitable product or niche
- add explicit commerce fields:
  - shopping intent
  - TikTok Shop signal
  - commerce confidence
- make shortlist handoff into Scene `03` explicit and durable

Likely owners:

- `scripts/run_tikmatrix_capture_bridge.py`
- `scripts/scene_report_presets.py`
- `references/scene-report-contract.md`

### Scene 02 - Daily Category Patrol

Priority: `P1`

Required parity upgrades:

- harden cadence semantics:
  - patrol frequency
  - append-to-same-board behavior
  - capture date field
  - stable header contract
- upgrade the daily summary so it highlights:
  - new breakouts today
  - rising signals today
  - anomalies worth escalation
- default the patrol to change-first output instead of re-listing old content
- support multi-keyword and multi-category watchlists as a first-class board shape
- auto-route strong patrol hits to Scene `03` and weak signals to patrol history

Likely owners:

- `scripts/run_scene02_patrol.py`
- `scripts/run_scene_workflow.py`
- `scripts/scene_report_presets.py`

### Scene 03 - Batch Viral Search Plus Deep Teardown

Priority: `P1`

Required parity upgrades:

- codify shortlist logic closer to the public workflow:
  - collect a broader candidate set first
  - explicitly deep-dive only the top few qualified videos
- force the report into three stable blocks:
  - per-video detailed teardown
  - common-pattern summary
  - creation recommendation
- preserve full script or subtitle content whenever evidence allows
- make time-axis conversion rhythm a standard output, not an occasional note
- shift the end product from analysis memo toward creator-ready playbook

Likely owners:

- `scripts/run_tikmatrix_capture_bridge.py`
- `scripts/scene_report_presets.py`
- `references/scene-report-contract.md`

### Scene 04 - Single Video Breakdown

Priority: `P1`

Required parity upgrades:

- standardize the timeline table as:
  - `Time Range | Scene Type | Visual Content | Spoken / On-Screen Script | Role In Conversion | Evidence Ref`
- add dedicated BGM analysis instead of treating audio as only transcript support
- enforce the three-part viral interpretation:
  - opening hook
  - conversion rhythm
  - visual style
- explicitly support no-voiceover videos built on subtitle, gesture, and motion logic
- classify the video type so the result becomes a stronger upstream signal for Scenes `05`, `17`, and `19`

Likely owners:

- `scripts/scene_report_presets.py`
- `scenarios/04-single-video-breakdown.md`
- `references/scene-report-contract.md`

### Scene 05 - Reverse-Engineer Video Prompt / Brief

Priority: `P1`

Required parity upgrades:

- adopt the fixed generator-ready schema from the public material:
  - `Style`
  - `Environment`
  - `Tone & Pacing`
  - `Camera`
  - `Lighting`
  - `Character`
  - `Shots`
  - `Background Sound`
  - `Transition / Editing`
- add shot-level output with fields such as:
  - duration
  - scene
  - subject
  - action
  - overlay or voiceover
- split the workflow into two explicit modes:
  - infer the original brief
  - adapt the brief for the user's product
- make the output cleaner as a downstream handoff for generation backends such as Sora-, Veo-, and image-model workflows
- push low-confidence marking down to field level, not only at report level

Likely owners:

- `scripts/scene_report_presets.py`
- `scenarios/05-reverse-engineer-video-prompt.md`
- `references/scene-report-contract.md`

### Scene 07 - Category Market Insight

Priority: `P1`

Required parity upgrades:

- add keyword extraction from titles and hashtags, not only from video conclusions
- standardize a decision table:
  - keyword
  - content heat
  - product performance
  - decision
  - why
- force explicit `do`, `do not do`, and `priority do` conclusions
- keep demand heat and product-side proof as separate dimensions
- add compact insight cards with top keywords, competition, demand strength, and one-line judgment

Likely owners:

- `scripts/scene_report_presets.py`
- `references/scene-quick-reference.md`

### Scene 08 - Comment Mining / Persona

Priority: `P1`

Required parity upgrades:

- design for cross-product merging by default instead of only single-product summarization
- preserve source-product labels all the way into the merged insight layer
- align the report to four stable blocks:
  - purchase factors
  - praise keywords
  - complaint pain points
  - price-band differences
- separate category-level base value from category-level improvement opportunity
- end with product-positioning and marketing-angle recommendations, not only persona notes

Likely owners:

- `scripts/import_tiktok_capture_pack.py`
- `scripts/scene_report_presets.py`
- `references/scene-report-contract.md`

### Scene 17 - Creator Distillation

Priority: `P1`

Required parity upgrades:

- add an account overview layer:
  - one-line positioning
  - average views
  - average likes
  - average comments
  - average shares
  - breakout rate
  - posting cadence
- compare high-interaction versus low-interaction content instead of only distilling commonality
- extract 3-5 hook formulas with:
  - original example
  - reusable template
- output a reusable script pacing model or time-line formula
- keep dedicated sections for:
  - visual style
  - BGM
  - hashtags
  - posting time
- make the distillation end in a new-script bridge rather than admiration or summary only

Likely owners:

- `scripts/scene_report_presets.py`
- `scenarios/17-creator-distillation.md`
- `references/scene-report-contract.md`

### Scene 18 - Competitor Account Weekly Report

Priority: `P1`

Required parity upgrades:

- treat 3-5 accounts as a horizontal monitoring matrix, not a stack of isolated summaries
- enforce a fixed weekly frame:
  - what they posted
  - which post broke out
  - what changed strategically
- strengthen cross-account comparison as a first-class report layer
- add breakout attribution, not only content inventory
- add strategy-shift detection as a stable operator output

Likely owners:

- `scripts/scene_report_presets.py`
- `scripts/run_scene_workflow.py`

### Scene 19 - Self-Account Retro And Optimization

Priority: `P1`

Required parity upgrades:

- make high-performer versus low-performer grouping the primary analytic lens
- force stronger conclusions:
  - do more
  - do less
  - stop
  - test next
- cluster by content mode before drawing performance conclusions
- tie content traits more explicitly to growth or ROI decisions when evidence allows
- end with a next-cycle testing plan, not only retrospective commentary

Likely owners:

- `scripts/scene_report_presets.py`
- `scripts/run_scene_workflow.py`

### Cross-Scene Platform-Fidelity Upgrades

Priority: `P1`

These apply across the 10 runtime-confirmed scenes above:

- strengthen Feishu-style spreadsheet and document output surfaces across `md`, `docx`, and especially `xlsx`
- organize scene outputs more like project-space artifacts and less like isolated prompt dumps
- deepen asset reuse between scenes so the same evidence can flow from collection to teardown to briefing
- reserve cleaner handoff fields for downstream model or renderer selection even when no final generator is attached yet
- keep outputs template-like and reusable, following the style shown by the lipstick teardown report instead of one-off notes

## 2026-05-08 Doc-Driven Full-Parity Gap List

This section is derived directly from the three reviewed source docs under `E:\22222222222222\99999\`:

- `Clipcat 使用手册🔥.docx`
- `ClipcatSkill - 让 OpenClaw 创作Tiktok爆款短视频.docx`
- `口红爆款视频拆解报告.docx`

The standard here is not "good enough as a Codex skill". The standard is "close as possible to the public Clipcat/OpenClaw platform behavior and delivery surface without unsafe automation claims."

### P0. Platform-Surface Gaps Still Not Fully Replicated

These are the largest parity gaps left after the current scene/runtime work.

- add Feishu-style delivery adapters instead of only local `md/docx/xlsx/json`
  - append-to-same-sheet behavior
  - fixed header preservation
  - date/week stamp append rules
  - report-plus-table dual delivery
- add a project-space execution layer instead of only file-first workflows
  - creative-director step
  - writer/screenwriter step
  - director/execution step
  - one-script vs four-variant branching state
- add async generation-job semantics for generation scenes
  - submit task
  - save `job_id`
  - re-check status later
  - collect finished asset links
- add reusable asset-library semantics
  - historical uploads
  - reusable reference videos
  - reusable product images
  - scene-to-scene asset carry-forward
- add final-renderer hook points for video/image production scenes
  - the docs describe completed video/image generation, not only briefs

Likely owners:

- `scripts/run_operator_workflow.py`
- `scripts/start_project_workflow.py`
- `references/direct-use.md`
- `references/automation-workflows.md`
- future adapter scripts under `scripts/`

### P0. Scene 06 External Data Boundary Still Needs Real Completion

The docs explicitly present TikTok Shop product/detail/comment capability as a product feature, not a future note.

Required parity upgrades:

- real product search entrypoint
- product detail fetch shape
  - price
  - sales
  - rating
  - review count
  - logistics/store info where available
- product comment fetch shape
- daily competitor-product watch semantics
- daily delta / anomaly alert semantics

Current status:

- this is still the biggest scene-level parity hole
- document it as missing data-source boundary until a safe source is attached

### P1. Scene 01 Must Feel Like A Search Board, Not Only A Report

Doc-derived gaps still open:

- strengthen the board feel around:
  - publish window
  - market
  - sort mode
  - TikTok Shop cart-only filter
- make the exported `xlsx` primary enough to resemble the "collect to Feishu table" expectation
- add clearer board columns for:
  - worth studying because
  - suitable product/category reuse
  - shopping/cart intent
  - commerce confidence
- persist stronger shortlist provenance:
  - which query found it
  - which lane it belongs to
  - why it escalates into Scene `03`
- add "viral community / template library" style grouping over repeated winners

### P1. Scene 02 Must Behave More Like A Scheduled Ops Product

Doc-derived gaps still open:

- strengthen daily append semantics:
  - same table
  - same headers
  - append by run date
  - preserve historical comparisons
- make the daily summary look more like a real operator digest:
  - today's new breakouts
  - today's upward movers
  - repeated hook families
  - what deserves teardown next
- strengthen multi-keyword and multi-category patrol board behavior
- add clearer weak-signal archive vs strong-signal escalation logic
- add delivery-layer semantics for scheduled follow-up, not only local output files

### P1. Scene 03 Still Needs More "Creation-Ready" Breakdown Depth

Doc-derived gaps still open:

- make the `TOP 3` or equivalent shortlist logic even more explicit in the exported report
- keep full-script extraction quality improving when captions are sparse
- add stronger cross-video common-pattern matrix:
  - hook
  - conversion phrasing
  - visual structure
  - duration rhythm
- push the report further from "analyst note" toward "creative playbook"
- add stronger handoff to downstream replication scenes, not only narrative recommendation

### P1. Scene 04 Still Needs More Clipcat-Style Breakdown Texture

Doc-derived gaps still open:

- expand the "time segment | visual scene | spoken line" feel to be even closer to the lipstick teardown artifact
- improve BGM/audio-role interpretation from "present" to "what audio is doing strategically"
- strengthen no-voiceover handling when the video works through subtitle + action alone
- add stronger creator/product/video-type labels that can feed Scene `05`, `17`, and `19`
- continue tuning docx/xlsx layout so this scene reads like a premium teardown artifact, not a generic export

### P1. Scene 05 Still Needs Generator-Specific Handoff Branches

Doc-derived gaps still open:

- keep the current structured schema, but add more generator-specific packaging for:
  - Sora-style use
  - Veo-style use
  - image-to-video adaptation use
- expand field-level confidence marking
- make the two operating modes even more explicit:
  - infer original prompt
  - adapt into product-specific new brief
- add stronger character-consistency and asset-dependency flags because the docs emphasize repeatable roles and fixed personas

### P1. Scene 07 Still Needs Better "Should We Enter This Category" Logic

Doc-derived gaps still open:

- separate demand heat from supply saturation more aggressively
- add clearer white-space judgment:
  - hot but crowded
  - promising and under-served
  - weak and not worth entering
- strengthen keyword cluster output so it resembles a decision board, not only an insight memo
- keep the final decision cards compact and operator-facing

### P1. Scene 08 Still Needs More Category-Level Comment Intelligence

Doc-derived gaps still open:

- deepen cross-product merging so the final artifact clearly feels category-level, not product-level
- keep source-product labels visible through all merged findings
- make the 4-block output shape stricter:
  - purchase factors
  - praise keywords
  - complaint pain points
  - price-band differences
- strengthen quote-level traceability for each insight
- add stronger jump from comment insight to:
  - positioning advice
  - messaging angle
  - product-improvement hypothesis

### P1. Scene 17 Still Needs Stronger "Formula System" Delivery

Doc-derived gaps still open:

- add series clustering before distillation when possible
- make each hook formula easier to reuse as a literal template
- expand pacing-model output so it can become a script blueprint with minimal editing
- keep visual/BGM/hashtag/posting-time sections stronger and more comparable
- tighten the final bridge from creator distillation into a new script request

### P1. Scene 18 Still Needs Multi-Week Competitor Matrix Depth

Doc-derived gaps still open:

- move from one-week good report to true multi-week matrix where data exists
- compare accounts horizontally by:
  - posting volume
  - breakout lane
  - hook family
  - strategic shift
- strengthen strategy-change detection rather than only "best posts this week"
- make the final weekly digest feel closer to a platform ops dispatch and less like a static report artifact

### P1. Scene 19 Still Needs Better Owned-Account Decision Quality

Doc-derived gaps still open:

- extend beyond content-performance recap into stronger next-cycle experiment planning
- make content-mode clustering more foundational before comparing winners and losers
- add best-posting-time and best-duration logic where data exists
- tie recommendations more explicitly to business outcomes when owned conversion/ROI evidence is available
- move toward a true "what to make next week" operating sheet

### P1. Video-Generation Scenes 09-13 Still Lack True Execution Parity

The docs describe these scenes as result-delivery capabilities, not only briefs.

Scene-level platform gaps:

- `09`
  - missing actual replication job submit / poll / retrieve flow
- `10`
  - missing actual image-to-video render backend
- `11`
  - missing full async loop:
    - search
    - shortlist
    - analyze
    - submit 3 jobs
    - save `job_id`
    - re-check later
    - collect finished links
- `12`
  - missing true multi-style batch generation result layer
- `13`
  - missing true multi-market batch generation result layer

### P1. Ecommerce-Image Scenes 14-16 Still Lack True Render Parity

The docs describe real image outputs and not only planning artifacts.

Scene-level platform gaps:

- `14`
  - missing actual full asset-family generation backend
- `15`
  - missing true translated-image output pipeline
- `16`
  - missing competitor-main-image analysis -> image generation closed loop

### P2. Enterprise And Notification Semantics Still Need A Safe Codex Equivalent

Doc-derived gaps still open:

- Feishu push
- DingTalk push
- WeChat push
- "message me when done" semantics for async jobs
- scheduled operator notification layer for patrol, weekly report, and product watch workflows

### P2. Role And Persona Consistency Still Need Better Representation

The docs repeatedly emphasize:

- fixed on-screen role consistency
- creative-director / writer / director collaboration
- multi-variant production

Remaining parity work:

- reserve better role-consistency fields in report/output contracts
- store persona/character requirements as reusable assets
- make 1-video vs 4-variant branching more explicit in workflow outputs
- add stronger "director-ready" and "writer-ready" intermediate artifacts

### Implementation Order For This Public-Parity Pass

1. land the public-source backlog in durable docs
2. upgrade Scene `04`, Scene `05`, and Scene `17` output structure first
3. validate preset integrity and doc references
4. then continue with Scene `01`, `02`, `03`, `07`, `08`, `18`, and `19`
