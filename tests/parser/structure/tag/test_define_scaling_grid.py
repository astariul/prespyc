"""Port of ArakneSwf's `tests/Parser/Structure/Tag/DefineScalingGridTagTest.php`."""

from __future__ import annotations

from prespyc.parser.reader import Reader
from prespyc.parser.structure.record.rectangle import Rectangle
from prespyc.parser.structure.tag.define_scaling_grid import DefineScalingGridTag


def test_read():
    reader = Reader(b"\x51\x00\x16\xe8")
    tag = DefineScalingGridTag.read(reader)

    assert tag.character_id == 81
    assert tag.splitter == Rectangle(xmin=-1, xmax=1, ymin=-1, ymax=1)
