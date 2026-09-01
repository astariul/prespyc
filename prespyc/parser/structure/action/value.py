"""Primitive ActionScript value, as pushed on the stack by `ActionPush`."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from prespyc.errors import Errors, InvalidDataError, OutOfBoundsError
from prespyc.parser.structure.action.type import Type

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class Value:
    """Stores a primitive ActionScript value with its type."""

    type: Type

    value: int | float | bytes | bool | None
    """The parsed value."""

    @classmethod
    def read_collection(cls, reader: Reader, length: int) -> list[Self]:
        """
        Read a collection of values from the reader.

        Values are read until `length` bytes have been consumed.
        """
        values: list[Self] = []
        byte_pos_end = reader.offset + length

        if byte_pos_end > reader.end:
            if reader.errors & Errors.OUT_OF_BOUNDS:
                raise OutOfBoundsError.read_too_many_bytes(reader.offset, reader.end, length)

            byte_pos_end = reader.end

        while reader.offset < byte_pos_end:
            type_id = reader.read_ui8()
            value_type = Type.try_from(type_id)

            if value_type is None:
                if reader.errors & Errors.INVALID_DATA:
                    raise InvalidDataError(f'Invalid value type "{type_id}" at offset {reader.offset}', reader.offset)

                continue

            match value_type:
                case Type.STRING:
                    value = reader.read_null_terminated_string()
                case Type.FLOAT:
                    value = reader.read_float()
                case Type.NULL:
                    value = None
                case Type.UNDEFINED:
                    value = None
                case Type.REGISTER:
                    value = reader.read_ui8()
                case Type.BOOLEAN:
                    value = reader.read_ui8() == 1
                case Type.DOUBLE:
                    value = reader.read_double()
                case Type.INTEGER:
                    value = reader.read_si32()
                case Type.CONSTANT8:
                    value = reader.read_ui8()
                case Type.CONSTANT16:
                    value = reader.read_ui16()

            values.append(cls(value_type, value))

        return values
