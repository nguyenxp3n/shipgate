# TeamNotes Security Specification

Backend authorization is authoritative. Access credentials are short-lived; refresh credentials rotate and are kept in Secure, HttpOnly, SameSite=Strict cookies. Credentialed browser mutations use explicit CSRF defenses and exact-origin CORS. Tenant scope is enforced on every organization operation. Invitation tokens are high entropy, single-use, stored as digests, expire after 24 hours, and can be revoked. Secret material is never logged.
