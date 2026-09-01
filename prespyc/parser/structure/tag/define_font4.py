"""DefineFont4 tag."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class DefineFont4Tag:
    """A font character holding an embedded OpenType (CFF) font program."""

    TYPE_V4: ClassVar[int] = 91

    font_id: int
    italic: bool
    bold: bool
    name: bytes
    data: bytes | None

    @classmethod
    def read(cls, reader: Reader, end: int) -> Self:
        """Read a DefineFont4 tag, whose data ends at the `end` byte offset."""
        font_id = reader.read_ui16()

        flags = reader.read_ui8()
        # 5 bits reserved
        font_flags_has_font_data = (flags & 0b00000100) != 0
        font_flags_italic = (flags & 0b00000010) != 0
        font_flags_bold = (flags & 0b00000001) != 0

        font_name = reader.read_null_terminated_string()
        font_data = reader.read_bytes_to(end) if font_flags_has_font_data else None

        return cls(
            font_id=font_id,
            italic=font_flags_italic,
            bold=font_flags_bold,
            name=font_name,
            data=font_data,
        )
