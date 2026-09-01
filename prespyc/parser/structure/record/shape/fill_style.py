"""Fill style record."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.errors import Errors, InvalidDataError
from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.gradient import Gradient
from prespyc.parser.structure.record.matrix import Matrix

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class FillStyle:
    """How a shape is filled: a solid color, a gradient or a bitmap."""

    SOLID: ClassVar[int] = 0x00
    LINEAR_GRADIENT: ClassVar[int] = 0x10
    RADIAL_GRADIENT: ClassVar[int] = 0x12
    FOCAL_GRADIENT: ClassVar[int] = 0x13
    REPEATING_BITMAP: ClassVar[int] = 0x40
    CLIPPED_BITMAP: ClassVar[int] = 0x41
    NON_SMOOTHED_REPEATING_BITMAP: ClassVar[int] = 0x42
    NON_SMOOTHED_CLIPPED_BITMAP: ClassVar[int] = 0x43

    type: int
    color: Color | None = None
    matrix: Matrix | None = None
    gradient: Gradient | None = None
    focal_gradient: Gradient | None = None
    bitmap_id: int | None = None
    bitmap_matrix: Matrix | None = None

    @classmethod
    def read(cls, reader: Reader, version: int) -> Self:
        """Read a fill style from the reader. `version` is the version of the shape tag, 1 to 4."""
        type_ = reader.read_ui8()

        match type_:
            case FillStyle.SOLID:
                style = cls(type_, color=Color.read_rgb(reader) if version < 3 else Color.read_rgba(reader))
            case FillStyle.LINEAR_GRADIENT | FillStyle.RADIAL_GRADIENT:
                style = cls(
                    type_,
                    matrix=Matrix.read(reader),
                    gradient=Gradient.read(reader, version > 2),
                )
            case FillStyle.FOCAL_GRADIENT:
                style = cls(
                    type_,
                    matrix=Matrix.read(reader),
                    focal_gradient=Gradient.read_focal(reader),
                )
            case (
                FillStyle.REPEATING_BITMAP
                | FillStyle.CLIPPED_BITMAP
                | FillStyle.NON_SMOOTHED_REPEATING_BITMAP
                | FillStyle.NON_SMOOTHED_CLIPPED_BITMAP
            ):
                style = cls(
                    type_,
                    bitmap_id=reader.read_ui16(),
                    bitmap_matrix=Matrix.read(reader),
                )
            case _:
                if reader.errors & Errors.INVALID_DATA:
                    raise InvalidDataError(f"Unsupported FillStyle type {type_}", reader.offset)

                style = cls(type_)

        reader.align_byte()

        return style

    @classmethod
    def read_collection(cls, reader: Reader, version: int) -> list[Self]:
        """
        Read a collection of fill styles from the reader.
        The number of fill styles is defined by the first byte (or 3 if extended).

        `version` is the version of the shape tag, 1 to 4.
        """
        fill_style_count = reader.read_ui8()
        fill_style_array = []

        if version >= 2 and fill_style_count == 0xFF:
            fill_style_count = reader.read_ui16()

        for _ in range(fill_style_count):
            fill_style_array.append(cls.read(reader, version))

        return fill_style_array
