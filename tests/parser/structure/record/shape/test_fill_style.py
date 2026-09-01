"""Port of ArakneSwf's `tests/Parser/Structure/Record/FillStyleTest.php`."""

from __future__ import annotations

import pytest

from prespyc.errors import InvalidDataError
from prespyc.parser.reader import Reader
from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.gradient import Gradient
from prespyc.parser.structure.record.gradient_record import GradientRecord
from prespyc.parser.structure.record.matrix import Matrix
from prespyc.parser.structure.record.shape.fill_style import FillStyle


def test_read_solid():
    reader = Reader(b"\x00\x10\x20\x30")
    assert FillStyle.read(reader, 1) == FillStyle(type=FillStyle.SOLID, color=Color(16, 32, 48))

    reader = Reader(b"\x00\x10\x20\x30\x40")
    assert FillStyle.read(reader, 3) == FillStyle(type=FillStyle.SOLID, color=Color(16, 32, 48, 64))


def test_read_linear_gradient():
    # 10 - linear gradient
    # 00 - empty matrix
    # 93 - spread mode: 2, interpolation mode: 1, 3 records
    # 00000000 - first record: ratio 0, color black
    # 80FF0000 - second record: ratio 128, color red
    # FF00FF00 - third record: ratio 255, color green
    reader = Reader(b"\x10\x00\x93\x00\x00\x00\x00\x80\xff\x00\x00\xff\x00\xff\x00")
    style = FillStyle.read(reader, 1)

    assert style.type == FillStyle.LINEAR_GRADIENT
    assert style.color is None
    assert style.bitmap_id is None
    assert style.bitmap_matrix is None
    assert style.focal_gradient is None
    assert style.gradient == Gradient(
        spread_mode=Gradient.SPREAD_MODE_REPEAT,
        interpolation_mode=Gradient.INTERPOLATION_MODE_LINEAR,
        records=[
            GradientRecord(0, Color(0, 0, 0)),
            GradientRecord(128, Color(255, 0, 0)),
            GradientRecord(255, Color(0, 255, 0)),
        ],
    )

    reader = Reader(b"\x10\x00\x93\x00\x00\x00\x00\x42\x80\xff\x00\x00\xff\xff\x00\xff\x00\xab")
    style = FillStyle.read(reader, 3)

    assert style.type == FillStyle.LINEAR_GRADIENT
    assert style.color is None
    assert style.bitmap_id is None
    assert style.bitmap_matrix is None
    assert style.focal_gradient is None
    assert style.gradient == Gradient(
        spread_mode=Gradient.SPREAD_MODE_REPEAT,
        interpolation_mode=Gradient.INTERPOLATION_MODE_LINEAR,
        records=[
            GradientRecord(0, Color(0, 0, 0, 66)),
            GradientRecord(128, Color(255, 0, 0, 255)),
            GradientRecord(255, Color(0, 255, 0, 171)),
        ],
    )


def test_read_radial_gradient():
    # 12 - radial gradient
    # 00 - empty matrix
    # 93 - spread mode: 2, interpolation mode: 1, 3 records
    # 00000000 - first record: ratio 0, color black
    # 80FF0000 - second record: ratio 128, color red
    # FF00FF00 - third record: ratio 255, color green
    reader = Reader(b"\x12\x00\x93\x00\x00\x00\x00\x80\xff\x00\x00\xff\x00\xff\x00")
    style = FillStyle.read(reader, 1)

    assert style.type == FillStyle.RADIAL_GRADIENT
    assert style.color is None
    assert style.bitmap_id is None
    assert style.bitmap_matrix is None
    assert style.focal_gradient is None
    assert style.gradient == Gradient(
        spread_mode=Gradient.SPREAD_MODE_REPEAT,
        interpolation_mode=Gradient.INTERPOLATION_MODE_LINEAR,
        records=[
            GradientRecord(0, Color(0, 0, 0)),
            GradientRecord(128, Color(255, 0, 0)),
            GradientRecord(255, Color(0, 255, 0)),
        ],
    )

    reader = Reader(b"\x12\x00\x93\x00\x00\x00\x00\x42\x80\xff\x00\x00\xff\xff\x00\xff\x00\xab")
    style = FillStyle.read(reader, 3)

    assert style.type == FillStyle.RADIAL_GRADIENT
    assert style.color is None
    assert style.bitmap_id is None
    assert style.bitmap_matrix is None
    assert style.focal_gradient is None
    assert style.gradient == Gradient(
        spread_mode=Gradient.SPREAD_MODE_REPEAT,
        interpolation_mode=Gradient.INTERPOLATION_MODE_LINEAR,
        records=[
            GradientRecord(0, Color(0, 0, 0, 66)),
            GradientRecord(128, Color(255, 0, 0, 255)),
            GradientRecord(255, Color(0, 255, 0, 171)),
        ],
    )


def test_read_focal_gradient():
    # 13 - focal gradient
    # 00 - empty matrix
    # 93 - spread mode: 2, interpolation mode: 1, 3 records
    # 0000000042 - first record: ratio 0, color black 66 alpha
    # 80FF0000FF - second record: ratio 128, color red 255 alpha
    # FF00FF00AB - third record: ratio 255, color green 171 alpha
    # 8007 - focal point 7.5
    reader = Reader(b"\x13\x00\x93\x00\x00\x00\x00\x42\x80\xff\x00\x00\xff\xff\x00\xff\x00\xab\x80\x07")
    style = FillStyle.read(reader, 3)

    assert style.type == FillStyle.FOCAL_GRADIENT
    assert style.color is None
    assert style.bitmap_id is None
    assert style.bitmap_matrix is None
    assert style.gradient is None
    assert style.focal_gradient == Gradient(
        spread_mode=Gradient.SPREAD_MODE_REPEAT,
        interpolation_mode=Gradient.INTERPOLATION_MODE_LINEAR,
        records=[
            GradientRecord(0, Color(0, 0, 0, 66)),
            GradientRecord(128, Color(255, 0, 0, 255)),
            GradientRecord(255, Color(0, 255, 0, 171)),
        ],
        focal_point=7.5,
    )


@pytest.mark.parametrize(
    ("data", "expected_type"),
    [
        (b"\x40\x05\x00\x00", FillStyle.REPEATING_BITMAP),
        (b"\x41\x05\x00\x00", FillStyle.CLIPPED_BITMAP),
        (b"\x42\x05\x00\x00", FillStyle.NON_SMOOTHED_REPEATING_BITMAP),
        (b"\x43\x05\x00\x00", FillStyle.NON_SMOOTHED_CLIPPED_BITMAP),
    ],
)
def test_read_bitmap(data, expected_type):
    assert FillStyle.read(Reader(data), 1) == FillStyle(type=expected_type, bitmap_id=5, bitmap_matrix=Matrix())


def test_read_unsupported_full_style():
    with pytest.raises(InvalidDataError, match="Unsupported FillStyle type 1"):
        FillStyle.read(Reader(b"\x01"), 1)


def test_read_unsupported_full_style_ignore_error():
    assert FillStyle.read(Reader(b"\x01", errors=0), 1) == FillStyle(type=1)
