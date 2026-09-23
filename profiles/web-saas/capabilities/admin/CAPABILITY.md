# Capability: admin

**Scope:** Privileged operator functions.  
**Authority:** Admin authorization/audit policy.

## Required project decisions
- step-up/re-auth.
- impersonation.
- destructive/bulk operations.
- reason/audit trail.
- privacy/export tools.

## Failure and security contract
The project must state dependency failures, retries/degradation/fail-closed behavior where applicable, data classification, authorization boundary, and evidence-producing tests. Disabled optional capabilities impose no implementation obligation.
