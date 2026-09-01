"""DefineShape tag, versions 1 to 3."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.record.rectangle import Rectangle
from prespyc.parser.structure.record.shape.shape_with_style import ShapeWithStyle

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class DefineShapeTag:
    """A shape character: its bounding box and the styled edges that draw it."""

    TYPE_V1: ClassVar[int] = 2
    TYPE_V2: ClassVar[int] = 22
    TYPE_V3: ClassVar[int] = 32

    version: int
    """Version of the tag, 1 to 3."""

    shape_id: int
    shape_bounds: Rectangle
    shapes: ShapeWithStyle

    @classmethod
    def read(cls, reader: Reader, version: int) -> Self:
        """Read a DefineShape tag. `version` is the version of the tag (should be 1, 2 or 3)."""
        return cls(
            version=version,
            shape_id=reader.read_ui16(),
            shape_bounds=Rectangle.read(reader),
            shapes=ShapeWithStyle.read(reader, version),
        )
