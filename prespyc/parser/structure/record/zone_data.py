"""Font alignment zone data."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ZoneData:
    """A single alignment zone dimension."""

    alignment_coordinate: float
    range: float
