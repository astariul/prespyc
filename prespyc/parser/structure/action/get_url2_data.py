"""Payload of the `ActionGetURL2` action."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class GetURL2Data:
    """Flags of an `ActionGetURL2` action. The URL and target come from the stack."""

    send_vars_method: int

    load_target_flag: bool

    load_variables_flag: bool

    @classmethod
    def read(cls, reader: Reader) -> Self:
        flags = reader.read_ui8()

        send_vars_method = (flags & 0b11000000) >> 6
        # 4 bits reserved, must be 0
        load_target_flag = (flags & 0b00000010) != 0
        load_variables_flag = (flags & 0b00000001) != 0

        return cls(send_vars_method, load_target_flag, load_variables_flag)
