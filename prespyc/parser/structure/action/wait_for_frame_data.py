"""Payload of the `ActionWaitForFrame` action."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class WaitForFrameData:
    """Frame to wait for, and how many actions to skip while it is not loaded."""

    frame: int

    skip_count: int

    @classmethod
    def read(cls, reader: Reader) -> Self:
        return cls(
            frame=reader.read_ui16(),
            skip_count=reader.read_ui8(),
        )
