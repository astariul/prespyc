"""Rectangle record."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from prespyc.errors import Errors, InvalidDataError

if TYPE_CHECKING:
    from collections.abc import Iterable

    from prespyc.parser.reader import Reader
    from prespyc.parser.structure.record.matrix import Matrix


@dataclass(frozen=True, slots=True)
class Rectangle:
    """A rectangle, as two points. Coordinates are in twips (1/20th of a pixel) and may be negative."""

    xmin: int
    xmax: int
    ymin: int
    ymax: int

    def __post_init__(self) -> None:
        assert self.xmin <= self.xmax
        assert self.ymin <= self.ymax

    @property
    def width(self) -> int:
        return self.xmax - self.xmin

    @property
    def height(self) -> int:
        return self.ymax - self.ymin

    def transform(self, matrix: Matrix) -> Rectangle:
        """
        Apply a transformation matrix and return the bounding box of the four transformed corners.
        """
        transform_x = matrix.transform_x
        transform_y = matrix.transform_y

        xs = (
            transform_x(self.xmin, self.ymin),
            transform_x(self.xmax, self.ymin),
            transform_x(self.xmin, self.ymax),
            transform_x(self.xmax, self.ymax),
        )
        ys = (
            transform_y(self.xmin, self.ymin),
            transform_y(self.xmax, self.ymin),
            transform_y(self.xmin, self.ymax),
            transform_y(self.xmax, self.ymax),
        )

        return Rectangle(min(xs), max(xs), min(ys), max(ys))

    def union(self, other: Rectangle) -> Rectangle:
        """Smallest rectangle containing both rectangles."""
        return Rectangle(
            self.xmin if self.xmin < other.xmin else other.xmin,
            self.xmax if self.xmax > other.xmax else other.xmax,
            self.ymin if self.ymin < other.ymin else other.ymin,
            self.ymax if self.ymax > other.ymax else other.ymax,
        )

    @classmethod
    def merge(cls, rectangles: Iterable[Rectangle]) -> Rectangle:
        """
        Smallest rectangle containing all the given rectangles.

        An empty input gives a rectangle with all coordinates set to 0.
        """
        merged: Rectangle | None = None

        for rectangle in rectangles:
            merged = rectangle if merged is None else merged.union(rectangle)

        return merged if merged is not None else Rectangle(0, 0, 0, 0)

    @classmethod
    def read(cls, reader: Reader) -> Self:
        nbits = reader.read_ub(5)
        assert nbits < 32

        xmin = reader.read_sb(nbits)
        xmax = reader.read_sb(nbits)
        ymin = reader.read_sb(nbits)
        ymax = reader.read_sb(nbits)

        if xmin > xmax:
            if reader.errors & Errors.INVALID_DATA:
                raise InvalidDataError(f"Invalid rectangle: xmin ({xmin}) is greater than xmax ({xmax})", reader.offset)

            xmin = xmax

        if ymin > ymax:
            if reader.errors & Errors.INVALID_DATA:
                raise InvalidDataError(f"Invalid rectangle: ymin ({ymin}) is greater than ymax ({ymax})", reader.offset)

            ymin = ymax

        ret = cls(xmin, xmax, ymin, ymax)

        reader.align_byte()

        return ret
