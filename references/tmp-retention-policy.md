# Tmp Retention Policy

This file defines how `tiktok-growth-operator.skill` should treat historical `tmp/` outputs and validator runtimes.

## Intent

- keep real historical runs available as evidence when they still explain platform parity or runtime behavior
- stop validators from treating old `tmp/` trees as their primary source of truth
- avoid manual one-by-one cleanup as the maintenance model

## Directory Split

Treat these roots differently:

- `tiktok-growth-operator.skill/testdata/validation/`
  - durable validator fixtures
  - package-owned
  - safe to depend on from validators
- `.codex-tmp/tgo-validate-*`
  - disposable validator execution roots
  - created only through `scripts/validator_runtime.py`
  - eligible for automatic age-based cleanup
- `tiktok-growth-operator.skill/tmp/2026050*_...`
  - historical operator runs, inspections, rerenders, and parity evidence
  - not validator-first inputs unless explicitly promoted

## Rules

1. Do not hand-delete historical `tmp/20260507_*` runs as routine maintenance.
2. If a validator needs data from a historical run more than once, promote the smallest stable subset into `testdata/validation/`.
3. If an old run only matters for display cleanup, use `scripts/rerender_scene_outputs.py` against that run instead of editing outputs by hand.
4. If a validator only needs a throwaway runtime, create it under `.codex-tmp/tgo-validate-*` and let `scripts/validator_runtime.py` manage cleanup.
5. Keep real parity evidence roots referenced in docs until an equivalent package-owned fixture or newer confirmed run replaces them.

## Preferred Cleanup Mechanisms

- validator temp cleanup:
  - `scripts/validator_runtime.py`
  - automatically removes old `.codex-tmp/tgo-validate-*` directories by age
- historical export normalization:
  - `scripts/rerender_scene_outputs.py`
  - use `--match`, `--since`, `--limit`, and `--summary-path`
- fixture promotion:
  - copy only the minimum stable files into `testdata/validation/`
  - update validator references to prefer the promoted fixture

## What Not To Do

- do not point new validators at arbitrary `tmp/` history first
- do not treat `.codex-tmp/` outputs as durable evidence
- do not delete old runs only because they are visually noisy in Explorer
- do not mix validator-temp cleanup and historical-evidence cleanup into one blunt script
