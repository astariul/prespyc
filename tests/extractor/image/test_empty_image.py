"""Port of ArakneSwf's `EmptyImageTest`."""

from __future__ import annotations

import io
from unittest.mock import Mock

from PIL import Image

from prespyc.extractor.image.empty_image import EmptyImage
from prespyc.parser.structure.record.color_transform import ColorTransform
from prespyc.parser.structure.record.image_data_type import ImageDataType
from prespyc.parser.structure.record.rectangle import Rectangle
from tests.support import assert_image_matches, fixture


class RecordingDrawer:
    """
    Minimal `Drawer`, standing in for the `SvgCanvas` the PHP test draws on.

    Only `image()` is ever called by an image character.
    """

    def __init__(self) -> None:
        self.images: list[object] = []

    def image(self, image: object) -> None:
        self.images.append(image)


def pixel(blob: bytes) -> tuple[tuple[int, int], tuple[int, int, int]]:
    """Size and single RGB pixel of a 1x1 encoded image."""
    with Image.open(io.BytesIO(blob)) as image:
        return image.size, image.convert("RGB").getpixel((0, 0))


def test_getters():
    image = EmptyImage(42)

    assert image.character_id == 42
    assert image.frames_count() == 1
    assert image.frames_count(True) == 1
    assert image.to_base64_data().startswith("data:image/png;base64,")
    assert image.bounds == Rectangle(0, 20, 0, 20)
    assert image.bounds is image.bounds
    assert image.to_best_format().type is ImageDataType.PNG
    assert image.to_best_format().data == EmptyImage.PNG_DATA


def test_to_png():
    assert_image_matches(EmptyImage(42).to_png(), fixture("extractor", "empty.png"))

    assert pixel(EmptyImage(42).to_png()) == ((1, 1), (0, 0, 0))


def test_to_jpeg():
    assert_image_matches(EmptyImage(42).to_jpeg(), fixture("extractor", "empty.jpeg"))

    assert pixel(EmptyImage(42).to_jpeg()) == ((1, 1), (0, 0, 0))


def test_transform_color():
    image = EmptyImage(42).transform_colors(ColorTransform(red_add=255))

    assert pixel(image.to_png()) == ((1, 1), (255, 0, 0))


def test_draw():
    image = EmptyImage(42)
    drawer = RecordingDrawer()

    assert image.draw(drawer) is drawer
    assert drawer.images == [image]


def test_modify():
    image = EmptyImage(42)
    new_image = EmptyImage(43)
    modifier = Mock()
    modifier.apply_on_image.return_value = new_image

    assert image.modify(modifier) is new_image
    modifier.apply_on_image.assert_called_once_with(image)
