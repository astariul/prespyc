"""Port of ArakneSwf's tests/Extractor/Timeline/TimelineTest.php."""

from __future__ import annotations

import importlib.util

import pytest

from prespyc.extractor.extractor import Extractor
from prespyc.extractor.modifier.base_character_modifier import BaseCharacterModifier
from prespyc.extractor.timeline.frame import Frame
from prespyc.extractor.timeline.timeline import Timeline
from prespyc.parser.structure.record.color_transform import ColorTransform
from prespyc.parser.structure.record.matrix import Matrix
from prespyc.parser.structure.record.rectangle import Rectangle
from prespyc.swf_file import SwfFile
from tests.support import assert_svg_matches, fixture

# `Extractor.character()` builds the image characters before anything else, so no fixture can be
# extracted until they are ported.
pytestmark = pytest.mark.skipif(
    any(
        importlib.util.find_spec(name) is None
        for name in (
            "prespyc.extractor.image.image_bits_definition",
            "prespyc.extractor.image.jpeg_image_definition",
            "prespyc.extractor.image.lossless_image_definition",
        )
    ),
    reason="the image characters are not ported yet, so Extractor.character() cannot resolve anything",
)


class _CountingModifier(BaseCharacterModifier):
    """Counts the calls of every hook, as the PHPUnit mocks of the original test do."""

    def __init__(self, timeline: Timeline, replacement: Timeline) -> None:
        self._timeline = timeline
        self._replacement = replacement
        self.timelines: list[Timeline] = []
        self.frames = 0
        self.shapes = 0
        self.sprites = 0

    def apply_on_timeline(self, timeline: Timeline) -> Timeline:
        self.timelines.append(timeline)

        return self._replacement if timeline is self._timeline else timeline

    def apply_on_frame(self, frame):
        self.frames += 1

        return frame

    def apply_on_shape(self, shape):
        self.shapes += 1

        return shape

    def apply_on_sprite(self, sprite):
        self.sprites += 1

        return sprite


def _character_65_timeline() -> Timeline:
    swf = SwfFile(fixture("extractor", "1047", "1047.swf"))

    return Extractor(swf).character(65).timeline


def test_getters():
    timeline = _character_65_timeline()

    assert timeline.bounds == Rectangle(-584, 209, -772, 67)
    assert len(timeline.frames) == 18
    assert timeline.frames_count() == 18
    assert timeline.frames_count(True) == 18


@pytest.mark.parametrize(
    ("frame", "golden"),
    [
        (0, "65-0.svg"),
        (10, "65-10.svg"),
        (17, "65-17.svg"),
        (250, "65-17.svg"),
    ],
)
def test_to_svg(frame: int, golden: str):
    timeline = _character_65_timeline()

    assert_svg_matches(timeline.to_svg(frame), fixture("extractor", "1047", "65_frames", golden))


def test_to_svg_all():
    timeline = _character_65_timeline()
    svgs = list(timeline.to_svg_all())

    assert len(svgs) == len(timeline.frames)

    for f, svg in enumerate(svgs):
        assert_svg_matches(svg, fixture("extractor", "1047", "65_frames", f"65-{f}.svg"))


def test_to_svg_all_without_subpixel_stroke():
    timeline = _character_65_timeline()
    svgs = list(timeline.to_svg_all(False))

    assert len(svgs) == len(timeline.frames)

    for f, svg in enumerate(svgs):
        assert_svg_matches(svg, fixture("extractor", "1047", "65_frames", f"65-{f}-no-sp-stroke.svg"))


def test_transform_colors():
    timeline = _character_65_timeline()
    transformed = timeline.transform_colors(
        ColorTransform(
            red_mult=0,
            green_mult=256,
            blue_mult=256,
            alpha_add=256,
        )
    )
    svgs = list(transformed.to_svg_all())

    assert len(svgs) == len(timeline.frames)

    for f, svg in enumerate(svgs):
        assert_svg_matches(svg, fixture("extractor", "1047", "65_frames", f"transformed-{f}.svg"))


def test_with_bounds():
    timeline = _character_65_timeline()
    transformed = timeline.with_bounds(Rectangle(0, 200, 0, 200))

    for frame in transformed.frames:
        assert frame.bounds == Rectangle(0, 200, 0, 200)

    svgs = list(transformed.to_svg_all())

    assert len(svgs) == len(timeline.frames)

    for f, svg in enumerate(svgs):
        assert_svg_matches(svg, fixture("extractor", "1047", "65_frames", f"new-bounds-{f}.svg"))


