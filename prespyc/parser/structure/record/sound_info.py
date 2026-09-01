"""Sound info record."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Self

from prespyc.parser.structure.record.sound_envelope import SoundEnvelope

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class SoundInfo:
    """Playback parameters of a sound."""

    sync_stop: bool
    sync_no_multiple: bool
    in_point: int | None
    out_point: int | None
    loop_count: int | None
    envelopes: list[SoundEnvelope] = field(default_factory=list)

    @classmethod
    def read(cls, reader: Reader) -> Self:
        flags = reader.read_ui8()
        # 2 bits reserved
        sync_stop = (flags & 0b00100000) != 0
        sync_no_multiple = (flags & 0b00010000) != 0
        has_envelope = (flags & 0b00001000) != 0
        has_loops = (flags & 0b00000100) != 0
        has_out_point = (flags & 0b00000010) != 0
        has_in_point = (flags & 0b00000001) != 0

        return cls(
            sync_stop=sync_stop,
            sync_no_multiple=sync_no_multiple,
            in_point=reader.read_ui32() if has_in_point else None,
            out_point=reader.read_ui32() if has_out_point else None,
            loop_count=reader.read_ui16() if has_loops else None,
            envelopes=cls._read_envelopes(reader) if has_envelope else [],
        )

    @staticmethod
    def _read_envelopes(reader: Reader) -> list[SoundEnvelope]:
        count = reader.read_ui8()
        envelopes = []

        for _ in range(count):
            envelopes.append(
                SoundEnvelope(
                    pos44=reader.read_ui32(),
                    left_level=reader.read_ui16(),
                    right_level=reader.read_ui16(),
                )
            )

        return envelopes
