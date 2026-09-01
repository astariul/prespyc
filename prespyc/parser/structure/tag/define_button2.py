"""DefineButton2 tag."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.record.button_cond_action import ButtonCondAction
from prespyc.parser.structure.record.button_record import ButtonRecord

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class DefineButton2Tag:
    """A button character, with per-transition actions and a menu tracking flag."""

    TYPE: ClassVar[int] = 34

    button_id: int
    track_as_menu: bool
    action_offset: int
    characters: list[ButtonRecord]
    actions: list[ButtonCondAction]

    @classmethod
    def read(cls, reader: Reader, end: int) -> Self:
        """Read a DefineButton2 tag, whose data ends at the `end` byte offset."""
        button_id = reader.read_ui16()
        reader.skip_bits(7)  # Reserved, must be 0
        track_as_menu = reader.read_bool()
        action_offset = reader.read_ui16()
        characters = ButtonRecord.read_collection(reader, 2)
        actions = ButtonCondAction.read_collection(reader, end) if action_offset != 0 else []

        return cls(
            button_id=button_id,
            track_as_menu=track_as_menu,
            action_offset=action_offset,
            characters=characters,
            actions=actions,
        )
