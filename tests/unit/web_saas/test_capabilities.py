import pytest

from project_finalizer.web_saas.capabilities import CapabilitySet


def test_disabled_extension_has_no_obligations() -> None:
    caps = CapabilitySet.from_mapping({"payments": "disabled"})
    assert caps.enabled("payments") is False
    assert "payments" not in caps.obligation_sets()


def test_unknown_capability_state_is_rejected() -> None:
    with pytest.raises(ValueError, match="capability state"):
        CapabilitySet.from_mapping({"payments": "maybe"})


def test_required_and_optional_enabled_count_as_enabled() -> None:
    caps = CapabilitySet.from_mapping({"frontend": "required", "email": "optional_enabled"})
    assert caps.enabled("frontend") is True
    assert caps.enabled("email") is True
