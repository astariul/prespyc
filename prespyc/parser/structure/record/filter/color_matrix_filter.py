"""Color matrix filter record."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.record.filter.filter import Filter

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class ColorMatrixFilter(Filter):
    """Color matrix filter."""

    FILTER_ID: ClassVar[int] = 6

    matrix: list[float]
    """Size must be 20."""

    def __post_init__(self) -> None:
        assert len(self.matrix) == 20

    @classmethod
    def _read(cls, reader: Reader) -> Self:
        matrix = []

        for _ in range(20):
            matrix.append(reader.read_float())

        return cls(matrix)
