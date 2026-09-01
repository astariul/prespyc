"""Port of ArakneSwf's `tests/Parser/Structure/Record/ColorTest.php`."""

from __future__ import annotations

from prespyc.parser.reader import Reader
from prespyc.parser.structure.record.color import Color


def test_read_rgb():
    reader = Reader(b"\x12\x34\x56")
    color = Color.read_rgb(reader)

    assert color.red == 18
    assert color.green == 52
    assert color.blue == 86
    assert color.alpha is None


def test_read_rgba():
    reader = Reader(b"\x12\x34\x56\x78")
    color = Color.read_rgba(reader)

    assert color.red == 18
    assert color.green == 52
    assert color.blue == 86
    assert color.alpha == 120
