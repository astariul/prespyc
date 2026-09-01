"""DefineMorphShape2 tag."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.record.morph_shape.morph_fill_style import MorphFillStyle
from prespyc.parser.structure.record.morph_shape.morph_line_style2 import MorphLineStyle2
from prespyc.parser.structure.record.rectangle import Rectangle
from prespyc.parser.structure.record.shape.shape_record import ShapeRecord

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader
    from prespyc.parser.structure.record.shape.curved_edge_record import CurvedEdgeRecord
    from prespyc.parser.structure.record.shape.end_shape_record import EndShapeRecord
    from prespyc.parser.structure.record.shape.straight_edge_record import StraightEdgeRecord
    from prespyc.parser.structure.record.shape.style_change_record import StyleChangeRecord


@dataclass(frozen=True, slots=True)
class DefineMorphShape2Tag:
    """A morph shape character, with edge bounds and stroke scaling flags."""

    TYPE: ClassVar[int] = 84

    character_id: int
    start_bounds: Rectangle
    end_bounds: Rectangle
    start_edge_bounds: Rectangle
    end_edge_bounds: Rectangle
    uses_non_scaling_strokes: bool
    uses_scaling_strokes: bool
    offset: int
    fill_styles: list[MorphFillStyle]
    line_styles: list[MorphLineStyle2]
    start_edges: list[StraightEdgeRecord | CurvedEdgeRecord | StyleChangeRecord | EndShapeRecord]
    end_edges: list[StraightEdgeRecord | CurvedEdgeRecord | StyleChangeRecord | EndShapeRecord]

    @classmethod
    def read(cls, reader: Reader) -> Self:
        """Read a DefineMorphShape2 tag from the given reader."""
        character_id = reader.read_ui16()
        start_bounds = Rectangle.read(reader)
        end_bounds = Rectangle.read(reader)

        start_edge_bounds = Rectangle.read(reader)
        end_edge_bounds = Rectangle.read(reader)

        flags = reader.read_ui8()
        # 6 bits are reserved
        uses_non_scaling_strokes = (flags & 0b00000010) != 0
        uses_scaling_strokes = (flags & 0b00000001) != 0

        # The shape version only changes the style records, and because morph shapes do not use basic styles,
        # we can safely ignore the version here
        return cls(
            character_id=character_id,
            start_bounds=start_bounds,
            end_bounds=end_bounds,
            start_edge_bounds=start_edge_bounds,
            end_edge_bounds=end_edge_bounds,
            uses_non_scaling_strokes=uses_non_scaling_strokes,
            uses_scaling_strokes=uses_scaling_strokes,
            offset=reader.read_ui32(),
            fill_styles=MorphFillStyle.read_collection(reader),
            line_styles=MorphLineStyle2.read_collection(reader),
            start_edges=ShapeRecord.read_collection(reader, 1),
            end_edges=ShapeRecord.read_collection(reader, 1),
        )
