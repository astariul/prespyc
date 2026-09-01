"""A shape defined by a start and an end state, interpolated at a ratio."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from prespyc.extractor.morph_shape.interpolate import MAX_RATIO as _MAX_RATIO
from prespyc.extractor.morph_shape.interpolate import interpolate_rectangle
from prespyc.extractor.shape.shape import Shape

if TYPE_CHECKING:
    from prespyc.extractor.morph_shape.morph_path import MorphPath
    from prespyc.parser.structure.record.color_transform import ColorTransform
    from prespyc.parser.structure.record.rectangle import Rectangle


@dataclass(frozen=True, slots=True)
class MorphShape:
    """
    The two states of a morph shape, with the paths that morph between them.

    The interpolation helpers themselves live in `prespyc.extractor.morph_shape.interpolate`, because
    the shape edges and the fill types call them too.
    """

    MAX_RATIO: ClassVar[int] = _MAX_RATIO
    """Ratio of the end state. 0 is the start state."""

    start_bounds: Rectangle
    end_bounds: Rectangle

    paths: list[MorphPath]

    def interpolate(self, ratio: int) -> Shape:
        """The shape at `ratio`, between 0 (the start state) and `MAX_RATIO` (the end state)."""
        bounds = self.bounds(ratio)
        paths = []

        for morph_path in self.paths:
            paths.append(morph_path.interpolate(ratio))

        return Shape(
            bounds.width,
            bounds.height,
            -bounds.xmin,
            -bounds.ymin,
            paths,
        )

    def bounds(self, ratio: int) -> Rectangle:
        """The shape bounds at `ratio`."""
        if ratio <= 0:
            return self.start_bounds

        if ratio >= self.MAX_RATIO:
            return self.end_bounds

        return interpolate_rectangle(self.start_bounds, self.end_bounds, ratio)

    def transform_colors(self, color_transform: ColorTransform) -> MorphShape:
        """
        Apply a color transform to the style of every path, and return a new morph shape.

        The current instance is never modified.
        """
        new_paths = []

        for path in self.paths:
            new_paths.append(path.transform_colors(color_transform))

        return MorphShape(
            self.start_bounds,
            self.end_bounds,
            new_paths,
        )
