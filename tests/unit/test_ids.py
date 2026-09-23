import pytest

from project_finalizer.ids import assert_unique_ids


def test_casefold_equivalent_ids_are_duplicates():
    with pytest.raises(ValueError, match="duplicate logical identifier"):
        assert_unique_ids(["Users", "users"])


def test_unicode_normalized_equivalent_ids_are_duplicates():
    with pytest.raises(ValueError, match="duplicate logical identifier"):
        assert_unique_ids(["Café", "Cafe\u0301"])
