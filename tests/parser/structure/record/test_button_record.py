"""Port of ArakneSwf's ButtonRecordTest."""

from __future__ import annotations

import pytest

from prespyc.errors import Errors
from prespyc.parser.structure.record.button_record import ButtonRecord
from prespyc.parser.structure.record.color_transform import ColorTransform
from prespyc.parser.structure.record.filter.color_matrix_filter import ColorMatrixFilter
from prespyc.parser.structure.record.matrix import Matrix
from tests.support import fixture, fixture_reader


def test_read_collection_v2():
    reader = fixture_reader(fixture("extractor", "core", "core.swf"), 597297)

    records = ButtonRecord.read_collection(reader, 2)

    assert len(records) == 9
    assert all(isinstance(record, ButtonRecord) for record in records)

    assert not records[0].state_hit_test
    assert not records[0].state_down
    assert not records[0].state_over
    assert records[0].state_up
    assert records[0].character_id == 310
    assert records[0].place_depth == 1
    assert records[0].matrix == Matrix()
    assert records[0].color_transform == ColorTransform()
    assert records[0].filters is None
    assert records[0].blend_mode is None

    assert not records[1].state_hit_test
    assert not records[1].state_down
    assert records[1].state_over
    assert records[1].state_up
    assert records[1].character_id == 312
    assert records[1].place_depth == 2
    assert records[1].matrix == Matrix(scale_x=-0.4789886474609375, scale_y=-0.4749908447265625)
    assert records[1].color_transform == ColorTransform(red_mult=0, green_mult=0, blue_mult=0, alpha_mult=128)


def test_read_collection_v1():
    reader = fixture_reader(fixture("extractor", "swf1", "new_theater.swf"), 5200)

    records = ButtonRecord.read_collection(reader, 1)
    assert len(records) == 4
    assert all(isinstance(record, ButtonRecord) for record in records)

    assert not records[0].state_hit_test
    assert not records[0].state_down
    assert records[0].state_over
    assert records[0].state_up
    assert records[0].character_id == 15
    assert records[0].place_depth == 2
    assert records[0].matrix == Matrix(
        scale_x=0.4801483154296875, scale_y=0.4801483154296875, translate_x=0, translate_y=1418
    )
    assert records[0].color_transform is None
    assert records[0].filters is None
    assert records[0].blend_mode is None


def test_read_with_filter():
    reader = fixture_reader(fixture("extractor", "core", "core.swf"), 1286804)

    records = ButtonRecord.read_collection(reader, 2)
    assert len(records) == 5

    assert not records[0].state_hit_test
    assert not records[0].state_down
    assert not records[0].state_over
    assert records[0].state_up
    assert records[0].character_id == 561
    assert records[0].place_depth == 1
    assert records[0].matrix == Matrix(translate_x=153, translate_y=132)
    assert records[0].color_transform == ColorTransform()
    assert len(records[0].filters) == 1

    filter_ = records[0].filters[0]
    assert isinstance(filter_, ColorMatrixFilter)
    assert filter_.matrix == pytest.approx(
        [
            1.6836779,
            0.019124676,
            0.29719734,
            0.0,
            -159.5,
            0.1515163,
            1.9003643,
            -0.051880665,
            0.0,
            -159.5,
            -0.11656176,
            0.43133074,
            1.685231,
            0.0,
            -159.5,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
        ],
        abs=0.00001,
    )


def test_read_collection_should_stop_on_stream_end():
    reader = fixture_reader(fixture("extractor", "core", "core.swf"), 597297, errors=Errors.NONE)
    reader = reader.chunk(597297, 597297 + 100)

    records = ButtonRecord.read_collection(reader, 2)

    assert len(records) == 8
    assert all(isinstance(record, ButtonRecord) for record in records)
