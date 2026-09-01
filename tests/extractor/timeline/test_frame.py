"""Port of ArakneSwf's tests/Extractor/Timeline/FrameTest.php."""

from __future__ import annotations

import importlib.util

import pytest

from prespyc.avm.processor import Processor
from prespyc.avm.state import State
from prespyc.extractor.drawer.svg.svg_canvas import SvgCanvas
from prespyc.extractor.extractor import Extractor
from prespyc.extractor.modifier.base_character_modifier import BaseCharacterModifier
from prespyc.extractor.sprite.sprite_definition import SpriteDefinition
from prespyc.extractor.timeline.frame import Frame
from prespyc.extractor.timeline.frame_object import FrameObject
from prespyc.parser.structure.action.opcode import Opcode
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
            "prespyc.extractor.image.empty_image",
            "prespyc.extractor.image.image_bits_definition",
            "prespyc.extractor.image.jpeg_image_definition",
            "prespyc.extractor.image.lossless_image_definition",
        )
    ),
    reason="the image characters are not ported yet, so Extractor.character() cannot resolve anything",
)


def _color_and_attach_modifier() -> BaseCharacterModifier:
    """The anonymous modifier of `FrameTest::modifyOneDepth()`: recolor, and attach a 1x1 image."""
    from prespyc.extractor.image.empty_image import EmptyImage

    class Modifier(BaseCharacterModifier):
        def apply_on_frame(self, frame: Frame) -> Frame:
            return frame.transform_colors(ColorTransform(red_mult=0))

        def apply_on_sprite(self, sprite: SpriteDefinition) -> SpriteDefinition:
            return sprite.with_attachment(
                Frame(
                    Rectangle(-500, 300, 12, 300),
                    {
                        0: FrameObject(
                            depth=5,
                            object=EmptyImage(0),
                            bounds=Rectangle(-500, 300, 12, 300),
                            matrix=Matrix(),
                        ),
                    },
                ),
                depth=20,
                name="modifier-added-object",
            )

    return Modifier()


def test_getters():
    swf = SwfFile(fixture("extractor", "1047", "1047.swf"))
    extractor = Extractor(swf)

    frame = extractor.by_name("staticR").timeline.frames[0]

    assert frame.bounds == Rectangle(-209, 584, -772, 67)
    assert len(frame.objects) == 1
    assert not frame.actions
    assert frame.label is None
    assert frame.frames_count() == 1
    assert frame.frames_count(True) == 18


def test_getters_with_label():
    swf = SwfFile(fixture("extractor", "1047", "1047.swf"))
    extractor = Extractor(swf)

    frame = extractor.character(65).timeline.frames[4]

    assert frame.bounds == Rectangle(-584, 209, -772, 67)
    assert len(frame.objects) == 17
    assert len(frame.actions) == 1
    assert frame.actions[0].actions[0].opcode is Opcode.ACTION_STOP
    assert frame.label == "static"
    assert frame.frames_count() == 1
    assert frame.frames_count(True) == 1


@pytest.mark.parametrize(
    ("frame_number", "golden"),
    [
        (0, "staticR.svg"),
        (2, "staticR-2.svg"),
        (4, "staticR-4.svg"),
        (145, "staticR-4.svg"),
    ],
)
def test_draw(frame_number: int, golden: str):
    swf = SwfFile(fixture("extractor", "1047", "1047.swf"))
    extractor = Extractor(swf)

    frame = extractor.by_name("staticR").timeline.frames[0]

    svg = frame.draw(SvgCanvas(frame.bounds), frame_number).render()
    assert_svg_matches(svg, fixture("extractor", "1047", golden))


def test_transform_colors():
    swf = SwfFile(fixture("extractor", "1047", "1047.swf"))
    extractor = Extractor(swf)

    frame = extractor.by_name("staticR").timeline.frames[0]

    transformed = frame.transform_colors(
        ColorTransform(
            red_mult=256,
            green_mult=128,
            blue_mult=64,
        )
    )

    assert transformed is not frame
    assert transformed != frame

    svg = transformed.draw(SvgCanvas(transformed.bounds)).render()
    assert_svg_matches(svg, fixture("extractor", "1047", "staticR-transformed.svg"))


def test_with_bounds():
    swf = SwfFile(fixture("extractor", "1047", "1047.swf"))
    extractor = Extractor(swf)

    frame = extractor.by_name("staticR").timeline.frames[0]

    transformed = frame.with_bounds(Rectangle(0, 100, 0, 100))

    assert transformed is not frame
    assert transformed != frame
    assert transformed.bounds == Rectangle(0, 100, 0, 100)

    svg = transformed.draw(SvgCanvas(transformed.bounds)).render()
    assert_svg_matches(svg, fixture("extractor", "1047", "staticR-new-bounds.svg"))


