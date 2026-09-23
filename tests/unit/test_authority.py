import pytest

from project_finalizer.authority import AuthorityMatrix
from project_finalizer.errors import WorkflowError


def test_subject_rejects_two_primary_authorities():
    raw = {
        "subjects": {
            "http_wire_format": {
                "primary": ["contracts/openapi/a.yaml", "contracts/openapi/b.yaml"],
                "composition": "single",
            }
        }
    }
    with pytest.raises(WorkflowError, match="exactly one primary"):
        AuthorityMatrix.from_mapping(raw)


def test_historical_path_cannot_be_normative():
    matrix = AuthorityMatrix.from_mapping({"subjects": {}})
    with pytest.raises(WorkflowError, match="historical"):
        matrix.assert_normative("docs/audits/historical/old.md")


def test_primary_for_single_subject():
    matrix = AuthorityMatrix.from_mapping(
        {"subjects": {"product_behavior": {"primary": ["docs/core/PRODUCT-SPEC.md"], "composition": "single"}}}
    )
    assert matrix.primary_for("product_behavior") == ("docs/core/PRODUCT-SPEC.md",)
