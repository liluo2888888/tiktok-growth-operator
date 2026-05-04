# Entry Selector

Use this file when the operator asks some version of:

- which board should I start with
- I know the outcome but not the preset slug
- I know my role or cadence but not the right template
- give me the fastest runnable starter for this request

The package now has six practical entry families. Choose the smallest family that matches how the operator is framing the work.

## Fast Rule

- use `single` when the request already maps to one narrow workflow
- use `combo` when you want several workflows bundled together without role, cadence, or vertical framing
- use `vertical` when the request is anchored to a niche, market, or seeded business context
- use `launch-board` when the request is outcome-first
- use `manager-board` when the request is role-first
- use `cadence-board` when the request is rhythm-first

## Family Guide

### `single`

Use this when the user already knows the workflow shape.

Examples:

- `I need competitor-to-publish for one beauty product`
- `给我一个 audience-to-live 工作流`

Best fit:

- one request
- one board
- minimal routing ambiguity

### `combo`

Use this when the user wants a combined board but is not framing the work as one role, one cadence, or one operating vertical.

Examples:

- `I want one board for competitor review plus publish prep`
- `给我一套从爆款拆解到测试的组合板`

Best fit:

- multi-preset need
- still generic
- operator wants a reusable board, not a seeded starter

### `vertical`

Use this when the request clearly belongs to a vertical or seeded business context.

Examples:

- `Give me the fastest beauty TikTok ops starter`
- `我做抖音美妆，直接给我一个能跑的 starter`

Best fit:

- beauty or another niche
- TikTok vs Douyin market defaults matter
- the board should come prefilled with practical defaults

### `launch-board`

Use this when the operator thinks in deliverables or this week's objective.

Examples:

- `I need a publish plan for this week`
- `我这周要做竞品复盘`
- `Set up a localization sprint`

Best fit:

- publish week
- competitor review
- comment-to-live conversion
- localization sprint
- viral testing sprint

### `manager-board`

Use this when the request is framed by the operator's responsibility.

Examples:

- `I'm the live operator for tonight's session`
- `我是内容运营，给我一个直接能开的板子`

Best fit:

- content operator
- live operator
- strategy operator
- growth operator

### `cadence-board`

Use this when the request is about the rhythm of work.

Examples:

- `Give me a daily board`
- `Set up my weekly competitor review`
- `我想要一个直播班次板`

Best fit:

- daily loops
- weekly review
- launch sprint
- live shift

## Current Best Slug By Intent

- publish this week -> `publish-week-board`
- tonight's live session -> `live-operator-board` or `live-shift-board`
- weekly competitor review -> `competitor-review-board` or `weekly-ops-board`
- beauty TikTok starter -> `beauty-us-ops-starter`
- beauty Douyin launch starter -> `douyin-beauty-launch-starter`
- ranked creator teardown starter -> `tiktok-ranked-creator-starter`
- one reusable growth board -> `growth-operator-board`
- one reusable daily board -> `daily-ops-board`

## Transparent Recommender

Use:

```powershell
python scripts/recommend_entry_board.py `
  --query "I need a publish plan for this week" `
  --format markdown
```

Turn one natural-language request directly into a local starter folder:

```powershell
python scripts/start_entry_board.py `
  --query "Give me a daily board for TikTok beauty ops"
```

Scaffold and immediately generate plus dry-run:

```powershell
python scripts/start_entry_board.py `
  --query "Give me a daily board for TikTok beauty ops" `
  --generate `
  --dry-run
```

If a recent `preset-template-bundle*` exists locally, both scripts now auto-discover it. You only need `--bundle-root` when you want to pin a specific bundle.

It returns:

- recommended entry family
- top board slugs
- matched signals
- fallback suggestions
- family-level score breakdown

Use JSON when another script or external tool needs the output:

```powershell
python scripts/recommend_entry_board.py `
  --query "我是今晚直播运营，帮我选入口板" `
  --format json
```

Use the unified router when you want the main operator surface to scaffold the board starter directly:

```powershell
python scripts/run_operator_workflow.py `
  --mode board `
  --query "Give me a daily board for TikTok beauty ops" `
  --generate `
  --dry-run
```

Auto mode can also resolve broad board-style requests into `board` when they are role-first, cadence-first, outcome-first, or seeded vertical requests rather than single-scene or multi-stage workflow requests.

## Operator Shortcut

If the operator does not know where to start:

1. run `recommend_entry_board.py`
2. pick the top slug
3. if that slug has a suite, use the suite-local `generate` -> `dry-run` -> `run` helpers
4. if the request is still too broad, move one family down:
   outcome -> role -> cadence -> combo

If you want the package to create a local starter folder for you, run `start_entry_board.py` instead of doing steps 1 to 3 manually.
