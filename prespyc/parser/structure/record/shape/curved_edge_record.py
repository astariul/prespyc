"""Curved edge shape record."""

from __future__ import annotations

from dataclasses import dataclass

from prespyc.parser.structure.record.shape.shape_record import ShapeRecord


@dataclass(frozen=True, slots=True)
class CurvedEdgeRecord(ShapeRecord):
    """A quadratic bezier curve, relative to the current position."""

    control_delta_x: int
    control_delta_y: int
    anchor_delta_x: int
    anchor_delta_y: int
