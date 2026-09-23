# Capability: operations

**Scope:** Runtime/deployment/recovery.  
**Authority:** Operations/deployment specification.

## Required project decisions
- configuration/secrets.
- health/readiness.
- deploy/rollback.
- backup/restore.
- incident runbook.

## Failure and security contract
The project must state dependency failures, retries/degradation/fail-closed behavior where applicable, data classification, authorization boundary, and evidence-producing tests. Disabled optional capabilities impose no implementation obligation.
