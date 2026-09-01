"""Port of ArakneSwf's `tests/Parser/Structure/Record/Shape/ShapeRecordTest.php`."""

from __future__ import annotations

from prespyc.parser.structure.record.shape.curved_edge_record import CurvedEdgeRecord
from prespyc.parser.structure.record.shape.end_shape_record import EndShapeRecord
from prespyc.parser.structure.record.shape.shape_record import ShapeRecord
from prespyc.parser.structure.record.shape.style_change_record import StyleChangeRecord
from tests.support import fixture, fixture_reader


def test_read_collection():
    reader = fixture_reader(fixture("sunAndShadow.swf"), 54)

    records = ShapeRecord.read_collection(reader, 1)

    assert len(records) == 10
    assert all(isinstance(record, ShapeRecord) for record in records)

    assert records[0] == StyleChangeRecord(
        state_new_styles=False,
        state_line_style=False,
        state_fill_style0=False,
        state_fill_style1=True,
        state_move_to=True,
        move_delta_x=0,
        move_delta_y=-1249,
        fill_style0=0,
        fill_style1=1,
        line_style=0,
        fill_styles=[],
        line_styles=[],
    )

    assert records[1] == CurvedEdgeRecord(
        control_delta_x=517,
        control_delta_y=0,
        anchor_delta_x=366,
        anchor_delta_y=366,
    )

    assert records[9] == EndShapeRecord()


def test_read_collection_v4():
    reader = fixture_reader(fixture("sunAndShadow.swf"), 380)

    records = ShapeRecord.read_collection(reader, 4)

    assert len(records) == 6
    assert all(isinstance(record, ShapeRecord) for record in records)

    assert records[0] == StyleChangeRecord(
        state_new_styles=False,
        state_line_style=True,
        state_fill_style0=False,
        state_fill_style1=False,
        state_move_to=True,
        move_delta_x=8000,
        move_delta_y=0,
        fill_style0=0,
        fill_style1=0,
        line_style=1,
        fill_styles=[],
        line_styles=[],
    )

    assert records[5] == EndShapeRecord()
