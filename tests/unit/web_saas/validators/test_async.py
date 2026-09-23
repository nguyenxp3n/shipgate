from project_finalizer.web_saas.validators.async_contracts import AsyncContractsValidator


def test_enabled_async_processing_requires_delivery_semantics(web_context_factory):
    ctx = web_context_factory(
        capabilities={"events": "optional_enabled"},
        async_contracts={"idempotency": None, "retry": None, "failure": None, "dead_letter": None},
    )
    codes = {i.code for i in AsyncContractsValidator().validate(ctx).issues}
    assert {
        "WS_ASYNC_IDEMPOTENCY_REQUIRED",
        "WS_ASYNC_RETRY_REQUIRED",
        "WS_ASYNC_FAILURE_REQUIRED",
        "WS_ASYNC_DEAD_LETTER_REQUIRED",
    } <= codes
