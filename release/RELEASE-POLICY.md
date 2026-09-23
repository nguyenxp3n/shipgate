# Release Policy

A V2.0.0 workflow release must:
- pass all applicable deterministic validators;
- contain no unresolved Critical or High release blocker;
- contain no unresolved protected decision required by the package blueprint;
- generate QA reports from machine evidence rather than hand-written PASS claims;
- exclude VCS metadata, virtual environments, caches, bytecode, and untrusted partial-run artifacts;
- generate `SHA256SUMS.txt` for staged package files, excluding the checksum file itself;
- generate a deterministic ZIP archive;
- verify the ZIP with a fresh extraction and per-file hashes;
- emit an external `.zip.sha256` sidecar because an archive cannot contain its own final digest without changing that digest.

Truthful assurance wording is mandatory. Build readiness does not imply target-product runtime or production validation. Independent review and AI-provider execution integration may be claimed only when corresponding evidence exists.
