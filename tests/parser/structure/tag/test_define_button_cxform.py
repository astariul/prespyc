"""Port of ArakneSwf's DefineButtonCxformTagTest."""

from __future__ import annotations

from prespyc.parser.reader import Reader
from prespyc.parser.structure.record.color_transform import ColorTransform
from prespyc.parser.structure.tag.define_button_cxform import DefineButtonCxformTag


def test_read():
    reader = Reader(b"\x17\x00\x00")

    tag = DefineButtonCxformTag.read(reader)

    assert tag.button_id == 23
    assert tag.color_transform == ColorTransform()
