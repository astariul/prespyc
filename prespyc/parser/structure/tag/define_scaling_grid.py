"""DefineScalingGrid tag: the 9-slice scaling grid of a character."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.record.rectangle import Rectangle

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class DefineScalingGridTag:
    """The centre rectangle of the 9-slice scaling grid applied to a character."""

    TYPE: ClassVar[int] = 78

    character_id: int
    splitter: Rectangle

    @classmethod
    def read(cls, reader: Reader) -> Self:
        return cls(
            character_id=reader.read_ui16(),
            splitter=Rectangle.read(reader),
        )
