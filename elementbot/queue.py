from __future__ import annotations

from .elements import ELEMENTS, Element
from .state import published_numbers


def next_element(data: dict) -> Element | None:
    done = published_numbers(data)
    for el in ELEMENTS:
        if el.z not in done:
            return el
    return None
