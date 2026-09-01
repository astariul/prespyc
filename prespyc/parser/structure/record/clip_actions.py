"""Clip actions record."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from prespyc.parser.structure.record.clip_action_record import ClipActionRecord
from prespyc.parser.structure.record.clip_event_flags import ClipEventFlags

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class ClipActions:
    """All the event handlers attached to a sprite instance."""

    all_event_flags: ClipEventFlags
    records: list[ClipActionRecord]

    @classmethod
    def read(cls, reader: Reader, version: int) -> Self:
        """Read a clip actions structure. `version` is the SWF version."""
        reader.skip_bytes(2)  # Reserved UI16, must be 0

        return cls(
            all_event_flags=ClipEventFlags.read(reader, version),
            records=ClipActionRecord.read_collection(reader, version),
        )
