# Idempotency Contract

Classify every retryable mutation. Define idempotency key source/scope, request fingerprinting, retention, replay response, concurrent duplicate behavior, transaction boundary, and conflicts. Money/entitlement/external-effect mutations require an explicit disposition rather than an implicit retry assumption.
