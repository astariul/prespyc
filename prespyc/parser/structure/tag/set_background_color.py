"""SetBackgroundColor tag: the stage background colour."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.record.color import Color

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class SetBackgroundColorTag:
    """Background colour of the stage. Has no alpha channel."""

    TYPE: ClassVar[int] = 9

    color: Color

    @classmethod
    def read(cls, reader: Reader) -> Self:
        return cls(Color.read_rgb(reader))
