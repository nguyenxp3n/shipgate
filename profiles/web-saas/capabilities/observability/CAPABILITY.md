# Capability: observability

**Scope:** Logs/metrics/traces/alerts.  
**Authority:** Operations observability standard.

## Required project decisions
- structured logs.
- request/correlation IDs.
- golden signals.
- PII redaction.
- alert ownership.

## Failure and security contract
The project must state dependency failures, retries/degradation/fail-closed behavior where applicable, data classification, authorization boundary, and evidence-producing tests. Disabled optional capabilities impose no implementation obligation.
