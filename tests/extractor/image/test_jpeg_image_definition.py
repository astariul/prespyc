"""Port of ArakneSwf's `JpegImageDefinitionTest`."""

from __future__ import annotations

import base64
from unittest.mock import Mock

from prespyc.extractor.image.jpeg_image_definition import JpegImageDefinition
from prespyc.parser.structure.record.color_transform import ColorTransform
from prespyc.parser.structure.record.image_data_type import ImageDataType
from prespyc.parser.structure.record.rectangle import Rectangle
from prespyc.parser.structure.tag.define_bits_jpeg2 import DefineBitsJPEG2Tag
from prespyc.parser.structure.tag.define_bits_jpeg3 import DefineBitsJPEG3Tag
from prespyc.swf_file import SwfFile
from tests.support import assert_image_matches, fixture


class RecordingDrawer:
    """Minimal `Drawer`, standing in for the `SvgCanvas` the PHP test draws on."""

    def __init__(self) -> None:
        self.images: list[object] = []

    def image(self, image: object) -> None:
        self.images.append(image)


def core_jpeg() -> JpegImageDefinition:
    """The opaque JPEG of `core.swf`, character 540."""
    swf = SwfFile(fixture("extractor", "core", "core.swf"))

    return JpegImageDefinition(next(tag for _, tag in swf.tags(DefineBitsJPEG2Tag.TYPE)))


def maps_jpeg(*character_ids: int) -> list[JpegImageDefinition]:
    """The JPEGs with an alpha channel of `maps/0.swf`, in file order."""
    swf = SwfFile(fixture("extractor", "maps", "0.swf"))

    return [
        JpegImageDefinition(tag) for _, tag in swf.tags(DefineBitsJPEG3Tag.TYPE) if tag.character_id in character_ids
    ]


def test_character_id():
    assert core_jpeg().character_id == 540


def test_bounds():
    image = core_jpeg()

    assert image.bounds == Rectangle(0, 12000, 0, 2020)
    assert image.bounds is image.bounds


def test_frames_count():
    image = core_jpeg()

    assert image.frames_count() == 1
    assert image.frames_count(True) == 1


def test_to_png_opaque_jpeg():
    assert_image_matches(core_jpeg().to_png(), fixture("extractor", "core", "jpeg-540.png"))


def test_to_jpeg_opaque_jpeg():
    assert_image_matches(core_jpeg().to_jpeg(), fixture("extractor", "core", "jpeg-540.png"))


def test_to_base64_data_jpeg():
    data = core_jpeg().to_base64_data()

    assert data.startswith("data:image/jpeg;base64,")
    assert_image_matches(base64.b64decode(data[23:]), fixture("extractor", "core", "jpeg-540.png"))


def test_to_best_format_jpeg():
    data = core_jpeg().to_best_format()

    assert data.type is ImageDataType.JPEG
    assert_image_matches(data.data, fixture("extractor", "core", "jpeg-540.png"))


def test_to_png_alpha_jpeg():
    images = maps_jpeg(507, 669)

    assert len(images) == 2
    assert_image_matches(images[0].to_png(), fixture("extractor", "maps", "jpeg-507.png"))
    assert_image_matches(images[1].to_png(), fixture("extractor", "maps", "jpeg-669.png"))


def test_to_base64_data_alpha_jpeg():
    data = maps_jpeg(507)[0].to_base64_data()

    assert data.startswith("data:image/png;base64,")
    assert_image_matches(base64.b64decode(data[22:]), fixture("extractor", "maps", "jpeg-507.png"))


def test_to_best_format_alpha_jpeg():
    data = maps_jpeg(507)[0].to_best_format()

    assert data.type is ImageDataType.PNG
    assert_image_matches(data.data, fixture("extractor", "maps", "jpeg-507.png"))


def test_to_jpeg_alpha_jpeg():
    images = maps_jpeg(507, 669)

    assert len(images) == 2
    assert_image_matches(images[0].to_jpeg(), fixture("extractor", "maps", "jpeg-507.jpg"))
    assert_image_matches(images[1].to_jpeg(), fixture("extractor", "maps", "jpeg-669.jpg"))
    # JPEG has no alpha channel, so the transparent parts of the PNG show their raw color.
    assert_image_matches(images[1].to_jpeg(), fixture("extractor", "maps", "jpeg-669.png"), 0.023)


def test_transform_colors():
    image = maps_jpeg(507)[0]
    transformed = image.transform_colors(ColorTransform(red_mult=0, blue_mult=0))

    assert_image_matches(transformed.to_png(), fixture("extractor", "maps", "jpeg-507-green.png"))


def test_transform_colors_cache():
    image = maps_jpeg(507)[0]
    transformed = image.transform_colors(ColorTransform(red_mult=0, blue_mult=0))

    assert_image_matches(transformed.to_png(), fixture("extractor", "maps", "jpeg-507-green.png"))

    assert image.transform_colors(ColorTransform(red_mult=0, blue_mult=0)) is transformed
    assert image.transform_colors(ColorTransform(red_mult=0, blue_mult=100)) is not transformed


def test_draw():
    image = maps_jpeg(507)[0]
    drawer = RecordingDrawer()

    assert image.draw(drawer) is drawer
    assert drawer.images[0] is image


def test_modify():
    image = maps_jpeg(507)[0]
    new_image = maps_jpeg(507)[0]
    modifier = Mock()
    modifier.apply_on_image.return_value = new_image

    assert image.modify(modifier) is new_image
    modifier.apply_on_image.assert_called_once_with(image)
