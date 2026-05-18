# TikTok Growth Operator Local PR Handoff

## Branch

- branch: `codex/tiktok-growth-operator-finish`
- local HEAD: `7a9642e` (pushed to `origin/codex/tiktok-growth-operator-finish`)
- skill subtree branch: `tiktok-growth-operator-main` → `origin/main` at `ace6b61`
- historical commit range on this line: `34c8344..7a9642e`

## Local Commits

- `1a6b713` feat(tiktok-growth-operator): add P1 schedules and Feishu structured board delivery
- `388b561` P1: comment pipeline, evidence refs, content graph, and Scene 02 patrol
- `a0cd67d` Add entry board selector and starter launcher
- `1841fc1` fix: close tiktok board routing and export validation
- `03a1776` fix: complete board batch validation and handoff docs
- `05e5027` test: add hermetic board batch execute smoke
- `34b9262` docs: add local PR handoff for tiktok operator
- `8e6716f` fix: harden board routing and goal run naming
- `3414056` docs: tighten handoff and debt notes
- `3985225` feat: add scene execution templates
- `a815237` feat: finalize tiktok direct-use templates and validation fixtures
- `39d60b2` feat: add creative brief quick refs and route eval fixtures
- `f501e16` feat: harden creative scene handoff contracts
- `98a94e4` feat: add creative production handoff packs

## Scope

This branch closes the TikTok Growth Operator board-entry line across:

- entry-board recommendation
- starter-board scaffolding
- unified router `board` mode
- project-launcher `board` mode
- batch-runner `board` mode
- batch preview reporting
- board execute smoke validation
- route-quality hardening for board-vs-scene-vs-goal requests
- long goal-run naming safety for Windows path length pressure
- scene-level direct-use execution templates across all 19 scenes
- scene quick-reference generation
- creative-brief quick references and route-eval fixtures
- creative production handoff packs for scenes `09` to `16`
- handoff and validation docs
- P1 operator schedules for scenes `01`–`08`, `17`–`19` with `operator_schedule_scene_*.json`
- structured Feishu board append (`scene01_collection_board` … `scene19_account_retro`) via registry
- one-click `--push-feishu` on `start_capture_pack_run.py`, `run_scene0203.py`, and `run_scene1819.py` (doc + board append by default)

## User-Facing Outcome

- operators can now ask for role-first, cadence-first, outcome-first, or vertical-first board starters through the same durable package
- batch orchestration understands `mode: board` directly
- board preview artifacts now surface bundle root, ranking count, and starter-run flags clearly
- starter folders now expose a clearer handoff order from scaffold to queue generation to dry-run to rerun
- scenes `09` to `16` can now hand off directly into production-facing creative packs instead of stopping at strategy briefs
- daily patrol / weekly competitor flows can push both Feishu doc bundles and fixed-header Bitable rows in one command

## Validation Run

Passed locally (2026-05-18):

- `python tiktok-growth-operator.skill/scripts/validate_platform_p0.py`
- `python tiktok-growth-operator.skill/scripts/validate_scene_ops.py`
- `python tiktok-growth-operator.skill/scripts/validate_capture_pack_workflows.py`

Feishu one-click smoke (credentials from `D:\hermes\.env`, scope `oneclick-smoke-20260518`):

- `run_scene0203.py --source fixture --push-feishu` → doc/bundle `status: ok`, `scene02_patrol_board` append `records_created: 5`
- `run_scene1819.py --preset matrix --scene18-only --push-feishu` → doc/bundle `status: ok`, `scene18_competitor_weekly` append `status: ok`

Earlier passes still apply:

Passed locally:

- `python -m py_compile "tiktok-growth-operator.skill\scripts\recommend_entry_board.py" "tiktok-growth-operator.skill\scripts\start_entry_board.py" "tiktok-growth-operator.skill\scripts\batch_run_operator_workflows.py" "tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- `python -m py_compile "tiktok-growth-operator.skill\scripts\generate_scene_report.py" "tiktok-growth-operator.skill\scripts\scene_report_presets.py" "tiktok-growth-operator.skill\scripts\generate_scene_quick_reference.py" "tiktok-growth-operator.skill\scripts\validate_scene_presets.py" "tiktok-growth-operator.skill\scripts\validate_skill_docs.py" "tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`
- `python "tiktok-growth-operator.skill\scripts\generate_scene_quick_reference.py"`
- `python "tiktok-growth-operator.skill\scripts\generate_creative_brief_quick_reference.py"`
- `python "tiktok-growth-operator.skill\scripts\validate_scene_presets.py"`
- `python "tiktok-growth-operator.skill\scripts\validate_skill_docs.py"`
- `python "tiktok-growth-operator.skill\scripts\validate_capture_pack_workflows.py"`
- `python "tiktok-growth-operator.skill\scripts\validate_export_outputs.py" --output-root ".\tiktok-growth-operator.skill\tmp\20260505_export_validation_suite_rerun"`
- `python "tiktok-growth-operator.skill\scripts\validate_all_workflows.py"`

