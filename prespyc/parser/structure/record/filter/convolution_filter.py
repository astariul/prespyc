"""Convolution filter record."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.filter.filter import Filter

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class ConvolutionFilter(Filter):
    """Convolution filter."""

    FILTER_ID: ClassVar[int] = 5

    matrix_x: int
    matrix_y: int
    divisor: float
    bias: float
    matrix: list[float]
    default_color: Color
    clamp: bool
    preserve_alpha: bool

    def __post_init__(self) -> None:
        assert len(self.matrix) == self.matrix_x * self.matrix_y

    @classmethod
    def _read(cls, reader: Reader) -> Self:
        matrix_x = reader.read_ui8()
        matrix_y = reader.read_ui8()
        divisor = reader.read_float()
        bias = reader.read_float()
        matrix = []

        for _ in range(matrix_x * matrix_y):
            matrix.append(reader.read_float())

        default_color = Color.read_rgba(reader)
        flags = reader.read_ui8()
        # 6 bits reserved (should be 0)
        clamp = (flags & 0b00000010) != 0
        preserve_alpha = (flags & 0b00000001) != 0

        return cls(
            matrix_x=matrix_x,
            matrix_y=matrix_y,
            divisor=divisor,
            bias=bias,
            matrix=matrix,
            default_color=default_color,
            clamp=clamp,
            preserve_alpha=preserve_alpha,
        )
