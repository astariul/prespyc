"""Port of ArakneSwf's `LosslessImageDefinitionTest`."""

from __future__ import annotations

import base64
from unittest.mock import Mock

from prespyc.extractor.image.lossless_image_definition import LosslessImageDefinition
from prespyc.parser.structure.record.color_transform import ColorTransform
from prespyc.parser.structure.record.image_bitmap_type import ImageBitmapType
from prespyc.parser.structure.record.image_data_type import ImageDataType
from prespyc.parser.structure.record.rectangle import Rectangle
from prespyc.parser.structure.tag.define_bits_lossless import DefineBitsLosslessTag
from prespyc.swf_file import SwfFile
from tests.support import assert_image_matches, fixture


class RecordingDrawer:
    """Minimal `Drawer`, standing in for the `SvgCanvas` the PHP test draws on."""

    def __init__(self) -> None:
        self.images: list[object] = []

    def image(self, image: object) -> None:
        self.images.append(image)


def lossless_tags(*path: str, version: int) -> list[DefineBitsLosslessTag]:
    tag_type = DefineBitsLosslessTag.TYPE_V1 if version == 1 else DefineBitsLosslessTag.TYPE_V2

    return [tag for _, tag in SwfFile(fixture(*path)).tags(tag_type)]


def maps_24bits() -> LosslessImageDefinition:
    return LosslessImageDefinition(lossless_tags("extractor", "maps", "0.swf", version=1)[0])


def maps_32bits() -> LosslessImageDefinition:
    tags = lossless_tags("extractor", "maps", "0.swf", version=2)

    return LosslessImageDefinition(next(tag for tag in tags if tag.character_id == 654))


def homestuck_8bits(version: int, bitmap_type: ImageBitmapType) -> list[LosslessImageDefinition]:
    tags = lossless_tags("extractor", "homestuck", "00004.swf", version=version)

    return [LosslessImageDefinition(tag) for tag in tags if tag.type is bitmap_type]


def test_character_id():
    assert maps_24bits().character_id == 534


def test_bounds():
    image = maps_24bits()

    assert image.bounds == Rectangle(0, 12000, 0, 6900)
    assert image.bounds is image.bounds


def test_frames_count():
    image = maps_24bits()

    assert image.frames_count() == 1
    assert image.frames_count(True) == 1


def test_to_png_full_color_without_alpha():
    assert_image_matches(maps_24bits().to_png(), fixture("extractor", "maps", "lossless-24bits.png"))


def test_to_jpeg_full_color_without_alpha():
    image = maps_24bits()

    assert_image_matches(image.to_jpeg(100), fixture("extractor", "maps", "lossless-24bits.jpg"))
    # A JPEG re-encode of the same pixels, so a handful of channels are one step off.
    assert_image_matches(image.to_jpeg(100), fixture("extractor", "maps", "lossless-24bits.png"), 0.0001)


def test_to_png_full_color_with_alpha():
    assert_image_matches(maps_32bits().to_png(), fixture("extractor", "maps", "lossless-32bits.png"))


def test_to_jpeg_full_color_with_alpha():
    image = maps_32bits()

    assert_image_matches(image.to_jpeg(100), fixture("extractor", "maps", "lossless-32bits.jpg"))
    # JPEG has no alpha channel, so the transparent parts of the PNG show their raw color.
    assert_image_matches(image.to_jpeg(100), fixture("extractor", "maps", "lossless-32bits.png"), 0.019)


def test_to_png_8bits_without_alpha():
    images = homestuck_8bits(1, ImageBitmapType.OPAQUE_8BIT)
    assert images

    for image in images:
        golden = fixture("extractor", "homestuck", f"lossless-8bits-opaque-{image.character_id}.png")
        assert_image_matches(image.to_png(), golden)


def test_to_jpeg_8bits_without_alpha():
    images = homestuck_8bits(1, ImageBitmapType.OPAQUE_8BIT)
    assert images

    for image in images:
        name = f"lossless-8bits-opaque-{image.character_id}"
        assert_image_matches(image.to_jpeg(100), fixture("extractor", "homestuck", f"{name}.jpg"))
        # JPEG re-encode of a palette image: the flat color areas ring a little.
        assert_image_matches(image.to_jpeg(100), fixture("extractor", "homestuck", f"{name}.png"), 0.0041)


def test_to_png_8bits_with_alpha():
    images = homestuck_8bits(2, ImageBitmapType.TRANSPARENT_8BIT)
    assert images

    for image in images:
        golden = fixture("extractor", "homestuck", f"lossless-8bits-alpha-{image.character_id}.png")
        assert_image_matches(image.to_png(), golden)


def test_to_jpeg_8bits_with_alpha():
    images = homestuck_8bits(2, ImageBitmapType.TRANSPARENT_8BIT)
    assert images

    for image in images:
        golden = fixture("extractor", "homestuck", f"lossless-8bits-alpha-{image.character_id}.png")
        # These images are mostly transparent, and JPEG drops the alpha channel.
        assert_image_matches(image.to_jpeg(100), golden, 0.19)


def test_to_base64_data():
    data = maps_32bits().to_base64_data()

    assert data.startswith("data:image/png;base64,")
    assert_image_matches(base64.b64decode(data[22:]), fixture("extractor", "maps", "lossless-32bits.png"))


def test_to_best_format():
    data = maps_32bits().to_best_format()

    assert data.type is ImageDataType.PNG
    assert_image_matches(data.data, fixture("extractor", "maps", "lossless-32bits.png"))


def test_transform_colors():
    transformed = maps_32bits().transform_colors(ColorTransform(red_mult=0, green_mult=0))

    assert_image_matches(transformed.to_png(), fixture("extractor", "maps", "lossless-32bits-blue.png"))


def test_draw():
    image = maps_32bits()
    drawer = RecordingDrawer()

    assert image.draw(drawer) is drawer
    assert drawer.images[0] is image


def test_modify():
    image = maps_32bits()
    new_image = maps_32bits()
    modifier = Mock()
    modifier.apply_on_image.return_value = new_image

    assert image.modify(modifier) is new_image
    modifier.apply_on_image.assert_called_once_with(image)
