"""Payload of the `ActionGetURL` action."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class GetURLData:
    """Target URL and window of an `ActionGetURL` action."""

    url: bytes

    target: bytes

    @classmethod
    def read(cls, reader: Reader) -> Self:
        return cls(
            reader.read_null_terminated_string(),
            reader.read_null_terminated_string(),
        )
