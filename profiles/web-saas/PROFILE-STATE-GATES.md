# web-saas Profile State Gates

`BUILD_READY` requires all enabled capability validators to pass. In particular, enabled authentication must have session/token and CSRF/CORS dispositions as applicable; enabled multi-tenancy must have a tenant boundary and isolation tests; enabled asynchronous processing must define idempotency/retry/failure semantics; enabled storage/webhook/AI surfaces must satisfy their security and authority obligations.
