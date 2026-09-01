"""Port of ArakneSwf's ButtonCondActionTest."""

from __future__ import annotations

import pytest

from prespyc.errors import Errors, InvalidDataError
from prespyc.parser.reader import Reader
from prespyc.parser.structure.action.opcode import Opcode
from prespyc.parser.structure.action.type import Type
from prespyc.parser.structure.action.value import Value
from prespyc.parser.structure.record.button_cond_action import ButtonCondAction
from tests.support import fixture, fixture_reader


def test_read_collection():
    reader = fixture_reader(fixture("extractor", "core", "core.swf"), 646131)

    actions = ButtonCondAction.read_collection(reader, 646162)

    assert len(actions) == 1
    assert all(isinstance(action, ButtonCondAction) for action in actions)

    assert not actions[0].idle_to_over_down
    assert not actions[0].out_down_to_idle
    assert not actions[0].out_down_to_over_down
    assert not actions[0].over_down_to_out_down
    assert actions[0].over_down_to_over_up
    assert not actions[0].over_up_to_over_down
    assert not actions[0].over_up_to_idle
    assert not actions[0].idle_to_over_up
    assert not actions[0].over_down_to_idle
    assert actions[0].key_press == 0
    assert len(actions[0].actions) == 4

    assert actions[0].actions[0].opcode == Opcode.ACTION_PUSH
    assert actions[0].actions[0].data == [Value(Type.DOUBLE, 0), Value(Type.STRING, b"sendCancel")]
    assert actions[0].actions[1].opcode == Opcode.ACTION_CALL_FUNCTION
    assert actions[0].actions[2].opcode == Opcode.ACTION_POP
    assert actions[0].actions[3].opcode == Opcode.NULL


def test_read_collection_invalid_size():
    reader = Reader(b"\x02\x00\x00\x00")

    with pytest.raises(InvalidDataError, match="Invalid ButtonCondAction size: 2"):
        ButtonCondAction.read_collection(reader, reader.end)


def test_read_collection_invalid_size_ignore_error():
    reader = Reader(b"\x02\x00\x00\x00", errors=Errors.NONE)

    assert ButtonCondAction.read_collection(reader, reader.end) == []
    assert reader.offset == reader.end


def test_read_collection_should_stop_on_stream_end():
    reader = Reader(b"\x10\x00" * 15, errors=Errors.NONE)

    assert len(ButtonCondAction.read_collection(reader, reader.end)) == 2
    assert reader.offset == reader.end
