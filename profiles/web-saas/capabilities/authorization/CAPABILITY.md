# Capability: authorization

**Scope:** Permissions and resource scopes.  
**Authority:** Backend authorization policy.

## Required project decisions
- role/permission catalog.
- tenant/resource scope.
- object ownership.
- admin/service identity behavior.
- test matrix.

## Failure and security contract
The project must state dependency failures, retries/degradation/fail-closed behavior where applicable, data classification, authorization boundary, and evidence-producing tests. Disabled optional capabilities impose no implementation obligation.
