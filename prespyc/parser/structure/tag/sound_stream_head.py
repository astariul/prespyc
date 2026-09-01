"""SoundStreamHead and SoundStreamHead2 tags."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class SoundStreamHeadTag:
    """Declares the format of the streaming sound of a timeline."""

    TYPE_V1: ClassVar[int] = 18
    TYPE_V2: ClassVar[int] = 45

    version: int
    playback_sound_rate: int
    playback_sound_size: int
    playback_sound_type: int
    stream_sound_compression: int
    stream_sound_rate: int
    stream_sound_size: int
    stream_sound_type: int
    stream_sound_sample_count: int
    latency_seek: int | None

    @classmethod
    def read(cls, reader: Reader, version: int) -> Self:
        """Read a SoundStreamHead or SoundStreamHead2 tag. `version` is either 1 or 2."""
        flags = reader.read_ui8()
        # 4 bits reserved
        playback_sound_rate = (flags >> 2) & 3  # 2 bits for sound rate
        playback16_bits = (flags & 0b00000010) != 0
        playback_stereo = (flags & 0b00000001) != 0

        flags = reader.read_ui8()
        compression = (flags >> 4) & 0x0F  # 4 bits for sound compression
        stream_sound_rate = (flags >> 2) & 0x03  # 2 bits for sound rate
        stream16_bits = (flags & 0b00000010) != 0
        stream_stereo = (flags & 0b00000001) != 0

        stream_sound_sample_count = reader.read_ui16()
        latency_seek = reader.read_si16() if compression == 2 else None

        return cls(
            version=version,
            playback_sound_rate=playback_sound_rate,
            playback_sound_size=1 if playback16_bits else 0,
            playback_sound_type=1 if playback_stereo else 0,
            stream_sound_compression=compression,
            stream_sound_rate=stream_sound_rate,
            stream_sound_size=1 if stream16_bits else 0,
            stream_sound_type=1 if stream_stereo else 0,
            stream_sound_sample_count=stream_sound_sample_count,
            latency_seek=latency_seek,
        )
