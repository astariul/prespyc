"""Port of ArakneSwf's `ImageBitsDefinitionTest`."""

from __future__ import annotations

import base64
from unittest.mock import Mock

from prespyc.extractor.image.image_bits_definition import ImageBitsDefinition
from prespyc.parser.structure.record.color_transform import ColorTransform
from prespyc.parser.structure.record.image_data_type import ImageDataType
from prespyc.parser.structure.record.rectangle import Rectangle
from prespyc.parser.structure.tag.define_bits import DefineBitsTag
from prespyc.parser.structure.tag.jpeg_tables import JPEGTablesTag
from prespyc.swf_file import SwfFile
from tests.support import assert_image_matches, fixture


class RecordingDrawer:
    """Minimal `Drawer`, standing in for the `SvgCanvas` the PHP test draws on."""

    def __init__(self) -> None:
        self.images: list[object] = []

    def image(self, image: object) -> None:
        self.images.append(image)


def all_images() -> list[ImageBitsDefinition]:
    """Every `DefineBits` image of `g2.swf`, sharing its single `JPEGTables` tag."""
    swf = SwfFile(fixture("extractor", "g2", "g2.swf"))
    jpeg_tables = next(tag for _, tag in swf.tags(JPEGTablesTag.TYPE))

    return [ImageBitsDefinition(tag, jpeg_tables) for _, tag in swf.tags(DefineBitsTag.TYPE)]


def first_image() -> ImageBitsDefinition:
    return all_images()[0]


def test_character_id():
    assert first_image().character_id == 244


def test_bounds():
    image = first_image()

    assert image.bounds == Rectangle(0, 15200, 0, 9100)
    assert image.bounds is image.bounds


def test_frames_count():
    image = first_image()

    assert image.frames_count() == 1
    assert image.frames_count(True) == 1


def test_to_png():
    for image in all_images():
        assert_image_matches(image.to_png(), fixture("extractor", "g2", f"bits-{image.character_id}.png"))


def test_to_base64_data():
    for image in all_images():
        data = image.to_base64_data()

        assert data.startswith("data:image/jpeg;base64,")
        assert_image_matches(
            base64.b64decode(data[23:]),
            fixture("extractor", "g2", f"bits-{image.character_id}.png"),
        )


def test_to_best_format():
    for image in all_images():
        data = image.to_best_format()

        assert data.type is ImageDataType.JPEG
        assert_image_matches(data.data, fixture("extractor", "g2", f"bits-{image.character_id}.png"))


def test_to_jpeg():
    for image in all_images():
        assert_image_matches(image.to_jpeg(), fixture("extractor", "g2", f"bits-{image.character_id}.png"))


def test_transform_colors():
    image = first_image()
    transformed = image.transform_colors(ColorTransform(green_mult=0, blue_mult=0))

    assert transformed.bounds is image.bounds
    assert transformed.character_id == image.character_id
    assert_image_matches(transformed.to_png(), fixture("extractor", "g2", "bits-244-red.png"))


def test_draw():
    for image in all_images():
        drawer = RecordingDrawer()

        assert image.draw(drawer) is drawer
        assert drawer.images[0] is image


def test_modify():
    image = first_image()
    new_image = first_image()
    modifier = Mock()
    modifier.apply_on_image.return_value = new_image

    assert image.modify(modifier) is new_image
    modifier.apply_on_image.assert_called_once_with(image)