def test_object_by_name():
    swf = SwfFile(fixture("extractor", "complex_sprite.swf"))
    extractor = Extractor(swf)

    frame = extractor.character(13).timeline.frames[0]

    assert frame.object_by_name("nonexistent") is None
    obj = frame.object_by_name("cheveux")

    assert obj is not None
    assert obj.name == "cheveux"
    assert obj.object is extractor.character(7)


def test_add_object_should_recompute_bounds():
    from prespyc.extractor.image.empty_image import EmptyImage

    swf = SwfFile(fixture("extractor", "1047", "1047.swf"))
    extractor = Extractor(swf)

    frame = extractor.character(65).timeline.frames[0]
    other = FrameObject(
        depth=10,
        object=EmptyImage(0),
        bounds=Rectangle(-500, 300, 12, 300),
        matrix=Matrix(),
    )

    new_frame = frame.add_object(other)

    assert new_frame is not frame
    assert new_frame.bounds == Rectangle(-584, 300, -772, 300)
    assert new_frame.objects[10] is other
    assert list(new_frame.objects) == sorted(new_frame.objects)


def test_compact():
    swf = SwfFile(fixture("extractor", "1047", "1047.swf"))
    extractor = Extractor(swf)

    timeline = extractor.character(61).timeline
    assert timeline.bounds == timeline.frames[0].bounds

    compact_frame = timeline.frames[0].compact()

    assert compact_frame is not timeline.frames[0]
    assert compact_frame.bounds != timeline.bounds
    assert compact_frame.bounds == Rectangle(-461, 212, -752, 67)


def test_modify_one_depth():
    swf = SwfFile(fixture("extractor", "1047", "1047.swf"))
    extractor = Extractor(swf)

    frame = extractor.character(65).timeline.frames[0]
    new_frame = frame.modify(_color_and_attach_modifier(), 1)

    assert new_frame != frame
    assert new_frame.bounds != frame.bounds
    assert new_frame.bounds == Rectangle(-636, 555, -803, 372)

    assert_svg_matches(
        new_frame.draw(SvgCanvas(new_frame.bounds)).render(),
        fixture("extractor", "1047", "frame-modify.svg"),
    )


def test_modify_no_depth():
    swf = SwfFile(fixture("extractor", "1047", "1047.swf"))
    extractor = Extractor(swf)

    frame = extractor.character(65).timeline.frames[0]
    new_frame = frame.modify(_color_and_attach_modifier(), 0)

    assert new_frame != frame
    assert new_frame.bounds == frame.bounds

    assert_svg_matches(
        new_frame.draw(SvgCanvas(new_frame.bounds)).render(),
        fixture("extractor", "1047", "frame-modify-only-frame.svg"),
    )


def test_modify_without_modification_should_return_same_instance():
    swf = SwfFile(fixture("extractor", "1047", "1047.swf"))
    extractor = Extractor(swf)

    frame = extractor.character(65).timeline.frames[0]

    assert frame.modify(BaseCharacterModifier()) is frame


def test_objects_by_name():
    swf = SwfFile(fixture("extractor", "complex_sprite.swf"))
    extractor = Extractor(swf)

    frame = extractor.character(13).timeline.frames[0]

    objects = frame.objects_by_name

    assert len(objects) == 3
    assert "bretelles" in objects
    assert "tunique" in objects
    assert "cheveux" in objects

    assert frame.objects[2] is objects["bretelles"]
    assert frame.objects[4] is objects["tunique"]
    assert frame.objects[6] is objects["cheveux"]


def test_run_actions():
    swf = SwfFile(fixture("extractor", "complex_sprite.swf"))
    extractor = Extractor(swf)

    frame = extractor.character(13).timeline.frames[0]
    state = State()
    state.variables = frame.objects_by_name

    class Gac:
        def __init__(self) -> None:
            self.called: list[tuple[object, object]] = []

        # The method name comes from the SWF bytecode, so it stays camelCase.
        def applyColor(self, element: object, color: object) -> None:
            self.called.append((element, color))

    gac = Gac()
    state.variables["GAC"] = gac

    assert frame.run(state, Processor(allow_function_call=True)) is state
    assert gac.called == [
        (frame.object_by_name("bretelles"), 2),
        (frame.object_by_name("cheveux"), 3),
        (frame.object_by_name("tunique"), 1),
    ]
