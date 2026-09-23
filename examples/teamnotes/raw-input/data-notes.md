# TeamNotes Data Notes

## Authoritative persistence
PostgreSQL is authoritative. Tables are owned by modules; modules may not mutate another module's tables directly.

## Core records
- auth: credentials, sessions
- users: user profiles
- organizations: organizations, memberships, invitations
- notes: notes
- sharing: note_shares
- notifications: notification intents and delivery attempts
- audit: immutable security/business audit records

All organization-scoped records carry `organization_id`. Cross-module durable effects use explicit commands or events. Asynchronous notification delivery uses transactional outbox plus idempotent consumer handling.
