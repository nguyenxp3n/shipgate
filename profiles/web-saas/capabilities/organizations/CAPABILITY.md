# Capability: organizations

**Scope:** Tenant/organization membership.  
**Authority:** Organization module and tenancy contract.

## Required project decisions
- tenant strategy.
- membership roles.
- isolation enforcement.
- deletion/export semantics.

## Failure and security contract
The project must state dependency failures, retries/degradation/fail-closed behavior where applicable, data classification, authorization boundary, and evidence-producing tests. Disabled optional capabilities impose no implementation obligation.
