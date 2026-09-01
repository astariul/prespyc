"""Port of ArakneSwf's `TransformedImageTest`."""

from __future__ import annotations

import base64
from unittest.mock import Mock

import pytest

from prespyc.extractor.image.transformed_image import TransformedImage
from prespyc.parser.structure.record.color_transform import ColorTransform
from prespyc.parser.structure.record.image_data_type import ImageDataType
from prespyc.parser.structure.record.rectangle import Rectangle
from tests.support import assert_image_matches, fixture

BASE_IMAGE_PNG = ("extractor", "g2", "bits-283.png")
BASE_IMAGE_WIDTH = 800
BASE_IMAGE_HEIGHT = 600
BASE_BOUNDS = Rectangle(0, BASE_IMAGE_WIDTH, 0, BASE_IMAGE_HEIGHT)


class RecordingDrawer:
    """Minimal `Drawer`, standing in for the `SvgCanvas` the PHP test draws on."""

    def __init__(self) -> None:
        self.images: list[object] = []

    def image(self, image: object) -> None:
        self.images.append(image)


def base_image(color_transform: ColorTransform) -> TransformedImage:
    return TransformedImage.from_png(1, BASE_BOUNDS, color_transform, fixture(*BASE_IMAGE_PNG).read_bytes())


@pytest.mark.parametrize(
    ("color_transform", "expected"),
    [
        (ColorTransform(), "bits-283.png"),
        (ColorTransform(red_mult=0), "bits-283-no-red.png"),
        (ColorTransform(green_mult=0), "bits-283-no-green.png"),
        (ColorTransform(blue_mult=0), "bits-283-no-blue.png"),
        (ColorTransform(alpha_mult=128), "bits-283-alpha50.png"),
        (ColorTransform(alpha_mult=64), "bits-283-alpha25.png"),
        (ColorTransform(alpha_mult=192), "bits-283-alpha75.png"),
        (ColorTransform(red_mult=128, green_mult=128, blue_mult=128), "bits-283-darken50.png"),
        (
            ColorTransform(
                red_mult=200,
                green_mult=75,
                blue_mult=256,
                red_add=50,
                green_add=-50,
                blue_add=100,
            ),
            "bits-283-complex-matrix.png",
        ),
    ],
)
def test_from_png(color_transform: ColorTransform, expected: str):
    image = base_image(color_transform)

    assert_image_matches(image.to_png(), fixture("extractor", "g2", expected))
    assert image.character_id == 1
    assert image.bounds == BASE_BOUNDS
    assert image.frames_count() == 1
    assert image.frames_count(True) == 1


def test_from_png_transparent_pixel_should_be_ignored():
    image = TransformedImage.from_png(
        1,
        Rectangle(0, 173, 0, 83),
        ColorTransform(
            red_mult=64,
            green_mult=128,
            blue_mult=192,
            alpha_mult=256,
            red_add=50,
            green_add=-50,
            blue_add=100,
            alpha_add=75,
        ),
        fixture("extractor", "g2", "20.png").read_bytes(),
    )

    assert_image_matches(image.to_png(), fixture("extractor", "g2", "20-transformed.png"))
    assert image.character_id == 1
    assert image.bounds == Rectangle(0, 173, 0, 83)
    assert image.frames_count() == 1
    assert image.frames_count(True) == 1


@pytest.mark.parametrize(
    ("color_transform", "expected"),
    [
        (ColorTransform(), "jpeg-525.jpg"),
        (ColorTransform(red_mult=0), "jpeg-525-no-red.png"),
        (ColorTransform(alpha_mult=128), "jpeg-525-alpha50.png"),
    ],
)
def test_from_jpeg(color_transform: ColorTransform, expected: str):
    image = TransformedImage.from_jpeg(
        1,
        Rectangle(0, 600, 0, 345),
        color_transform,
        fixture("extractor", "maps", "jpeg-525.jpg").read_bytes(),
    )

    assert_image_matches(image.to_png(), fixture("extractor", "maps", expected))
    assert image.character_id == 1
    assert image.bounds == Rectangle(0, 600, 0, 345)


def test_to_base64_data():
    image = base_image(ColorTransform(red_mult=0))

    assert image.to_base64_data().startswith("data:image/png;base64,")
    assert_image_matches(
        base64.b64decode(image.to_base64_data()[22:]),
        fixture("extractor", "g2", "bits-283-no-red.png"),
    )


def test_to_best_format():
    data = base_image(ColorTransform(red_mult=0)).to_best_format()

    assert data.type is ImageDataType.PNG
    assert_image_matches(data.data, fixture("extractor", "g2", "bits-283-no-red.png"))


def test_to_jpeg():
    image = base_image(ColorTransform(red_mult=0))

    # A JPEG re-encode of the transformed pixels, compared against the lossless golden.
    assert_image_matches(image.to_jpeg(100), fixture("extractor", "g2", "bits-283-no-red.png"), 0.0021)


def test_transform_colors():
    transformed = base_image(ColorTransform(red_mult=0)).transform_colors(ColorTransform(alpha_mult=128))

    assert_image_matches(transformed.to_png(), fixture("extractor", "g2", "bits-283-no-red-alpha50.png"))


def test_draw():
    image = base_image(ColorTransform(red_mult=0))
    drawer = RecordingDrawer()

    assert image.draw(drawer) is drawer
    assert drawer.images[0] is image


def test_modify():
    image = base_image(ColorTransform(red_mult=0))
    new_image = base_image(ColorTransform(red_mult=0))
    modifier = Mock()
    modifier.apply_on_image.return_value = new_image

    assert image.modify(modifier) is new_image
    modifier.apply_on_image.assert_called_once_with(image)
