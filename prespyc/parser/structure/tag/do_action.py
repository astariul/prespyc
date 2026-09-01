"""DoAction tag: an ActionScript 2 block attached to a frame."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.action.action_record import ActionRecord

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class DoActionTag:
    """Actions executed when the frame holding this tag is displayed."""

    TYPE: ClassVar[int] = 12

    actions: list[ActionRecord]

    @classmethod
    def read(cls, reader: Reader, end: int) -> Self:
        """Read a DoAction tag from the reader, until the end offset is reached."""
        return cls(ActionRecord.read_collection(reader, end))
