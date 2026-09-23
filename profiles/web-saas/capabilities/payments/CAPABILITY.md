# Capability: payments

**Scope:** Provider payment/subscription integration.  
**Authority:** Provider state and application entitlement state are distinct.

## Required project decisions
- webhook verification.
- idempotency/dedupe.
- out-of-order handling.
- reconciliation.
- entitlement authority.

## Failure and security contract
The project must state dependency failures, retries/degradation/fail-closed behavior where applicable, data classification, authorization boundary, and evidence-producing tests. Disabled optional capabilities impose no implementation obligation.