Key assertions now covered by `validate_all_workflows.py`:

- board-style routing resolves to `board`
- weekly competitor review resolves to `board`
- `给我一个日常运营板` resolves to `board`
- `我想做一个美妆TikTok日更运营板` resolves to `board` and picks `beauty-us-ops-starter`
- `帮我做一个多市场本地化发布流程` resolves to `goal`
- long workflow requests return a bounded `run_name`
- every scene now has a required Chinese and English `execution_template`
- the quick-reference index regenerates clean UTF-8 Chinese direct-call text
- route-eval fixtures now assert board and goal routing expectations explicitly
- scenes `09` to `16` now validate stronger creative production handoff sections
- batch preview preserves board fields
- hermetic batch board execute smoke creates:
  - starter root
  - generated queue
  - preset report
  - batch report
  - batch result JSON

## Review Summary

- correctness: no blocking issues found in the final review pass
- architecture: changes stay inside the owning package and validator layer
- security: no new unsafe external automation path was introduced
- debt: the batch-board execute validation gap is now closed locally
- debt: board validation no longer depends on a preexisting `.codex-tmp` bundle tree
- debt: creative-scene production handoff is now a first-class validated pack, not a manual post-step
- residual risk: natural-language routing is still heuristic and should eventually grow into a corpus-driven eval set

## 2026-05-18 Business Run (Real TikTok + Capture-Pack)

### Live TikMatrix collection (blocked)

