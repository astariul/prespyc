"""Payload of the `ActionGotoFrame2` action."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class GotoFrame2Data:
    """Flags and scene bias of an `ActionGotoFrame2` action. The frame comes from the stack."""

    scene_bias_flag: bool

    play_flag: bool

    scene_bias: int | None

    @classmethod
    def read(cls, reader: Reader) -> Self:
        flags = reader.read_ui8()

        # 6bits reserved
        scene_bias_flag = (flags & 0b00000010) != 0
        play_flag = (flags & 0b00000001) != 0

        scene_bias = reader.read_ui16() if scene_bias_flag else None

        return cls(scene_bias_flag, play_flag, scene_bias)
