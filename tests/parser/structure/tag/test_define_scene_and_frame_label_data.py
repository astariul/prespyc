"""Port of ArakneSwf's `tests/Parser/Structure/Tag/DefineSceneAndFrameLabelDataTagTest.php`."""

from __future__ import annotations

from prespyc.errors import Errors
from prespyc.parser.reader import Reader
from prespyc.parser.structure.tag.define_scene_and_frame_label_data import DefineSceneAndFrameLabelDataTag


def test_read_should_stop_at_end_of_data():
    reader = Reader(
        b"\xff\xff\xff\xff\xfftest\x00\xff\xff\xff\xff\xfftest\x00"
        b"\xff\xff\xff\xff\xfftest\x00\xff\xff\xff\xff\xfftest\x00",
        errors=Errors.NONE,
    )
    tag = DefineSceneAndFrameLabelDataTag.read(reader)

    assert len(tag.scene_offsets) == 4
    assert len(tag.scene_names) == 4
    assert len(tag.frame_numbers) == 0
    assert len(tag.frame_labels) == 0
