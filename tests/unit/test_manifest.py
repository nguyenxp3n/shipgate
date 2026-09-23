from project_finalizer.manifest import load_workflow_manifest


def test_root_manifest_declares_v2_and_python_range(repo_root):
    manifest = load_workflow_manifest(repo_root / "WORKFLOW-MANIFEST.yaml")
    assert manifest.version == "2.0.0"
    assert manifest.python == ">=3.12,<3.13"
    assert manifest.profiles["web-saas"] == "2.0.0"


def test_root_manifest_indexes_normative_artifacts_and_release_metadata(repo_root):
    manifest = load_workflow_manifest(repo_root / "WORKFLOW-MANIFEST.yaml")

    assert "docs/superpowers/specs/shipgate-architecture-spec.md" in manifest.normative_artifacts
    assert "core/authority/AUTHORITY-MATRIX.yaml" in manifest.normative_artifacts
    assert manifest.release_archive == "shipgate.zip"
    assert manifest.release_sidecar == "shipgate.zip.sha256"
    assert "QA-BUILD-READINESS.md" in manifest.qa_reports
