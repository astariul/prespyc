"""Morph line style record."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from prespyc.parser.structure.record.color import Color

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class MorphLineStyle:
    """The line style of a morph shape: every attribute has a start and an end value."""

    start_width: int
    end_width: int
    start_color: Color
    end_color: Color

    @classmethod
    def read_collection(cls, reader: Reader) -> list[Self]:
        """
        Read a MorphLineStyle collection.

        The collection size is determined by the first byte read (or 3 if extended).
        """
        count = reader.read_ui8()

        if count == 0xFF:
            count = reader.read_ui16()

        return [
            cls(
                start_width=reader.read_ui16(),
                end_width=reader.read_ui16(),
                start_color=Color.read_rgba(reader),
                end_color=Color.read_rgba(reader),
            )
            for _ in range(count)
        ]
