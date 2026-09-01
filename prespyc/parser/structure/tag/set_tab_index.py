"""SetTabIndex tag: the tab order of a displayed object."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class SetTabIndexTag:
    """Tab order of the object at the given depth."""

    TYPE: ClassVar[int] = 66

    depth: int
    tab_index: int

    @classmethod
    def read(cls, reader: Reader) -> Self:
        return cls(
            depth=reader.read_ui16(),
            tab_index=reader.read_ui16(),
        )
