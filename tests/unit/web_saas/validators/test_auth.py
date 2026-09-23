from project_finalizer.web_saas.validators.auth import AuthValidator


def test_cookie_credentials_require_csrf_disposition(web_context_factory):
    ctx = web_context_factory(auth={"credential_transport": "cookie", "csrf": None})
    report = AuthValidator().validate(ctx)
    assert "WS_AUTH_CSRF_REQUIRED" in {i.code for i in report.issues}


def test_cross_origin_credentials_require_explicit_origins(web_context_factory):
    ctx = web_context_factory(
        auth={"cross_origin_credentials": True, "cors_allowed_origins": ["*"]}
    )
    report = AuthValidator().validate(ctx)
    assert "WS_AUTH_CORS_EXACT_ORIGINS_REQUIRED" in {i.code for i in report.issues}
