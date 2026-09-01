"""Button condition action record."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.errors import Errors, InvalidDataError
from prespyc.parser.structure.action.action_record import ActionRecord

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class ButtonCondAction:
    """Actions triggered by a button state transition or a key press."""

    KEY_LEFT_ARROW: ClassVar[int] = 1
    KEY_RIGHT_ARROW: ClassVar[int] = 2
    KEY_HOME: ClassVar[int] = 3
    KEY_END: ClassVar[int] = 4
    KEY_INSERT: ClassVar[int] = 5
    KEY_DELETE: ClassVar[int] = 6
    KEY_BACKSPACE: ClassVar[int] = 8
    KEY_ENTER: ClassVar[int] = 13
    KEY_UP_ARROW: ClassVar[int] = 14
    KEY_DOWN_ARROW: ClassVar[int] = 15
    KEY_PAGE_UP: ClassVar[int] = 16
    KEY_PAGE_DOWN: ClassVar[int] = 17
    KEY_TAB: ClassVar[int] = 18
    KEY_ESCAPE: ClassVar[int] = 19

    size: int
    idle_to_over_down: bool
    out_down_to_idle: bool
    out_down_to_over_down: bool
    over_down_to_out_down: bool
    over_down_to_over_up: bool
    over_up_to_over_down: bool
    over_up_to_idle: bool
    idle_to_over_up: bool

    key_press: int
    """
    The key code to trigger the action.

    For swf 4 and earlier, this value is always 0. For later versions, the keycode can be one of the
    KEY_* constants, or the ASCII code between 32 and 126.
    """

    over_down_to_idle: bool
    actions: list[ActionRecord] = field(default_factory=list)

    @classmethod
    def read_collection(cls, reader: Reader, end: int) -> list[Self]:
        """Parse a button cond action collection from the reader until the `end` byte offset."""
        actions = []

        while True:
            start = reader.offset
            size = reader.read_ui16()

            # The size must be at least 4 bytes (2 for size, 2 for flags).
            if size != 0 and size < 4:
                if reader.errors & Errors.INVALID_DATA:
                    raise InvalidDataError(f"Invalid ButtonCondAction size: {size}", start)

                # Ignore the record and skip to the end
                reader.skip_to(end)
                break

            flags = reader.read_ui8()
            idle_to_over_down = (flags & 0b10000000) != 0
            out_down_to_idle = (flags & 0b01000000) != 0
            out_down_to_over_down = (flags & 0b00100000) != 0
            over_down_to_out_down = (flags & 0b00010000) != 0
            over_down_to_over_up = (flags & 0b00001000) != 0
            over_up_to_over_down = (flags & 0b00000100) != 0
            over_up_to_idle = (flags & 0b00000010) != 0
            idle_to_over_up = (flags & 0b00000001) != 0

            flags = reader.read_ui8()
            key_press = (flags >> 1) & 0b01111111  # 7 bits
            over_down_to_idle = (flags & 0b00000001) != 0

            end_of_record = end if size == 0 else start + size
            action_records = ActionRecord.read_collection(reader, end_of_record)

            actions.append(
                cls(
                    size=size,
                    idle_to_over_down=idle_to_over_down,
                    out_down_to_idle=out_down_to_idle,
                    out_down_to_over_down=out_down_to_over_down,
                    over_down_to_out_down=over_down_to_out_down,
                    over_down_to_over_up=over_down_to_over_up,
                    over_up_to_over_down=over_up_to_over_down,
                    over_up_to_idle=over_up_to_idle,
                    idle_to_over_up=idle_to_over_up,
                    key_press=key_press,
                    over_down_to_idle=over_down_to_idle,
                    actions=action_records,
                )
            )

            if size == 0 or reader.offset >= end:
                break

        return actions
