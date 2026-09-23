# Capability: jobs

**Scope:** Background work.  
**Authority:** Job contract.

## Required project decisions
- queue/worker authority.
- retry/backoff.
- idempotency.
- dead-letter/poison handling.
- observability.

## Failure and security contract
The project must state dependency failures, retries/degradation/fail-closed behavior where applicable, data classification, authorization boundary, and evidence-producing tests. Disabled optional capabilities impose no implementation obligation.
