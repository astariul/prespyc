"""SoundStreamBlock tag."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class SoundStreamBlockTag:
    """One frame's worth of streaming sound data."""

    TYPE: ClassVar[int] = 19

    sound_data: bytes

    @classmethod
    def read(cls, reader: Reader, end: int) -> Self:
        """Read a SoundStreamBlock tag, whose data ends at the `end` byte offset."""
        return cls(reader.read_bytes_to(end))
