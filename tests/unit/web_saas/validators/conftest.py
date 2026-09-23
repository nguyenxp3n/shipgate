from types import SimpleNamespace

import pytest


def _factory(**overrides):
    data = {
        "capabilities": {},
        "auth": {},
        "security": {},
        "permissions": {},
        "database": {},
        "async_contracts": {},
        "operations": {},
        "test_matrix": {},
        "work_packages": (),
    }
    data.update(overrides)
    return SimpleNamespace(**data)


@pytest.fixture
def web_context_factory():
    return _factory
