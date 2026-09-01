"""FrameLabel tag."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class FrameLabelTag:
    """Names the current frame, so it can be targeted by `gotoAndPlay` and friends."""

    TYPE: ClassVar[int] = 43

    label: bytes
    named_anchor: bool = False

    @classmethod
    def read(cls, reader: Reader, end: int) -> Self:
        """Read a FrameLabel tag, whose data ends at the `end` byte offset."""
        # Parse null-terminated string
        label = reader.read_null_terminated_string()

        # Since SWF 6, the flag namedAnchor is present to create a named anchor
        # So we need to check if there is still data to read, and if so, read the flag
        has_more_data = reader.offset < end

        return cls(
            label,
            has_more_data and reader.read_ui8() == 1,
        )
