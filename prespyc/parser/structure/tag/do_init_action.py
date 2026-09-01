"""DoInitAction tag: the initialisation actions of a sprite."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.action.action_record import ActionRecord

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class DoInitActionTag:
    """Actions executed once, before the sprite is displayed for the first time."""

    TYPE: ClassVar[int] = 59

    sprite_id: int
    actions: list[ActionRecord]

    @classmethod
    def read(cls, reader: Reader, end: int) -> Self:
        return cls(
            sprite_id=reader.read_ui16(),
            actions=ActionRecord.read_collection(reader, end),
        )
