# 2026-05-17 TikTok Scene06 Product Data Closure

## Goal

Close the main Scene `06` parity gap by turning the existing TikTok Shop product sync helpers into an explicit, runnable, validated workflow entrypoint.

## Why This Task Exists

- `Scene 06` already has report templates and fallback logic.
- The repo already contains `tiktok_shop_source.py` and `sync_tiktok_shop_capture.py`.
- The main gap is workflow closure: the product sync path is not exposed clearly enough through the normal capture-pack and unified operator entrypoints.

## Scope

1. expose explicit Scene `06` shop-sync arguments on the durable capture-pack runner
2. pass those arguments through the unified `run_operator_workflow.py` entrypoint
3. trigger product sync before import when requested
4. add or strengthen one end-to-end validation path
5. update the direct-use docs so the new path is discoverable

## Non-Goals

- building a new risky collector
- adding unsafe automation
- rewriting the existing Scene `06` report contract
- coupling Scene `06` to unrelated TikMatrix account workflows

## Planned File Owners

- `tiktok-growth-operator.skill/scripts/start_capture_pack_run.py`
- `tiktok-growth-operator.skill/scripts/run_operator_workflow.py`
- `tiktok-growth-operator.skill/scripts/validate_platform_integrations.py`
- `tiktok-growth-operator.skill/references/direct-use.md`

## Validation

- Python compile for edited scripts
- targeted integration validation for the Scene `06` shop-sync path
- representative Scene `06` capture-pack smoke run using the mock shop HTTP fixture

## Result Notes

- Done locally on 2026-05-18: capture-pack and unified router expose `--shop-sync`; `validate_platform_integrations.py` passes (HTTP mock, verified-source guard, Scene 06 capture run, partner gateway mock, renderer HTTP).
- Remaining: run live gateway with real Partner credentials when available; check off §7 in `scene06-shop-gateway-spec.md` against production hosts.
