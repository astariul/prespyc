"""Transformation matrix record."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from prespyc._util import num, php_round, round_int

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class Matrix:
    """A 2D transformation matrix."""

    scale_x: float = 1.0
    """Horizontal scaling factor. Parameter A of the matrix."""

    scale_y: float = 1.0
    """Vertical scaling factor. Parameter D of the matrix."""

    rotate_skew0: float = 0.0
    """First skew factor. Parameter B of the matrix."""

    rotate_skew1: float = 0.0
    """Second skew factor. Parameter C of the matrix."""

    translate_x: int = 0
    """X-axis translation, in twips. Parameter E (or Tx) of the matrix."""

    translate_y: int = 0
    """Y-axis translation, in twips. Parameter F (or Ty) of the matrix."""

    def translate(self, x: int, y: int) -> Matrix:
        """
        Add a translation and return a new matrix.

        The translation goes through the current matrix before being applied.
        """
        return Matrix(
            self.scale_x,
            self.scale_y,
            self.rotate_skew0,
            self.rotate_skew1,
            round_int(self.scale_x * x + self.rotate_skew1 * y + self.translate_x),
            round_int(self.rotate_skew0 * x + self.scale_y * y + self.translate_y),
        )

    def transform_x(self, x: int, y: int) -> int:
        """X coordinate of `(x, y)` transformed by the matrix."""
        return round_int(self.scale_x * x + self.rotate_skew1 * y + self.translate_x)

    def transform_y(self, x: int, y: int) -> int:
        """Y coordinate of `(x, y)` transformed by the matrix."""
        return round_int(self.rotate_skew0 * x + self.scale_y * y + self.translate_y)

    def to_svg_transformation(self, undo_twip_scale: bool = False) -> str:
        """
        SVG `matrix(...)` representation.

        With `undo_twip_scale`, the scaling factors are divided by 20, undoing the conversion to
        twips.
        """
        scale_x = self.scale_x
        scale_y = self.scale_y
        rotate_skew0 = self.rotate_skew0
        rotate_skew1 = self.rotate_skew1

        if undo_twip_scale:
            scale_x /= 20
            scale_y /= 20
            rotate_skew0 /= 20
            rotate_skew1 /= 20

        return (
            f"matrix({num(php_round(scale_x, 4))}, {num(php_round(rotate_skew0, 4))}, "
            f"{num(php_round(rotate_skew1, 4))}, {num(php_round(scale_y, 4))}, "
            f"{num(php_round(self.translate_x / 20, 4))}, {num(php_round(self.translate_y / 20, 4))})"
        )

    @classmethod
    def read(cls, reader: Reader) -> Self:
        scale_x = 1.0
        scale_y = 1.0
        rotate_skew0 = 0.0
        rotate_skew1 = 0.0
        translate_x = 0
        translate_y = 0

        if reader.read_bool():
            scale_bits = reader.read_ub(5)
            assert scale_bits < 32
            scale_x = reader.read_fb(scale_bits)
            scale_y = reader.read_fb(scale_bits)

        if reader.read_bool():
            rotate_bits = reader.read_ub(5)
            assert rotate_bits < 32
            rotate_skew0 = reader.read_fb(rotate_bits)
            rotate_skew1 = reader.read_fb(rotate_bits)

        translate_bits = reader.read_ub(5)

        if translate_bits != 0:
            assert translate_bits < 32
            translate_x = reader.read_sb(translate_bits)
            translate_y = reader.read_sb(translate_bits)

        reader.align_byte()

        return cls(scale_x, scale_y, rotate_skew0, rotate_skew1, translate_x, translate_y)