def test_with_attachment():
    timeline = SwfFile(fixture("extractor", "1", "1.swf")).timeline(False)
    other = SwfFile(fixture("extractor", "62", "62.swf")).timeline()

    combined = timeline.with_attachment(other, depth=10, name="attached")

    assert_svg_matches(combined.to_svg(), fixture("extractor", "1", "with-attachment.svg"))
    assert combined.bounds == Rectangle(-565, 11186, -1236, 16118)

    for frame in combined.frames:
        obj = frame.object_by_name("attached")
        assert obj is not None
        assert obj.object is other


def test_modify_frames():
    timeline = _character_65_timeline()

    class Modifier(BaseCharacterModifier):
        def apply_on_timeline(self, timeline: Timeline) -> Timeline:
            return timeline.transform_colors(ColorTransform(green_mult=0))

        def apply_on_frame(self, frame: Frame) -> Frame:
            return Frame(
                bounds=frame.bounds.transform(Matrix(2.0, 3.0)),
                objects=frame.objects,
                actions=frame.actions,
                label=frame.label,
            )

    modified = timeline.modify(Modifier(), 1)

    assert_svg_matches(modified.to_svg(), fixture("extractor", "1047", "65_frames", "modified.svg"))

    assert modified.bounds != timeline.bounds
    assert modified.bounds == timeline.bounds.transform(Matrix(2.0, 3.0))


def test_modify_only_current():
    timeline = _character_65_timeline()
    new_timeline = Timeline(timeline.bounds, *timeline.frames)

    modifier = _CountingModifier(timeline, new_timeline)
    modified = timeline.modify(modifier, 0)

    assert modified is new_timeline
    assert len(modifier.timelines) == 1
    assert modifier.timelines[0] is timeline
    assert modifier.frames == 0


def test_modify_one_depth():
    timeline = _character_65_timeline()
    new_timeline = Timeline(timeline.bounds, *timeline.frames)

    modifier = _CountingModifier(timeline, new_timeline)
    modified = timeline.modify(modifier, 1)

    assert modified is new_timeline
    assert len(modifier.timelines) == 1
    assert modifier.timelines[0] is timeline
    assert modifier.frames == 18


def test_modify_all_depths():
    timeline = _character_65_timeline()
    new_timeline = Timeline(timeline.bounds, *timeline.frames)

    modifier = _CountingModifier(timeline, new_timeline)
    modified = timeline.modify(modifier)

    assert modified is new_timeline
    assert len(modifier.timelines) == 325
    assert modifier.frames == 342
    assert modifier.shapes == 324
    assert modifier.sprites == 324


def test_modify_without_modification_should_return_same_instance():
    timeline = _character_65_timeline()

    assert timeline.modify(BaseCharacterModifier()) is timeline


def test_frame_by_label():
    timeline = _character_65_timeline()

    assert timeline.frame_by_label("static") is timeline.frames[4]
    assert timeline.frame_by_label("static").label == "static"
    assert timeline.frame_by_label("not_found") is None


def test_keep_frame_by_label_found():
    timeline = _character_65_timeline()
    new_timeline = timeline.keep_frame_by_label("static")

    assert len(new_timeline.frames) == 1
    assert new_timeline.frames[0].label == "static"
    assert new_timeline.frames[0] is timeline.frames[4]
    assert new_timeline.bounds is timeline.bounds


def test_keep_frame_by_label_not_found():
    timeline = _character_65_timeline()
    new_timeline = timeline.keep_frame_by_label("not_found")

    assert len(new_timeline.frames) == 1
    assert new_timeline.frames[0].label is None
    assert new_timeline.frames[0] is timeline.frames[0]
    assert new_timeline.bounds is timeline.bounds


def test_keep_frame_by_number_found():
    timeline = _character_65_timeline()
    new_timeline = timeline.keep_frame_by_number(5)

    assert len(new_timeline.frames) == 1
    assert new_timeline.frames[0].label == "static"
    assert new_timeline.frames[0] is timeline.frames[4]
    assert new_timeline.bounds is timeline.bounds


def test_keep_frame_by_number_too_low():
    timeline = _character_65_timeline()
    new_timeline = timeline.keep_frame_by_number(0)

    assert len(new_timeline.frames) == 1
    assert new_timeline.frames[0].label is None
    assert new_timeline.frames[0] is timeline.frames[0]
    assert new_timeline.bounds is timeline.bounds


def test_keep_frame_by_number_too_high():
    timeline = _character_65_timeline()
    new_timeline = timeline.keep_frame_by_number(42)

    assert len(new_timeline.frames) == 1
    assert new_timeline.frames[0].label is None
    assert new_timeline.frames[0] is timeline.frames[17]
    assert new_timeline.bounds is timeline.bounds
