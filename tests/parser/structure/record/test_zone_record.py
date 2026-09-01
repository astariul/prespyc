"""Port of ArakneSwf's ZoneRecordTest."""

from __future__ import annotations

import pytest

from prespyc.parser.structure.record.zone_record import ZoneRecord
from tests.support import fixture, fixture_reader


def _coordinates(record: ZoneRecord) -> list[float]:
    """Flatten the zone data of a record, so it can be compared with a delta."""
    return [value for data in record.data for value in (data.alignment_coordinate, data.range)]


def test_read_collection():
    reader = fixture_reader(fixture("extractor", "core", "core.swf"), 103680)

    records = ZoneRecord.read_collection(reader, 114780)
    assert len(records) == 1110

    assert len(records[0].data) == 2
    assert _coordinates(records[0]) == pytest.approx([0, 0, 0, 0], abs=0.00001)
    assert not records[0].mask_y
    assert not records[0].mask_x

    assert len(records[1].data) == 2
    assert _coordinates(records[1]) == pytest.approx([0, 0, 0, 1.7255859375], abs=0.00001)
    assert records[1].mask_y
    assert records[1].mask_x

    assert len(records[2].data) == 2
    assert _coordinates(records[2]) == pytest.approx([0.428955078125, 0, 0.49365234375, 1.759765625], abs=0.00001)
    assert records[2].mask_y
    assert records[2].mask_x
