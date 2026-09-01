"""Port of ArakneSwf's DefineFontAlignZonesTagTest."""

from __future__ import annotations

from prespyc.parser.structure.tag.define_font_align_zones import DefineFontAlignZonesTag
from tests.support import fixture, fixture_reader


def test_read():
    reader = fixture_reader(fixture("parser", "Examples1.swf"), 115)

    tag = DefineFontAlignZonesTag.read(reader, 128)

    assert tag.font_id == 1
    assert tag.csm_table_hint == 1
    assert len(tag.zone_table) == 1
    assert len(tag.zone_table[0].data) == 2
    assert tag.zone_table[0].data[0].alignment_coordinate == 0.2005615234375
    assert tag.zone_table[0].data[0].range == 0.0
    assert tag.zone_table[0].data[1].alignment_coordinate == 0.0
    assert tag.zone_table[0].data[1].range == 1.716796875
    assert tag.zone_table[0].mask_x
    assert tag.zone_table[0].mask_y
