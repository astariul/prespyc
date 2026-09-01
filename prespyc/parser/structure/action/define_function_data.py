"""Payload of the `ActionDefineFunction` action."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class DefineFunctionData:
    """Signature of a function declared by `ActionDefineFunction`."""

    name: bytes

    parameters: list[bytes]

    code_size: int
    """Length in bytes of the action records making up the function body."""

    @classmethod
    def read(cls, reader: Reader) -> Self:
        name = reader.read_null_terminated_string()
        params = []
        num_params = reader.read_ui16()

        for _ in range(num_params):
            params.append(reader.read_null_terminated_string())

        code_size = reader.read_ui16()

        return cls(name, params, code_size)
