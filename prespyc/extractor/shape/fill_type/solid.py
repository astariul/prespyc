"""Solid color fill."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from prespyc.parser.structure.record.color import Color

if TYPE_CHECKING:
    from prespyc.parser.structure.record.color_transform import ColorTransform


@dataclass(frozen=True, slots=True)
class Solid:
    """A single color fill."""

    color: Color

    @property
    def hash(self) -> str:
        color = self.color
        alpha = color.alpha if color.alpha is not None else 255

        return "S" + str((color.red << 24) | (color.green << 16) | (color.blue << 8) | alpha)

    def transform_colors(self, color_transform: ColorTransform) -> Solid:
        return Solid(color_transform.transform(self.color))

    def interpolate(self, other: Solid, ratio: int) -> Solid:
        from prespyc.extractor.morph_shape.interpolate import interpolate_color

        return Solid(interpolate_color(self.color, other.color, ratio))
