"""Straight edge shape record."""

from __future__ import annotations

from dataclasses import dataclass

from prespyc.parser.structure.record.shape.shape_record import ShapeRecord


@dataclass(frozen=True, slots=True)
class StraightEdgeRecord(ShapeRecord):
    """A straight line, relative to the current position."""

    general_line_flag: bool
    vertical_line_flag: bool
    delta_x: int
    delta_y: int
