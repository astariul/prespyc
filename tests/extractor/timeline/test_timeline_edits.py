"""Building a variant of a timeline: frames held, repeated, reordered, or other characters."""

from __future__ import annotations

from prespyc.extractor.drawer.converter import Converter
from prespyc.extractor.timeline.frame_object import FrameObject
from prespyc.extractor.timeline.timeline import Timeline
from prespyc.parser.structure.record.matrix import Matrix
from prespyc.swf_file import SwfFile
from tests.support import fixture


def _extractor():
    return SwfFile(fixture("extractor", "1047", "1047.swf")).extractor


def _timeline() -> Timeline:
    return _extractor()[65].timeline  # 18 frames


def test_pad_to_holds_the_last_frame() -> None:
    timeline = _timeline()

    assert timeline.pad_to(20).frames == (*timeline.frames, timeline.frames[-1], timeline.frames[-1])
    assert timeline.pad_to(5).frames == timeline.frames


def test_repeat() -> None:
    timeline = _timeline()

    assert timeline.repeat(3).frames == timeline.frames * 3


def test_rotate_starts_the_loop_on_another_frame() -> None:
    timeline = _timeline()

    assert timeline.rotate(5).frames == timeline.frames[5:] + timeline.frames[:5]


def test_hold_plays_frames_longer() -> None:
    timeline = _timeline()
    first, *others, last = timeline.frames

    assert timeline.hold({0: 2, 17: 1}).frames == (first, first, first, *others, last, last)


def test_keep_ranges() -> None:
    timeline = _timeline()

    assert timeline.keep_ranges([(0, 3), (10, 12)]).frames == timeline.frames[0:3] + timeline.frames[10:12]


def test_edits_keep_the_bounds() -> None:
    timeline = _timeline()

    assert timeline.rotate(3).bounds == timeline.bounds


def test_sequence_plays_one_drawable_per_frame() -> None:
    extractor = _extractor()
    head, foot = extractor[13], extractor[15]
    tag_matrix = Matrix(translate_x=100)

    timeline = Timeline.sequence(head, foot, depth=2, tag_matrix=tag_matrix)

    assert [frame.objects for frame in timeline.frames] == [
        {2: FrameObject.place(2, head, tag_matrix)},
        {2: FrameObject.place(2, foot, tag_matrix)},
    ]
    assert timeline.bounds == head.bounds.transform(tag_matrix).union(foot.bounds.transform(tag_matrix))


def test_sequence_draws_a_drawable_where_it_draws_itself() -> None:
    head = _extractor()[13]
    converter = Converter()

    assert converter.to_image(Timeline.sequence(head)).tobytes() == converter.to_image(head).tobytes()