- Runtime: `E:\tiktok\TikMatrix\.venv-api\Scripts\python.exe` (not `.venv`)
- Attempt: `profile-posts-browser-download` → `https://www.tiktok.com/@tiktok`, `count=3`
- Result: **failed** — Playwright `Page.goto: net::ERR_CONNECTION_TIMED_OUT` (no fresh `profile_posts.json` under `E:\tiktok\TikMatrix\tmp\`)
- Unblock: stable access to `tiktok.com` (proxy/VPN if required), then re-run the command in `references/direct-use.md` §真实 TikMatrix Bridge; use `.venv-api` path in docs until `.venv` is restored

### TikMatrix → operator bridge (passed, validation exports)

Hermetic exports under `tiktok-growth-operator.skill/testdata/validation/tikmatrix/`:

```powershell
cd "D:\我的文档\Documents\Playground 4\tiktok-growth-operator.skill"
python scripts/run_tikmatrix_capture_bridge.py `
  --profile-posts-json "testdata\validation\tikmatrix\live-profile-posts-browser-batch\mrorangecat555\profile_posts.json" `
  --downloads-json "testdata\validation\tikmatrix\skill-batch-download\downloads.json" `
  --scene 01 --name bridge-validation-20260518 `
  --project "TikMatrix Bridge Validation" --market US --min-likes 100 --qualified-count 3 `
  --formats md,json --output-root "tmp\20260518_tikmatrix_bridge_live"
```

- `qualified_count: 2`, report: `tmp/20260518_tikmatrix_bridge_live/operator-run/scene-01/scene-01-bridge-validation-20260518.json`

### Capture-pack business scenes (passed, real pack layout)

Fixture pack: `testdata/validation/captures/tiktok-analysis-pack-smoke-20260423f`

```powershell
$cap = "testdata\validation\captures\tiktok-analysis-pack-smoke-20260423f"
$out = "tmp\20260518_real_business_capture_pack"
foreach ($s in "01","04","05","07") {
  python scripts/start_capture_pack_run.py --scene $s --capture-root $cap `
    --name "business-smoke-20260518-s$s" --project "Business Smoke 20260518" `
    --output-root $out --formats md,json
}
```

- Reports under `tmp/20260518_real_business_capture_pack/scene-0{1,4,5,7}/`
- Optional next: add `--push-feishu` (credentials from `D:\hermes\.env`) or run Scene `02`/`18` patrol flows from `direct-use.md`

## GitHub / PR Strategy (do not merge monorepo into skill `main`)

| Target | What to push | PR? |
|--------|----------------|-----|
| [tiktok-growth-operator `main`](https://github.com/liluo2888888/tiktok-growth-operator) | **Subtree only** — `tiktok-growth-operator.skill/` at repo root | No PR from `codex/tiktok-growth-operator-finish` (different history/layout) |
| `origin/codex/tiktok-growth-operator-finish` | Full Playground monorepo backup | Optional compare link for humans; **not** for merging into skill `main` |
| `playground-4` remote | Whole workspace branch | Create repo first, then `git push -u playground codex/tiktok-growth-operator-finish` |

Recommended close-out (no `gh` required):

1. `git subtree split --prefix=tiktok-growth-operator.skill -b tiktok-growth-operator-main`
2. `git push origin tiktok-growth-operator-main:main`
3. On GitHub: **Releases → tag** e.g. `v2026.05.18` on `main` with validation + Feishu smoke notes (optional)
4. If you need a review thread: open a **GitHub Issue** on `tiktok-growth-operator` with checklist (validators, Feishu smoke, Scene 06 live Partner later) — not a cross-repo PR

`gh auth login` only needed for `gh pr create` / `gh issue create` from CLI.

## Remaining Blocker

- `origin` is configured: `https://github.com/liluo2888888/tiktok-growth-operator.git`
- `gh` is not authenticated on this machine (`gh auth login` required) — PR creation still blocked until login
- Live TikTok browser collection blocked by network timeout to `tiktok.com` on this machine
- subtree push to `main` may still fail on network; retry locally if needed

### Unblock Checklist

双 remote（本机已配置）：

| Remote | URL | 用途 |
|--------|-----|------|
| `origin` | `https://github.com/liluo2888888/tiktok-growth-operator.git` | 子树推技能包到 `main` |
| `playground` | `https://github.com/liluo2888888/playground-4.git` | 推完整 Playground 分支（需先在 GitHub 建空仓库） |

```powershell
cd "D:\我的文档\Documents\Playground 4"

# A) 技能包 → tiktok-growth-operator main（仅 skill 目录）
git subtree split --prefix=tiktok-growth-operator.skill -b tiktok-growth-operator-main
git push -u origin tiktok-growth-operator-main:main

# B) Playground 整仓分支 → playground-4（先创建仓库：GitHub New repo「playground-4」，不要初始化 README）
git push -u playground codex/tiktok-growth-operator-finish

# 若 playground-4 尚未创建，也可先把 monorepo 分支推到 tiktok 仓库作备份分支：
git push -u origin codex/tiktok-growth-operator-finish
```

Playground 本地最新：`a68f63c`（`codex/tiktok-growth-operator-finish`）。子树 `main` 已推至 `592b642`；整仓分支 push 若遇 `Connection reset`，在本机网络稳定后重跑 B) 或 `origin` 备份分支命令。推送前可选 `git repack -a -d -f`（对象库约 4GB 松散对象时较慢）。

GitHub 账号：[liluo2888888](https://github.com/liluo2888888) · 仓库：[tiktok-growth-operator](https://github.com/liluo2888888/tiktok-growth-operator)

Scope the PR to `tiktok-growth-operator.skill/` plus this handoff report; do not sweep unrelated untracked workspace folders.

## Suggested PR Title

- `Complete TikTok operator handoff packs, validation fixtures, and final docs`

## Suggested PR Body

### Summary

- add and harden the board-entry surface for TikTok Growth Operator
- extend batch execution to support `mode: board`
- improve starter and batch handoff artifacts
- add hermetic execute-smoke coverage for board batch flows
- harden board routing quality and long goal-run naming safety
- add direct-use Chinese starter commands, creative quick references, and route-eval fixtures
- add validated creative production handoff packs for scenes `09` to `16`

### Testing

- ran compile checks for edited Python scripts
- ran `validate_skill_docs.py`
- ran `validate_export_outputs.py`
- ran `validate_all_workflows.py`

### Notes

- local branch is ready for push after remote configuration, but no remote work was performed
- workspace still contains many unrelated untracked files outside this feature line
