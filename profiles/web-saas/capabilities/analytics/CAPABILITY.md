# Capability: analytics

**Scope:** Derived analytics telemetry.  
**Authority:** Business source remains authority.

## Required project decisions
- event/data minimization.
- PII handling.
- sampling/retention.
- delivery failure behavior.

## Failure and security contract
The project must state dependency failures, retries/degradation/fail-closed behavior where applicable, data classification, authorization boundary, and evidence-producing tests. Disabled optional capabilities impose no implementation obligation.
