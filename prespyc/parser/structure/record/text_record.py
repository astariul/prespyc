"""Text record."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Self

from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.glyph_entry import GlyphEntry

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class TextRecord:
    """A run of glyphs sharing a font, color and position."""

    type: int
    """Should be always 1."""

    font_id: int | None
    color: Color | None
    x_offset: int | None
    y_offset: int | None

    height: int | None
    """The text height in twips (1/20 of a pixel). Defined only if `font_id` is not None."""

    glyphs: list[GlyphEntry] = field(default_factory=list)

    @classmethod
    def read_collection(cls, reader: Reader, glyph_bits: int, advance_bits: int, with_alpha: bool) -> list[Self]:
        """
        Read a text record collection. Records are read until an empty flag is found.

        `glyph_bits` and `advance_bits` are the number of bits used to encode the glyph index and
        the advance. `with_alpha` selects a text color with an alpha channel (for `DefineText2`).
        """
        records = []

        while reader.offset < reader.end:
            flags = reader.read_ui8()

            if flags == 0:
                break

            type_ = flags >> 7
            # 3 bits reserved
            has_font = (flags & 0b1000) != 0
            has_color = (flags & 0b0100) != 0
            has_y_offset = (flags & 0b0010) != 0
            has_x_offset = (flags & 0b0001) != 0

            font_id = reader.read_ui16() if has_font else None
            color = (Color.read_rgba(reader) if with_alpha else Color.read_rgb(reader)) if has_color else None
            x_offset = reader.read_si16() if has_x_offset else None
            y_offset = reader.read_si16() if has_y_offset else None
            height = reader.read_ui16() if has_font else None

            records.append(
                cls(
                    type=type_,
                    font_id=font_id,
                    color=color,
                    x_offset=x_offset,
                    y_offset=y_offset,
                    height=height,
                    glyphs=GlyphEntry.read_collection(reader, glyph_bits, advance_bits),
                )
            )

            reader.align_byte()

        return records
