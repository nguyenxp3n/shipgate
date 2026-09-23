# TeamNotes Domain Model

## Aggregates
- User: account profile referenced by memberships.
- Organization: tenant boundary containing memberships and invitations.
- Note: organization-owned authored content with visibility rules.
- Share: authorization relation granting a member note access.
- NotificationIntent: durable request for eventual delivery.
- AuditRecord: append-only record of privileged or security-relevant actions.

## Invariants
- A note belongs to exactly one organization.
- A share recipient must have active membership in the note's organization.
- Membership/tenant scope is checked server-side for every organization resource.
- Invitation tokens are single-use and expire after 24 hours.
- Notification failure never changes already committed note, sharing, or membership state.
