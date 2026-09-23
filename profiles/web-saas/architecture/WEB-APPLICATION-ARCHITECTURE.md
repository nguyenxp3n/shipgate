# Web Application Architecture

This profile defines obligations, not a framework choice. The target project must freeze the browser rendering model, routing authority, API boundary, authentication bootstrap, backend authorization authority, persistence authority, asynchronous boundaries, deployment topology, trust boundaries, and failure behavior before build readiness.

## Required decisions

- Rendering: SPA, SSR, hybrid, or another explicit model with cache implications.
- Routing: browser/server ownership, protected-route bootstrap, deep-link behavior, and 404 behavior.
- API: versioning, base path, generated types policy, error envelope, idempotency, pagination, and retry semantics.
- State: authoritative server state, local UI state, authentication/session state, and offline policy.
- Security: browser trust boundary, credential transport, CSRF/CORS/CSP disposition, private-cache policy, and third-party script policy.
- Data: database authority, module ownership, transaction boundaries, retention, and recovery.
- Operations: build/runtime artifact, configuration injection, health/readiness, observability, deployment ordering, rollback, and backup/restore.

## Forbidden ambiguity

UI visibility is never authorization. Cache/search/analytics replicas are derived unless a project-specific authority decision says otherwise. A synchronous response may not promise a foreign-module durable result that is only eventually produced. Protected security/data/public-interface decisions require an explicit decision record rather than an agent guess.
