"""Clip action record."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from prespyc.parser.structure.action.action_record import ActionRecord
from prespyc.parser.structure.record.clip_event_flags import ClipEventFlags

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class ClipActionRecord:
    """Actions triggered by a set of clip events."""

    flags: ClipEventFlags
    size: int

    key_code: int | None
    """
    The key code, from the `ButtonCondAction` constants.

    None if `ClipEventFlags.KEY_PRESS` is not set.
    """

    actions: list[ActionRecord]

    @classmethod
    def read_collection(cls, reader: Reader, version: int) -> list[Self]:
        """
        Read a clip action record collection.

        The end of the collection is marked by a record with all flags set to 0. `version` is the
        SWF version.
        """
        records = []

        while reader.offset < reader.end:
            flags = ClipEventFlags.read(reader, version)

            if flags.flags == 0:
                break

            size = reader.read_ui32()
            actions_end_offset = reader.offset + size
            key_code = reader.read_ui8() if flags.has(ClipEventFlags.KEY_PRESS) else None
            actions = ActionRecord.read_collection(reader, actions_end_offset)

            records.append(
                cls(
                    flags=flags,
                    size=size,
                    key_code=key_code,
                    actions=actions,
                )
            )

        return records
