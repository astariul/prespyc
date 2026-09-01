"""StartSound2 tag."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.record.sound_info import SoundInfo

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class StartSound2Tag:
    """Starts (or stops) the playback of a sound, designated by its AS3 class name."""

    TYPE: ClassVar[int] = 89

    sound_class_name: bytes
    sound_info: SoundInfo

    @classmethod
    def read(cls, reader: Reader) -> Self:
        return cls(
            sound_class_name=reader.read_null_terminated_string(),
            sound_info=SoundInfo.read(reader),
        )
