"""Port of ArakneSwf's `tests/Parser/SwfTest.php`."""

from __future__ import annotations

import random
import re
import struct
import zlib

import pytest

from prespyc._util import php_json_encode
from prespyc.errors import Errors
from prespyc.parser.structure.action.opcode import Opcode
from prespyc.parser.structure.action.type import Type
from prespyc.parser.structure.action.value import Value
from prespyc.parser.structure.raw_tag import RawTag
from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.filter.color_matrix_filter import ColorMatrixFilter
from prespyc.parser.structure.record.rectangle import Rectangle
from prespyc.parser.structure.tag.define_scene_and_frame_label_data import DefineSceneAndFrameLabelDataTag
from prespyc.parser.structure.tag.define_shape4 import DefineShape4Tag
from prespyc.parser.structure.tag.define_sprite import DefineSpriteTag
from prespyc.parser.structure.tag.do_action import DoActionTag
from prespyc.parser.structure.tag.end import EndTag
from prespyc.parser.structure.tag.place_object3 import PlaceObject3Tag
from prespyc.parser.structure.tag.set_background_color import SetBackgroundColorTag
from prespyc.parser.structure.tag.show_frame import ShowFrameTag
from prespyc.parser.swf import Swf
from tests.support import fixture


def load(*parts: str, errors: int = Errors.ALL) -> Swf:
    """`Swf::fromString(file_get_contents(...))` — the PHP tests' one-liner."""
    return Swf.from_bytes(fixture(*parts).read_bytes(), errors)


def test_simple_variables():
    swf = load("simple.swf")

    assert swf.header.version == 6
    assert swf.header.signature == "CWS"
    assert swf.header.frame_rate == 50.0
    assert swf.header.frame_count == 1
    assert swf.header.frame_size == Rectangle(xmin=0, xmax=20, ymin=0, ymax=20)

    assert len(swf.tags) == 4
    assert swf.tags[0].type == 9
    assert swf.tags[1].type == 12
    assert swf.tags[2].type == 1
    assert swf.tags[3].type == 0

    assert swf.parse(swf.tags[0]) == SetBackgroundColorTag(Color(0, 0, 0))

    do_action_tag = swf.parse(swf.tags[1])
    assert isinstance(do_action_tag, DoActionTag)
    actions = do_action_tag.actions
    assert len(actions) == 12

    assert actions[0].opcode is Opcode.ACTION_CONSTANT_POOL
    assert actions[0].data == [b"simple_int", b"simple_string", b"abc", b"simple_float", b"simple_bool", b"simple_null"]

    assert actions[1].opcode is Opcode.ACTION_PUSH
    assert actions[1].data == [Value(Type.CONSTANT8, 0), Value(Type.INTEGER, 123)]
    assert actions[2].opcode is Opcode.ACTION_SET_VARIABLE
    assert actions[2].data is None

    assert actions[3].opcode is Opcode.ACTION_PUSH
    assert actions[3].data == [Value(Type.CONSTANT8, 1), Value(Type.CONSTANT8, 2)]
    assert actions[4].opcode is Opcode.ACTION_SET_VARIABLE
    assert actions[4].data is None

    assert actions[5].opcode is Opcode.ACTION_PUSH
    assert actions[5].data == [Value(Type.CONSTANT8, 3), Value(Type.DOUBLE, 1.23)]
    assert actions[6].opcode is Opcode.ACTION_SET_VARIABLE
    assert actions[6].data is None

    assert actions[7].opcode is Opcode.ACTION_PUSH
    assert actions[7].data == [Value(Type.CONSTANT8, 4), Value(Type.BOOLEAN, True)]
    assert actions[8].opcode is Opcode.ACTION_SET_VARIABLE
    assert actions[8].data is None

    assert actions[9].opcode is Opcode.ACTION_PUSH
    assert actions[9].data == [Value(Type.CONSTANT8, 5), Value(Type.NULL, None)]
    assert actions[10].opcode is Opcode.ACTION_SET_VARIABLE
    assert actions[10].data is None

    assert actions[11].opcode is Opcode.NULL

    assert swf.parse(swf.tags[2]) == ShowFrameTag()
    assert swf.parse(swf.tags[3]) == EndTag()


