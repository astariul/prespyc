"""Color transform record."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader

from prespyc.parser.structure.record.color import Color


@dataclass(frozen=True, slots=True)
class ColorTransform:
    """A color transform. Multiplier terms are expressed over 256."""

    red_mult: int = 256
    green_mult: int = 256
    blue_mult: int = 256
    alpha_mult: int = 256
    red_add: int = 0
    green_add: int = 0
    blue_add: int = 0
    alpha_add: int = 0

    def transform(self, color: Color) -> Color:
        """Apply the transform to a color."""
        red = color.red * self.red_mult / 256 + self.red_add
        green = color.green * self.green_mult / 256 + self.green_add
        blue = color.blue * self.blue_mult / 256 + self.blue_add
        alpha = (color.alpha if color.alpha is not None else 255) * self.alpha_mult / 256 + self.alpha_add

        if red < 0:
            red = 0
        elif red > 255:
            red = 255

        if green < 0:
            green = 0
        elif green > 255:
            green = 255

        if blue < 0:
            blue = 0
        elif blue > 255:
            blue = 255

        if alpha < 0:
            alpha = 0
        elif alpha > 255:
            alpha = 255

        return Color(int(red), int(green), int(blue), int(alpha))

    def append(self, next_transform: ColorTransform) -> ColorTransform:
        """
        Combine with another transform, as if this one were applied first and the other second.

        Not exactly the same as applying both transforms to a color one after the other, because
        each application clamps to 0-255.
        """
        return ColorTransform(
            red_mult=(self.red_mult * next_transform.red_mult) >> 8,
            green_mult=(self.green_mult * next_transform.green_mult) >> 8,
            blue_mult=(self.blue_mult * next_transform.blue_mult) >> 8,
            alpha_mult=(self.alpha_mult * next_transform.alpha_mult) >> 8,
            red_add=((self.red_add * next_transform.red_mult) >> 8) + next_transform.red_add,
            green_add=((self.green_add * next_transform.green_mult) >> 8) + next_transform.green_add,
            blue_add=((self.blue_add * next_transform.blue_mult) >> 8) + next_transform.blue_add,
            alpha_add=((self.alpha_add * next_transform.alpha_mult) >> 8) + next_transform.alpha_add,
        )

    @classmethod
    def read(cls, reader: Reader, with_alpha: bool) -> Self:
        has_add_terms = reader.read_bool()
        has_mult_terms = reader.read_bool()
        nbits = reader.read_ub(4)
        assert nbits < 16

        red_mult = 256
        green_mult = 256
        blue_mult = 256
        alpha_mult = 256
        red_add = 0
        green_add = 0
        blue_add = 0
        alpha_add = 0

        if has_mult_terms:
            red_mult = reader.read_sb(nbits)
            green_mult = reader.read_sb(nbits)
            blue_mult = reader.read_sb(nbits)

            if with_alpha:
                alpha_mult = reader.read_sb(nbits)

        if has_add_terms:
            red_add = reader.read_sb(nbits)
            green_add = reader.read_sb(nbits)
            blue_add = reader.read_sb(nbits)

            if with_alpha:
                alpha_add = reader.read_sb(nbits)

        reader.align_byte()

        return cls(red_mult, green_mult, blue_mult, alpha_mult, red_add, green_add, blue_add, alpha_add)
