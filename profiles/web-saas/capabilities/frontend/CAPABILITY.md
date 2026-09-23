# Capability: frontend

**Scope:** Browser UI.  
**Authority:** API contracts and backend authorization.

## Required project decisions
- rendering/routing model.
- state boundaries.
- screen state matrix.
- accessibility.
- private cache/offline policy.

## Failure and security contract
The project must state dependency failures, retries/degradation/fail-closed behavior where applicable, data classification, authorization boundary, and evidence-producing tests. Disabled optional capabilities impose no implementation obligation.
