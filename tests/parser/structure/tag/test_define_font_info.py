"""Port of ArakneSwf's DefineFontInfoTagTest."""

from __future__ import annotations

from prespyc.parser.structure.tag.define_font_info import DefineFontInfoTag
from tests.support import fixture, fixture_reader


def test_read():
    reader = fixture_reader(fixture("extractor", "swf1", "new_theater.swf"), 3993)

    tag = DefineFontInfoTag.read(reader, 1, 4039)

    assert tag.version == 1
    assert tag.font_id == 6
    assert tag.font_name == b"Zurich Blk BT"
    assert not tag.font_flags_small_text
    assert tag.font_flags_shift_jis
    assert not tag.font_flags_ansi
    assert not tag.font_flags_italic
    assert tag.font_flags_bold
    assert not tag.font_flags_wide_codes
    assert tag.code_table == [
        32,
        39,
        48,
        50,
        65,
        70,
        72,
        76,
        83,
        97,
        98,
        99,
        100,
        101,
        102,
        104,
        105,
        107,
        108,
        109,
        110,
        111,
        112,
        114,
        115,
        116,
        117,
        119,
        122,
    ]
    assert tag.language_code is None
