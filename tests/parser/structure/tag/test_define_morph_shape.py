"""Port of ArakneSwf's DefineMorphShapeTagTest."""

from __future__ import annotations

from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.morph_shape.morph_fill_style import MorphFillStyle
from prespyc.parser.structure.record.morph_shape.morph_line_style import MorphLineStyle
from prespyc.parser.structure.record.rectangle import Rectangle
from prespyc.parser.structure.record.shape.shape_record import ShapeRecord
from prespyc.parser.structure.tag.define_morph_shape import DefineMorphShapeTag
from tests.support import fixture, fixture_reader


def test_read():
    reader = fixture_reader(fixture("extractor", "core", "core.swf"), 1287509)

    tag = DefineMorphShapeTag.read(reader)

    assert tag.character_id == 571
    assert tag.start_bounds == Rectangle(xmin=-464, xmax=99, ymin=-348, ymax=389)
    assert tag.end_bounds == Rectangle(xmin=-664, xmax=-101, ymin=-348, ymax=389)

    assert tag.fill_styles == [
        MorphFillStyle(
            type=MorphFillStyle.SOLID,
            start_color=Color(255, 255, 0, 255),
            end_color=Color(255, 255, 0, 255),
        )
    ]

    assert tag.line_styles == [
        MorphLineStyle(
            start_width=0,
            end_width=0,
            start_color=Color(0, 0, 0, 0),
            end_color=Color(0, 0, 0, 0),
        )
    ]

    assert len(tag.start_edges) == 11
    assert all(isinstance(record, ShapeRecord) for record in tag.start_edges)
    assert len(tag.end_edges) == 11
    assert all(isinstance(record, ShapeRecord) for record in tag.end_edges)
