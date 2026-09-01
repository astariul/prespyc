"""Morphing between two paths of a morph shape."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from prespyc.extractor.morph_shape.interpolate import MAX_RATIO, interpolate_color, interpolate_int
from prespyc.extractor.shape.path import Path
from prespyc.extractor.shape.path_style import PathStyle

if TYPE_CHECKING:
    from prespyc.extractor.shape.fill_type.fill_type import FillType
    from prespyc.parser.structure.record.color_transform import ColorTransform


@dataclass(frozen=True, slots=True)
class MorphPath:
    """
    Morphing between two paths.

    Both paths must have the same number of edges.
    """

    start: Path
    end: Path

    def __post_init__(self) -> None:
        assert len(self.start.edges) == len(self.end.edges)

    def interpolate(self, ratio: int) -> Path:
        """The path at `ratio`: 0 is the start path, `MAX_RATIO` the end path."""
        if ratio <= 0:
            return self.start

        if ratio >= MAX_RATIO:
            return self.end

        edges = []

        for index, start_edge in enumerate(self.start.edges):
            end_edge = self.end.edges[index]
            edges.append(start_edge.interpolate(end_edge, ratio))

        return Path(
            edges,
            self._interpolate_style(self.start.style, self.end.style, ratio),
        )

    def transform_colors(self, color_transform: ColorTransform) -> MorphPath:
        return MorphPath(
            self.start.transform_colors(color_transform),
            self.end.transform_colors(color_transform),
        )

    def _interpolate_style(self, start: PathStyle, end: PathStyle, ratio: int) -> PathStyle:
        line_width = interpolate_int(start.line_width, end.line_width, ratio)
        assert line_width >= 0

        line_color = None

        if start.line_color is not None and end.line_color is not None:
            line_color = interpolate_color(start.line_color, end.line_color, ratio)

        return PathStyle(
            fill=self._interpolate_fill_style(start.fill, end.fill, ratio),
            line_color=line_color,
            line_fill=self._interpolate_fill_style(start.line_fill, end.line_fill, ratio),
            line_width=line_width,
        )

    def _interpolate_fill_style(self, start: FillType | None, end: FillType | None, ratio: int) -> FillType | None:
        # PHP: `!$start instanceof $end` — the end fill type is the class to check against, so a
        # radial gradient does match a linear one, but not the other way around.
        if start is None or end is None or not isinstance(start, type(end)):
            return None

        if start == end:
            return start

        return start.interpolate(end, ratio)
