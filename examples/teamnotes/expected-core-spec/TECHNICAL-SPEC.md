# TeamNotes Technical Specification

TeamNotes uses a web client, HTTP API, PostgreSQL, and a background worker. PostgreSQL is authoritative. Modules communicate through explicit synchronous contracts or durable events; direct foreign-table writes are prohibited. Notification delivery uses local transaction plus outbox, then an idempotent worker consumer. Redis may be used for cache/rate limiting but is never business authority.
