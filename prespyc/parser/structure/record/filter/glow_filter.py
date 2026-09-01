"""Glow filter record."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.filter.filter import Filter

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class GlowFilter(Filter):
    """Glow filter."""

    FILTER_ID: ClassVar[int] = 2

    glow_color: Color
    blur_x: float
    blur_y: float
    strength: float
    inner_glow: bool
    knockout: bool
    composite_source: bool
    passes: int

    @classmethod
    def _read(cls, reader: Reader) -> Self:
        return cls(
            glow_color=Color.read_rgba(reader),
            blur_x=reader.read_fixed(),
            blur_y=reader.read_fixed(),
            strength=reader.read_fixed8(),
            inner_glow=reader.read_bool(),
            knockout=reader.read_bool(),
            composite_source=reader.read_bool(),
            passes=reader.read_ub(5),
        )
