# Capability: users

**Scope:** User profile/preferences.  
**Authority:** Users module contract.

## Required project decisions
- owned fields.
- privacy classification.
- update/delete/export semantics.
- cross-module references.

## Failure and security contract
The project must state dependency failures, retries/degradation/fail-closed behavior where applicable, data classification, authorization boundary, and evidence-producing tests. Disabled optional capabilities impose no implementation obligation.
