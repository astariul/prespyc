"""Port of ArakneSwf's `tests/Parser/Structure/Action/OpcodeTest.php`."""

from __future__ import annotations

import re

import pytest

from prespyc.errors import Errors, InvalidDataError, OutOfBoundsError
from prespyc.parser.reader import Reader
from prespyc.parser.structure.action.define_function2_data import DefineFunction2Data
from prespyc.parser.structure.action.define_function_data import DefineFunctionData
from prespyc.parser.structure.action.get_url2_data import GetURL2Data
from prespyc.parser.structure.action.get_url_data import GetURLData
from prespyc.parser.structure.action.goto_frame2_data import GotoFrame2Data
from prespyc.parser.structure.action.opcode import Opcode
from prespyc.parser.structure.action.type import Type
from prespyc.parser.structure.action.value import Value
from prespyc.parser.structure.action.wait_for_frame_data import WaitForFrameData
from tests.support import fixture, fixture_reader


def test_read_data_go_to_frame():
    reader = Reader(b"\x01\x02")
    assert Opcode.ACTION_GOTO_FRAME.read_data(reader, 2) == 513


def test_read_data_get_url():
    reader = Reader(b"http://example.com\0target\0")
    assert Opcode.ACTION_GET_URL.read_data(reader, 2) == GetURLData(b"http://example.com", b"target")


def test_read_data_store_register():
    reader = Reader(b"\x42")
    assert Opcode.ACTION_STORE_REGISTER.read_data(reader, 1) == 66


def test_read_data_constant_pool():
    reader = Reader(b"\x03\x00foo\0bar\0baz\0")
    assert Opcode.ACTION_CONSTANT_POOL.read_data(reader, 14) == [b"foo", b"bar", b"baz"]


def test_read_data_wait_for_frame():
    reader = Reader(b"\x01\x02\x03")
    assert Opcode.ACTION_WAIT_FOR_FRAME.read_data(reader, 3) == WaitForFrameData(513, 3)


def test_read_data_set_target():
    reader = Reader(b"target\0")
    assert Opcode.ACTION_SET_TARGET.read_data(reader, 7) == b"target"


def test_read_data_go_to_label():
    reader = Reader(b"label\0")
    assert Opcode.ACTION_GO_TO_LABEL.read_data(reader, 6) == b"label"


def test_read_data_wait_for_frame2():
    reader = Reader(b"\x03")
    assert Opcode.ACTION_WAIT_FOR_FRAME2.read_data(reader, 1) == 3


def test_read_data_define_function2():
    reader = fixture_reader(fixture("sunAndShadow.swf"), 1150)

    data = Opcode.ACTION_DEFINE_FUNCTION2.read_data(reader, 24)

    assert isinstance(data, DefineFunction2Data)
    assert data.name == b""  # Method has no name, it's a class member
    assert data.parameters == [b"coord1", b"coord2"]
    assert data.registers == [6, 5]
    assert data.register_count == 7
    assert data.preload_parent_flag is False
    assert data.preload_root_flag is False
    assert data.suppress_super_flag is True
    assert data.preload_super_flag is False
    assert data.suppress_arguments_flag is True
    assert data.preload_arguments_flag is False
    assert data.suppress_this_flag is True
    assert data.preload_this_flag is False
    assert data.preload_global_flag is False


def test_read_data_with():
    reader = Reader(b"\x03\x00foo")
    assert Opcode.ACTION_WITH.read_data(reader, 5) == b"foo"


def test_read_data_action_push():
    reader = fixture_reader(fixture("simple.swf"), 101)

    assert Opcode.ACTION_PUSH.read_data(reader, 7) == [
        Value(Type.CONSTANT8, 0),
        Value(Type.INTEGER, 123),
    ]


def test_read_data_action_push_invalid_type():
    reader = Reader(b"\x42")

    with pytest.raises(InvalidDataError, match=re.escape('Invalid value type "66" at offset 1')):
        Opcode.ACTION_PUSH.read_data(reader, 1)


def test_read_data_action_push_invalid_type_ignore():
    reader = Reader(b"\x42", errors=Errors.NONE)
    assert Opcode.ACTION_PUSH.read_data(reader, 1) == []


def test_read_data_action_push_end_out_of_bound():
    reader = Reader(b"\x42")

    with pytest.raises(OutOfBoundsError, match=re.escape("Cannot read 10 bytes from offset 0, end is at 1")):
        Opcode.ACTION_PUSH.read_data(reader, 10)


def test_read_data_action_push_end_out_of_bound_ignore():
    reader = fixture_reader(fixture("simple.swf"), 101, errors=Errors.NONE)
    reader = reader.chunk(101, 108)

    assert Opcode.ACTION_PUSH.read_data(reader, 10) == [
        Value(Type.CONSTANT8, 0),
        Value(Type.INTEGER, 123),
    ]


def test_read_data_action_jump():
    reader = Reader(b"\x02\x00")
    assert Opcode.ACTION_JUMP.read_data(reader, 2) == 2


def test_read_data_action_if():
    reader = Reader(b"\x02\x00")
    assert Opcode.ACTION_IF.read_data(reader, 2) == 2


def test_read_data_get_url2():
    reader = Reader(b"\x81")
    assert Opcode.ACTION_GET_URL2.read_data(reader, 1) == GetURL2Data(
        send_vars_method=2,
        load_target_flag=False,
        load_variables_flag=True,
    )


def test_read_data_define_function():
    reader = fixture_reader(fixture("function.swf"), 82)

    data = Opcode.ACTION_DEFINE_FUNCTION.read_data(reader, 25)

    assert isinstance(data, DefineFunctionData)
    assert data.name == b"myFunction"
    assert data.parameters == [b"arg1", b"arg2"]
    assert data.code_size == 137


def test_read_data_goto_frame2():
    reader = Reader(b"\x02\x42\x00")
    assert Opcode.ACTION_GOTO_FRAME2.read_data(reader, 3) == GotoFrame2Data(
        scene_bias_flag=True,
        play_flag=False,
        scene_bias=66,
    )


def test_read_data_unsupported_opcode():
    # The opcode name follows the Python member naming, so `ACTION_ADD` where PHP writes `ActionAdd`.
    with pytest.raises(InvalidDataError, match=re.escape("Unexpected data for opcode ACTION_ADD, actionLength=42")):
        Opcode.ACTION_ADD.read_data(Reader(b""), 42)


def test_read_data_unsupported_opcode_ignore_error():
    assert Opcode.ACTION_ADD.read_data(Reader(b"abcd", errors=Errors.NONE), 4) == b"abcd"
