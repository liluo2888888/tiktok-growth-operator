# Feature Map

This package recreates the source system as a pure Codex scene pack.

## Core Capability Families

### A. Search and ranking

- collect viral candidates
- rank them by worth studying
- track repeated topic changes over time

### B. Product and market insight

- study category demand from visible content and comments
- compare competitor products
- extract category-level user language

### C. Video understanding

- break down hooks, pacing, proof, and CTA logic
- reverse-engineer visual and script patterns
- distill creator style

### D. Creation planning

- write replication briefs
- write product-video briefs
- create multi-style test matrices
- create localization packs

### E. Creative asset planning

- design image packs
- design translation briefs
- benchmark competitor main images

### F. Retrospective systems

- weekly competitor account review
- self-account content retro

### G. Publish-readiness systems

- generate publish-note packs for title, hook, cover, caption, and tags
- organize reusable scene workspaces for asset prep and operator handoff
- produce review checklists for manual or approved downstream publishing

### H. Live-ops assist systems

- live-room monitoring templates
- moderator and host response prompt packs
- anomaly review and escalation checklists

### I. Explicit exclusions

- fake engagement and cold-start manipulation
- mass auto-reply or comment hijacking
- device spoofing, anti-detection, and account farming
- cloud-phone control claims without real infrastructure

## Pure Codex Reproduction Target

What this package tries to fully reproduce:

- all 19 business scenarios
- the output usefulness of the original workflows
- the operator logic behind the scenes

What this package does not try to fake:

- private backend generation
- guaranteed TikTok Shop access
- built-in project-space UI
- unsafe engagement or evasion infrastructure

## Design Translation

Original product pattern:

- command + backend + scene

Pure Codex replacement:

- evidence intake + scene workflow + prompt pack + deliverable contract

## Recommended Multi-Scene Chains

- viral discovery: `01 -> 03 -> 17`
- category entry: `01 -> 07 -> 08 -> 09`
- creative testing: `10 -> 12 -> 11 -> 14`
- localization: `13 -> 15 -> 16`
- competitor monitoring: `06 -> 18 -> 17`
- account improvement: `19 -> 18 -> 12`
- publish handoff: `09 -> 12 -> 14` plus `publish-prep` pack
- live support: `08 -> 18 -> 19` plus `live-assist` pack

## Goal Template Layer

The package supports plain-language workflow routing on top of the base scene chains.

Built-in templates:

- `topic-to-publish`: `category-entry + creative-testing + publish-handoff`
- `competitor-weekly-and-breakdown`: `competitor-monitoring`
- `account-retro-to-next-test`: `account-improvement`
- `viral-to-testing`: `viral-discovery + creative-testing`
- `category-to-localized-launch`: `category-entry + localization + publish-handoff`
- `competitor-to-publish`: `competitor-monitoring + creative-testing + publish-handoff`
- `audience-to-live`: `category-entry + live-support`
- `weekly-monitor-to-next-test`: `competitor-monitoring + account-improvement`

This layer turns business requests such as `topic selection -> creative testing -> publish handoff` into one merged scene workflow plus the correct derived operator packs.

## Unified Execution Layer

The package now has three execution surfaces:

- scene-level workflow creation
- goal-level merged workflow creation
- operator-pack generation

The unified entrypoint is `scripts/run_operator_workflow.py`, which routes those three modes through one command surface without changing the underlying durable scripts.

It now also supports an auto-routing layer:

- detect pack-like requests
- detect single-scene requests
- route all other natural-language requests into the goal/template layer
