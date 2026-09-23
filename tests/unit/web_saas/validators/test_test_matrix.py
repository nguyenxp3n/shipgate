from project_finalizer.web_saas.validators.test_matrix import TestMatrixValidator


def test_invariant_activates_only_when_wp_is_reached(web_context_factory):
    invariant = {"id": "AUTH-1", "active_from_wp": "WP-002", "required_tests": ["security"]}
    early = web_context_factory(test_matrix={"invariants": [invariant], "available": []}, work_packages=({"id":"WP-001","state":"READY"},))
    late = web_context_factory(test_matrix={"invariants": [invariant], "available": []}, work_packages=({"id":"WP-002","state":"READY"},))
    assert TestMatrixValidator().validate(early).ok
    assert "WS_TEST_REQUIRED_CLASS_MISSING" in {i.code for i in TestMatrixValidator().validate(late).issues}
