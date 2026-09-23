# Capability: audit-log

**Scope:** Security/audit evidence.  
**Authority:** Append-oriented audit contract.

## Required project decisions
- who/what/target/when/result/request id.
- sensitive-field redaction.
- retention/access.

## Failure and security contract
The project must state dependency failures, retries/degradation/fail-closed behavior where applicable, data classification, authorization boundary, and evidence-producing tests. Disabled optional capabilities impose no implementation obligation.
