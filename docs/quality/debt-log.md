# Debt Log

Track known issues that are real but not yet worth fixing immediately.

## Entry Template

```md
## YYYY-MM-DD - Short title
- Area: <path-or-domain>
- Type: duplication | stale-doc | boundary | naming | test-gap | performance | other
- Evidence: what was observed
- Risk: low | medium | high
- Suggested fix: smallest reasonable next step
- Status: open | planned | fixed
```

## Entries

<!-- Add new entries below this line -->

## 2026-04-26 - Workspace zone boundaries are implicit
- Area: repository root
- Type: boundary
- Evidence: durable skill packages, temp runs, generated outputs, and imported projects are mixed at the top level without a previously documented ownership model
- Risk: medium
- Suggested fix: keep this Harness map updated and gradually move repeated one-off utilities into `scripts/` or the owning skill package
- Status: open

## 2026-05-04 - Export validator does not inspect DOCX internals
- Area: `tiktok-growth-operator.skill/scripts/validate_export_outputs.py`
- Type: test-gap
- Evidence: the export regression suite confirms render success and XLSX structure, but it only checks DOCX file existence, not bookmarks, captions, or navigation links
- Risk: medium
- Suggested fix: add a lightweight DOCX structure check using `python-docx` to assert cover metadata presence, section bookmarks, and navigation text
- Status: fixed

## 2026-05-04 - Reference set is still partially duplicated
- Area: `tiktok-growth-operator.skill/references/`
- Type: duplication
- Evidence: `direct-use.md`, `automation-workflows.md`, and `final-handoff.md` intentionally overlap on entrypoints and validation commands to stay usable from multiple paths
- Risk: low
- Suggested fix: if the reference set grows further, extract one compact command index and let the others point to it instead of repeating command blocks
- Status: fixed

## 2026-05-05 - Batch validation does not yet exercise board execution
- Area: `tiktok-growth-operator.skill/scripts/validate_all_workflows.py`
- Type: test-gap
- Evidence: the current suite now asserts batch board preview payloads, but it still does not execute a generated board queue end-to-end inside batch mode
- Risk: low
- Suggested fix: add one hermetic batch fixture that points at a stable local template bundle and runs `mode: board` with `generate` plus board-local `dry_run`
- Status: fixed

## 2026-05-04 - Some generated Markdown source text had mojibake
- Area: `tiktok-growth-operator.skill/SKILL.md`, `tiktok-growth-operator.skill/references/`
- Type: stale-doc
- Evidence: invocation examples, prompt blocks, source names, and article wording contained garbled Chinese text before the final review pass
- Risk: medium
- Suggested fix: keep `validate_skill_docs.py` enforcing mojibake detection on the core operator docs and extend coverage if more references become operator-facing
- Status: fixed

## 2026-05-04 - Workspace is still effectively uninitialized for normal git history
- Area: repository root
- Type: other
- Evidence: `git ls-files` returns 0 and there is no configured remote, so version-control closure can only be local until the workspace is intentionally initialized or connected
- Risk: medium
- Suggested fix: decide whether this workspace should become a real tracked repository, then add the desired remote and baseline commit strategy before relying on branch/PR workflows
- Status: open

## 2026-05-05 - Board validation still depends on one local exported bundle fixture
- Area: `tiktok-growth-operator.skill/scripts/validate_all_workflows.py`
- Type: test-gap
- Evidence: the earlier hermetic board execute smoke depended on a locally available `.codex-tmp/preset-template-bundle-v9` tree instead of building its own fixture inside validation
- Risk: medium
- Suggested fix: generate a minimal fixture on demand inside validation or check in one small stable fixture owned by the skill package
- Status: fixed

## 2026-05-05 - Natural-language route quality is still heuristic-first
- Area: `tiktok-growth-operator.skill/scripts/run_operator_workflow.py`, `tiktok-growth-operator.skill/scripts/recommend_entry_board.py`
- Type: test-gap
- Evidence: board, scene, goal, and capture-pack routing is now explainable and now uses a versioned route-eval fixture corpus in `references/route-eval-fixtures.json`, asserted by `scripts/validate_all_workflows.py` across both the unified router and the board recommender
- Risk: medium
- Suggested fix: keep growing the fixture set with real operator requests whenever routing rules change, instead of adding ad hoc one-off assertions only in validator code
- Status: fixed

## 2026-05-07 - Platform-parity gaps are now external boundaries, not package ambiguities
- Area: `tiktok-growth-operator.skill/references/clipcat-openclaw-parity-audit.md`
- Type: boundary
- Evidence: scenes `02` and `06`, final media rendering, delivery pushes, and privileged account mutation still depend on source-platform credentials, render backends, or external integrations rather than missing package templates
- Risk: low
- Suggested fix: keep these gaps labeled as external boundaries in parity docs instead of letting them drift back into ambiguous “unfinished feature” status
- Status: fixed

## 2026-05-08 - Validation fixtures still depend on mutable temp outputs
- Area: `tiktok-growth-operator.skill/scripts/validate_export_outputs.py`, `tiktok-growth-operator.skill/scripts/validate_capture_pack_workflows.py`
- Type: test-gap
- Evidence: this started as a real gap when validators still depended on `tiktok-growth-operator.skill/tmp/*` historical runs and external `E:\tiktok\TikMatrix\tmp\...` roots; as of May 8, 2026, the remaining Scene `02` patrol validation path was moved to package-owned `testdata/validation/tikmatrix/*`, and the current green validator surface is now driven by package-owned fixtures first
- Risk: low
- Suggested fix: optional next cleanup is to document the fixture inventory under `testdata/validation/` and further reduce validator writes into `tmp/` during execution, but no functional dependency on external mutable roots remains
- Status: fixed

## 2026-05-08 - Historical tmp retention policy was implicit
- Area: `tiktok-growth-operator.skill/references/tmp-retention-policy.md`, `tiktok-growth-operator.skill/testdata/validation/README.md`
- Type: stale-doc
- Evidence: validator runtimes had already moved to `.codex-tmp/tgo-validate-*`, but the package still lacked one explicit rule set distinguishing disposable validator roots from historical parity-evidence roots under `tiktok-growth-operator.skill/tmp/`
- Risk: low
- Suggested fix: publish one package-level tmp retention policy and point validation docs at it so cleanup behavior is documented instead of tribal knowledge
- Status: fixed

## 2026-05-10 - Root temp-directory retention is still ambiguous
- Area: workspace root `.codex-tmp/` and root-level `tmp*` directories
- Type: boundary
- Evidence: low-risk cleanup safely removed root caches, lock files, and root-level `tmp*` or `_tmp*` files, but `.codex-tmp/` still contained 643 entries spanning validator runs, smoke outputs, exported artifacts, and named scenario checks that may still carry evidence value
- Risk: medium
- Suggested fix: document one root-level retention rule that distinguishes disposable validator scratch paths from historical evidence directories, then add an automated cleanup script that only removes the disposable class
- Status: open
