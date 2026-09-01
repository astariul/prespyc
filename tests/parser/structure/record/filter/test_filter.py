"""Tests for the graphic filter records."""

from __future__ import annotations

import pytest

from prespyc.errors import Errors, InvalidDataError
from prespyc.parser.reader import Reader
from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.filter.bevel_filter import BevelFilter
from prespyc.parser.structure.record.filter.blur_filter import BlurFilter
from prespyc.parser.structure.record.filter.color_matrix_filter import ColorMatrixFilter
from prespyc.parser.structure.record.filter.convolution_filter import ConvolutionFilter
from prespyc.parser.structure.record.filter.drop_shadow_filter import DropShadowFilter
from prespyc.parser.structure.record.filter.filter import Filter
from prespyc.parser.structure.record.filter.glow_filter import GlowFilter
from prespyc.parser.structure.record.filter.gradient_bevel_filter import GradientBevelFilter
from prespyc.parser.structure.record.filter.gradient_glow_filter import GradientGlowFilter
from tests.support import fixture, fixture_reader

DROP_SHADOW = b"\x00\x10\x20\x30\x40\x00\x80\x02\x00\x00\x40\x10\x00\x00\x00\xd0\x00\x00\x00\x02\x00\x80\x00\x43"
BLUR = b"\x01\x00\x80\x04\x00\x00\x00\x05\x00\xa0"
GLOW = b"\x02\x10\x20\x30\x40\x00\x80\x02\x00\x00\x40\x10\x00\x80\x00\x43"


def test_read_drop_shadow():
    reader = Reader(b"\x01" + DROP_SHADOW)
    filters = Filter.read_collection(reader)
    assert len(filters) == 1

    assert filters[0] == DropShadowFilter(
        drop_shadow_color=Color(16, 32, 48, 64),
        blur_x=2.5,
        blur_y=16.25,
        angle=208.0,
        distance=2.0,
        strength=0.5,
        inner_shadow=False,
        knockout=True,
        composite_source=False,
        passes=3,
    )


def test_read_blur():
    reader = Reader(b"\x01" + BLUR)
    filters = Filter.read_collection(reader)
    assert len(filters) == 1

    assert filters[0] == BlurFilter(blur_x=4.5, blur_y=5.0, passes=20)


def test_read_glow():
    reader = Reader(b"\x01" + GLOW)
    filters = Filter.read_collection(reader)
    assert len(filters) == 1

    assert filters[0] == GlowFilter(
        glow_color=Color(16, 32, 48, 64),
        blur_x=2.5,
        blur_y=16.25,
        strength=0.5,
        inner_glow=False,
        knockout=True,
        composite_source=False,
        passes=3,
    )


def test_read_bevel():
    reader = fixture_reader(fixture("extractor", "core", "core.swf"), 530012)

    filters = Filter.read_collection(reader)
    assert len(filters) == 1
    assert filters[0] == BevelFilter(
        highlight_color=Color(255, 255, 255, 255),
        shadow_color=Color(0, 0, 0, 255),
        blur_x=5.0,
        blur_y=5.0,
        angle=0.7853851318359375,
        distance=1.0,
        strength=1.0,
        inner_shadow=True,
        knockout=False,
        composite_source=True,
        on_top=False,
        passes=1,
    )


def test_read_gradient_glow():
    reader = fixture_reader(fixture("parser", "graphics.swf"), 107225)

    filters = Filter.read_collection(reader)

    assert len(filters) == 1
    assert filters[0] == GradientGlowFilter(
        num_colors=4,
        gradient_colors=[
            Color(255, 0, 0, 0),
            Color(0, 0, 255, 118),
            Color(255, 255, 0, 187),
            Color(255, 0, 255, 255),
        ],
        gradient_ratio=[0, 64, 191, 255],
        blur_x=5.0,
        blur_y=5.0,
        angle=0.7853851318359375,
        distance=5.0,
        strength=1.0,
        inner_shadow=False,
        knockout=False,
        composite_source=True,
        on_top=False,
        passes=1,
    )


