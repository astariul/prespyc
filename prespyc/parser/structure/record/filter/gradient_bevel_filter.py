"""Gradient bevel filter record."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.filter.filter import Filter

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class GradientBevelFilter(Filter):
    """Gradient bevel filter."""

    FILTER_ID: ClassVar[int] = 7

    num_colors: int

    gradient_colors: list[Color]
    """Size is equal to `num_colors`."""

    gradient_ratio: list[int]
    """Size is equal to `num_colors`."""

    blur_x: float
    blur_y: float
    angle: float
    distance: float
    strength: float
    inner_shadow: bool
    knockout: bool
    composite_source: bool
    on_top: bool
    passes: int

    def __post_init__(self) -> None:
        assert len(self.gradient_colors) == self.num_colors
        assert len(self.gradient_ratio) == self.num_colors

    @classmethod
    def _read(cls, reader: Reader) -> Self:
        num_colors = reader.read_ui8()
        gradient_colors = []
        gradient_ratio = []

        for _ in range(num_colors):
            gradient_colors.append(Color.read_rgba(reader))

        for _ in range(num_colors):
            gradient_ratio.append(reader.read_ui8())

        return cls(
            num_colors=num_colors,
            gradient_colors=gradient_colors,
            gradient_ratio=gradient_ratio,
            blur_x=reader.read_fixed(),
            blur_y=reader.read_fixed(),
            angle=reader.read_fixed(),
            distance=reader.read_fixed(),
            strength=reader.read_fixed8(),
            inner_shadow=reader.read_bool(),
            knockout=reader.read_bool(),
            composite_source=reader.read_bool(),
            on_top=reader.read_bool(),
            passes=reader.read_ub(4),
        )
