"""Port of ArakneSwf's ClipActionRecordTest."""

from __future__ import annotations

from prespyc.parser.reader import Reader
from prespyc.parser.structure.record.clip_action_record import ClipActionRecord


def test_read_collection_should_stop_at_end_of_data():
    reader = Reader(
        b"\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00"
        b"\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00"
    )
    records = ClipActionRecord.read_collection(reader, 3)

    assert len(records) == 5
