"""DefineFont2 and DefineFont3 tags."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.record.font_layout import FontLayout
from prespyc.parser.structure.record.shape.shape_record import ShapeRecord

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader
    from prespyc.parser.structure.record.shape.curved_edge_record import CurvedEdgeRecord
    from prespyc.parser.structure.record.shape.end_shape_record import EndShapeRecord
    from prespyc.parser.structure.record.shape.straight_edge_record import StraightEdgeRecord
    from prespyc.parser.structure.record.shape.style_change_record import StyleChangeRecord


@dataclass(frozen=True, slots=True)
class DefineFont2Or3Tag:
    """A font character with a name, a code table and an optional layout."""

    TYPE_V2: ClassVar[int] = 48
    TYPE_V3: ClassVar[int] = 75

    version: int
    font_id: int
    font_flags_shift_jis: bool
    font_flags_small_text: bool
    font_flags_ansi: bool
    font_flags_wide_codes: bool
    font_flags_italic: bool
    font_flags_bold: bool
    language_code: int
    font_name: bytes
    num_glyphs: int
    offset_table: list[int]
    glyph_shape_table: list[list[StraightEdgeRecord | CurvedEdgeRecord | StyleChangeRecord | EndShapeRecord]]
    code_table: list[int]
    layout: FontLayout | None

    @classmethod
    def read(cls, reader: Reader, version: int) -> Self:
        """Read a DefineFont2 or DefineFont3 tag. `version` is the tag version, 2 or 3."""
        font_id = reader.read_ui16()

        flags = reader.read_ui8()
        font_flags_has_layout = (flags & 0b10000000) != 0
        font_flags_shift_jis = (flags & 0b01000000) != 0
        font_flags_small_text = (flags & 0b00100000) != 0
        font_flags_ansi = (flags & 0b00010000) != 0
        font_flags_wide_offsets = (flags & 0b00001000) != 0
        font_flags_wide_codes = (flags & 0b00000100) != 0 or version > 2  # Wide codes are always used in version 3
        font_flags_italic = (flags & 0b00000010) != 0
        font_flags_bold = (flags & 0b00000001) != 0

        language_code = reader.read_ui8()
        font_name_length = reader.read_ui8()
        font_name = reader.read_bytes(font_name_length)[:-1]  # Remove trailing NULL
        num_glyphs = reader.read_ui16()

        offset_table = []
        for _ in range(num_glyphs):
            offset_table.append(reader.read_ui32() if font_flags_wide_offsets else reader.read_ui16())

        # CodeTableOffset: not used by the implementation, so simply skip it
        if font_flags_wide_offsets:
            reader.skip_bytes(4)  # UI32
        else:
            reader.skip_bytes(2)  # UI16

        glyph_shape_table = []
        for _ in range(num_glyphs):
            glyph_shape_table.append(ShapeRecord.read_collection(reader, 1))

        code_table = []
        for _ in range(num_glyphs):
            code_table.append(reader.read_ui16() if font_flags_wide_codes else reader.read_ui8())

        layout = FontLayout.read(reader, num_glyphs, font_flags_wide_codes) if font_flags_has_layout else None

        return cls(
            version,
            font_id,
            font_flags_shift_jis,
            font_flags_small_text,
            font_flags_ansi,
            font_flags_wide_codes,
            font_flags_italic,
            font_flags_bold,
            language_code,
            font_name,
            num_glyphs,
            offset_table,
            glyph_shape_table,
            code_table,
            layout,
        )
