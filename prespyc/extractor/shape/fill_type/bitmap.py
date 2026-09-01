"""Bitmap fill."""

from __future__ import annotations

import zlib
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from prespyc.extractor.image.image_character import ImageCharacter
    from prespyc.parser.structure.record.color_transform import ColorTransform
    from prespyc.parser.structure.record.matrix import Matrix


@dataclass(frozen=True, slots=True)
class Bitmap:
    """A raster image fill."""

    bitmap: ImageCharacter
    matrix: Matrix
    smoothed: bool = True
    repeat: bool = False
    _hash: str = field(default="", init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "_hash", self._compute_hash())

    @property
    def hash(self) -> str:
        return self._hash

    def transform_colors(self, color_transform: ColorTransform) -> Bitmap:
        # Note: PHP drops `smoothed`/`repeat` here too.
        return Bitmap(self.bitmap.transform_colors(color_transform), self.matrix)

    def interpolate(self, other: Bitmap, ratio: int) -> Bitmap:
        """Only the matrix is interpolated."""
        from prespyc.extractor.morph_shape.interpolate import interpolate_matrix

        return Bitmap(self.bitmap, interpolate_matrix(self.matrix, other.matrix, ratio), self.smoothed, self.repeat)

    def _compute_hash(self) -> str:
        from prespyc.extractor.image.transformed_image import TransformedImage

        image_hash = str(self.bitmap.character_id)

        # A color transform must give a different hash, so mix in the transformed pixels.
        if isinstance(self.bitmap, TransformedImage):
            image_hash += "-" + str(zlib.crc32(self.bitmap.to_png()))

        prefix = ("R" if self.repeat else "C") + "B"

        if not self.smoothed:
            prefix += "N"

        return prefix + image_hash + "-" + str(zlib.crc32(self.matrix.to_svg_transformation().encode()))
