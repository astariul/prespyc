"""Execution of the parsed ActionScript 2 bytecode."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from prespyc._util import num, php_json_encode
from prespyc.avm.api.script_array import ScriptArray
from prespyc.avm.api.script_object import ScriptObject, is_int, to_json_value
from prespyc.avm.state import State
from prespyc.errors import SwfError
from prespyc.parser.structure.action.opcode import Opcode
from prespyc.parser.structure.action.type import Type

if TYPE_CHECKING:
    from prespyc.parser.structure.action.action_record import ActionRecord
    from prespyc.parser.structure.action.value import Value


@dataclass(frozen=True, slots=True)
class Processor:
    """
    Executes the parsed AVM bytecode.

    Stateless: everything the bytecode reads or writes lives in the `State` passed to `run()`, so a
    single processor can drive several independent states.
    """

    allow_function_call: bool = True
    """
    Whether method and function calls are executed.

    When false, every call pushes `None` without running anything. Keep it false for untrusted
    files: the called code is whatever the file asks for.
    """

    def run(self, actions: list[ActionRecord], state: State | None = None) -> State:
        """Run the given actions and return the final state."""
        if state is None:
            state = State()

        for action in actions:
            self.execute(state, action)

        return state

    def execute(self, state: State, action: ActionRecord) -> None:
        """Execute a single instruction."""
        match action.opcode:
            case Opcode.ACTION_CONSTANT_POOL:
                state.constants = [_decode(entry) for entry in action.data]
            case Opcode.ACTION_PUSH:
                state.stack.extend(self.to_python_values(state, *action.data))
            case Opcode.ACTION_SET_VARIABLE:
                self._set_variable(state)
            case Opcode.ACTION_GET_VARIABLE:
                self._get_variable(state)
            case Opcode.ACTION_GET_MEMBER:
                self._get_member(state)
            case Opcode.ACTION_CALL_METHOD:
                self._call_method(state)
            case Opcode.ACTION_POP:
                _pop(state.stack)
            case Opcode.ACTION_NEW_OBJECT:
                self._new_object(state)
            case Opcode.ACTION_INIT_OBJECT:
                self._init_object(state)
            case Opcode.ACTION_INIT_ARRAY:
                self._init_array(state)
            case Opcode.ACTION_SET_MEMBER:
                self._set_member(state)
            case Opcode.ACTION_TO_STRING:
                self._to_string(state)
            case Opcode.ACTION_TO_NUMBER:
                self._to_number(state)
            case Opcode.ACTION_CALL_FUNCTION:
                self._call_function(state)
            case Opcode.NULL:
                pass
            case _:
                raise SwfError(
                    f"Unknown action: {action.opcode.name} {php_json_encode(to_json_value(action))} "
                    f"Stack: {php_json_encode(to_json_value(state.stack))}"
                )

    @staticmethod
    def to_python_values(state: State, *values: Value) -> list[Any]:
        """
        Resolve parsed ActionScript values into host values.

        Only constant pool references need resolving; every other type is already a Python value,
        apart from a string, which the parser hands over as raw bytes.
        """
        parsed: list[Any] = []

        for value in values:
            match value.type:
                case Type.CONSTANT8 | Type.CONSTANT16:
                    parsed.append(state.constants[_php_to_int(value.value)])
                case Type.STRING:
                    parsed.append(_decode(value.value))
                # TODO register
                case _:
                    parsed.append(value.value)

        return parsed

    def _set_variable(self, state: State) -> None:
        value = _pop(state.stack)
        name = _php_to_string(_pop(state.stack))

        state.variables[name] = value

    def _get_variable(self, state: State) -> None:
        index = len(state.stack) - 1
        assert index >= 0

        var_name = state.stack[index]
        assert isinstance(var_name, str) or is_int(var_name)

        # PHP normalises an integer-like array key, so `variables[5]` and `variables['5']` are the
        # same entry there; `State.variables` is keyed by `str`, hence the cast.
        state.stack[index] = state.variables.get(var_name if isinstance(var_name, str) else str(var_name))

    def _get_member(self, state: State) -> None:
        property_name = _pop(state.stack)
        assert isinstance(property_name, str) or is_int(property_name)
        script_object = _pop(state.stack)

        if script_object is None:
            state.stack.append(None)
            return

        if isinstance(script_object, (list, dict)) or (
            isinstance(script_object, ScriptArray) and is_int(property_name)
        ):
            state.stack.append(_offset_get(script_object, property_name))
            return

        if isinstance(script_object, ScriptObject):
            # PHP's `$scriptObject->$propertyName` goes through __get(), which is the same lookup
            # as the item access — and returns null for an unknown property.
            state.stack.append(script_object[property_name])
            return

        state.stack.append(getattr(script_object, _php_to_string(property_name), None))

    def _call_method(self, state: State) -> None:
        method_name = _php_to_string(_pop(state.stack))
        script_object = _pop(state.stack)
        argument_count = _php_to_int(_pop(state.stack))
        args = _splice(state.stack, argument_count) if argument_count > 0 else []

        if not self.allow_function_call:
            state.stack.append(None)
            return

        if not _is_object(script_object):
            state.stack.append(None)
            return

        if not _method_exists(script_object, method_name) and (
            not isinstance(script_object, ScriptObject)
            or not script_object.has_property(method_name)
            or not callable(getattr(script_object, method_name))
        ):
            state.stack.append(None)
            return

        state.stack.append(getattr(script_object, method_name)(*reversed(args)))

    def _new_object(self, state: State) -> None:
        type_name = _php_to_string(_pop(state.stack))
        argument_count = _php_to_int(_pop(state.stack))
        args = list(reversed(_splice(state.stack, argument_count))) if argument_count > 0 else []

        match type_name:
            case "Object":
                state.stack.append(ScriptObject())
            case "Array":
                state.stack.append(ScriptArray(*args))
            case _:
                raise SwfError(f"Unknown object type: {type_name}")

    def _init_object(self, state: State) -> None:
        properties_count = _php_to_int(_pop(state.stack))
        args = _splice(state.stack, properties_count * 2) if properties_count > 0 else []
        properties: dict[Any, Any] = {}

        for i in range(2 * properties_count - 2, -1, -2):
            key = args[i]
            value = args[i + 1]

            assert isinstance(key, str) or is_int(key)
            properties[key] = value

        state.stack.append(ScriptObject(properties))

    def _init_array(self, state: State) -> None:
        size = _php_to_int(_pop(state.stack))
        values = list(reversed(_splice(state.stack, size))) if size > 0 else []

        # TODO use a ScriptArray?
        state.stack.append(values)

    def _set_member(self, state: State) -> None:
        value = _pop(state.stack)
        property_name = _pop(state.stack)
        script_object = _pop(state.stack)

        if script_object is None:
            return

        # Float that is an integer: use it as an int
        if isinstance(property_name, float) and math.isfinite(property_name) and int(property_name) == property_name:
            property_name = int(property_name)

        if not is_int(property_name):
            property_name = _php_to_string(property_name)

        if isinstance(script_object, ScriptObject):
            # Only ScriptArray overrides the item write, and on a plain ScriptObject PHP's `__set`
            # and `offsetSet` are the same call, so this covers both branches of the original.
            script_object[property_name] = value
            return

        setattr(script_object, _php_to_string(property_name), value)

    def _to_string(self, state: State) -> None:
        index = len(state.stack) - 1
        assert index >= 0

        state.stack[index] = _php_to_string(state.stack[index])

    def _to_number(self, state: State) -> None:
        index = len(state.stack) - 1
        assert index >= 0

        state.stack[index] = _php_to_float(state.stack[index])

    def _call_function(self, state: State) -> None:
        function_name = _php_to_string(_pop(state.stack))
        argument_count = _php_to_int(_pop(state.stack))
        args = list(reversed(_splice(state.stack, argument_count))) if argument_count > 0 else []

        match function_name:
            case "Boolean":
                state.stack.append(_php_truthy(args[0]))
            case "String":
                state.stack.append(_php_to_string(args[0]))
            case "Number":
                state.stack.append(_php_to_float(args[0]))
            case _:
                state.stack.append(self._call_custom_function(state, function_name, args))

    def _call_custom_function(self, state: State, function_name: str, args: list[Any]) -> Any:
        if not self.allow_function_call:
            return None

        function = state.functions.get(function_name)

        if function is None:
            raise SwfError(f"Unknown function: {function_name}")

        return function(*args)


def _decode(raw: bytes) -> str:
    """
    Decode a SWF string the AVM handles as text: a variable name, or a constant pool entry.

    The processor never sees the SWF version, so UTF-8 is assumed. That is right from SWF 6 on, and
    older files are Latin-1 — identical for the ASCII identifiers AVM bytecode actually carries.
    """
    return raw.decode("utf-8", errors="replace")


def _pop(stack: list[Any]) -> Any:
    """PHP `array_pop()`: popping an empty stack yields `None` instead of raising."""
    return stack.pop() if stack else None


def _splice(stack: list[Any], count: int) -> list[Any]:
    """PHP `array_splice($stack, -$count)`: pop the last `count` entries, in stack order."""
    removed = stack[-count:]
    del stack[-count:]

    return removed


def _offset_get(container: Any, key: Any) -> Any:
    """Read an entry of a PHP array or of a `ScriptArray`, `None` when it does not exist."""
    if isinstance(container, ScriptArray):
        return container[key]

    if isinstance(container, dict):
        return container.get(key)

    if is_int(key) and 0 <= key < len(container):
        return container[key]

    return None


def _is_object(value: Any) -> bool:
    """PHP `is_object()`: false for `null`, a bool, a number, a string and an array."""
    if value is None:
        return False

    return not isinstance(value, (bool, int, float, str, bytes, list, dict, tuple))


def _method_exists(value: Any, name: str) -> bool:
    """
    PHP `method_exists()`.

    Looks the name up on the *class*, so a callable stored as an instance property does not count —
    which is exactly the distinction the original relies on.
    """
    return callable(getattr(type(value), name, None))


# --------------------------------------------------------------------- PHP type juggling
#
# The AVM leans on PHP's loose casts, which have no Python equivalent, so each one is spelled out
# here. Python's own conversions differ on every line that matters: `str(1.0)` is `'1.0'` where PHP
# writes `'1'`, `int('12abc')` raises where PHP yields `12`, and `bool('0')` is true where PHP says
# false.

_LEADING_NUMBER = re.compile(r"\s*[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?")


def _php_string_to_number(text: str) -> int | float:
    """
    PHP's numeric interpretation of a string: the leading numeric prefix, else `0`.

    So `'12abc'` is `12`, `'  1.5'` is `1.5`, `'1e3'` is `1000.0` and `'abc'` is `0`.
    """
    match = _LEADING_NUMBER.match(text)

    if match is None:
        return 0

    literal = match.group(0).strip()

    if literal in ("", "+", "-"):
        return 0

    if "." in literal or "e" in literal or "E" in literal:
        return float(literal)

    return int(literal)


def _php_to_string(value: Any) -> str:
    """PHP `(string)` cast."""
    if value is None:
        return ""

    if value is True:
        return "1"

    if value is False:
        return ""

    if isinstance(value, str):
        return value

    if isinstance(value, bytes):
        return _decode(value)

    if isinstance(value, int):
        return str(value)

    if isinstance(value, float):
        # PHP formats a float with `precision=14` and drops the trailing `.0`.
        return num(value)

    if isinstance(value, (list, dict)):
        return "Array"

    return str(value)


def _php_to_int(value: Any) -> int:
    """PHP `(int)` cast: truncates toward zero, and reads the leading number of a string."""
    if value is None:
        return 0

    if value is True:
        return 1

    if value is False:
        return 0

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        # PHP 8 casts a non-finite float to 0.
        return int(value) if math.isfinite(value) else 0

    if isinstance(value, bytes):
        value = _decode(value)

    if isinstance(value, str):
        return _php_to_int(_php_string_to_number(value))

    if isinstance(value, (list, dict)):
        return 1 if value else 0

    return 1


def _php_to_float(value: Any) -> float:
    """PHP `(float)` cast."""
    if value is None:
        return 0.0

    if value is True:
        return 1.0

    if value is False:
        return 0.0

    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, bytes):
        value = _decode(value)

    if isinstance(value, str):
        return float(_php_string_to_number(value))

    if isinstance(value, (list, dict)):
        return 1.0 if value else 0.0

    return 1.0


def _php_truthy(value: Any) -> bool:
    """PHP `(bool)` cast: `'0'` is false, `'0.0'` is true, and an object is always true."""
    if value is None or value is False:
        return False

    if value is True:
        return True

    if isinstance(value, int):
        return value != 0

    if isinstance(value, float):
        # NAN is true, like any value that is not zero; -0.0 is false.
        return value != 0.0

    if isinstance(value, str):
        return value not in ("", "0")

    if isinstance(value, bytes):
        return value not in (b"", b"0")

    if isinstance(value, (list, dict)):
        return len(value) > 0

    return True