def test_big_values():
    swf = load("big.swf")

    do_action_tag = swf.parse(swf.tags[1])
    assert isinstance(do_action_tag, DoActionTag)
    actions = do_action_tag.actions
    assert len(actions) == 10

    assert actions[0].opcode is Opcode.ACTION_CONSTANT_POOL
    assert actions[0].data == [b"big_int", b"negative_int", b"big_float", b"negative_float"]

    assert actions[1].opcode is Opcode.ACTION_PUSH
    assert actions[1].data == [Value(Type.CONSTANT8, 0), Value(Type.INTEGER, 1234567890)]
    assert actions[2].opcode is Opcode.ACTION_SET_VARIABLE
    assert actions[2].data is None

    assert actions[3].opcode is Opcode.ACTION_PUSH
    assert actions[3].data == [Value(Type.CONSTANT8, 1), Value(Type.INTEGER, -1234567890)]
    assert actions[4].opcode is Opcode.ACTION_SET_VARIABLE
    assert actions[4].data is None

    assert actions[5].opcode is Opcode.ACTION_PUSH
    assert actions[5].data == [Value(Type.CONSTANT8, 2), Value(Type.DOUBLE, 1234567890123.1235)]
    assert actions[6].opcode is Opcode.ACTION_SET_VARIABLE
    assert actions[6].data is None

    assert actions[7].opcode is Opcode.ACTION_PUSH
    assert actions[7].data == [Value(Type.CONSTANT8, 3), Value(Type.DOUBLE, -1234567890123.1235)]
    assert actions[8].opcode is Opcode.ACTION_SET_VARIABLE
    assert actions[8].data is None

    assert actions[9].opcode is Opcode.NULL


def _dump(data: object) -> str:
    """`json_encode($action->data)`, for the action payloads `objects.swf` holds."""
    if data is None:
        return "null"

    if isinstance(data, bytes):
        return php_json_encode(data.decode("utf-8"))

    if isinstance(data, Value):
        return php_json_encode({"type": data.type.value, "value": data.value})

    if isinstance(data, list):
        return "[" + ",".join(_dump(item) for item in data) + "]"

    raise TypeError(f"Cannot dump {type(data).__name__}")


# `$action->opcode->name` in PHP, so the case names are the port's UPPER_SNAKE ones.
OBJECTS_ACTIONS = """\
ACTION_CONSTANT_POOL(["bag","Object","a","b","arr","Array","inlined_object","c","hello","d","inlined_array","get_member","array_access","get_member_str"])
ACTION_PUSH([{"type":8,"value":0},{"type":7,"value":0},{"type":8,"value":1}])
ACTION_NEW_OBJECT(null)
ACTION_SET_VARIABLE(null)
ACTION_PUSH([{"type":8,"value":0}])
ACTION_GET_VARIABLE(null)
ACTION_PUSH([{"type":8,"value":2},{"type":7,"value":1}])
ACTION_SET_MEMBER(null)
ACTION_PUSH([{"type":8,"value":0}])
ACTION_GET_VARIABLE(null)
ACTION_PUSH([{"type":8,"value":3},{"type":5,"value":false}])
ACTION_SET_MEMBER(null)
ACTION_PUSH([{"type":8,"value":4},{"type":7,"value":0},{"type":8,"value":5}])
ACTION_NEW_OBJECT(null)
ACTION_SET_VARIABLE(null)
ACTION_PUSH([{"type":8,"value":4}])
ACTION_GET_VARIABLE(null)
ACTION_PUSH([{"type":7,"value":0},{"type":7,"value":1}])
ACTION_SET_MEMBER(null)
ACTION_PUSH([{"type":8,"value":4}])
ACTION_GET_VARIABLE(null)
ACTION_PUSH([{"type":7,"value":1},{"type":7,"value":2}])
ACTION_SET_MEMBER(null)
ACTION_PUSH([{"type":8,"value":6},{"type":8,"value":7},{"type":6,"value":1.3},{"type":8,"value":9},{"type":8,"value":8},{"type":7,"value":2}])
ACTION_INIT_OBJECT(null)
ACTION_SET_VARIABLE(null)
ACTION_PUSH([{"type":8,"value":10},{"type":7,"value":3},{"type":7,"value":2},{"type":7,"value":1},{"type":7,"value":3}])
ACTION_INIT_ARRAY(null)
ACTION_SET_VARIABLE(null)
ACTION_PUSH([{"type":8,"value":11},{"type":8,"value":0}])
ACTION_GET_VARIABLE(null)
ACTION_PUSH([{"type":8,"value":2}])
ACTION_GET_MEMBER(null)
ACTION_SET_VARIABLE(null)
ACTION_PUSH([{"type":8,"value":12},{"type":8,"value":4}])
ACTION_GET_VARIABLE(null)
ACTION_PUSH([{"type":7,"value":1}])
ACTION_GET_MEMBER(null)
ACTION_SET_VARIABLE(null)
ACTION_PUSH([{"type":8,"value":13},{"type":8,"value":0}])
ACTION_GET_VARIABLE(null)
ACTION_PUSH([{"type":8,"value":3}])
ACTION_GET_MEMBER(null)
ACTION_SET_VARIABLE(null)
NULL(null)"""


