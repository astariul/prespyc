"""Shape with style record."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from prespyc.parser.structure.record.shape.fill_style import FillStyle
from prespyc.parser.structure.record.shape.line_style import LineStyle
from prespyc.parser.structure.record.shape.shape_record import ShapeRecord

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader
    from prespyc.parser.structure.record.shape.curved_edge_record import CurvedEdgeRecord
    from prespyc.parser.structure.record.shape.end_shape_record import EndShapeRecord
    from prespyc.parser.structure.record.shape.straight_edge_record import StraightEdgeRecord
    from prespyc.parser.structure.record.shape.style_change_record import StyleChangeRecord


@dataclass(frozen=True, slots=True)
class ShapeWithStyle:
    """Shape structure of `DefineShapeTag` and `DefineShape4Tag`."""

    fill_styles: list[FillStyle]
    line_styles: list[LineStyle]
    shape_records: list[StraightEdgeRecord | CurvedEdgeRecord | StyleChangeRecord | EndShapeRecord]

    @classmethod
    def read(cls, reader: Reader, version: int) -> Self:
        """Read a shape with style from the reader. `version` is the version of the shape tag, 1 to 4."""
        return cls(
            FillStyle.read_collection(reader, version),
            LineStyle.read_collection(reader, version),
            ShapeRecord.read_collection(reader, version),
        )
