"""Morph gradient record."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from prespyc.parser.structure.record.color import Color


@dataclass(frozen=True, slots=True)
class MorphGradientRecord:
    """A control point of a morph gradient: a ratio and a color for the start and the end shape."""

    start_ratio: int
    start_color: Color
    end_ratio: int
    end_color: Color
