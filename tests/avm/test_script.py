"""`Script`: what an action block does, read off its bytecode."""

from __future__ import annotations

from prespyc.avm.script import Property, Script
from prespyc.parser.structure.action.action_record import ActionRecord
from prespyc.parser.structure.action.goto_frame2_data import GotoFrame2Data
from prespyc.parser.structure.action.opcode import Opcode
from prespyc.parser.structure.action.type import Type
from prespyc.parser.structure.action.value import Value


def block(*actions: tuple) -> list[ActionRecord]:
    """Action records out of `(opcode, data)` pairs, ended by the block terminator."""
    records = [ActionRecord(offset, opcode, 0, data) for offset, (opcode, data) in enumerate(actions)]

    return [*records, ActionRecord(len(records), Opcode.NULL, 0, None)]


def push(*values: tuple[Type, object]) -> tuple:
    return Opcode.ACTION_PUSH, [Value(type, value) for type, value in values]


def test_stop() -> None:
    script = Script(block((Opcode.ACTION_STOP, None)))

    assert script.stops
    assert script.halts


def test_goto_frame_stops_unless_it_plays() -> None:
    goto_and_stop = Script(block((Opcode.ACTION_GOTO_FRAME, 2)))
    goto_and_play = Script(block((Opcode.ACTION_GOTO_FRAME, 2), (Opcode.ACTION_PLAY, None)))

    assert goto_and_stop.goto_and_stop
    assert not goto_and_play.goto_and_stop
    assert not goto_and_play.halts


def test_goto_label_stops_unless_it_plays() -> None:
    assert Script(block((Opcode.ACTION_GO_TO_LABEL, b"end"))).goto_and_stop
    assert not Script(block((Opcode.ACTION_GO_TO_LABEL, b"b"), (Opcode.ACTION_PLAY, None))).goto_and_stop


def test_goto_random_frame() -> None:
    # gotoAndStop(random(3) + 1)
    script = Script(
        block(
            push((Type.INTEGER, 3)),
            (Opcode.ACTION_RANDOM_NUMBER, None),
            push((Type.INTEGER, 1)),
            (Opcode.ACTION_ADD2, None),
            (Opcode.ACTION_GOTO_FRAME2, GotoFrame2Data(scene_bias_flag=False, play_flag=False, scene_bias=None)),
        )
    )

    assert script.goto_and_stop
    assert script.uses_random


def test_goto_and_stop_method_through_the_constant_pool() -> None:
    # this.gotoAndStop(2)
    script = Script(
        block(
            (Opcode.ACTION_CONSTANT_POOL, [b"this", b"gotoAndStop"]),
            push((Type.INTEGER, 2), (Type.INTEGER, 1), (Type.CONSTANT8, 0)),
            (Opcode.ACTION_GET_VARIABLE, None),
            push((Type.CONSTANT8, 1)),
            (Opcode.ACTION_CALL_METHOD, None),
            (Opcode.ACTION_POP, None),
        )
    )

    assert script.strings == {"this", "gotoAndStop"}
    assert script.calls == {"gotoAndStop"}
    assert script.goto_and_stop


def test_math_random() -> None:
    script = Script(
        block(
            push((Type.INTEGER, 0), (Type.STRING, b"Math")),
            (Opcode.ACTION_GET_VARIABLE, None),
            push((Type.STRING, b"random")),
            (Opcode.ACTION_CALL_METHOD, None),
        )
    )

    assert script.uses_random


def test_set_property_index_is_read_under_a_computed_value() -> None:
    # t = random(15); _xscale = 70 + 2 * t; _yscale = 70 + 2 * t;
    scale = [
        (Opcode.ACTION_GET_VARIABLE, None),
        (Opcode.ACTION_MULTIPLY, None),
        (Opcode.ACTION_ADD2, None),
        (Opcode.ACTION_SET_PROPERTY, None),
    ]
    script = Script(
        block(
            (Opcode.ACTION_CONSTANT_POOL, [b"t", b""]),
            push((Type.CONSTANT8, 0), (Type.INTEGER, 15)),
            (Opcode.ACTION_RANDOM_NUMBER, None),
            (Opcode.ACTION_SET_VARIABLE, None),
            push((Type.CONSTANT8, 1), (Type.INTEGER, 2), (Type.INTEGER, 70), (Type.INTEGER, 2), (Type.CONSTANT8, 0)),
            *scale,
            push((Type.CONSTANT8, 1), (Type.INTEGER, 3), (Type.INTEGER, 70), (Type.INTEGER, 2), (Type.CONSTANT8, 0)),
            *scale,
        )
    )

    assert script.properties_written == {Property.XSCALE, Property.YSCALE}
    assert script.properties_read == set()


def test_properties_by_name() -> None:
    # _parent._alpha = _parent._alpha - 3.34
    script = Script(
        block(
            (Opcode.ACTION_CONSTANT_POOL, [b"_parent", b"_alpha"]),
            push((Type.CONSTANT8, 0)),
            (Opcode.ACTION_GET_VARIABLE, None),
            push((Type.CONSTANT8, 1), (Type.CONSTANT8, 0)),
            (Opcode.ACTION_GET_VARIABLE, None),
            push((Type.CONSTANT8, 1)),
            (Opcode.ACTION_GET_MEMBER, None),
            push((Type.DOUBLE, 3.34)),
            (Opcode.ACTION_SUBTRACT, None),
            (Opcode.ACTION_SET_MEMBER, None),
        )
    )

    assert script.properties_read == {Property.ALPHA}
    assert script.properties_written == {Property.ALPHA}
    assert not script.halts
