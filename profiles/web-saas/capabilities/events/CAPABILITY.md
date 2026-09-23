# Capability: events

**Scope:** Domain/event propagation.  
**Authority:** Event schemas and interaction contracts.

## Required project decisions
- envelope/versioning.
- producer/consumer.
- ordering.
- retry/idempotency.
- retention/replay.

## Failure and security contract
The project must state dependency failures, retries/degradation/fail-closed behavior where applicable, data classification, authorization boundary, and evidence-producing tests. Disabled optional capabilities impose no implementation obligation.
