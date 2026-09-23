# Capability: email

**Scope:** Email delivery.  
**Authority:** Notification intent is separate from provider delivery.

## Required project decisions
- template ownership.
- provider/failure behavior.
- critical token semantics.
- rate/abuse controls.

## Failure and security contract
The project must state dependency failures, retries/degradation/fail-closed behavior where applicable, data classification, authorization boundary, and evidence-producing tests. Disabled optional capabilities impose no implementation obligation.
