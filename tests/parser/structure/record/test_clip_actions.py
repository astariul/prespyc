"""Port of ArakneSwf's ClipActionsTest."""

from __future__ import annotations

from prespyc.parser.structure.action.opcode import Opcode
from prespyc.parser.structure.action.type import Type
from prespyc.parser.structure.action.value import Value
from prespyc.parser.structure.record.clip_actions import ClipActions
from prespyc.parser.structure.record.clip_event_flags import ClipEventFlags
from tests.support import fixture, fixture_reader


def test_read():
    reader = fixture_reader(fixture("extractor", "core", "core.swf"), 529791)

    clip_actions = ClipActions.read(reader, 9)

    assert clip_actions.all_event_flags.has(ClipEventFlags.CONSTRUCT)
    assert not clip_actions.all_event_flags.has(ClipEventFlags.DATA)
    assert not clip_actions.all_event_flags.has(ClipEventFlags.KEY_PRESS)
    assert not clip_actions.all_event_flags.has(ClipEventFlags.KEY_DOWN)

    assert len(clip_actions.records) == 1
    assert clip_actions.records[0].flags.has(ClipEventFlags.CONSTRUCT)
    assert clip_actions.records[0].size == 58
    assert len(clip_actions.records[0].actions) == 7

    actions = clip_actions.records[0].actions
    assert actions[0].opcode == Opcode.ACTION_PUSH
    assert actions[0].data == [Value(Type.STRING, b"enabled"), Value(Type.BOOLEAN, True)]
    assert actions[1].opcode == Opcode.ACTION_SET_VARIABLE
    assert actions[2].data == [Value(Type.STRING, b"handCursor"), Value(Type.BOOLEAN, False)]
    assert actions[3].opcode == Opcode.ACTION_SET_VARIABLE
    assert actions[4].data == [Value(Type.STRING, b"styleName"), Value(Type.STRING, b"default")]
    assert actions[5].opcode == Opcode.ACTION_SET_VARIABLE
    assert actions[6].opcode == Opcode.NULL
