from __future__ import annotations

import unicodedata
from collections.abc import Iterable


def normalize_id(value: str) -> str:
    return unicodedata.normalize("NFC", value).casefold()


def assert_unique_ids(values: Iterable[str]) -> None:
    seen: dict[str, str] = {}
    for value in values:
        logical = normalize_id(value)
        if logical in seen:
            raise ValueError(f"duplicate logical identifier: {seen[logical]!r} and {value!r}")
        seen[logical] = value
