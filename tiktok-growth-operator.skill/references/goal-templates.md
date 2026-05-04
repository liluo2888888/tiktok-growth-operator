# Goal Templates

Use this file when the operator wants to describe an end-to-end TikTok or Douyin workflow in plain language instead of selecting one scene or one goal slug manually.

## Why This Exists

The 19 scenes are already usable one by one, but many real requests are multi-stage:

- topic selection -> testing -> publish handoff
- competitor monitoring -> weekly review -> creator breakdown
- account retro -> next testing cycle
- category research -> localization -> launch prep
- audience language mining -> live-room operator support

This template layer lets `scripts/recommend_scene_chain.py` and `scripts/start_goal_workflow.py` expand those requests into one merged workflow.

## Routing Rules

- match the user query against built-in workflow templates first
- if no template matches, fall back to the best single goal chain
- preserve scene order across component goals
- remove duplicate scenes
- preserve any derived operator packs from component goals

## Built-In Templates

### `topic-to-publish`

- description: go from topic selection to creative testing and publish handoff
- component goals: `category-entry`, `creative-testing`, `publish-handoff`
- merged chain: `01 -> 07 -> 08 -> 09 -> 10 -> 12 -> 11 -> 14`
- derived packs: `publish-prep`
- example query:
  `I want a Douyin workflow from topic selection to creative testing to publish handoff`

### `competitor-weekly-and-breakdown`

- description: track competitors weekly and distill the strongest creator or content pattern
- component goals: `competitor-monitoring`
- merged chain: `06 -> 18 -> 17`
- example query:
  `I want competitor weekly monitoring and creator breakdown`

### `account-retro-to-next-test`

- description: review account performance and turn it into the next testing cycle
- component goals: `account-improvement`
- merged chain: `19 -> 18 -> 12`
- example query:
  `I want an account retro that outputs the next testing matrix`

### `viral-to-testing`

- description: go from viral discovery and teardown to a structured testing program
- component goals: `viral-discovery`, `creative-testing`
- merged chain: `01 -> 03 -> 17 -> 10 -> 12 -> 11 -> 14`
- example query:
  `I want to turn viral teardown into a reusable creative testing workflow`

### `category-to-localized-launch`

- description: research a category, localize the angle, and prepare publish-ready launch materials
- component goals: `category-entry`, `localization`, `publish-handoff`
- merged chain: `01 -> 07 -> 08 -> 09 -> 13 -> 15 -> 16 -> 12 -> 14`
- derived packs: `publish-prep`
- example query:
  `I want a multi-market workflow from category research to localized launch`

### `competitor-to-publish`

- description: use competitor monitoring to drive creative testing and publish handoff
- component goals: `competitor-monitoring`, `creative-testing`, `publish-handoff`
- merged chain: `06 -> 18 -> 17 -> 10 -> 12 -> 11 -> 14 -> 09`
- derived packs: `publish-prep`
- example query:
  `I want to monitor competitors and turn the findings into publish-ready test assets`

### `audience-to-live`

- description: turn category insight and audience language into a live-room operator workflow
- component goals: `category-entry`, `live-support`
- merged chain: `01 -> 07 -> 08 -> 09 -> 18 -> 19`
- derived packs: `live-assist`
- example query:
  `I want a workflow from comment mining to live-session moderator prompts`

### `weekly-monitor-to-next-test`

- description: use competitor monitoring and account retro to define the next testing cycle
- component goals: `competitor-monitoring`, `account-improvement`
- merged chain: `06 -> 18 -> 17 -> 19 -> 12`
- example query:
  `I want to use weekly competitor review and account retro to define the next test cycle`

## Operator Notes

- templates are safe routing helpers, not hidden automation
- a matched template does not imply live crawling, publishing, or account control
- if the requested workflow implies unsafe automation, downgrade to planning, analysis, handoff packs, and manual checklists
