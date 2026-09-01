"""Port of ArakneSwf's `MorphFillStyleTest`."""

from __future__ import annotations

import pytest

from prespyc.errors import Errors, InvalidDataError
from prespyc.parser.reader import Reader
from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.matrix import Matrix
from prespyc.parser.structure.record.morph_shape.morph_fill_style import MorphFillStyle
from prespyc.parser.structure.record.morph_shape.morph_gradient import MorphGradient
from prespyc.parser.structure.record.morph_shape.morph_gradient_record import MorphGradientRecord
from tests.support import fixture, fixture_reader

GRADIENT_BODY = (
    b"\x00"  # Start gradient matrix (empty)
    b"\x08\x48"  # End gradient matrix translate (2, 4)
    b"\x43"  # Gradients flags : 0b0100_0011 - spread 1, interpolation 0, 3 records
    b"\x00\xff\x00\x00\xff\x00\xff\x00\x00\x00"  # Record 1
    b"\x80\x00\xff\x00\xff\x40\x00\xff\x00\x00"  # Record 2
    b"\xff\x00\x00\xff\xff\x80\x00\x00\xff\x00"  # Record 3
)

GRADIENT_RECORDS = [
    MorphGradientRecord(
        start_ratio=0,
        start_color=Color(255, 0, 0, 255),
        end_ratio=0,
        end_color=Color(255, 0, 0, 0),
    ),
    MorphGradientRecord(
        start_ratio=128,
        start_color=Color(0, 255, 0, 255),
        end_ratio=64,
        end_color=Color(0, 255, 0, 0),
    ),
    MorphGradientRecord(
        start_ratio=255,
        start_color=Color(0, 0, 255, 255),
        end_ratio=128,
        end_color=Color(0, 0, 255, 0),
    ),
]

BITMAP_BODY = (
    b"\x02\x01"  # Bitmap ID (258)
    b"\x00"  # Start matrix (empty)
    b"\x08\x48"  # End matrix translate (2, 4)
)


def test_read_collection():
    reader = fixture_reader(fixture("parser", "morphshape.swf"), 1429)

    styles = MorphFillStyle.read_collection(reader)

    assert len(styles) == 1
    assert styles[0] == MorphFillStyle(
        type=MorphFillStyle.SOLID,
        start_color=Color(255, 0, 0, 255),
        end_color=Color(0, 255, 0, 255),
    )


def test_read_collection_extended():
    reader = Reader(b"\xff\xf4\x01" + b"\x00\x10\x20\x30\x40\x40\x30\x20\x10" * 500)
    styles = MorphFillStyle.read_collection(reader)

    assert len(styles) == 500
    assert all(isinstance(style, MorphFillStyle) for style in styles)


def test_read_solid():
    reader = Reader(b"\x00\x10\x20\x30\x40\x40\x30\x20\x10")
    style = MorphFillStyle.read(reader)

    assert style == MorphFillStyle(
        type=MorphFillStyle.SOLID,
        start_color=Color(16, 32, 48, 64),
        end_color=Color(64, 48, 32, 16),
    )


@pytest.mark.parametrize(
    ("type_byte", "expected_type"),
    [
        (b"\x10", MorphFillStyle.LINEAR_GRADIENT),
        (b"\x12", MorphFillStyle.RADIAL_GRADIENT),
    ],
)
def test_read_gradient(type_byte, expected_type):
    reader = Reader(type_byte + GRADIENT_BODY)
    style = MorphFillStyle.read(reader)

    assert style == MorphFillStyle(
        type=expected_type,
        start_gradient_matrix=Matrix(),
        end_gradient_matrix=Matrix(translate_x=2, translate_y=4),
        gradient=MorphGradient(
            spread_mode=MorphGradient.SPREAD_MODE_REFLECT,
            interpolation_mode=MorphGradient.INTERPOLATION_MODE_NORMAL,
            records=GRADIENT_RECORDS,
        ),
    )


def test_read_focal_gradient():
    reader = Reader(b"\x13" + GRADIENT_BODY + b"\x40\x03")  # Type, gradient, focal point
    style = MorphFillStyle.read(reader)

    assert style == MorphFillStyle(
        type=MorphFillStyle.FOCAL_RADIAL_GRADIENT,
        start_gradient_matrix=Matrix(),
        end_gradient_matrix=Matrix(translate_x=2, translate_y=4),
        gradient=MorphGradient(
            spread_mode=MorphGradient.SPREAD_MODE_REFLECT,
            interpolation_mode=MorphGradient.INTERPOLATION_MODE_NORMAL,
            records=GRADIENT_RECORDS,
            focal_point=3.25,
        ),
    )


@pytest.mark.parametrize(
    ("type_byte", "expected_type"),
    [
        (b"\x40", MorphFillStyle.REPEATING_BITMAP),
        (b"\x41", MorphFillStyle.CLIPPED_BITMAP),
        (b"\x42", MorphFillStyle.NON_SMOOTHED_REPEATING_BITMAP),
        (b"\x43", MorphFillStyle.NON_SMOOTHED_CLIPPED_BITMAP),
    ],
)
def test_read_bitmap(type_byte, expected_type):
    reader = Reader(type_byte + BITMAP_BODY)
    style = MorphFillStyle.read(reader)

    assert style == MorphFillStyle(
        type=expected_type,
        bitmap_id=258,
        start_bitmap_matrix=Matrix(),
        end_bitmap_matrix=Matrix(translate_x=2, translate_y=4),
    )


def test_read_unsupported_type():
    reader = Reader(b"\x01")

    with pytest.raises(InvalidDataError, match="Unknown MorphFillStyle type: 1"):
        MorphFillStyle.read(reader)


def test_read_unsupported_type_ignore_error():
    reader = Reader(b"\x01", errors=Errors.NONE)

    assert MorphFillStyle.read(reader) == MorphFillStyle(type=1)
