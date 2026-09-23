# Capability: api

**Scope:** HTTP/public API.  
**Authority:** OpenAPI wire shape plus normative API semantics.

## Required project decisions
- versioning/base path.
- error envelope.
- authentication/authorization metadata.
- idempotency.
- pagination/retry.

## Failure and security contract
The project must state dependency failures, retries/degradation/fail-closed behavior where applicable, data classification, authorization boundary, and evidence-producing tests. Disabled optional capabilities impose no implementation obligation.
