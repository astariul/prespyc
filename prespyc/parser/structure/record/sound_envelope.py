"""Sound envelope record."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SoundEnvelope:
    """One point of a sound volume envelope."""

    pos44: int
    left_level: int
    right_level: int
