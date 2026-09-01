"""DefineMorphShape tag."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.record.morph_shape.morph_fill_style import MorphFillStyle
from prespyc.parser.structure.record.morph_shape.morph_line_style import MorphLineStyle
from prespyc.parser.structure.record.rectangle import Rectangle
from prespyc.parser.structure.record.shape.shape_record import ShapeRecord

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader
    from prespyc.parser.structure.record.shape.curved_edge_record import CurvedEdgeRecord
    from prespyc.parser.structure.record.shape.end_shape_record import EndShapeRecord
    from prespyc.parser.structure.record.shape.straight_edge_record import StraightEdgeRecord
    from prespyc.parser.structure.record.shape.style_change_record import StyleChangeRecord


@dataclass(frozen=True, slots=True)
class DefineMorphShapeTag:
    """A morph shape character: a start shape and an end shape the player interpolates between."""

    TYPE: ClassVar[int] = 46

    character_id: int
    start_bounds: Rectangle
    end_bounds: Rectangle
    offset: int
    fill_styles: list[MorphFillStyle]
    line_styles: list[MorphLineStyle]
    start_edges: list[StraightEdgeRecord | CurvedEdgeRecord | StyleChangeRecord | EndShapeRecord]
    end_edges: list[StraightEdgeRecord | CurvedEdgeRecord | StyleChangeRecord | EndShapeRecord]

    @classmethod
    def read(cls, reader: Reader) -> Self:
        """Read a DefineMorphShape tag from the given reader."""
        # The shape version only changes the style records, and because morph shapes do not use basic styles,
        # we can safely ignore the version here
        return cls(
            character_id=reader.read_ui16(),
            start_bounds=Rectangle.read(reader),
            end_bounds=Rectangle.read(reader),
            offset=reader.read_ui32(),
            fill_styles=MorphFillStyle.read_collection(reader),
            line_styles=MorphLineStyle.read_collection(reader),
            start_edges=ShapeRecord.read_collection(reader, 1),
            end_edges=ShapeRecord.read_collection(reader, 1),
        )
