"""Payload of the `ActionDefineFunction2` action."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class DefineFunction2Data:
    """Signature, register allocation and preload flags of an `ActionDefineFunction2` action."""

    name: bytes

    register_count: int

    preload_parent_flag: bool

    preload_root_flag: bool

    suppress_super_flag: bool

    preload_super_flag: bool

    suppress_arguments_flag: bool

    preload_arguments_flag: bool

    suppress_this_flag: bool

    preload_this_flag: bool

    preload_global_flag: bool

    parameters: list[bytes]

    registers: list[int]
    """Register each parameter is preloaded into, in the same order as `parameters`."""

    code_size: int
    """Length in bytes of the action records making up the function body."""

    @classmethod
    def read(cls, reader: Reader) -> Self:
        function_name = reader.read_null_terminated_string()
        num_params = reader.read_ui16()
        register_count = reader.read_ui8()

        flags = reader.read_ui8()
        preload_parent_flag = (flags & 0b10000000) != 0
        preload_root_flag = (flags & 0b01000000) != 0
        suppress_super_flag = (flags & 0b00100000) != 0
        preload_super_flag = (flags & 0b00010000) != 0
        suppress_arguments_flag = (flags & 0b00001000) != 0
        preload_arguments_flag = (flags & 0b00000100) != 0
        suppress_this_flag = (flags & 0b00000010) != 0
        preload_this_flag = (flags & 0b00000001) != 0
        # 7 bits Reserved
        preload_global_flag = (reader.read_ui8() & 0b00000001) != 0

        parameters = []
        registers = []

        for _ in range(num_params):
            registers.append(reader.read_ui8())
            parameters.append(reader.read_null_terminated_string())

        code_size = reader.read_ui16()

        return cls(
            function_name,
            register_count,
            preload_parent_flag,
            preload_root_flag,
            suppress_super_flag,
            preload_super_flag,
            suppress_arguments_flag,
            preload_arguments_flag,
            suppress_this_flag,
            preload_this_flag,
            preload_global_flag,
            parameters,
            registers,
            code_size,
        )
