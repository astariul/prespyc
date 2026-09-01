"""Blur filter record."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.record.filter.filter import Filter

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class BlurFilter(Filter):
    """Blur filter."""

    FILTER_ID: ClassVar[int] = 1

    blur_x: float
    blur_y: float
    passes: int

    @classmethod
    def _read(cls, reader: Reader) -> Self:
        return cls(
            blur_x=reader.read_fixed(),
            blur_y=reader.read_fixed(),
            passes=(reader.read_ui8() >> 3) & 31,  # 5 bits for passes, 3 bits reserved
        )
