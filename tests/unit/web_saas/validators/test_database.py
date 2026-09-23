from project_finalizer.web_saas.validators.database import DatabaseValidator


def test_multitenant_entity_requires_boundary_and_isolation_test(web_context_factory):
    ctx = web_context_factory(
        capabilities={"multi_tenant": "optional_enabled"},
        database={"entities": [{"id": "project", "tenant_owned": True, "tenant_key": None, "enforcement": None}]},
        test_matrix={"security": []},
    )
    codes = {i.code for i in DatabaseValidator().validate(ctx).issues}
    assert "WS_DB_TENANT_BOUNDARY_REQUIRED" in codes
    assert "WS_TEST_TENANT_ISOLATION_REQUIRED" in codes
