# Clipcat OpenClaw Parity Audit

This file records what `tiktok-growth-operator.skill` already reproduces from the public Clipcat/OpenClaw TikTok workflow, what is only partially reproduced, and what still depends on external infrastructure.

## Sources Audited

- Tencent Cloud article: [OpenClaw 集成抖音自动化引擎](https://cloud.tencent.com/developer/article/2640429)
  Public page date observed: March 18, 2026.
- Clipcat OpenClaw page: [clipcat.ai/tiktok/openclaw](https://clipcat.ai/tiktok/openclaw)
- Local DOCX: `E:\22222222222222\ClipcatSkill - 让 OpenClaw 创作Tiktok爆款短视频.docx`
- Local DOCX: `E:\22222222222222\Clipcat 使用手册🔥.docx`
- Local DOCX: `E:\22222222222222\口红爆款视频拆解报告.docx`

## Bottom Line

`tiktok-growth-operator.skill` already achieves strong parity for the operator-facing layer:

- all 19 documented business scenes exist as direct callable Codex prompts and workflow templates
- all 19 scenes have structured output contracts and scene-specific execution templates
- the package has a unified router, board mode, batch mode, quick references, and handoff packs
- real TikTok collector outputs from `E:\tiktok\TikMatrix` can already be bridged into the operator runtime without modifying the collector project

It does **not** fully reproduce the proprietary Clipcat/OpenClaw backend layer:

- no Clipcat CLI
- no Clipcat API key flow
- no hosted project-space UI
- no built-in final video render backend
- no built-in final ecommerce image render backend
- no Feishu push, DingTalk push, or WeChat push
- no official TikTok Shop or Douyin privileged API credentials
- no cloud-phone publishing, anti-detection, or risky engagement automation

## Capability Family Audit

| Capability family | Source expectation | Codex package status | Notes |
| --- | --- | --- | --- |
| 19 business scenes | Full public workflow coverage in the skill DOCX | Fully replicated | All 19 scenes exist in `scenarios/`, `scene_report_presets.py`, quick references, and direct-use templates |
| One-line prompts for operators | Clipcat/OpenClaw prompt-first usage | Fully replicated | Direct-use, quick-reference, and bilingual execution templates exist |
| Search, teardown, creator distillation, review outputs | Core Clipcat analysis value | Fully replicated | Markdown/JSON/DOCX/XLSX outputs and scene-aware reports are in place |
| Unified workflow entry | Better than source | Fully replicated and extended | `run_operator_workflow.py`, board mode, batch mode, and goal templates exceed the original public packaging |
| Real TikTok collection bridge | Source uses Clipcat/OpenClaw collection backends | Partially replicated | Real `TikMatrix` exports now feed the operator runtime through `run_tikmatrix_capture_bridge.py` |
| Video analysis from public TikTok links | Public Clipcat skill can analyze videos | Partially replicated | Strong at template/report level; real runtime depends on upstream collector evidence or manually supplied link evidence |
| Product-image-to-video generation | Clipcat directly renders videos | Partially replicated | Codex produces briefs, prompts, shot plans, and testing matrices, not final rendered videos |
| Viral replication generation | Clipcat directly renders new videos | Partially replicated | Codex reproduces replication logic and handoff packs; final rendering still requires another generator |
| Ecommerce image generation | Clipcat directly renders images | Partially replicated | Codex reproduces briefs, benchmark logic, localization instructions, and asset-family planning |
| Image translation final output | Clipcat claims direct translated images | Partially replicated | Scene 15 is intentionally a blueprint and review flow, not a fabricated OCR-and-redraw engine |
| Project-space multi-agent UI | Clipcat has Creative Director / Writer / Director style UI flow | Partially replicated | Codex mirrors this with reports, workspaces, and handoff packs, but not a hosted interactive UI |
| Logged-in account operations | newest reply, notice, following request, following or follower watch | Partially replicated | Safe operator pack now exists through TikMatrix account-ops bridge; no unsafe auto-mutation |
| Feishu table/doc delivery | Public docs repeatedly mention Feishu output | Missing by design | Package writes durable local artifacts instead of pushing to Feishu |
| DingTalk / WeChat integration | Enterprise product positioning | Missing by design | No chat-app push integrations in this package |
| Official TikTok Shop product APIs | Public Clipcat/OpenClaw skill can query product info/comments | Missing in this package | Current package focuses on operator logic and TikMatrix-fed TikTok evidence, not Shop API wrappers |
| Douyin official API / account automation | Tencent article covers official APIs and account management | Missing / external | Requires live credentials and a separate integration surface |
| Cloud-phone RPA publish automation | Tencent article covers Airtest/Appium/cloud phone flows | Explicitly not replicated | Excluded for safety and because no such runtime exists here |
| Risk-control / anti-detection | Tencent article covers disguise, behavior tuning, and similar tactics | Explicitly not replicated | Unsafe and out of scope |
| Auto-reply / hijack / spam conversion loops | Tencent article discusses interaction automation | Explicitly not replicated | Replaced by safe reply drafting and live-assist packs |

## Scene-Level Audit

Status legend:

- `Full template parity`: direct callable prompt/workflow template exists and matches the public scene intent
- `Real runtime confirmed`: already run end to end from real TikMatrix evidence or a real TikMatrix-derived capture pack in this workspace
- `Runtime supported`: supported by current capture-pack runtime but not yet revalidated in this audit pass
- `Prompt-first only`: good template parity exists, but current real collector bridge does not yet provide a dedicated end-to-end proof path
- `External-data boundary`: intentionally not claimed as real-runtime complete because the missing gap is a source-platform or renderer dependency, not a missing template

| Scene | Public intent | Codex parity | Real runtime status | Notes |
| --- | --- | --- | --- | --- |
| 01 | Viral video collection | Full template parity | Real runtime confirmed | Confirmed with richer real `mustsharenews` and `sherrinandyixi` exports on May 7, 2026, plus a restored original `.venv` `mustsharenews` run on May 7, 2026; ranked shortlist now carries stronger caption/hook/topic recovery where metadata exists |
| 02 | Daily category patrol | Full template parity | Real runtime confirmed | A local patrol runtime now exists inside this package: it can ingest TikMatrix search/topic evidence, persist snapshots, compute deltas and alerts, and now auto-chain the P1 queue into a real follow-on Scene 03 teardown run; remote scheduler/push integrations remain external |
| 03 | Batch viral search plus deep teardown | Full template parity | Real runtime confirmed | Confirmed with richer real `mustsharenews` and `sherrinandyixi` ranked shortlists on May 7, 2026, plus the real patrol-triggered handoff run on May 8, 2026; shortlist now feeds a deeper teardown with recovered hook/topic/authority fields where metadata exists |
| 04 | Single video breakdown | Full template parity | Real runtime confirmed | Confirmed from a real TikMatrix-derived ranked capture pack on May 7, 2026 and re-smoked again through the frozen single-video download fixture on May 8, 2026; the runtime reconstructs one ranked reference into hook, setup, proof, close, and adaptation paths |
| 05 | Reverse-engineer video prompt | Full template parity | Real runtime confirmed | Confirmed from a real TikMatrix-derived ranked capture pack on May 7, 2026; the runtime turns one ranked reference into a structured inferred brief with confidence boundaries |
| 06 | Competitor product dashboard | Full template parity | External-data boundary | TikTok Shop product/detail/comment data source is not implemented in this package |
| 07 | Category market insight | Full template parity | Real runtime confirmed | Confirmed from a real TikMatrix-derived ranked capture pack on May 7, 2026 |
| 08 | Multi-product comment mining and persona report | Full template parity | Real runtime confirmed | Confirmed with real `mrorangecat555` comments export on May 6, 2026 |
| 09 | Reference-video replication brief | Full template parity | Real runtime confirmed | Confirmed from a real TikMatrix-derived ranked capture pack on May 7, 2026; produces replication brief and downstream handoff packs |
| 10 | Product-image-to-video brief | Full template parity | Real runtime confirmed | Confirmed from a real TikMatrix-derived ranked capture pack on May 7, 2026 as a production-safe brief layer; final rendered video remains external |
| 11 | Hot-video replication pipeline | Full template parity | Real runtime confirmed | Confirmed with real `mrorangecat555` profile/download exports on May 7, 2026; final generation remains external |
| 12 | One-product multi-style testing matrix | Full template parity | Real runtime confirmed | Confirmed with real `mrorangecat555` profile/download exports on May 7, 2026 |
| 13 | Multi-market localization pack | Full template parity | Real runtime confirmed | Confirmed with real `mrorangecat555` profile/download exports and explicit target markets on May 7, 2026 |
| 14 | Launch asset family pack | Full template parity | Real runtime confirmed | Confirmed with real `mrorangecat555` profile/download exports on May 7, 2026 |
| 15 | Image translation brief | Full template parity | Real runtime confirmed | Confirmed as blueprint-only output from real `mrorangecat555` profile/download exports on May 7, 2026 |
| 16 | Competitor main-image benchmark | Full template parity | Real runtime confirmed | Confirmed with real `mrorangecat555` profile/download exports on May 7, 2026 |
| 17 | Creator distillation | Full template parity | Real runtime confirmed | Confirmed with real `mrorangecat555` profile export on May 6, 2026 |
| 18 | Competitor account weekly report | Full template parity | Real runtime confirmed | Confirmed with real `mrorangecat555` profile/download exports on May 7, 2026 |
| 19 | Self-account retro and optimization | Full template parity | Real runtime confirmed | Confirmed with real `mrorangecat555` profile/download exports on May 7, 2026 |

## What Is Already Proven In This Workspace

These end-to-end runs were already completed against real `TikMatrix` exports or real TikMatrix-derived capture packs:

- bounded Scene `02` patrol runtime from real TikMatrix search/topic exports:
  - `E:\tiktok\TikMatrix\tmp\search-live-orange-cat`
  - `E:\tiktok\TikMatrix\tmp\topic-live-orangecat`
- real TikMatrix bridge plus collector-backed runtime:
  - scenes `01` and `03` from `mustsharenews`
  - scenes `01` and `03` from `sherrinandyixi`
  - scenes `08`, `11`, `12`, `13`, `14`, `15`, `16`, `17`, `18`, and `19`
- real capture-pack runtime validation from `captures/tiktok-analysis-pack-smoke-20260423f`:
  - scene `04`
  - scene `05`
  - scene `07`
  - scene `09`
  - scene `10`
- real account-ops assist bridge validation from logged-in TikMatrix exports:
  - `newest_reply`
  - `notice_multi`
  - `following_request_list`
  - `following_list`
  - `follower_list`
  - `live_following`

Representative confirmed output roots:

- `tiktok-growth-operator.skill/tmp/20260507_010741-tikmatrix-bridge-mustsharenews-scene01-real-rerun`
- `tiktok-growth-operator.skill/tmp/20260507_010740-tikmatrix-bridge-mustsharenews-scene03-real-rerun`
- `tiktok-growth-operator.skill/tmp/20260507_010741-tikmatrix-bridge-sherrinandyixi-scene01-real-rerun`
- `tiktok-growth-operator.skill/tmp/20260507_010741-tikmatrix-bridge-sherrinandyixi-scene03-real-rerun`
- `tiktok-growth-operator.skill/tmp/20260507_014554-tikmatrix-bridge-mustsharenews-scene01-venv-restored`
- `tiktok-growth-operator.skill/tmp/20260507_014554-tikmatrix-bridge-mustsharenews-scene03-venv-restored`
- `tiktok-growth-operator.skill/tmp/20260507_validation_capture_scene04`
- `.codex-tmp/tgo-validate-capture-*/scene04_single_video`
- `tiktok-growth-operator.skill/tmp/20260507_validation_capture_scene05`
- `tiktok-growth-operator.skill/tmp/20260507_validation_capture_scene07`
- `tiktok-growth-operator.skill/tmp/20260507_validation_capture_scene09`
- `tiktok-growth-operator.skill/tmp/20260507_validation_capture_scene10`
- `tiktok-growth-operator.skill/tmp/20260507_validate_tikmatrix_account_ops_bridge`

Key result:

- the collector project stayed untouched
- the original `E:\tiktok\TikMatrix\.venv` runtime is restored and real-run confirmed for browser collection and browser download
- Scene `02` now has a local durable patrol loop that persists category state, computes deltas, emits alerts, and can auto-prepare a Scene `03` follow-up pack
- the operator package now produces scene outputs and derived handoff packs from real TikTok evidence across scenes `01`, `02`, `03`, `04`, `05`, `07`, `08`, `09`, `10`, `11`, `12`, `13`, `14`, `15`, `16`, `17`, `18`, and `19`
- the bridge enriches ranked-video evidence with downloaded single-video metadata when available, improving `Scene 01` shortlist quality and `Scene 03` teardown quality without touching the collector project
- logged-in inbox and relationship exports can now be synthesized into a safe `account-ops-assist` operator pack without mutating account state
- the main entrypoints and render/bridge layers now share one text-normalization path, and historical `scene-*.json` outputs can be re-rendered in batch through `scripts/rerender_scene_outputs.py`
- representative real-runtime `Scene 01`, `Scene 02`, and `Scene 03` exports were re-rendered and spot-checked again on May 7, 2026; current Markdown, DOCX, and XLSX outputs no longer show actual generated-file garbling, bidi control-character leakage, or the earlier Scene `03` Markdown table break
- the Scene 02 -> Scene 03 patrol-to-teardown chain was re-run on May 8, 2026 with rich-export QC; current DOCX/XLSX outputs no longer leak absolute workspace paths and now report `0` broken asset paths
- the Scene 02 -> Scene 03 chain was re-run again on May 8, 2026 at `tiktok-growth-operator.skill/tmp/20260508_scene02_scene03_chain_qc_v4`; current `Working Context`, `Notes`, DOCX cover pages, and XLSX summary sheets now read more like operator-facing deliverables than runtime dumps
- package-level validators were repaired and re-run on May 8, 2026; `validate_skill_docs.py`, `validate_scene_presets.py`, `validate_export_outputs.py`, `validate_capture_pack_workflows.py`, and `validate_all_workflows.py` are currently green again against the fixtures that still exist in this workspace
- validator history scanning is now isolated away from historical `tiktok-growth-operator.skill/tmp/*` roots by default, and validator temp creation/cleanup is centralized through `scripts/validator_runtime.py`

## Remaining Gaps To Full Public-Feature Parity

These are the main remaining gaps if the target is "looks and behaves like Clipcat/OpenClaw from the outside":

1. Final media generation backends
- final rendered short videos for scenes `09` to `13`
- final rendered ecommerce images for scenes `14` to `16`

2. Source-platform integrations
- TikTok Shop product/detail/comment APIs for scene `06`
- live direct platform hooks for richer scene `18` and `19` telemetry
- Douyin-specific data sources if the user wants China-side parity, not only TikTok parity

3. Delivery integrations
- Feishu table/doc push
- DingTalk / WeChat delivery
- scheduled notification loop

3a. Logged-in account mutation layer
- the package can now synthesize inbox and relationship exports into an operator pack
- it still does not auto-send replies, auto-approve requests, or mutate account state

4. Hosted operator experience
- web project-space UI
- multi-agent confirmation loop with interactive state
- reusable asset library UI

5. Enterprise-only external surfaces that this package intentionally avoids
- cloud-phone RPA publish automation
- account warm-up / `养号`
- risky engagement automation
- anti-detection / spoofing tactics

## Recommended Next Work

If continuing from here, prioritize in this order:

1. add optional downstream renderer hooks for scenes `09` to `16` so briefs can call a local or remote generation engine
2. add optional delivery adapters for Feishu-style export push without changing the core skill contract
3. add TikTok Shop product/detail/comment integrations for scene `06` without coupling them to the collector runtime
4. keep TikTok-only and Douyin-only data sources clearly separated instead of mixing assumptions

## 2026-05-07 Richer Real Account Reruns

Additional real reruns were completed against richer TikTok accounts to improve `Scene 01` and `Scene 03` proof quality without modifying `E:\tiktok\TikMatrix`.

- `mustsharenews`
  - collector root: `E:\tiktok\TikMatrix\tmp\codex-mustsharenews-profile-post-downloads-20260507\mustsharenews`
  - `Scene 01` output root: `D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260507_010741-tikmatrix-bridge-mustsharenews-scene01-real-rerun`
  - `Scene 03` output root: `D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260507_010740-tikmatrix-bridge-mustsharenews-scene03-real-rerun`
- `sherrinandyixi`
  - collector root: `E:\tiktok\TikMatrix\tmp\codex-sherrinandyixi-profile-post-downloads-20260507\sherrinandyixi`
  - `Scene 01` output root: `D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260507_010741-tikmatrix-bridge-sherrinandyixi-scene01-real-rerun`
  - `Scene 03` output root: `D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill\tmp\20260507_010741-tikmatrix-bridge-sherrinandyixi-scene03-real-rerun`

Current recommended real fixtures:

- use `mustsharenews` when you want longer captions, authority-led packaging, and mixed image/video evidence
- use `sherrinandyixi` when you want creator-native hooks, episodic caption patterns, and subtitle-rich video rows
- keep `mrorangecat555` only as a weaker fallback fixture, not the primary benchmark for `Scene 01` or `Scene 03`

## Audit Verdict

If the target is:

- "把 19 个场景都补成可直接调用的 prompt/workflow 模板"
  - status: effectively complete
- "用真实 TikTok 采集项目喂给这个 skill，真正跑通链路"
  - status: substantially complete for the current safe operator surface and already proven on real scenes `01`, `03`, `04`, `05`, `07`, `08`, `09`, `10`, `11`, `12`, `13`, `14`, `15`, `16`, `17`, `18`, and `19`, with the original `E:\tiktok\TikMatrix\.venv` chain restored and confirmed again on May 7, 2026
- "一模一样复刻 Clipcat/OpenClaw 的整个平台能力"
  - status: not complete, because the hosted generation backends, app integrations, and privileged automation surfaces are external and not present in this repo


