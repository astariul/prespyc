"""Port of ArakneSwf's DefineMorphShape2TagTest."""

from __future__ import annotations

from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.morph_shape.morph_line_style2 import MorphLineStyle2
from prespyc.parser.structure.record.rectangle import Rectangle
from prespyc.parser.structure.record.shape.shape_record import ShapeRecord
from prespyc.parser.structure.tag.define_morph_shape2 import DefineMorphShape2Tag
from tests.support import fixture, fixture_reader


def test_read():
    reader = fixture_reader(fixture("extractor", "core", "core.swf"), 2215533)

    tag = DefineMorphShape2Tag.read(reader)

    assert tag.character_id == 1558
    assert tag.start_bounds == Rectangle(xmin=-770, xmax=770, ymin=-770, ymax=770)
    assert tag.end_bounds == Rectangle(xmin=-710, xmax=710, ymin=-710, ymax=710)
    assert tag.start_edge_bounds == Rectangle(xmin=-720, xmax=720, ymin=-720, ymax=720)
    assert tag.end_edge_bounds == Rectangle(xmin=-660, xmax=660, ymin=-660, ymax=660)

    assert tag.fill_styles == []

    assert tag.line_styles == [
        MorphLineStyle2(
            start_width=100,
            end_width=100,
            start_cap_style=0,
            join_style=0,
            no_h_scale=False,
            no_v_scale=False,
            pixel_hinting=False,
            no_close=False,
            end_cap_style=0,
            miter_limit_factor=None,
            start_color=Color(41, 38, 31, 255),
            end_color=Color(41, 38, 31, 255),
            fill_style=None,
        )
    ]

    assert tag.uses_scaling_strokes
    assert not tag.uses_non_scaling_strokes

    assert len(tag.start_edges) == 13
    assert all(isinstance(record, ShapeRecord) for record in tag.start_edges)
    assert len(tag.end_edges) == 13
    assert all(isinstance(record, ShapeRecord) for record in tag.end_edges)
