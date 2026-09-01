"""Port of ArakneSwf's `MorphLineStyle2Test`."""

from __future__ import annotations

from prespyc.parser.reader import Reader
from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.morph_shape.morph_fill_style import MorphFillStyle
from prespyc.parser.structure.record.morph_shape.morph_line_style2 import MorphLineStyle2
from tests.support import fixture, fixture_reader


def test_read_collection():
    reader = fixture_reader(fixture("parser", "morphshape.swf"), 1439)

    styles = MorphLineStyle2.read_collection(reader)

    assert len(styles) == 1
    assert styles[0] == MorphLineStyle2(
        start_width=20,
        end_width=100,
        start_cap_style=MorphLineStyle2.CAP_ROUND,
        join_style=MorphLineStyle2.JOIN_ROUND,
        no_h_scale=False,
        no_v_scale=False,
        pixel_hinting=False,
        no_close=False,
        end_cap_style=MorphLineStyle2.CAP_ROUND,
        miter_limit_factor=None,
        start_color=Color(0, 0, 0, 255),
        end_color=Color(0, 0, 255, 255),
        fill_style=None,
    )


def test_read_with_fill_style():
    reader = Reader(
        b"\x01"  # count 1
        b"\x14\x00"  # start width 20
        b"\x28\x00"  # end width 40
        b"\xa9"  # flags - start cap square, join miter, hasFill true, noHScale false, noVScale false, pixelHinting true
        b"\x02"  # flags - noClose false, end cap square
        b"\x80\x03"  # Miter limit factor 3.5
        b"\x00\x10\x20\x30\x40\x40\x30\x20\x10"  # Fill style solid
    )

    styles = MorphLineStyle2.read_collection(reader)

    assert len(styles) == 1
    assert styles[0] == MorphLineStyle2(
        start_width=20,
        end_width=40,
        start_cap_style=MorphLineStyle2.CAP_SQUARE,
        join_style=MorphLineStyle2.JOIN_MITER,
        no_h_scale=False,
        no_v_scale=False,
        pixel_hinting=True,
        no_close=False,
        end_cap_style=MorphLineStyle2.CAP_SQUARE,
        miter_limit_factor=896,  # 3.5 in float
        start_color=None,
        end_color=None,
        fill_style=MorphFillStyle(
            type=MorphFillStyle.SOLID,
            start_color=Color(16, 32, 48, 64),
            end_color=Color(64, 48, 32, 16),
        ),
    )


def test_read_collection_extended():
    reader = Reader(b"\xff\xf4\x01" + b"\x14\x00\x28\x00\x00\x00\x10\x20\x30\x40\x40\x30\x20\x10" * 500)

    styles = MorphLineStyle2.read_collection(reader)

    assert len(styles) == 500
    assert all(isinstance(style, MorphLineStyle2) for style in styles)
