"""Glyph entry record."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class GlyphEntry:
    """A glyph index with its advance value."""

    glyph_index: int
    advance: int

    @classmethod
    def read_collection(cls, reader: Reader, glyph_bits: int, advance_bits: int) -> list[Self]:
        """
        Read a collection of glyph entries. The first byte defines the number of entries to read.

        `glyph_bits` and `advance_bits` are the number of bits used to encode `glyph_index` and
        `advance`.
        """
        count = reader.read_ui8()
        entries = []

        for _ in range(count):
            glyph_index = reader.read_ub(glyph_bits)
            advance = reader.read_sb(advance_bits)

            entries.append(cls(glyph_index=glyph_index, advance=advance))

        return entries
