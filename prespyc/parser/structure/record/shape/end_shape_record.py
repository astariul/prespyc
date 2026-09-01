"""End of shape record."""

from __future__ import annotations

from dataclasses import dataclass

from prespyc.parser.structure.record.shape.shape_record import ShapeRecord


@dataclass(frozen=True, slots=True)
class EndShapeRecord(ShapeRecord):
    """Marks the end of a shape record collection."""
