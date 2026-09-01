"""Port of `tests/Extractor/Shape/FillType/SolidTest.php`."""

from __future__ import annotations

from prespyc.extractor.shape.fill_type.solid import Solid
from prespyc.parser.structure.record.color import Color


def test_interpolate():
    start = Solid(Color(42, 112, 205, 5))
    end = Solid(Color(202, 50, 100))

    assert start.interpolate(end, 0) == Solid(Color(42, 112, 205, 5))
    assert start.interpolate(end, 32768) == Solid(Color(122, 80, 152, 130))
    assert start.interpolate(end, 65535) == Solid(Color(202, 50, 100, 255))
