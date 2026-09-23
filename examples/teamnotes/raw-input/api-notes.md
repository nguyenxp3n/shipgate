# TeamNotes API Notes

## Public API expectations
- JSON API lives under `/api/v1`.
- Authentication/session endpoints: login, refresh, logout.
- Organization endpoints: list memberships, invite member, revoke membership.
- Note endpoints: list, create, get, update, share, unshare.
- Admin audit endpoint returns organization-scoped audit records.
- Mutation responses return canonical error envelopes on failure.
- Retried invitation creation must be idempotent for the same organization/email/idempotency key.

## Invitation API draft
A historical API draft says invitation tokens expire after **48 hours**. This conflicts with the product note and requires a protected product/security decision instead of silent normalization.
