"""ShowFrame tag: renders the current display list and advances to the next frame."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True, slots=True)
class ShowFrameTag:
    """Marks the end of a frame. Carries no data."""

    TYPE: ClassVar[int] = 1
