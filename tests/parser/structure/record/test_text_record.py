"""Port of ArakneSwf's TextRecordTest."""

from __future__ import annotations

from prespyc.parser.reader import Reader
from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.glyph_entry import GlyphEntry
from prespyc.parser.structure.record.text_record import TextRecord
from tests.support import fixture, fixture_reader


def test_read_without_alpha():
    reader = fixture_reader(fixture("extractor", "swf1", "new_theater.swf"), 4349)

    records = TextRecord.read_collection(reader, 5, 10, False)
    assert len(records) == 1
    record = records[0]

    assert record.type == 1
    assert record.font_id == 6
    assert record.color == Color(153, 153, 153)
    assert record.x_offset == 278
    assert record.y_offset == 424
    assert record.height == 440

    glyphs = record.glyphs
    assert len(glyphs) == 21
    assert all(isinstance(glyph, GlyphEntry) for glyph in glyphs)

    assert glyphs[0] == GlyphEntry(27, 413)
    assert glyphs[1] == GlyphEntry(15, 291)
    assert glyphs[2] == GlyphEntry(9, 267)
    assert glyphs[10] == GlyphEntry(0, 147)
    assert glyphs[20] == GlyphEntry(3, 291)


def test_read_should_stop_at_end_of_data():
    reader = Reader(b"\x80\x00\x80\x00\x80\x00\x80\x00")
    records = TextRecord.read_collection(reader, 0, 0, False)

    assert len(records) == 4
