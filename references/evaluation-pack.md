# Evaluation Pack

## High-Frequency Success Cases

- `case_01`: user asks for a TikTok viral search workflow and the skill routes to `search`
- `case_02`: user asks for a single-video teardown and the skill routes to `breakdown` or a Codex-only teardown
- `case_03`: user asks for category insight and the skill combines `search_items`, `product_detail`, or report templates correctly

## High-Risk Confirmation Cases

- `case_04`: user asks to replicate a viral video and the skill shows the planned `clipcat replicate` command before executing
- `case_05`: user asks to generate product video or images and the skill warns about paid async execution

## Tool Failure Cases

- `case_06`: `clipcat` is not installed; the skill downgrades to analysis/planning mode
- `case_07`: API key is missing; the skill explains the missing credential instead of faking execution

## Long-Context Cases

- `case_08`: user provides multiple long materials and the skill compresses them into a clean feature map instead of echoing raw text

## Mode Switching Cases

- `case_09`: user begins with strategy only, then asks to execute; the skill switches from `codex_only` to `clipcat_cli` cleanly

## Release Gate

Treat this package as valid only if:

- the public command map matches current `clipcat --help` output
- paid commands are never treated as silent defaults
- async behavior is documented clearly
- reproduction claims stay within public evidence
