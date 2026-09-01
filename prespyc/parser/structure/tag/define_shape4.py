"""DefineShape4 tag."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.record.rectangle import Rectangle
from prespyc.parser.structure.record.shape.shape_with_style import ShapeWithStyle

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class DefineShape4Tag:
    """A shape character with stroke hinting and an extra edge bounding box."""

    TYPE_V4: ClassVar[int] = 83

    shape_id: int
    shape_bounds: Rectangle
    edge_bounds: Rectangle
    reserved: int
    uses_fill_winding_rule: bool
    uses_non_scaling_strokes: bool
    uses_scaling_strokes: bool
    shapes: ShapeWithStyle

    @classmethod
    def read(cls, reader: Reader) -> Self:
        return cls(
            shape_id=reader.read_ui16(),
            shape_bounds=Rectangle.read(reader),
            edge_bounds=Rectangle.read(reader),
            reserved=reader.read_ub(5),
            uses_fill_winding_rule=reader.read_bool(),
            uses_non_scaling_strokes=reader.read_bool(),
            uses_scaling_strokes=reader.read_bool(),
            shapes=ShapeWithStyle.read(reader, 4),
        )
