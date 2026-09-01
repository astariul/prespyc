"""Port of ArakneSwf's ClipEventFlagsTest."""

from __future__ import annotations

from prespyc.parser.reader import Reader
from prespyc.parser.structure.record.clip_event_flags import ClipEventFlags


def test_read_swf5():
    reader = Reader(b"\x29\x98")
    flags = ClipEventFlags.read(reader, 5)

    assert not flags.has(ClipEventFlags.KEY_UP)
    assert not flags.has(ClipEventFlags.KEY_DOWN)
    assert flags.has(ClipEventFlags.MOUSE_UP)
    assert not flags.has(ClipEventFlags.MOUSE_DOWN)
    assert flags.has(ClipEventFlags.MOUSE_MOVE)
    assert not flags.has(ClipEventFlags.UNLOAD)
    assert not flags.has(ClipEventFlags.ENTER_FRAME)
    assert flags.has(ClipEventFlags.LOAD)

    assert flags.has(ClipEventFlags.DRAG_OVER)
    assert not flags.has(ClipEventFlags.ROLL_OUT)
    assert not flags.has(ClipEventFlags.ROLL_OVER)
    assert flags.has(ClipEventFlags.RELEASE_OUTSIDE)
    assert flags.has(ClipEventFlags.RELEASE)
    assert not flags.has(ClipEventFlags.PRESS)
    assert not flags.has(ClipEventFlags.INITIALIZE)
    assert not flags.has(ClipEventFlags.DATA)

    assert not flags.has(ClipEventFlags.CONSTRUCT)
    assert not flags.has(ClipEventFlags.KEY_PRESS)
    assert not flags.has(ClipEventFlags.DRAG_OUT)


def test_read_swf7():
    reader = Reader(b"\x29\x98\x03\x00")
    flags = ClipEventFlags.read(reader, 6)

    assert not flags.has(ClipEventFlags.KEY_UP)
    assert not flags.has(ClipEventFlags.KEY_DOWN)
    assert flags.has(ClipEventFlags.MOUSE_UP)
    assert not flags.has(ClipEventFlags.MOUSE_DOWN)
    assert flags.has(ClipEventFlags.MOUSE_MOVE)
    assert not flags.has(ClipEventFlags.UNLOAD)
    assert not flags.has(ClipEventFlags.ENTER_FRAME)
    assert flags.has(ClipEventFlags.LOAD)

    assert flags.has(ClipEventFlags.DRAG_OVER)
    assert not flags.has(ClipEventFlags.ROLL_OUT)
    assert not flags.has(ClipEventFlags.ROLL_OVER)
    assert flags.has(ClipEventFlags.RELEASE_OUTSIDE)
    assert flags.has(ClipEventFlags.RELEASE)
    assert not flags.has(ClipEventFlags.PRESS)
    assert not flags.has(ClipEventFlags.INITIALIZE)
    assert not flags.has(ClipEventFlags.DATA)

    assert not flags.has(ClipEventFlags.CONSTRUCT)
    assert flags.has(ClipEventFlags.KEY_PRESS)
    assert flags.has(ClipEventFlags.DRAG_OUT)
