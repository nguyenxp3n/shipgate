# Capability: auth

**Scope:** Identity/session lifecycle.  
**Authority:** Authentication security specification.

## Required project decisions
- credential source.
- verification/recovery.
- session/token storage and rotation.
- CSRF/CORS applicability.
- rate limits/revocation.

## Failure and security contract
The project must state dependency failures, retries/degradation/fail-closed behavior where applicable, data classification, authorization boundary, and evidence-producing tests. Disabled optional capabilities impose no implementation obligation.
