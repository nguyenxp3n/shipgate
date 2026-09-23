# web-saas Work Package Rules

`WP-000` is the mandatory bootstrap entry point. It establishes repository structure, pinned toolchain, command gateway, formatting/lint/typecheck/test commands, environment bootstrap, generated-code locations, migration directories when applicable, and CI skeleton.

Every later WP declares dependency IDs, authority references, allowed and forbidden paths, interfaces consumed/produced, schema/migration/security impact, activated critical invariants, executable acceptance commands, evidence and explicit **stop conditions**. Any newly discovered **protected** product/API/database/security/privacy/deployment decision is a stop condition and requires a Decision Request/ADR rather than an agent guess.

The compiler emits a DAG, not a fictional fixed sequence. Disabled capabilities generate no WP. READY work may not depend on blocked/unready dependencies.
