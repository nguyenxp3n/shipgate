# TeamNotes Deployment Specification

Deploy web, API, worker, PostgreSQL, and optional Redis as independently observable components. Run backward-compatible migrations before application rollout. `/livez` is process-only; `/readyz` gates traffic without leaking dependency details. Maintain daily encrypted database backups and perform periodic restore verification. Email provider failure degrades notification delivery rather than authoritative business state.
