"""Font layout record."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Self

from prespyc.parser.structure.record.kerning_record import KerningRecord
from prespyc.parser.structure.record.rectangle import Rectangle

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class FontLayout:
    """Glyph metrics of a `DefineFont2Or3Tag`."""

    ascent: int
    descent: int
    leading: int
    advance_table: list[int]
    bounds_table: list[Rectangle]
    kerning_table: list[KerningRecord] = field(default_factory=list)

    @classmethod
    def read(cls, reader: Reader, num_glyphs: int, wide_codes: bool) -> Self:
        """
        Read a font layout record.

        `num_glyphs` is the number of glyphs in the font. `wide_codes` selects 16-bit glyph codes
        instead of 8-bit ones for the kerning table.
        """
        ascent = reader.read_si16()
        descent = reader.read_si16()
        leading = reader.read_si16()

        advance_table = []
        for _ in range(num_glyphs):
            advance_table.append(reader.read_si16())

        bounds_table = []
        for _ in range(num_glyphs):
            bounds_table.append(Rectangle.read(reader))

        kerning_count = reader.read_ui16()
        kerning_table = []
        for _ in range(kerning_count):
            code1 = reader.read_ui16() if wide_codes else reader.read_ui8()
            code2 = reader.read_ui16() if wide_codes else reader.read_ui8()
            adjustment = reader.read_si16()

            kerning_table.append(KerningRecord(code1, code2, adjustment))

        return cls(ascent, descent, leading, advance_table, bounds_table, kerning_table)
