# Testing Standard

Tests are selected by risk and contract: unit tests for local behavior, integration tests for real component boundaries/data constraints, contract tests for public machine contracts, security tests for attack/authorization/tenant boundaries, end-to-end tests for critical user journeys, migration/recovery tests for data change and restore behavior, and release tests for package/deployment integrity.

New behavior uses test-first development where executable code is changed. Critical invariants must have stable IDs and explicit required test classes. Mocking must not replace the real side effect/constraint whose behavior is under test.
