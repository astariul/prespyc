"""How nested timelines play: from their placement, looping unless a script stops them."""

from __future__ import annotations

from prespyc.extractor.drawer.converter import Converter
from prespyc.extractor.shape.shape_builder import ShapeBuilder
from prespyc.extractor.timeline.frame import Frame
from prespyc.extractor.timeline.frame_object import FrameObject
from prespyc.extractor.timeline.timeline import Timeline
from prespyc.parser.structure.action.action_record import ActionRecord
from prespyc.parser.structure.action.opcode import Opcode
from prespyc.parser.structure.record.clip_action_record import ClipActionRecord
from prespyc.parser.structure.record.clip_actions import ClipActions
from prespyc.parser.structure.record.clip_event_flags import ClipEventFlags
from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.shape.fill_style import FillStyle
from prespyc.parser.structure.tag.do_action import DoActionTag
from prespyc.swf_file import SwfFile
from tests.support import fixture

RED, GREEN, BLUE, GREY = (255, 0, 0, 255), (0, 255, 0, 255), (0, 0, 255, 255), (128, 128, 128, 255)
STOP = [ActionRecord(0, Opcode.ACTION_STOP, 0, None), ActionRecord(1, Opcode.NULL, 0, None)]


def _square(color: tuple[int, ...]):
    extractor = SwfFile(fixture("extractor", "1047", "1047.swf")).extractor

    return (
        ShapeBuilder(extractor)
        .fill(FillStyle(FillStyle.SOLID, color=Color(*color[:3])))
        .move_to(0, 0)
        .line_to(200, 0)
        .line_to(200, 200)
        .line_to(0, 200)
        .line_to(0, 0)
        .build(1000)
    )


def _clip(*colors: tuple[int, ...], stop_on_last: bool = False) -> Timeline:
    """A clip showing one colour per frame, which may `stop()` on its last frame."""
    clip = Timeline.sequence(*(_square(color) for color in colors))

    if not stop_on_last:
        return clip

    last = clip.frames[-1]

    return Timeline(clip.bounds, *clip.frames[:-1], Frame(last.bounds, last.objects, [DoActionTag(STOP)]))


def _color(drawable, frame: int) -> tuple[int, ...]:
    return Converter().to_image(drawable, frame).getpixel((5, 5))


def test_nested_clip_loops():
    parent = Timeline.sequence(_clip(RED, GREEN, BLUE))

    assert _color(parent, 4) == GREEN


def test_nested_clip_that_stops_holds_its_last_frame():
    parent = Timeline.sequence(_clip(RED, GREEN, BLUE, stop_on_last=True))

    assert _color(parent, 4) == BLUE


def test_placement_handler_that_stops_holds_the_last_frame():
    load = ClipActionRecord(ClipEventFlags(ClipEventFlags.LOAD), 0, None, STOP)
    parent = Timeline.sequence(_clip(RED, GREEN, BLUE))
    [frame] = parent.frames
    [placed] = frame.objects.values()
    stopped = Timeline(
        parent.bounds,
        Frame(frame.bounds, {1: placed.with_(clip_actions=ClipActions(ClipEventFlags(1), [load]))}),
    )

    assert _color(stopped, 4) == BLUE


def test_child_plays_from_the_frame_placing_it():
    placed = FrameObject.place(1, _clip(RED, GREEN, BLUE))
    grey = FrameObject.place(1, _square(GREY))
    bounds = placed.bounds
    parent = Timeline(bounds, Frame(bounds, {1: grey}), Frame(bounds, {1: placed}), Frame(bounds, {1: placed}))

    assert _color(parent, 1) == RED
    assert _color(parent, 2) == GREEN


def test_child_on_every_frame_keeps_playing_when_the_parent_loops():
    placed = FrameObject.place(1, _clip(RED, GREEN, BLUE))
    bounds = placed.bounds
    parent = Timeline(bounds, Frame(bounds, {1: placed}), Frame(bounds, {1: placed}))

    # The parent is back on its first frame, its child has played 4 frames.
    assert _color(parent, 4) == GREEN


def test_child_placed_again_restarts_when_the_parent_loops():
    grey = FrameObject.place(1, _square(GREY))
    placed = FrameObject.place(1, _clip(RED, GREEN, BLUE))
    bounds = placed.bounds
    parent = Timeline(bounds, Frame(bounds, {1: grey}), Frame(bounds, {1: placed}))

    # Second loop of the parent: the child was placed again one frame ago.
    assert _color(parent, 3) == RED
