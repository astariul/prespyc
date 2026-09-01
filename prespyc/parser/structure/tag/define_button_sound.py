"""DefineButtonSound tag."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.record.sound_info import SoundInfo

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class DefineButtonSoundTag:
    """
    The sounds played on each of the four button state transitions.

    Slot 0 is over-up-to-idle, 1 is idle-to-over-up, 2 is over-up-to-over-down and 3 is
    over-down-to-over-up. A character id of 0 means no sound for that transition, and the matching
    sound info is then absent.
    """

    TYPE: ClassVar[int] = 17

    button_id: int
    button_sound_char0: int
    button_sound_info0: SoundInfo | None
    button_sound_char1: int
    button_sound_info1: SoundInfo | None
    button_sound_char2: int
    button_sound_info2: SoundInfo | None
    button_sound_char3: int
    button_sound_info3: SoundInfo | None

    @classmethod
    def read(cls, reader: Reader) -> Self:
        button_id = reader.read_ui16()
        char0 = reader.read_ui16()
        info0 = SoundInfo.read(reader) if char0 != 0 else None
        char1 = reader.read_ui16()
        info1 = SoundInfo.read(reader) if char1 != 0 else None
        char2 = reader.read_ui16()
        info2 = SoundInfo.read(reader) if char2 != 0 else None
        char3 = reader.read_ui16()
        info3 = SoundInfo.read(reader) if char3 != 0 else None

        return cls(
            button_id=button_id,
            button_sound_char0=char0,
            button_sound_info0=info0,
            button_sound_char1=char1,
            button_sound_info1=info1,
            button_sound_char2=char2,
            button_sound_info2=info2,
            button_sound_char3=char3,
            button_sound_info3=info3,
        )
