"""Port of ArakneSwf's DefineFontTagTest."""

from __future__ import annotations

from prespyc.parser.structure.record.shape.end_shape_record import EndShapeRecord
from prespyc.parser.structure.record.shape.straight_edge_record import StraightEdgeRecord
from prespyc.parser.structure.record.shape.style_change_record import StyleChangeRecord
from prespyc.parser.structure.tag.define_font import DefineFontTag
from tests.support import fixture, fixture_reader


def test_read():
    reader = fixture_reader(fixture("extractor", "swf1", "new_theater.swf"), 2062)

    tag = DefineFontTag.read(reader)

    assert tag.font_id == 6
    assert len(tag.offset_table) == 29
    assert all(isinstance(offset, int) for offset in tag.offset_table)
    assert tag.offset_table[0] == 58
    assert tag.offset_table[1] == 60
    assert tag.offset_table[28] == 1893
    assert len(tag.glyph_shape_data) == 29

    assert tag.glyph_shape_data[0] == [EndShapeRecord()]
    assert tag.glyph_shape_data[1] == [
        StyleChangeRecord(
            state_new_styles=False,
            state_line_style=True,
            state_fill_style0=False,
            state_fill_style1=True,
            state_move_to=True,
            move_delta_x=38,
            move_delta_y=-719,
            fill_style0=0,
            fill_style1=1,
            line_style=0,
            fill_styles=[],
            line_styles=[],
        ),
        StraightEdgeRecord(
            general_line_flag=False,
            vertical_line_flag=False,
            delta_x=110,
            delta_y=0,
        ),
        StraightEdgeRecord(
            general_line_flag=False,
            vertical_line_flag=True,
            delta_x=0,
            delta_y=281,
        ),
        StraightEdgeRecord(
            general_line_flag=False,
            vertical_line_flag=False,
            delta_x=-110,
            delta_y=0,
        ),
        StraightEdgeRecord(
            general_line_flag=False,
            vertical_line_flag=True,
            delta_x=0,
            delta_y=-281,
        ),
        EndShapeRecord(),
    ]
