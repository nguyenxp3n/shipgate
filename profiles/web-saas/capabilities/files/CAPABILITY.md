# Capability: files

**Scope:** Object/file storage.  
**Authority:** File contract and storage authority.

## Required project decisions
- MIME/content validation.
- size/provider.
- authorization/signed URLs.
- malware/metadata policy.
- retention/orphan cleanup.

## Failure and security contract
The project must state dependency failures, retries/degradation/fail-closed behavior where applicable, data classification, authorization boundary, and evidence-producing tests. Disabled optional capabilities impose no implementation obligation.
