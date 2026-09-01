"""StartSound tag."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.record.sound_info import SoundInfo

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class StartSoundTag:
    """Starts (or stops) the playback of a sound character."""

    TYPE: ClassVar[int] = 15

    sound_id: int
    sound_info: SoundInfo

    @classmethod
    def read(cls, reader: Reader) -> Self:
        return cls(
            sound_id=reader.read_ui16(),
            sound_info=SoundInfo.read(reader),
        )
