# Migration Notes

## Current Platform

- Codex skill package with optional Clipcat CLI execution

## Platform-Agnostic Layers To Keep

- feature map
- command map
- truthfulness boundary
- paid-action confirmation rules
- async task handling pattern
- report templates

## Platform-Specific Layers

- `SKILL.md` frontmatter
- `agents/openai.yaml`
- local shell command examples

## Migration Targets

### Claude/OpenClaw-style skill

Preserve:

- scenario routing
- command discipline
- short main skill file plus references

### Generic agent or OpenAI assistant

Preserve:

- feature map
- report templates
- execution-mode split

Downgrade:

- shell-specific examples
- Codex-specific file references
