"""DefineFont tag."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.record.shape.shape_record import ShapeRecord

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader
    from prespyc.parser.structure.record.shape.curved_edge_record import CurvedEdgeRecord
    from prespyc.parser.structure.record.shape.end_shape_record import EndShapeRecord
    from prespyc.parser.structure.record.shape.straight_edge_record import StraightEdgeRecord
    from prespyc.parser.structure.record.shape.style_change_record import StyleChangeRecord


@dataclass(frozen=True, slots=True)
class DefineFontTag:
    """A font character: the glyph shapes, without any layout or code table."""

    TYPE_V1: ClassVar[int] = 10

    font_id: int
    offset_table: list[int]
    glyph_shape_data: list[list[StraightEdgeRecord | CurvedEdgeRecord | StyleChangeRecord | EndShapeRecord]]

    @classmethod
    def read(cls, reader: Reader) -> Self:
        """Read a DefineFont tag from the reader."""
        font_id = reader.read_ui16()

        # The first offset must point to the first glyph, and because each offset is 2 bytes,
        # the number of glyphs is the offset of the first glyph divided by 2.
        num_glyphs = reader.peek_ui16() >> 1

        offset_table = []
        for _ in range(num_glyphs):
            offset_table.append(reader.read_ui16())

        glyph_shape_data = []
        for _ in range(num_glyphs):
            glyph_shape_data.append(ShapeRecord.read_collection(reader, 1))

        return cls(
            font_id=font_id,
            offset_table=offset_table,
            glyph_shape_data=glyph_shape_data,
        )
