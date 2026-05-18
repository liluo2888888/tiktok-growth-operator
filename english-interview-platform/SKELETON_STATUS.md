# Skeleton Status

## What Exists

- Mobile app skeleton under `apps/mobile`
- Go microservice skeletons under `services/`
- Shared contracts placeholder under `packages/contracts`
- ADR for service boundaries under `packages/docs`
- Local infra compose file under `infra/docker`

## What Is Not Done Yet

- No database migrations yet
- No real OpenAI realtime token flow yet
- No shared CI or Makefile yet
- No real scoring or LLM feedback pipeline yet

## Local Environment Blockers

### Go

`where go` resolves to `E:\goenv\go\bin\go.exe`, but the active environment reports:

`go: cannot find GOROOT directory: C:\Program Files\Go`

This means `GOROOT` must be corrected before compilation.

### Node / npm

`node` exists, but `npm` resolves to a broken module path in the current environment.

This must be fixed before installing Expo dependencies.

## Recommended Next Step

1. Bring up a working local PostgreSQL runtime and run end-to-end persistence smoke tests
2. Add a unified error envelope across gateway and services
3. Add interview turn state and recording/transcript placeholders

## Current Workaround

The repository now includes local scripts that bypass the broken default environment:

- `scripts/dev-env.ps1`
- `scripts/run-api-gateway.cmd`
- `scripts/run-session-service.cmd`
- `scripts/install-mobile.cmd`
- `scripts/run-mobile.cmd`

These scripts use:

- `C:\toolchains\go1.24.3-tar\go\bin\go.exe`
- `C:\Users\Administrator\AppData\Roaming\npm\pnpm.cmd`

## Verified Now

- `api-gateway` can run locally with the repo script
- `session-service` can run locally with the repo script
- `apps/mobile` dependencies were installed with the roaming `pnpm`
- `pnpm exec expo --version` succeeds
- `pnpm run start -- --help` succeeds
- `api-gateway` now proxies session bootstrap to `session-service`
- `mobile` now has a 3-step flow:
  - `index` -> `role`
  - `role` -> `mission`
  - `mission` -> `interview`
- `mobile` now also includes a `feedback` placeholder screen
- `session-service` request/response handling was split out of `main.go`
- `sessionId` is now generated as a unique random value instead of being hardcoded
- `session-service` now uses a PostgreSQL-backed repository abstraction instead of an in-memory store
- `session-service` now defaults to the PostgreSQL backend
- `session-service` keeps `file` only as an explicit local fallback backend
- `sqlite` backend support has been removed
- `session-service` now exposes `GET /v1/sessions/{id}`
- `session-service` now also supports `POST /v1/sessions/{id}/turns`
- `api-gateway` now proxies `GET /v1/mobile/sessions/{id}`
- `api-gateway` now proxies `POST /v1/mobile/sessions/{id}/turns`
- `mobile` feedback screen now loads structured session detail from the backend
- `mobile` interview screen now uses the voice main path: record → transcribe → edit transcript → submit turn (see `apps/mobile/README.md`)
- `mobile` interview screen still supports legacy text submit path only when ASR key is missing (manual transcript entry)
- session detail now includes structured `turns` with:
  - `id`
  - `speaker`
  - `createdAt`
  - `question`
  - `answer`
  - `feedback.summary`
  - `feedback.improvementTip`
- session detail now also includes:
  - `stage`
  - `currentQuestion`
  - derived legacy-compatible `transcript`
- session turn generation now uses session-local state instead of only static mission defaults
- `session-service` now ensures the PostgreSQL `interview_sessions` schema on startup
- local PostgreSQL init SQL now exists under `infra/docker/init/001_create_interview_sessions.sql`
- local file-backed persistence has been smoke-tested end-to-end
- Go build passes for `api-gateway` and `session-service`
- TypeScript check passes for `apps/mobile`

## Validation Notes

- `session-service` now compiles with `github.com/lib/pq`
- `session-service` no longer depends on `modernc.org/sqlite`
- local end-to-end PostgreSQL validation now passes through Docker:
  - `scripts/smoke-postgres-session.ps1`
  - isolated ports `18080` / `18082` / `55432`
  - `bootstrap -> persist -> detail` verified against PostgreSQL
- bundled Windows PostgreSQL remains optional fallback only; Docker is the standard smoke path
- the local Go runtime path was repaired for this workspace by switching repo scripts to:
  - `C:\toolchains\go1.24.3-tar\go`
- the previous runtime failures were caused by:
  - broken system/user `GOROOT` values
  - a polluted `E:\goenv\go\src\go.mod`
- verified local dev path:
  - explicit fallback only: `SESSION_REPOSITORY_BACKEND=file`
  - `scripts/smoke-file-session.ps1`
  - `POST /v1/mobile/session/bootstrap`
  - `POST /v1/mobile/sessions/{id}/turns`
  - `GET /v1/mobile/sessions/{id}`
  - turn-level structured payload returned and persisted
  - file persistence written to `services/session-service/data/sessions.json`
  - smoke result confirms:
    - `turnCount = 3`
    - `stage = closing`
    - `currentQuestion = What would you do differently next time?`
- PostgreSQL smoke now also verified:
  - `scripts/smoke-postgres-session.ps1`
  - Docker `postgres:16` on port `55432`
  - persisted row confirmed in `interview_sessions`
