"""Edit text layout record."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class EditTextLayout:
    """Paragraph layout of a `DefineEditTextTag`."""

    align: int
    left_margin: int
    right_margin: int
    indent: int
    leading: int

    @classmethod
    def read(cls, reader: Reader) -> Self:
        return cls(
            align=reader.read_ui8(),
            left_margin=reader.read_ui16(),
            right_margin=reader.read_ui16(),
            indent=reader.read_ui16(),
            leading=reader.read_si16(),
        )
