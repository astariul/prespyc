"""Port of ArakneSwf's `tests/Parser/Structure/Record/LineStyleTest.php`."""

from __future__ import annotations

from prespyc.parser.reader import Reader
from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.matrix import Matrix
from prespyc.parser.structure.record.shape.fill_style import FillStyle
from prespyc.parser.structure.record.shape.line_style import LineStyle


def test_read_collection_without_alpha():
    reader = Reader(b"\x03\x01\x00\xff\xff\xff\x10\x00\x20\x30\x40\xab\x42\x00\x05\xfe")
    styles = LineStyle.read_collection(reader, 2)

    assert len(styles) == 3

    assert styles[0].width == 1
    assert styles[0].color == Color(255, 255, 255)

    assert styles[1].width == 16
    assert styles[1].color == Color(32, 48, 64)

    assert styles[2].width == 17067
    assert styles[2].color == Color(0, 5, 254)


def test_read_collection_with_alpha():
    reader = Reader(b"\x03\x01\x00\xff\xff\xff\xff\x10\x00\x20\x30\x40\x50\xab\x42\x00\x05\xfe\xa0")
    styles = LineStyle.read_collection(reader, 3)

    assert len(styles) == 3

    assert styles[0].width == 1
    assert styles[0].color == Color(255, 255, 255, 255)

    assert styles[1].width == 16
    assert styles[1].color == Color(32, 48, 64, 80)

    assert styles[2].width == 17067
    assert styles[2].color == Color(0, 5, 254, 160)


def test_read_collection_extended_size():
    reader = Reader(b"\xff\xe8\x03" + b"\x01\x00\xff\xff\xff" * 1000)
    styles = LineStyle.read_collection(reader, 2)

    assert len(styles) == 1000

    for style in styles:
        assert style.width == 1
        assert style.color == Color(255, 255, 255)


def test_read_collection_v4_with_fill_style():
    # 01 - count: 1
    # 0001 - width: 256
    # 9B - cap: 2, join: 1, hasFill: true, noHScale: false, noVScale: true, pixelHinting: true
    # 05 - no close: true, end cap: 1
    # 400500 - repeating bitmap 5
    # 00 - empty matrix
    reader = Reader(b"\x01\x00\x01\x9b\x05\x40\x05\x00\x00")
    styles = LineStyle.read_collection(reader, 4)

    assert len(styles) == 1

    assert styles[0] == LineStyle(
        width=256,
        color=None,
        start_cap_style=2,
        join_style=1,
        has_fill_flag=True,
        no_h_scale_flag=False,
        no_v_scale_flag=True,
        pixel_hinting_flag=True,
        no_close=True,
        end_cap_style=1,
        fill_type=FillStyle(
            type=FillStyle.REPEATING_BITMAP,
            bitmap_id=5,
            bitmap_matrix=Matrix(),
        ),
    )
