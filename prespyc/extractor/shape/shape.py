"""A shape extracted from a SWF file."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from prespyc.extractor.shape.path import Path
    from prespyc.parser.structure.record.color_transform import ColorTransform


@dataclass(frozen=True, slots=True)
class Shape:
    """
    A set of paths with a size and an offset. All values are in twips (1/20th of a pixel).
    """

    width: int
    height: int
    x_offset: int
    y_offset: int

    paths: list[Path]
    """Paths in drawing order. Line paths come after fill paths."""

    def transform_colors(self, color_transform: ColorTransform) -> Shape:
        return Shape(
            self.width,
            self.height,
            self.x_offset,
            self.y_offset,
            [path.transform_colors(color_transform) for path in self.paths],
        )
