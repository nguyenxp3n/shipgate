from project_finalizer.web_saas.validators.security import SecurityValidator


def test_enabled_file_and_webhook_surfaces_require_policies(web_context_factory):
    ctx = web_context_factory(
        capabilities={"files": "optional_enabled", "webhooks": "optional_enabled"},
        security={"file_policy": None, "webhook_policy": None},
    )
    codes = {i.code for i in SecurityValidator().validate(ctx).issues}
    assert {"WS_SEC_FILE_POLICY_REQUIRED", "WS_SEC_WEBHOOK_POLICY_REQUIRED"} <= codes


def test_not_applicable_security_surface_requires_evidence(web_context_factory):
    ctx = web_context_factory(security={"ssrf": {"status": "NOT_APPLICABLE", "evidence": []}})
    codes = {i.code for i in SecurityValidator().validate(ctx).issues}
    assert "WS_SEC_NA_EVIDENCE_REQUIRED" in codes
