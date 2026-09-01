"""Kerning record."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class KerningRecord:
    """Advance adjustment between a pair of glyphs."""

    code1: int
    code2: int
    adjustment: int
