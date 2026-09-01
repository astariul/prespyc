"""Port of ArakneSwf's `tests/Parser/Structure/Action/ActionRecordTest.php`."""

from __future__ import annotations

import re

import pytest

from prespyc.errors import Errors, InvalidDataError, OutOfBoundsError
from prespyc.parser.reader import Reader
from prespyc.parser.structure.action.action_record import ActionRecord
from prespyc.parser.structure.action.opcode import Opcode
from prespyc.parser.structure.action.type import Type
from prespyc.parser.structure.action.value import Value
from tests.support import fixture, fixture_reader


def test_read_collection():
    reader = fixture_reader(fixture("simple.swf"), 27)

    actions = ActionRecord.read_collection(reader, 147)

    assert all(isinstance(action, ActionRecord) for action in actions)
    assert len(actions) == 11

    assert actions[0].opcode is Opcode.ACTION_CONSTANT_POOL
    assert actions[0].data == [b"simple_int", b"simple_string", b"abc", b"simple_float", b"simple_bool", b"simple_null"]
    assert actions[1].opcode is Opcode.ACTION_PUSH
    assert actions[1].data == [Value(Type.CONSTANT8, 0), Value(Type.INTEGER, 123)]
    assert actions[2].opcode is Opcode.ACTION_SET_VARIABLE
    assert actions[2].data is None


def test_read_collection_invalid_opcode_should_be_ignored():
    reader = Reader(b"\x01\x07", errors=Errors.NONE)

    actions = ActionRecord.read_collection(reader, 2)

    assert len(actions) == 1
    assert actions[0].opcode is Opcode.ACTION_STOP
    assert actions[0].data is None


def test_read_collection_invalid_opcode():
    reader = Reader(b"\x01\x07")

    with pytest.raises(InvalidDataError, match=re.escape('Invalid action code "1" at offset 1')):
        ActionRecord.read_collection(reader, 2)


def test_too_many_data_read():
    reader = Reader(b"\x8cABCD\x00")

    with pytest.raises(
        OutOfBoundsError,
        match=re.escape("Trying to access data after the end of the input stream (offset: 2, end: 2)"),
    ):
        ActionRecord.read_collection(reader, 2)


def test_too_many_data_read_ignore_error():
    reader = Reader(b"\x8cABCD\x00", errors=Errors.NONE)
    actions = ActionRecord.read_collection(reader, 2)

    assert reader.offset == 2
    assert len(actions) == 1
    assert actions[0].opcode is Opcode.ACTION_GO_TO_LABEL
    assert actions[0].data == b""


def test_end_already_reached():
    reader = Reader(b"")
    actions = ActionRecord.read_collection(reader, 0)

    assert len(actions) == 0


def test_end_out_of_bounds():
    reader = fixture_reader(fixture("simple.swf"), 27)
    reader = reader.chunk(27, 147)

    with pytest.raises(
        OutOfBoundsError,
        match=re.escape("Trying to access data after the end of the input stream (offset: 148, end: 147)"),
    ):
        ActionRecord.read_collection(reader, 148)


def test_end_out_of_bounds_ignore():
    reader = fixture_reader(fixture("simple.swf"), 27, errors=Errors.NONE)
    reader = reader.chunk(27, 147)

    actions = ActionRecord.read_collection(reader, 148)

    assert all(isinstance(action, ActionRecord) for action in actions)
    assert len(actions) == 11
