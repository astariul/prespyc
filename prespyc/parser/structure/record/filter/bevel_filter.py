"""Bevel filter record."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.filter.filter import Filter

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class BevelFilter(Filter):
    """Bevel filter."""

    FILTER_ID: ClassVar[int] = 3

    highlight_color: Color
    """Note: the documentation seems to be incorrect, the highlight color is before the shadow one."""

    shadow_color: Color
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

    @classmethod
    def _read(cls, reader: Reader) -> Self:
        return cls(
            highlight_color=Color.read_rgba(reader),
            shadow_color=Color.read_rgba(reader),
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
