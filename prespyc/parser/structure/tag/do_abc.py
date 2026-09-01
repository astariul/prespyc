"""DoABC tag: an ActionScript 3 bytecode block."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class DoABCTag:
    """An AVM2 (ActionScript 3) bytecode block. `prespyc` does not interpret it."""

    TYPE: ClassVar[int] = 82

    flags: int
    name: bytes
    data: bytes

    @classmethod
    def read(cls, reader: Reader, end: int) -> Self:
        return cls(
            flags=reader.read_ui32(),
            name=reader.read_null_terminated_string(),
            data=reader.read_bytes_to(end),
        )
