# TeamNotes Security Notes

- Web sessions use short-lived access credentials plus rotating refresh credentials in a Secure, HttpOnly, SameSite=Strict cookie.
- Credentialed browser mutations require an explicit CSRF defense and exact-origin CORS policy.
- Authorization is enforced by the backend; hidden UI is not authorization.
- Every organization-scoped query and mutation enforces membership/tenant scope.
- Passwords are stored with a modern memory-hard password hash.
- Invitation tokens are high-entropy, single-use, revocable, and stored as non-reversible token digests.
- Security/audit logs must not contain passwords, cookies, refresh tokens, or raw invitation tokens.
