"""Protect tag: marks the file as not importable into an authoring tool."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class ProtectTag:
    """Asks the authoring tool not to open the file, optionally unless a password is given."""

    TYPE: ClassVar[int] = 24

    password: bytes | None
    """Password is an MD5 hash of the password."""

    @classmethod
    def read(cls, reader: Reader, end: int) -> Self:
        # Password is only present if tag length is not 0
        # It's stored as a null-terminated string
        return cls(password=reader.read_null_terminated_string() if end > reader.offset else None)
