"""RemoveObject2 tag."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class RemoveObject2Tag:
    """Removes whatever character is on the display list at the given depth."""

    TYPE: ClassVar[int] = 28

    depth: int

    @classmethod
    def read(cls, reader: Reader) -> Self:
        return cls(reader.read_ui16())
