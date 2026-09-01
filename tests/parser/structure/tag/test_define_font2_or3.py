"""Port of ArakneSwf's DefineFont2Or3TagTest."""

from __future__ import annotations

from prespyc.parser.structure.record.rectangle import Rectangle
from prespyc.parser.structure.record.shape.end_shape_record import EndShapeRecord
from prespyc.parser.structure.tag.define_font2_or3 import DefineFont2Or3Tag
from tests.support import fixture, fixture_reader


def test_read():
    reader = fixture_reader(fixture("extractor", "core", "core.swf"), 38)

    tag = DefineFont2Or3Tag.read(reader, 3)

    assert tag.version == 3
    assert not tag.font_flags_shift_jis
    assert not tag.font_flags_small_text
    assert not tag.font_flags_ansi
    assert tag.font_flags_wide_codes
    assert tag.font_flags_italic
    assert tag.font_flags_bold
    assert tag.language_code == 1
    assert tag.font_name == b"Verdana"
    assert tag.num_glyphs == 1110
    assert len(tag.offset_table) == 1110
    assert tag.offset_table[0] == 4444
    assert tag.offset_table[1109] == 96915
    assert len(tag.glyph_shape_table) == 1110
    assert tag.glyph_shape_table[0] == [EndShapeRecord()]
    assert len(tag.code_table) == 1110
    assert all(isinstance(code, int) for code in tag.code_table)
    assert all(0 <= code <= 2**16 - 1 for code in tag.code_table)
    assert tag.layout is not None
    assert tag.layout.ascent == 20600
    assert tag.layout.descent == 4300
    assert len(tag.layout.advance_table) == 1110
    assert all(isinstance(advance, int) for advance in tag.layout.advance_table)
    assert all(-(2**15) <= advance <= 2**15 - 1 for advance in tag.layout.advance_table)
    assert len(tag.layout.bounds_table) == 1110
    assert all(isinstance(bounds, Rectangle) for bounds in tag.layout.bounds_table)
    assert tag.layout.kerning_table == []
