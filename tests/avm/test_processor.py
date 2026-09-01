"""Port of ArakneSwf's `tests/Avm/ProcessorTest.php`."""

from __future__ import annotations

import re
import zlib
from typing import Any

import pytest

from prespyc.avm.api.script_array import ScriptArray
from prespyc.avm.api.script_object import ScriptObject
from prespyc.avm.processor import Processor
from prespyc.avm.state import State
from prespyc.errors import SwfError
from prespyc.parser.structure.action.action_record import ActionRecord
from prespyc.parser.structure.action.opcode import Opcode
from prespyc.parser.structure.action.type import Type
from prespyc.parser.structure.action.value import Value
from prespyc.parser.structure.tag.do_action import DoActionTag
from prespyc.swf_file import SwfFile
from tests.support import fixture


def _run(swf: SwfFile, processor: Processor, state: State) -> None:
    for _, tag in swf.tags(DoActionTag.TYPE):
        processor.run(tag.actions, state)


def _crc32_modulo(value: str, modulo: int) -> int:
    """The `crc32($v) % $o` body of the PHP fixtures' test function."""
    return zlib.crc32(value.encode()) % modulo


def test_function_call() -> None:
    swf = SwfFile(fixture("func_call.swf"))
    state = State()
    processor = Processor()

    calling_args: list[Any] = []

    def my_function(*args: Any) -> int:
        calling_args[:] = args
        return _crc32_modulo(args[0], args[1])

    state.functions["myFunction"] = my_function

    _run(swf, processor, state)

    assert calling_args == ["foo", 123]
    assert state.variables["ret"] == 23


def test_function_call_disabled() -> None:
    swf = SwfFile(fixture("func_call.swf"))
    state = State()
    processor = Processor(allow_function_call=False)

    calling_args: list[Any] = []

    def my_function(*args: Any) -> int:
        calling_args[:] = args
        return _crc32_modulo(args[0], args[1])

    state.functions["myFunction"] = my_function

    _run(swf, processor, state)

    assert calling_args == []
    assert state.variables["ret"] is None


def test_function_call_invalid_function() -> None:
    swf = SwfFile(fixture("func_call.swf"))
    state = State()
    processor = Processor()

    with pytest.raises(SwfError, match=re.escape("Unknown function: myFunction")):
        _run(swf, processor, state)


def test_undefined_elements() -> None:
    swf = SwfFile(fixture("undefined.swf"))
    processor = Processor()
    state = State()

    _run(swf, processor, state)

    assert len(state.variables) == 7
    assert state.variables["not_exists"] is None
    assert state.variables["get_member"] is None
    assert state.variables["get_member2"] is None
    assert state.variables["get_member3"] is None
    assert state.variables["get_member4"] is None
    assert state.variables["ret"] is None
    assert state.variables["o"] == ScriptObject()


def test_method_call_success() -> None:
    swf = SwfFile(fixture("methods.swf"))
    processor = Processor()
    state = State()

    class Target:
        def __init__(self) -> None:
            self.args: list[Any] | None = None

        def method(self, *args: Any) -> int:
            self.args = list(args)
            return _crc32_modulo(args[0], args[1])

    obj = Target()
    state.variables["myObject"] = obj

    _run(swf, processor, state)

    assert obj.args == ["foo", 123]
    assert state.variables["ret"] == 23


def test_method_call_script_object_success() -> None:
    swf = SwfFile(fixture("methods.swf"))
    processor = Processor()
    state = State()
    obj = ScriptObject()

    def method(*args: Any) -> int:
        obj.args = list(args)
        return _crc32_modulo(args[0], args[1])

    obj.method = method
    state.variables["myObject"] = obj

    _run(swf, processor, state)

    assert obj.args == ["foo", 123]
    assert state.variables["ret"] == 23


def test_method_call_script_object_property_not_callable() -> None:
    swf = SwfFile(fixture("methods.swf"))
    processor = Processor()
    state = State()
    obj = ScriptObject()
    obj.method = False
    state.variables["myObject"] = obj

    _run(swf, processor, state)

    assert state.variables["ret"] is None


def test_method_call_not_object() -> None:
    swf = SwfFile(fixture("methods.swf"))
    processor = Processor()
    state = State()
    state.variables["myObject"] = False

    _run(swf, processor, state)

    assert state.variables["ret"] is None


def test_method_call_disabled() -> None:
    swf = SwfFile(fixture("methods.swf"))
    processor = Processor(allow_function_call=False)
    state = State()

    class Target:
        def __init__(self) -> None:
            self.args: list[Any] | None = None

        def method(self, *args: Any) -> int:
            self.args = list(args)
            return _crc32_modulo(args[0], args[1])

    obj = Target()
    state.variables["myObject"] = obj

    _run(swf, processor, state)

    assert obj.args is None
    assert state.variables["ret"] is None


