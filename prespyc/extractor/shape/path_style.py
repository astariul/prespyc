"""Drawing style of a path."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from prespyc.extractor.shape.fill_type.fill_type import FillType
    from prespyc.parser.structure.record.color import Color
    from prespyc.parser.structure.record.color_transform import ColorTransform


@dataclass(frozen=True, slots=True)
class PathStyle:
    """
    How a path is drawn. Shared by fill and line paths, and used as the key that merges paths with
    the same style.
    """

    fill: FillType | None = None
    """Fill style and color. `None` means the path is not filled."""

    line_color: Color | None = None
    """Line color. `None` means the path is not stroked, unless `line_fill` is set."""

    line_fill: FillType | None = None
    """
    Fill applied to the stroke, within its width, instead of filling the polygon as `fill` does.
    """

    line_width: int = 0
    """Line width in twips. Only meaningful when `line_color` or `line_fill` is set."""

    reverse: bool = False
    """
    Whether the edges are added in reverse order. True for style0 fill paths.

    Not part of the hash: it only affects path building.
    """

    id: str | None = None
    """Explicit grouping key. When `None`, the hash is derived from the style itself."""

    _hash: str = field(default="", init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if self.id is not None:
            object.__setattr__(self, "_hash", self.id)
        else:
            fill_hash = self.fill.hash if self.fill is not None else ""
            line_fill_hash = self.line_fill.hash if self.line_fill is not None else ""
            object.__setattr__(
                self,
                "_hash",
                f"{fill_hash}{line_fill_hash}-{_color_hash(self.line_color)}-{self.line_width}",
            )

    @property
    def hash(self) -> str:
        """Grouping key of the style."""
        return self._hash

    @property
    def is_line_style(self) -> bool:
        """Whether the style strokes a line."""
        return self.line_color is not None or self.line_fill is not None

    @property
    def is_empty(self) -> bool:
        """Whether the style draws nothing at all."""
        return self.fill is None and self.line_width == 0

    def transform_colors(self, color_transform: ColorTransform) -> PathStyle:
        return PathStyle(
            self.fill.transform_colors(color_transform) if self.fill is not None else None,
            self.line_color.transform(color_transform) if self.line_color is not None else None,
            self.line_fill.transform_colors(color_transform) if self.line_fill is not None else None,
            self.line_width,
            self.reverse,
        )


def _color_hash(color: Color | None) -> int:
    if color is None:
        return -1

    alpha = color.alpha if color.alpha is not None else 255

    return (color.red << 24) | (color.green << 16) | (color.blue << 8) | alpha
