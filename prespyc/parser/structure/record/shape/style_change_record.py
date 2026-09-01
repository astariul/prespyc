"""Style change shape record."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from prespyc.parser.structure.record.shape.shape_record import ShapeRecord

if TYPE_CHECKING:
    from prespyc.parser.structure.record.shape.fill_style import FillStyle
    from prespyc.parser.structure.record.shape.line_style import LineStyle


@dataclass(frozen=True, slots=True)
class StyleChangeRecord(ShapeRecord):
    """A change of the current drawing styles, and optionally a move of the current position."""

    state_new_styles: bool
    state_line_style: bool
    state_fill_style0: bool
    state_fill_style1: bool
    state_move_to: bool
    move_delta_x: int
    move_delta_y: int
    fill_style0: int
    fill_style1: int
    line_style: int
    fill_styles: list[FillStyle]
    line_styles: list[LineStyle]

    @property
    def reset(self) -> bool:
        """
        Whether a full draw context reset is requested.
        If true, following drawing should be performed like a new shape.
        """
        return (
            self.state_new_styles
            and self.state_line_style
            and self.state_fill_style0
            and self.state_fill_style1
            and self.state_move_to
        )
