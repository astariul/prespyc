"""What an action block does, read off its bytecode without running it."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING, Any

from prespyc.parser.structure.action.opcode import Opcode
from prespyc.parser.structure.action.type import Type

if TYPE_CHECKING:
    from collections.abc import Sequence

    from prespyc.parser.structure.action.action_record import ActionRecord


class Property(IntEnum):
    """A movie clip property, by the index `ActionGetProperty` and `ActionSetProperty` take."""

    X = 0
    Y = 1
    XSCALE = 2
    YSCALE = 3
    CURRENTFRAME = 4
    TOTALFRAMES = 5
    ALPHA = 6
    VISIBLE = 7
    WIDTH = 8
    HEIGHT = 9
    ROTATION = 10
    TARGET = 11
    FRAMESLOADED = 12
    NAME = 13
    DROPTARGET = 14
    URL = 15
    HIGHQUALITY = 16
    FOCUSRECT = 17
    SOUNDBUFTIME = 18
    QUALITY = 19
    XMOUSE = 20
    YMOUSE = 21


_PROPERTIES_BY_NAME = {"_" + property.name.lower(): property for property in Property}
"""Properties by their ActionScript name, `_x`, `_xscale`... Property names are case-insensitive."""


class Script:
    """
    An action block — a frame script or a clip event handler — and what it does.

    The bytecode is read, not run. The stack is followed as far as constants go, so a string is
    known whether it is pushed inline or through the constant pool, and so are the names of the calls
    and of the properties, as long as the script spells them out.
    """

    __slots__ = ("_reading", "actions")

    def __init__(self, actions: Sequence[ActionRecord]) -> None:
        self.actions = actions
        self._reading: _Reading | None = None

    def has(self, *opcodes: Opcode) -> bool:
        """Whether the block runs any of `opcodes`."""
        return any(action.opcode in opcodes for action in self.actions)

    @property
    def strings(self) -> frozenset[str]:
        """Every string the block pushes."""
        return self._read().strings

    @property
    def calls(self) -> frozenset[str]:
        """Names of the functions and methods the block calls."""
        return self._read().calls

    @property
    def properties_read(self) -> frozenset[Property]:
        """Clip properties the block reads, by `getProperty()` or by name (`_x`, `this._alpha`)."""
        return self._read().properties_read

    @property
    def properties_written(self) -> frozenset[Property]:
        """Clip properties the block sets, by `setProperty()` or by name (`_x = 3`, `this._alpha = 50`)."""
        return self._read().properties_written

    @property
    def stops(self) -> bool:
        """Whether the block runs `stop()`."""
        return self.has(Opcode.ACTION_STOP)

    @property
    def goto_and_stop(self) -> bool:
        """
        Whether the block runs `gotoAndStop()`: to a frame number or a label, computed or not, or as
        a method call.

        A frame number or a label alone means `gotoAndStop()`; followed by `play()`, `gotoAndPlay()`.
        """
        actions = [action for action in self.actions if action.opcode is not Opcode.NULL]

        for index, action in enumerate(actions):
            if action.opcode in (Opcode.ACTION_GOTO_FRAME, Opcode.ACTION_GO_TO_LABEL):
                if index + 1 == len(actions) or actions[index + 1].opcode is not Opcode.ACTION_PLAY:
                    return True
            elif action.opcode is Opcode.ACTION_GOTO_FRAME2 and not action.data.play_flag:
                return True

        return "gotoAndStop" in self.calls

    @property
    def halts(self) -> bool:
        """Whether the block stops the clip, by `stop()` or `gotoAndStop()`."""
        return self.stops or self.goto_and_stop

    @property
    def uses_random(self) -> bool:
        """Whether the block rolls a random number, by `random()` or `Math.random()`."""
        return self.has(Opcode.ACTION_RANDOM_NUMBER) or "random" in self.calls

    def _read(self) -> _Reading:
        if self._reading is None:
            self._reading = _read(self.actions)

        return self._reading


_UNKNOWN = object()
"""A stack value the script computes."""

_EFFECTS: dict[Opcode, tuple[int, int]] = {
    opcode: (pops, pushes)
    for (pops, pushes), opcodes in {
        (0, 0): (
            Opcode.NULL,
            Opcode.ACTION_GOTO_FRAME,
            Opcode.ACTION_GET_URL,
            Opcode.ACTION_NEXT_FRAME,
            Opcode.ACTION_PREVIOUS_FRAME,
            Opcode.ACTION_PLAY,
            Opcode.ACTION_STOP,
            Opcode.ACTION_TOGGLE_QUALITY,
            Opcode.ACTION_STOP_SOUNDS,
            Opcode.ACTION_WAIT_FOR_FRAME,
            Opcode.ACTION_SET_TARGET,
            Opcode.ACTION_GO_TO_LABEL,
            Opcode.ACTION_JUMP,
            Opcode.ACTION_END_DRAG,
            Opcode.ACTION_CONSTANT_POOL,
            Opcode.ACTION_STORE_REGISTER,
            Opcode.ACTION_TRY,
        ),
        (0, 1): (Opcode.ACTION_GET_TIME,),
        (1, 0): (
            Opcode.ACTION_POP,
            Opcode.ACTION_IF,
            Opcode.ACTION_CALL,
            Opcode.ACTION_GOTO_FRAME2,
            Opcode.ACTION_SET_TARGET2,
            Opcode.ACTION_REMOTE_SPRITE,
            Opcode.ACTION_WAIT_FOR_FRAME2,
            Opcode.ACTION_TRACE,
            Opcode.ACTION_DEFINE_LOCAL2,
            Opcode.ACTION_WITH,
            Opcode.ACTION_RETURN,
            Opcode.ACTION_THROW,
        ),
        (1, 1): (
            Opcode.ACTION_NOT,
            Opcode.ACTION_STRING_LENGTH,
            Opcode.ACTION_MB_STRING_LENGTH,
            Opcode.ACTION_TO_INTEGER,
            Opcode.ACTION_CHAR_TO_ASCII,
            Opcode.ACTION_ASCII_TO_CHAR,
            Opcode.ACTION_MB_CHAR_TO_ASCII,
            Opcode.ACTION_MB_ASCII_TO_CHAR,
            Opcode.ACTION_RANDOM_NUMBER,
            Opcode.ACTION_DELETE2,
            Opcode.ACTION_TARGET_PATH,
            Opcode.ACTION_TO_NUMBER,
            Opcode.ACTION_TO_STRING,
            Opcode.ACTION_TYPE_OF,
            Opcode.ACTION_DECREMENT,
            Opcode.ACTION_INCREMENT,
        ),
        (2, 0): (
            Opcode.ACTION_GET_URL2,
            Opcode.ACTION_DEFINE_LOCAL,
            Opcode.ACTION_EXTENDS,
        ),
        (2, 1): (
            Opcode.ACTION_ADD,
            Opcode.ACTION_SUBTRACT,
            Opcode.ACTION_MULTIPLY,
            Opcode.ACTION_DIVIDE,
            Opcode.ACTION_EQUALS,
            Opcode.ACTION_LESS,
            Opcode.ACTION_AND,
            Opcode.ACTION_OR,
            Opcode.ACTION_STRING_EQUALS,
            Opcode.ACTION_STRING_ADD,
            Opcode.ACTION_STRING_LESS,
            Opcode.ACTION_DELETE,
            Opcode.ACTION_EQUALS2,
            Opcode.ACTION_ADD2,
            Opcode.ACTION_LESS2,
            Opcode.ACTION_MODULE,
            Opcode.ACTION_BIT_AND,
            Opcode.ACTION_BIT_LSHIFT,
            Opcode.ACTION_BIT_OR,
            Opcode.ACTION_BIT_RSHIFT,
            Opcode.ACTION_BIT_URSHIFT,
            Opcode.ACTION_BIT_XOR,
            Opcode.ACTION_INSTANCE_OF,
            Opcode.ACTION_STRICT_EQUALS,
            Opcode.ACTION_GREATER,
            Opcode.ACTION_STRING_GREATER,
            Opcode.ACTION_CAST_OP,
        ),
        (3, 0): (Opcode.ACTION_CLONE_SPRITE,),
        (3, 1): (Opcode.ACTION_STRING_EXTRACT, Opcode.ACTION_MB_STRING_EXTRACT),
    }.items()
    for opcode in opcodes
}
"""Values an opcode pops and pushes, for the opcodes whose effect does not depend on the stack."""


@dataclass(frozen=True, slots=True)
class _Reading:
    """What a pass over the bytecode finds."""

    strings: frozenset[str]
    calls: frozenset[str]
    properties_read: frozenset[Property]
    properties_written: frozenset[Property]


class _Stack(list):
    """The script stack, as far as constants go: anything computed is `_UNKNOWN`."""

    def pop_value(self) -> Any:
        """The top of the stack, unknown when the script popped more than it pushed."""
        return self.pop() if self else _UNKNOWN

    def pop_arguments(self, per_argument: int = 1) -> None:
        """Pop an argument count, then that many arguments."""
        count = self.pop_value()

        if not isinstance(count, (int, float)) or isinstance(count, bool):
            self.clear()
            return

        for _ in range(int(count) * per_argument):
            self.pop_value()


def _read(actions: Sequence[ActionRecord]) -> _Reading:
    strings: set[str] = set()
    calls: set[str] = set()
    read: set[Property] = set()
    written: set[Property] = set()

    pool: list[str] = []
    stack = _Stack()
    # A function body runs on a stack of its own: the outer stack waits here, with the offset the
    # body ends at.
    outer: list[tuple[int, _Stack]] = []

    for action in actions:
        while outer and action.offset >= outer[-1][0]:
            stack = outer.pop()[1]

        match action.opcode:
            case Opcode.ACTION_CONSTANT_POOL:
                pool = [_decode(entry) for entry in action.data]
            case Opcode.ACTION_PUSH:
                for value in action.data:
                    resolved = _resolve(value, pool)
                    stack.append(resolved)

                    if isinstance(resolved, str):
                        strings.add(resolved)
            case Opcode.ACTION_PUSH_DUPLICATE:
                top = stack.pop_value()
                stack += [top, top]
            case Opcode.ACTION_STACK_SWAP:
                top = stack.pop_value()
                below = stack.pop_value()
                stack += [top, below]
            case Opcode.ACTION_GET_VARIABLE:
                _add_property(read, stack.pop_value())
                stack.append(_UNKNOWN)
            case Opcode.ACTION_SET_VARIABLE:
                stack.pop_value()
                _add_property(written, stack.pop_value())
            case Opcode.ACTION_GET_MEMBER:
                _add_property(read, stack.pop_value())
                stack.pop_value()
                stack.append(_UNKNOWN)
            case Opcode.ACTION_SET_MEMBER:
                stack.pop_value()
                _add_property(written, stack.pop_value())
                stack.pop_value()
            case Opcode.ACTION_GET_PROPERTY:
                _add_property_index(read, stack.pop_value())
                stack.pop_value()
                stack.append(_UNKNOWN)
            case Opcode.ACTION_SET_PROPERTY:
                stack.pop_value()
                _add_property_index(written, stack.pop_value())
                stack.pop_value()
            case Opcode.ACTION_CALL_FUNCTION | Opcode.ACTION_NEW_OBJECT:
                name = stack.pop_value()
                stack.pop_arguments()
                stack.append(_UNKNOWN)

                if action.opcode is Opcode.ACTION_CALL_FUNCTION and isinstance(name, str):
                    calls.add(name)
            case Opcode.ACTION_CALL_METHOD | Opcode.ACTION_NEW_METHOD:
                name = stack.pop_value()
                stack.pop_value()
                stack.pop_arguments()
                stack.append(_UNKNOWN)

                if action.opcode is Opcode.ACTION_CALL_METHOD and isinstance(name, str):
                    calls.add(name)
            case Opcode.ACTION_INIT_ARRAY:
                stack.pop_arguments()
                stack.append(_UNKNOWN)
            case Opcode.ACTION_INIT_OBJECT:
                stack.pop_arguments(per_argument=2)
                stack.append(_UNKNOWN)
            case Opcode.ACTION_IMPLEMENTS_OP:
                stack.pop_value()
                stack.pop_arguments()
            case Opcode.ACTION_DEFINE_FUNCTION | Opcode.ACTION_DEFINE_FUNCTION2:
                # A function without a name is an expression: its value is pushed.
                if not action.data.name:
                    stack.append(_UNKNOWN)

                # The body follows the header: opcode (1 byte), length (2 bytes), payload.
                outer.append((action.offset + 3 + action.length + action.data.code_size, stack))
                stack = _Stack()
            case _ if action.opcode in _EFFECTS:
                pops, pushes = _EFFECTS[action.opcode]

                for _ in range(pops):
                    stack.pop_value()

                stack += [_UNKNOWN] * pushes
            case _:
                # Enumerations and drags leave a stack whose size the bytecode does not tell.
                stack.clear()

    return _Reading(frozenset(strings), frozenset(calls), frozenset(read), frozenset(written))


def _resolve(value: Any, pool: list[str]) -> Any:
    """The value an `ActionPush` entry puts on the stack."""
    match value.type:
        case Type.STRING:
            return _decode(value.value)
        case Type.CONSTANT8 | Type.CONSTANT16:
            return pool[value.value] if value.value < len(pool) else _UNKNOWN
        case Type.REGISTER:
            return _UNKNOWN
        case _:
            return value.value


def _add_property(properties: set[Property], name: Any) -> None:
    if isinstance(name, str) and (property := _PROPERTIES_BY_NAME.get(name.lower())) is not None:
        properties.add(property)


def _add_property_index(properties: set[Property], index: Any) -> None:
    if isinstance(index, (int, float)) and not isinstance(index, bool) and int(index) in Property._value2member_map_:
        properties.add(Property(int(index)))


def _decode(raw: bytes) -> str:
    """Bytecode strings are identifiers: UTF-8 and Latin-1 agree on them."""
    return raw.decode("utf-8", errors="replace")
