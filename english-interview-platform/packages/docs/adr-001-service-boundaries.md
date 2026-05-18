# ADR-001 Service Boundaries

## Status

Accepted

## Decision

The first service decomposition is:

- `api-gateway`
- `identity-service`
- `session-service`
- `interview-service`
- `feedback-service`
- `billing-service`

## Rationale

- Session orchestration has different scaling pressure from interview content.
- Feedback generation is a natural async boundary.
- Billing should not couple tightly to interview execution logic.
