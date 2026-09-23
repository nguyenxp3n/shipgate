# Transactional Outbox and Consumer Inbox

When a durable local write must publish an asynchronous cross-module effect, commit the local state and outbox record in the same database transaction. A dispatcher publishes after commit. Consumers are **idempotent** and persist an inbox/deduplication record when repeated delivery could duplicate effects.

Retries, ordering, dead-letter/poison handling, retention and observability are explicit. Application containers/services must not gain a host **Docker socket** or equivalent privileged daemon access to implement event delivery.
