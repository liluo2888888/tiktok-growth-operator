# Prompt Runtime Design

## Goal

Convert a “Clipcat-style TikTok growth request” into a pure Codex execution path with no dependency on Clipcat CLI.

## Runtime Layers

### 1. Router layer

Map the request into one or more scenario IDs.

Primary route keys:

- search
- teardown
- product
- comments
- replication
- video brief
- image brief
- creator/account
- retrospective

### 2. Evidence layer

Before writing conclusions, decide what evidence exists:

- live links
- spreadsheets
- screenshots
- transcripts
- exported comments
- user notes only

If the evidence is thin, downgrade the workflow from `execution` to `preparation + synthesis`.

### 3. Scenario layer

Each scenario owns:

- minimum inputs
- workflow steps
- direct prompt
- output contract
- fallback path

### 4. Shared synthesis layer

Use reusable prompt blocks for:

- ranking
- teardown
- comment mining
- creator distillation
- script generation
- localization
- test matrix design

### 5. Delivery layer

Default to:

- concise summary first
- then the core logic
- then reusable next actions

## Execution Modes

### `live-analysis`

Use when fresh URLs or current market/account data are available and can be checked.

### `evidence-pack-analysis`

Use when the user provides local docs, spreadsheets, screenshots, or exports.

### `planning-only`

Use when the user wants the exact workflow and prompts before collecting evidence.

## Fallback Pattern

If a scenario cannot be fully executed:

1. state the missing evidence
2. provide the exact collection checklist
3. provide the ready-to-run prompt template
4. provide the expected output shape

## Reuse Pattern

Do not rewrite the whole methodology every time.

Instead:

1. route
2. load one scenario file
3. load shared templates only if needed
4. execute
