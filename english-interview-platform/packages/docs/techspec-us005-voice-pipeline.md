# Tech Spec: US-005 Voice Pipeline

| Field | Value |
|------|------|
| Version | v1.0 |
| Date | 2026-05-17 |
| Related PRD | [prd-mvp-quest-english.md](./prd-mvp-quest-english.md) |
| Related ASR Spec | [techspec-us004-voice-asr.md](./techspec-us004-voice-asr.md) |
| Status | Implemented (mobile MVP) |

## Goal

Deliver the MVP voice interview path:
`record -> transcribe -> preview -> submit turn -> feedback`.

The first release keeps the existing session contract unchanged. The backend still accepts plain text `answer` for `POST /v1/mobile/sessions/{id}/turns`.

## Non-Goals

- Do not store raw audio on the service side.
- Do not change `session-service` turn schema in the first pass.
- Do not build realtime bidirectional voice chat yet.
- Do not add multi-language ASR in MVP.

## Architecture

```text
apps/mobile
  interview screen
    -> recorder (expo-av)
    -> asr provider
    -> editable transcript preview
    -> existing turn submit API
    -> feedback screen

api-gateway
  remains unchanged for MVP

session-service
  remains text-turn based
```

## Recommended MVP Flow

1. User opens `interview` screen and sees current question.
2. User taps `Start Recording`.
3. App requests microphone permission and starts local recording.
4. User taps `Stop`.
5. App transcribes the local audio.
6. App shows transcript in an editable field.
7. User edits transcript if needed.
8. User taps `Submit`.
9. App calls existing `POST /v1/mobile/sessions/{id}/turns`.
10. App routes to `feedback`.

## Mobile Dependencies

- `expo-av`
- `expo-file-system`

## Recording Rules

- Default format: `.m4a`
- Sample rate: 44100 Hz
- Channel: mono
- Max duration: 120s
- Minimum duration: 10s
- Cache location: local temp directory only
- Delete audio after submit or re-record

## State Machine

```text
idle -> requesting_permission -> ready
ready -> recording -> recorded
recorded -> transcribing -> transcript_ready
transcript_ready -> submitting -> success
transcribing -> transcribe_failed
submitting -> submit_failed
* -> idle (cancel / restart)
```

## ASR Provider Contract

```ts
export type AsrResult = {
  transcript: string;
  confidence?: number;
  language?: string;
  durationMs: number;
};

export interface AsrProvider {
  transcribe(localUri: string): Promise<AsrResult>;
}
```

## MVP Recommendation

Use a client-side ASR provider first.

Rationale:
- fastest to validate
- no backend contract change
- keeps `session-service` simple

If API key exposure becomes a concern, move ASR behind `api-gateway` in a later iteration.

## API Contract

Keep:

```http
POST /v1/mobile/sessions/{sessionId}/turns
Content-Type: application/json

{ "answer": "<ASR transcript, optionally edited>" }
```

Optional later extension:

```http
POST /v1/mobile/sessions/{sessionId}/turns/audio
Content-Type: multipart/form-data
```

## UX Requirements

- show current question
- show record / stop / re-record
- show countdown or duration
- show editable transcript
- disable submit below 10s
- show clear error states
- auto route to feedback on success

## Error Handling

- mic permission denied -> explain and route to settings
- audio too short -> block submit
- ASR failure -> retry and re-record
- turn API failure -> retry
- empty transcript -> block submit

## Validation

- unit test recorder state transitions
- mock ASR success / timeout / empty transcript
- smoke test voice flow against existing session APIs

