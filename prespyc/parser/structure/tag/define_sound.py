"""DefineSound tag."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class DefineSoundTag:
    """An embedded sound character, with its raw sample data."""

    TYPE: ClassVar[int] = 14

    sound_id: int
    sound_format: int
    sound_rate: int

    is16_bits: bool
    """Named SoundSize on spec. 0 = 8 bits, 1 = 16 bits."""

    stereo: bool
    """Named SoundType on spec. 0 = mono, 1 = stereo."""

    sound_sample_count: int
    sound_data: bytes

    @classmethod
    def read(cls, reader: Reader, end: int) -> Self:
        """Read a DefineSound tag, whose data ends at the `end` byte offset."""
        sound_id = reader.read_ui16()

        flags = reader.read_ui8()
        sound_format = (flags >> 4) & 0x0F  # 4 bits for sound format
        rate = (flags >> 2) & 0x03  # 2 bits for sound rate
        is16_bits = (flags & 0b00000010) != 0
        stereo = (flags & 0b00000001) != 0

        sample_count = reader.read_ui32()
        data = reader.read_bytes_to(end)

        return cls(
            sound_id=sound_id,
            sound_format=sound_format,
            sound_rate=rate,
            is16_bits=is16_bits,
            stereo=stereo,
            sound_sample_count=sample_count,
            sound_data=data,
        )
