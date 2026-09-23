# TeamNotes Operations Notes

- Web frontend, API, worker, PostgreSQL, and optional Redis are separately observable runtime components.
- `/livez` reports process liveness; `/readyz` reports ability to accept traffic without leaking dependency secrets.
- Structured logs include request/correlation IDs and redact secrets.
- Database backups run daily with documented retention and restore verification.
- Deployments run backward-compatible migrations before application rollout and support forward-fix recovery.
- Email provider outage degrades notification delivery; committed business state remains authoritative.
