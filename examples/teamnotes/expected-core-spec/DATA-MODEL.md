# TeamNotes Data Model

| Module | Owned records |
| --- | --- |
| auth | credentials, sessions |
| users | user_profiles |
| organizations | organizations, memberships, invitations |
| notes | notes |
| sharing | note_shares |
| notifications | notification_intents, delivery_attempts |
| audit | audit_records |

All organization-scoped records carry `organization_id`. Foreign keys constrain identity where appropriate, but only the owning module mutates its records. Durable cross-module effects use explicit interaction contracts. Retention and deletion behavior are defined per record class before production readiness.
