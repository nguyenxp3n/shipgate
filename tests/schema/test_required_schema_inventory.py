REQUIRED = {
    "workflow-manifest", "project", "project-state", "profile", "requirement",
    "conflict", "decision-request", "authority-matrix", "artifact", "module",
    "ownership", "interaction", "command", "test-invariant", "work-package",
    "work-package-graph", "audit-finding", "audit-disposition", "run-record",
    "change-transaction", "readiness-report", "release-manifest",
}


def test_required_schema_inventory_exists(repo_root):
    actual = {p.name.removesuffix(".schema.json") for p in (repo_root / "schemas").glob("*.schema.json")}
    assert REQUIRED <= actual
