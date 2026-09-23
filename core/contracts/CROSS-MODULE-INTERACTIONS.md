# Cross-Module Interactions

Every interaction is one of `SYNC_QUERY`, `SYNC_COMMAND`, `SAME_REQUEST_ORCHESTRATION`, `DOMAIN_EVENT`, `BACKGROUND_JOB`, `OUTBOX_EVENT`, or `EXTERNAL_WEBHOOK` and declares producer, consumer, transaction boundary, idempotency, timeout, and failure behavior.

A synchronous API response may not promise a foreign module's eventual write as authoritative unless a synchronous contract exists for that effect.
