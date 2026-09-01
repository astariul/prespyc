"""A single ActionScript 2 bytecode instruction, with its decoded payload."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self

from prespyc.errors import Errors, InvalidDataError, OutOfBoundsError
from prespyc.parser.structure.action.opcode import Opcode

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class ActionRecord:
    """One instruction of an action block, as consumed by the AVM."""

    offset: int
    """Offset of the action record in the action block, i.e. the address a jump targets."""

    opcode: Opcode

    length: int
    """Length in bytes of the payload. `0` when the action takes no payload."""

    data: Any
    """Decoded payload, whose shape depends on the opcode. `None` when there is none."""

    @classmethod
    def read_collection(cls, reader: Reader, end: int) -> list[Self]:
        """Read action records until the end of the current action block."""
        if reader.offset >= end:
            return []

        if end > reader.end:
            if reader.errors & Errors.OUT_OF_BOUNDS:
                raise OutOfBoundsError.read_after_end(end, reader.end)

            end = reader.end

        actions: list[Self] = []

        chunk = reader.chunk(reader.offset, end)
        reader.skip_to(end)

        while chunk.offset < end:
            offset = chunk.offset
            action_length = 0

            if (action_code := chunk.read_ui8()) == 0:
                actions.append(cls(offset, Opcode.NULL, 0, None))
                continue

            if action_code >= 0x80:
                action_length = chunk.read_ui16()

            opcode = Opcode.try_from(action_code)

            if opcode is None:
                if reader.errors & Errors.INVALID_DATA:
                    raise InvalidDataError(
                        f'Invalid action code "{action_code}" at offset {chunk.offset}', chunk.offset
                    )

                continue

            action_data = opcode.read_data(chunk, action_length) if action_length > 0 else None
            actions.append(cls(offset, opcode, action_length, action_data))

        return actions
