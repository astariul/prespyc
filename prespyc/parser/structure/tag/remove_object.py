"""RemoveObject tag."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class RemoveObjectTag:
    """Removes a character from the display list, matching both its id and its depth."""

    TYPE: ClassVar[int] = 5

    character_id: int
    depth: int

    @classmethod
    def read(cls, reader: Reader) -> Self:
        return cls(
            character_id=reader.read_ui16(),
            depth=reader.read_ui16(),
        )
