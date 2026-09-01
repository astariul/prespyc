"""EnableDebugger and EnableDebugger2 tags: the debugging password of the file."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class EnableDebuggerTag:
    """Allows the file to be debugged, with the given password."""

    TYPE_V1: ClassVar[int] = 58
    TYPE_V2: ClassVar[int] = 64

    version: int
    """The version of the EnableDebugger tag: either 1 or 2, depending on the tag type."""

    password: bytes

    @classmethod
    def read(cls, reader: Reader, version: int) -> Self:
        if version == 2:
            reader.skip_bytes(2)  # Reserved, must be 0

        return cls(
            version=version,
            password=reader.read_null_terminated_string(),
        )
