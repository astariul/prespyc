"""Morph fill style record."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.errors import Errors, InvalidDataError
from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.matrix import Matrix
from prespyc.parser.structure.record.morph_shape.morph_gradient import MorphGradient

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class MorphFillStyle:
    """The fill style of a morph shape: every attribute has a start and an end value."""

    SOLID: ClassVar[int] = 0x00
    LINEAR_GRADIENT: ClassVar[int] = 0x10
    RADIAL_GRADIENT: ClassVar[int] = 0x12
    FOCAL_RADIAL_GRADIENT: ClassVar[int] = 0x13
    REPEATING_BITMAP: ClassVar[int] = 0x40
    CLIPPED_BITMAP: ClassVar[int] = 0x41
    NON_SMOOTHED_REPEATING_BITMAP: ClassVar[int] = 0x42
    NON_SMOOTHED_CLIPPED_BITMAP: ClassVar[int] = 0x43

    type: int
    start_color: Color | None = None
    end_color: Color | None = None
    start_gradient_matrix: Matrix | None = None
    end_gradient_matrix: Matrix | None = None
    gradient: MorphGradient | None = None
    bitmap_id: int | None = None
    start_bitmap_matrix: Matrix | None = None
    end_bitmap_matrix: Matrix | None = None

    @classmethod
    def read(cls, reader: Reader) -> Self:
        """Read a MorphFillStyle from the given reader."""
        type_ = reader.read_ui8()

        match type_:
            case cls.SOLID:
                return cls(
                    type=type_,
                    start_color=Color.read_rgba(reader),
                    end_color=Color.read_rgba(reader),
                )
            case cls.LINEAR_GRADIENT | cls.RADIAL_GRADIENT:
                return cls(
                    type=type_,
                    start_gradient_matrix=Matrix.read(reader),
                    end_gradient_matrix=Matrix.read(reader),
                    gradient=MorphGradient.read(reader, focal=False),
                )
            case cls.FOCAL_RADIAL_GRADIENT:
                return cls(
                    type=type_,
                    start_gradient_matrix=Matrix.read(reader),
                    end_gradient_matrix=Matrix.read(reader),
                    gradient=MorphGradient.read(reader, focal=True),
                )
            case (
                cls.REPEATING_BITMAP
                | cls.CLIPPED_BITMAP
                | cls.NON_SMOOTHED_REPEATING_BITMAP
                | cls.NON_SMOOTHED_CLIPPED_BITMAP
            ):
                return cls(
                    type=type_,
                    bitmap_id=reader.read_ui16(),
                    start_bitmap_matrix=Matrix.read(reader),
                    end_bitmap_matrix=Matrix.read(reader),
                )
            case _:
                if reader.errors & Errors.INVALID_DATA:
                    raise InvalidDataError(f"Unknown MorphFillStyle type: {type_}", reader.offset)

                return cls(type_)

    @classmethod
    def read_collection(cls, reader: Reader) -> list[Self]:
        """
        Read multiple MorphFillStyle from the reader.

        The count of elements is determined by the first byte (or 3 bytes for extended).
        """
        count = reader.read_ui8()

        if count == 0xFF:
            count = reader.read_ui16()

        return [cls.read(reader) for _ in range(count)]
