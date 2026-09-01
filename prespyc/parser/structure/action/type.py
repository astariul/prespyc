"""Types of the primitive values pushed on the ActionScript stack."""

from __future__ import annotations

from enum import IntEnum


class Type(IntEnum):
    """Type of an ActionScript value, as stored in an `ActionPush` payload."""

    STRING = 0
    """Null-terminated string."""

    FLOAT = 1
    """32 bits float."""

    NULL = 2

    UNDEFINED = 3

    REGISTER = 4
    """Register number. Unsigned 8 bits."""

    BOOLEAN = 5

    DOUBLE = 6
    """64 bits float."""

    INTEGER = 7
    """32 bits signed integer."""

    CONSTANT8 = 8
    """8 bits constant id. Reference to constant pool."""

    CONSTANT16 = 9
    """16 bits constant id. Reference to constant pool."""

    @classmethod
    def try_from(cls, value: int) -> Type | None:
        """Member with this type id, or `None` when the id is not a known type."""
        try:
            return cls(value)
        except ValueError:
            return None
