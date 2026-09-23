# Capability: cache

**Scope:** Derived performance cache.  
**Authority:** Authoritative source remains elsewhere.

## Required project decisions
- key format.
- TTL.
- invalidation.
- failure behavior.
- privacy/staleness tolerance.

## Failure and security contract
The project must state dependency failures, retries/degradation/fail-closed behavior where applicable, data classification, authorization boundary, and evidence-producing tests. Disabled optional capabilities impose no implementation obligation.
