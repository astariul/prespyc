"""Reflex tag: the rfxswf generator marker."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class ReflexTag:
    """
    This tag mark the swf as created by rfxswf.
    It can be ignored.

    Note: this tag is not documented in the official SWF documentation.
    """

    TYPE: ClassVar[int] = 777

    name: bytes

    @classmethod
    def read(cls, reader: Reader, end: int) -> Self:
        return cls(reader.read_bytes_to(end))
