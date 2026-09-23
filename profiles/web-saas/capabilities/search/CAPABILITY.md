# Capability: search

**Scope:** Derived search index.  
**Authority:** Primary data store remains authority by default.

## Required project decisions
- index pipeline.
- consistency.
- reindex.
- delete propagation.
- recovery/versioning.

## Failure and security contract
The project must state dependency failures, retries/degradation/fail-closed behavior where applicable, data classification, authorization boundary, and evidence-producing tests. Disabled optional capabilities impose no implementation obligation.
