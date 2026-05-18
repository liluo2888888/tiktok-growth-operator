# Mobile App

React Native + Expo application for Quest English / Interview Quest Pack.

## Stack

- Expo SDK 52
- React Native
- TypeScript
- Expo Router

## App flow (R1)

```text
/onboarding → /quest-map → /quest-start → /interview → /feedback → /passport
```

## Passport (US-006)

- Completing a round on **Feedback** issues a stamp (local AsyncStorage for MVP).
- **`/passport`** — stamp list and empty state.
- **`/passport/[id]`** — scores + **Share stamp** (native: PNG poster via `react-native-view-shot`; web: text share).
- Backend `POST/GET /v1/mobile/passport/stamps` (header `X-Device-Id`); falls back to local cache if API is down.

## Analytics (I-03)

- `src/services/analytics.ts` — `track()` for 8 PRD funnel events; local log + pending queue.
- `POST /v1/mobile/analytics/events` (header `X-Device-Id`) — batch ingest via session-service; smoke: `scripts/smoke-analytics-events.ps1`.

## Loading UI (I-08)

- `src/components/LoadingOverlay.tsx` — `mode="card"` (inline) or `mode="fullscreen"` (submit/share blocking).
- Used on home, quest-map, interview, feedback, passport, and ASR transcribe.

## Error UI (I-02)

- `src/components/ErrorBanner.tsx` — shared error + retry on interview, feedback, and passport share failures.

## P0 Gate

- Checklist: `packages/docs/p0-gate-checklist.md`
- Automated: `scripts/smoke-p0-gate.ps1` (R1 + passport + analytics)

## Streak (US-008)

- Home (`app/index.tsx`) shows **day streak**, **today done / open**, and a **Continue today's quest** CTA.
- Completing one interview round (`interview.tsx` submit success) records UTC-day completion in `src/storage/streak.ts`.
- Rules: consecutive UTC days increment streak; missing a day resets displayed streak to 0 until the next completion; only one increment per UTC day.
- Suggested quest picks the first mission that is not `completed` on the Quest Map.

## Legal (`/legal`)

Privacy, voice/ASR third-party notice, and beta retention policy. Linked from home and onboarding.

- First launch goes to **Onboarding** (goal + role saved in AsyncStorage).
- **Quest Map** lists `self_intro` and `behavioral` missions with completion status.
- Legacy routes `/role` and `/mission` still exist for quick testing.

## Voice main path (US-005)

Spec: `packages/docs/techspec-us005-voice-pipeline.md`

The interview screen (`app/interview.tsx`) uses:

1. **Record** — `expo-av` via `src/audio/recorder.ts`
2. **Transcribe** — OpenAI Whisper (`src/services/asr/whisperProvider.ts`)
3. **Preview / edit** — `VoiceAnswerPanel` + transcript `TextInput`
4. **Submit** — `POST /v1/mobile/sessions/{id}/turns` with text `answer`
5. **Feedback** — `app/feedback.tsx` after successful submit

## Setup

```powershell
cd apps\mobile
C:\Users\Administrator\AppData\Roaming\npm\pnpm.cmd install
copy .env.example .env
# Edit .env: set EXPO_PUBLIC_OPENAI_API_KEY for auto transcription
```

Start backend (`api-gateway` + `session-service`), then:

```powershell
..\..\scripts\run-mobile.cmd
```

Without `EXPO_PUBLIC_OPENAI_API_KEY`, you can still **record** and **type** the transcript manually after stopping.

## Web full flow (no phone)

1. Start backend (`run-session-service.cmd` + `run-api-gateway.cmd`).
2. From repo root: `scripts\run-web.cmd` (or `pnpm web` in `apps/mobile`).
3. In the browser:
   - Complete **Onboarding** (or use **Reset onboarding** on home in dev).
   - **Quest Map** → pick a mission → **Begin Practice**.
   - On **Interview**: click **Type answer (web)**, enter ≥3 words in English, **Submit Answer**.
   - **Feedback**: scores, turn review, helpful rating → **Passport** stamp modal.
4. API smoke (no UI): `..\..\scripts\smoke-r1-flow.ps1`

## Checks

```powershell
pnpm typecheck
pnpm test
..\..\scripts\smoke-voice-turn.ps1
..\..\scripts\smoke-r1-flow.ps1
..\..\scripts\smoke-passport-stamps.ps1
```

## Physical device (真机联调)

### 1. One-time setup

```powershell
# From repo root — writes apps/mobile/.env with your WLAN IP
..\..\scripts\setup-device-env.ps1

# Edit apps/mobile/.env — paste your OpenAI key for auto transcription
```

### 2. Start backend (two terminals)

```powershell
..\..\scripts\run-session-service.cmd
..\..\scripts\run-api-gateway.cmd
```

### 3. Preflight

```powershell
..\..\scripts\device-debug.ps1
```

If **localhost OK** but **LAN IP fails**, allow port 8080 in Windows Firewall (Admin PowerShell):

```powershell
netsh advfirewall firewall add rule name="English Interview API 8080" dir=in action=allow protocol=TCP localport=8080
```

### 4. Start Expo (after `.env` exists)

```powershell
pnpm start
```

Scan QR with **Expo Go**. Phone and PC must be on the **same Wi‑Fi** (not guest/isolated VLAN).

### 5. On-device debug UI

In development builds, the **Interview** screen shows a **Device debug** panel:

- API base URL (must be `http://192.168.x.x:8080`, not `localhost`)
- **Ping API** — should show `OK (200)`
- ASR key — `set` or `missing`

After changing `.env`, **restart Expo** (`Ctrl+C` then `pnpm start`, or press `r` in the Expo terminal).

### Common failures

| Symptom | Fix |
|--------|-----|
| `Failed to bootstrap session` / Network request failed | Wrong API URL or firewall; run `device-debug.ps1` |
| `localhost` in debug panel | Run `setup-device-env.ps1`, restart Expo |
| Permission denied (mic) | Settings → app → allow microphone |
| Transcription fails, submit works | Set `EXPO_PUBLIC_OPENAI_API_KEY`, or use **Type Manually** |
| Android HTTP blocked | `app.json` → `usesCleartextTraffic: true` (already set) |
