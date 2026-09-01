"""Port of ArakneSwf's `tests/Parser/Structure/Record/ShapeWithStyleTest.php`."""

from __future__ import annotations

from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.shape.fill_style import FillStyle
from prespyc.parser.structure.record.shape.line_style import LineStyle
from prespyc.parser.structure.record.shape.shape_record import ShapeRecord
from prespyc.parser.structure.record.shape.shape_with_style import ShapeWithStyle
from tests.support import fixture, fixture_reader


def test_read():
    reader = fixture_reader(fixture("1317.swf"), 39)

    data = ShapeWithStyle.read(reader, 3)

    assert len(data.fill_styles) == 1
    assert len(data.line_styles) == 1

    assert data.fill_styles[0] == FillStyle(type=FillStyle.SOLID, color=Color(54, 109, 97, 255))
    assert data.line_styles[0] == LineStyle(width=10, color=Color(0, 0, 0, 105))

    assert len(data.shape_records) == 6
    assert all(isinstance(record, ShapeRecord) for record in data.shape_records)