def test_read_convolution():
    reader = Reader(
        b"\x01\x05\x03\x04\x00\x00\x20\x40\x00\x00\x40\x40\xcd\xcc\x8c\x3f\x33\x33\x13\x40\x00\x00\x60\x40"
        b"\x66\x66\x96\x40\xcd\xcc\xbc\x40\x33\x33\xc3\x40\x66\x66\xe6\x40\x66\x66\x06\x41\x9a\x99\x19\x41"
        b"\xcd\xcc\x2c\x41\x00\x00\x30\x41\x33\x33\x43\x41\x0c\x22\x38\x4e\x01"
    )
    filters = Filter.read_collection(reader)

    expected = ConvolutionFilter(
        matrix_x=3,
        matrix_y=4,
        divisor=2.5,
        bias=3.0,
        matrix=[
            1.1,
            2.3,
            3.5,
            4.7,
            5.9,
            6.1,
            7.2,
            8.4,
            9.6,
            10.8,
            11.0,
            12.2,
        ],
        default_color=Color(12, 34, 56, 78),
        clamp=False,
        preserve_alpha=True,
    )

    assert len(filters) == 1
    actual = filters[0]
    assert actual.matrix_x == expected.matrix_x
    assert actual.matrix_y == expected.matrix_y
    assert actual.divisor == pytest.approx(expected.divisor, abs=0.00001)
    assert actual.bias == pytest.approx(expected.bias, abs=0.00001)
    assert actual.matrix == pytest.approx(expected.matrix, abs=0.00001)
    assert actual.default_color == expected.default_color
    assert actual.clamp == expected.clamp
    assert actual.preserve_alpha == expected.preserve_alpha


def test_read_color_matrix():
    reader = fixture_reader(fixture("parser", "graphics.swf"), 107124)

    filters = Filter.read_collection(reader)

    assert len(filters) == 1
    assert isinstance(filters[0], ColorMatrixFilter)
    assert filters[0].matrix == pytest.approx(
        [
            -1.3619517,
            -0.9858965,
            4.0578485,
            0.0,
            6.2150044,
            0.8791733,
            1.871353,
            -1.0405262,
            0.0,
            6.215005,
            -3.036176,
            5.034479,
            -0.2883033,
            0.0,
            6.2150035,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
        ],
        abs=0.00001,
    )


def test_read_gradient_bevel():
    reader = fixture_reader(fixture("parser", "graphics.swf"), 106553)

    filters = Filter.read_collection(reader)

    assert len(filters) == 1
    assert filters[0] == GradientBevelFilter(
        num_colors=5,
        gradient_colors=[
            Color(255, 0, 0, 255),
            Color(0, 255, 255, 140),
            Color(0, 0, 255, 0),
            Color(255, 255, 0, 78),
            Color(255, 0, 255, 255),
        ],
        gradient_ratio=[0, 64, 128, 191, 255],
        blur_x=5.0,
        blur_y=5.0,
        angle=0.7853851318359375,
        distance=5.0,
        strength=1.0,
        inner_shadow=True,
        knockout=False,
        composite_source=True,
        on_top=False,
        passes=1,
    )


def test_read_collection():
    reader = Reader(b"\x03" + DROP_SHADOW + BLUR + GLOW)

    filters = Filter.read_collection(reader)

    assert len(filters) == 3
    assert isinstance(filters[0], DropShadowFilter)
    assert isinstance(filters[1], BlurFilter)
    assert isinstance(filters[2], GlowFilter)


def test_read_collection_unknown_filter():
    reader = Reader(b"\x03" + DROP_SHADOW + b"\xff" + GLOW)

    with pytest.raises(InvalidDataError, match="Unknown filter type 255"):
        Filter.read_collection(reader)


def test_read_collection_unknown_filter_ignore_error():
    reader = Reader(b"\x03" + DROP_SHADOW + b"\xff" + GLOW, errors=Errors.NONE)

    filters = Filter.read_collection(reader)

    assert len(filters) == 2
    assert isinstance(filters[0], DropShadowFilter)
    assert isinstance(filters[1], GlowFilter)
