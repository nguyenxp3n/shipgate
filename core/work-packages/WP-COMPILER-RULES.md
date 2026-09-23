# Work-Package Compiler Rules

The compiler creates a deterministic DAG with `WP-000` as the root. It derives dependencies from approved module/contracts and never resolves protected ambiguity; unresolved protected edges create Decision Request requirements and leave the package blocked.