def test_objects():
    swf = load("objects.swf")

    do_action_tag = swf.parse(swf.tags[1])
    assert isinstance(do_action_tag, DoActionTag)
    assert len(do_action_tag.actions) == 45

    actions = [f"{action.opcode.name}({_dump(action.data)})" for action in do_action_tag.actions]

    assert "\n".join(actions) == OBJECTS_ACTIONS


def test_parse_float():
    swf = load("extractor", "62", "62.swf")

    tag = swf.parse(swf.dictionary[19])
    assert isinstance(tag, DefineSpriteTag)

    matrix = None

    for place_object in tag.tags:
        if (
            isinstance(place_object, PlaceObject3Tag)
            and place_object.surface_filter_list
            and isinstance(place_object.surface_filter_list[0], ColorMatrixFilter)
        ):
            matrix = place_object.surface_filter_list[0].matrix

    assert matrix == pytest.approx(
        [
            0.6462849,
            0.9110194,
            -0.30730438,
            0.0,
            109.12499,
            0.21911979,
            0.8362024,
            0.19467786,
            0.0,
            109.125,
            0.6046222,
            0.3182575,
            0.32712013,
            0.0,
            109.12499,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
        ],
        abs=0.00001,
    )


def test_dictionary():
    swf = load("extractor", "62", "62.swf")

    assert len(swf.dictionary) == 19
    assert all(isinstance(tag, RawTag) for tag in swf.dictionary.values())

    assert swf.dictionary[1].type == DefineShape4Tag.TYPE_V4
    assert swf.dictionary[19].type == DefineSpriteTag.TYPE


def test_encoded_u32():
    swf = load("139.swf")
    tag = None

    for pos in swf.tags:
        if pos.type == 86:
            tag = swf.parse(pos)
            break

    assert isinstance(tag, DefineSceneAndFrameLabelDataTag)

    assert tag.scene_offsets == [0]
    assert tag.frame_numbers == [
        0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 68, 72, 76,
        86, 90, 94, 98, 102, 106, 110, 114, 118, 122, 126, 130, 134, 138, 142, 146, 150, 154, 158, 162,
    ]  # fmt: skip


def test_from_bytes_invalid_signature():
    with pytest.raises(ValueError, match=re.escape("Unsupported SWF signature: inv")):
        Swf.from_bytes(b"invalid signature")


def test_from_bytes_invalid_file_length():
    with pytest.raises(ValueError, match=re.escape("Invalid SWF file length: 5")):
        Swf.from_bytes(b"FWS\x01\x05\x00\x00\x00\x00\x00")


def test_from_bytes_simple_not_compressed():
    swf = Swf.from_bytes(b"FWS\x01\x10\x00\x00\x00\x0f\x80\x00\x01\x01\x00\x00\x00")

    assert swf.header.signature == "FWS"
    assert swf.header.version == 1
    assert swf.header.file_length == 16
    assert swf.header.frame_size == Rectangle(xmin=-1, xmax=-1, ymin=-1, ymax=-1)
    assert swf.header.frame_rate == 1.0
    assert swf.header.frame_count == 1
    assert swf.tags == [RawTag(0, 16, 0)]


def test_from_bytes_simple_compressed():
    before = b"CWS\x01\x10\x00\x00\x00"
    body = b"\x0f\x80\x00\x01\x01\x00\x00\x00"
    swf = Swf.from_bytes(before + zlib.compress(body, 9))

    assert swf.header.signature == "CWS"
    assert swf.header.version == 1
    assert swf.header.file_length == 16
    assert swf.header.frame_size == Rectangle(xmin=-1, xmax=-1, ymin=-1, ymax=-1)
    assert swf.header.frame_rate == 1.0
    assert swf.header.frame_count == 1
    assert swf.tags == [RawTag(0, 16, 0)]


def test_fuzzing_ignore_errors():
    """Random noise behind a valid header must never raise once every error flag is off."""
    randomizer = random.Random(0x5EED)

    for _ in range(10):
        size = 1_000_000
        data = b"FWS\x01" + struct.pack("<I", size) + randomizer.randbytes(size)

        swf = Swf.from_bytes(data, errors=Errors.NONE)

        assert swf.header.signature == "FWS"
        assert swf.header.version == 1
        assert swf.header.file_length == size

        for tag in swf.tags:
            swf.parse(tag)


def test_truncated_swf():
    content = fixture("extractor", "core", "core.swf").read_bytes()
    truncated = Swf.from_bytes(content[:1_000_000], errors=Errors.NONE)
    valid = Swf.from_bytes(content, errors=Errors.NONE)

    assert len(truncated.tags) == 1349

    for index, tag in enumerate(truncated.tags):
        assert valid.tags[index] == tag

        # Check only small tags for performance reasons
        if tag.length < 5000:
            assert valid.parse(valid.tags[index]) == truncated.parse(tag)
