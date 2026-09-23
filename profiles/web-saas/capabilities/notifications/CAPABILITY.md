# Capability: notifications

**Scope:** Notification intents/channels.  
**Authority:** Business mutation commits independently unless product rule says otherwise.

## Required project decisions
- intent ownership.
- channel routing.
- retry/dedupe.
- preferences.
- delivery evidence.

## Failure and security contract
The project must state dependency failures, retries/degradation/fail-closed behavior where applicable, data classification, authorization boundary, and evidence-producing tests. Disabled optional capabilities impose no implementation obligation.
