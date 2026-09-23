# Capability: database

**Scope:** Authoritative persistence.  
**Authority:** Data model plus migrations.

## Required project decisions
- engine/version.
- ownership.
- constraints.
- transactions.
- migration/retention/backup.

## Failure and security contract
The project must state dependency failures, retries/degradation/fail-closed behavior where applicable, data classification, authorization boundary, and evidence-producing tests. Disabled optional capabilities impose no implementation obligation.
