"""End tag: marks the end of a tag list."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True, slots=True)
class EndTag:
    """Last tag of a tag list. Carries no data."""

    TYPE: ClassVar[int] = 0
