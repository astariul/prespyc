"""Clip event flags record."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class ClipEventFlags:
    """
    Bitfield wrapper for clip event flags.

    Flags can be 16 or 32 bits long, depending on the SWF version (16 for <= 5, 32 for >= 6).
    """

    # First byte
    KEY_UP: ClassVar[int] = 0x80
    KEY_DOWN: ClassVar[int] = 0x40
    MOUSE_UP: ClassVar[int] = 0x20
    MOUSE_DOWN: ClassVar[int] = 0x10
    MOUSE_MOVE: ClassVar[int] = 0x08
    UNLOAD: ClassVar[int] = 0x04
    ENTER_FRAME: ClassVar[int] = 0x02
    LOAD: ClassVar[int] = 0x01

    # Second byte
    DRAG_OVER: ClassVar[int] = 0x8000
    ROLL_OUT: ClassVar[int] = 0x4000
    ROLL_OVER: ClassVar[int] = 0x2000
    RELEASE_OUTSIDE: ClassVar[int] = 0x1000
    RELEASE: ClassVar[int] = 0x0800
    PRESS: ClassVar[int] = 0x0400
    INITIALIZE: ClassVar[int] = 0x0200
    DATA: ClassVar[int] = 0x0100

    # Third byte (SWF >= 6)
    CONSTRUCT: ClassVar[int] = 0x040000
    KEY_PRESS: ClassVar[int] = 0x020000
    DRAG_OUT: ClassVar[int] = 0x010000

    flags: int

    def has(self, flag: int) -> bool:
        """Whether `flag`, one of the `ClipEventFlags` constants, is set in the bitfield."""
        return (self.flags & flag) == flag

    @classmethod
    def read(cls, reader: Reader, version: int) -> Self:
        """
        Read the flags.

        `version` is the SWF version: up to 5 the flags are 16 bits long, otherwise 32 bits.
        """
        return cls(reader.read_ui16() if version <= 5 else reader.read_ui32())
