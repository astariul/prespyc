"""DefineButton tag."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.action.action_record import ActionRecord
from prespyc.parser.structure.record.button_record import ButtonRecord

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class DefineButtonTag:
    """A button character: its states and the actions triggered when it is clicked."""

    TYPE: ClassVar[int] = 7

    button_id: int
    characters: list[ButtonRecord]
    actions: list[ActionRecord]

    @classmethod
    def read(cls, reader: Reader, end: int) -> Self:
        """Read a DefineButton tag, whose data ends at the `end` byte offset."""
        return cls(
            button_id=reader.read_ui16(),
            characters=ButtonRecord.read_collection(reader, 1),
            actions=ActionRecord.read_collection(reader, end),
        )