def test_array() -> None:
    swf = SwfFile(fixture("array.swf"))
    processor = Processor()
    state = State()

    _run(swf, processor, state)

    arr5 = ScriptArray()
    arr5[0] = 1

    assert state.variables == {
        "arr1": ScriptArray(),
        "arr1_length": 0,
        "arr2": ScriptArray(None, None, None, None, None),
        "arr2_length": 5,
        "arr3": ScriptArray(1, 2, 3),
        "arr3_length": 3,
        "arr4": ScriptArray(1, 2, 3, None, None, None, None, None, None, None),
        "arr4_length": 10,
        "arr5": arr5,
        "arr5_length": 1,
        "arr6": ScriptArray(41, 42, 43),
        "arr6_length": 3,
    }


def test_inline_array_get_member() -> None:
    state = State()
    processor = Processor()

    processor.execute(state, ActionRecord(0, Opcode.ACTION_PUSH, 0, [Value(Type.STRING, b"arr")]))
    processor.execute(
        state,
        ActionRecord(
            0,
            Opcode.ACTION_PUSH,
            0,
            [Value(Type.STRING, b"foo"), Value(Type.STRING, b"bar"), Value(Type.INTEGER, 2)],
        ),
    )
    processor.execute(state, ActionRecord(0, Opcode.ACTION_INIT_ARRAY, 0, None))
    processor.execute(state, ActionRecord(0, Opcode.ACTION_SET_VARIABLE, 0, None))  # arr = ['foo', 'bar']
    processor.execute(state, ActionRecord(0, Opcode.ACTION_PUSH, 0, [Value(Type.STRING, b"val")]))
    processor.execute(state, ActionRecord(0, Opcode.ACTION_PUSH, 0, [Value(Type.STRING, b"arr")]))
    processor.execute(state, ActionRecord(0, Opcode.ACTION_GET_VARIABLE, 0, None))
    processor.execute(state, ActionRecord(0, Opcode.ACTION_PUSH, 0, [Value(Type.INTEGER, 1)]))
    processor.execute(state, ActionRecord(0, Opcode.ACTION_GET_MEMBER, 0, None))
    processor.execute(state, ActionRecord(0, Opcode.ACTION_SET_VARIABLE, 0, None))  # val = arr[1]

    assert state.variables["arr"] == ["bar", "foo"]
    assert state.variables["val"] == "foo"


def test_new_object_class_not_found() -> None:
    state = State()
    processor = Processor()

    with pytest.raises(SwfError, match=re.escape("Unknown object type: NotExists")):
        processor.execute(
            state,
            ActionRecord(0, Opcode.ACTION_PUSH, 0, [Value(Type.INTEGER, 0), Value(Type.STRING, b"NotExists")]),
        )
        processor.execute(state, ActionRecord(0, Opcode.ACTION_NEW_OBJECT, 0, None))


def test_opcode_not_supported() -> None:
    state = State()
    processor = Processor()

    # The opcode name is the Python enum member name, as everywhere else in the port.
    message = 'Unknown action: ACTION_PREVIOUS_FRAME {"offset":0,"opcode":5,"length":0,"data":null} Stack: []'

    with pytest.raises(SwfError, match=re.escape(message)):
        processor.execute(state, ActionRecord(0, Opcode.ACTION_PREVIOUS_FRAME, 0, None))


# ------------------------------------------------------------------------ PHP type juggling
#
# No counterpart in ProcessorTest.php: these pin the loose casts the AVM relies on, which the
# fixtures above only graze. The expected values are PHP's, not Python's.


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, ""),
        (True, "1"),
        (False, ""),
        (123, "123"),
        (1.0, "1"),
        (-0.0, "-0"),
        (1234.5678, "1234.5678"),
        (0.1 + 0.2, "0.3"),
        (1e25, "1.0E+25"),
        ("abc", "abc"),
        ([1, 2], "Array"),
    ],
)
def test_to_string(value: Any, expected: str) -> None:
    state = State()
    state.stack.append(value)

    Processor().execute(state, ActionRecord(0, Opcode.ACTION_TO_STRING, 0, None))

    assert state.stack == [expected]


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, 0.0),
        (True, 1.0),
        (False, 0.0),
        (123, 123.0),
        ("1234", 1234.0),
        ("12abc", 12.0),
        ("12.5abc", 12.5),
        ("1e3", 1000.0),
        ("abc", 0.0),
        ("", 0.0),
    ],
)
def test_to_number(value: Any, expected: float) -> None:
    state = State()
    state.stack.append(value)

    Processor().execute(state, ActionRecord(0, Opcode.ACTION_TO_NUMBER, 0, None))

    assert state.stack == [expected]


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, False),
        (0, False),
        (1, True),
        (-0.0, False),
        ("", False),
        ("0", False),
        ("0.0", True),
        ("false", True),
        ([], False),
        ([0], True),
        (ScriptObject(), True),
    ],
)
def test_boolean_function(value: Any, expected: bool) -> None:
    state = State()
    state.stack.extend([value, 1, "Boolean"])

    Processor().execute(state, ActionRecord(0, Opcode.ACTION_CALL_FUNCTION, 0, None))

    assert state.stack == [expected]
