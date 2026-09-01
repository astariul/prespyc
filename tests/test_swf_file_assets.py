"""
The asset accessors of `SwfFileTest.php`, which need the extractor.

The rest of that class is in `tests/test_swf_file.py`, and its `execute()`/`variables()` methods in
`tests/test_swf_file_variables.py`.
"""

from __future__ import annotations

from prespyc.extractor.sprite.sprite_definition import SpriteDefinition
from prespyc.swf_file import SwfFile
from tests.support import assert_svg_matches, fixture

EXPORTED_1047 = {
    "runR": 29,
    "runL": 43,
    "bonusR": 53,
    "bonusL": 56,
    "anim0R": 62,
    "anim0L": 64,
    "staticR": 66,
    "staticL": 68,
    "walkL": 70,
    "walkR": 72,
    "anim1R": 77,
    "anim1L": 79,
    "hitR": 91,
    "hitL": 95,
    "dieR": 97,
    "dieL": 99,
}


def test_asset_by_name():
    swf = SwfFile(fixture("extractor", "1047", "1047.swf"))

    static_r = swf.asset_by_name("staticR")

    assert isinstance(static_r, SpriteDefinition)
    assert static_r.id == 66
    assert_svg_matches(static_r.to_svg(), fixture("extractor", "1047", "staticR.svg"))


def test_asset_by_id():
    swf = SwfFile(fixture("extractor", "complex_sprite.swf"))
    sprite = swf.asset_by_id(13)

    assert isinstance(sprite, SpriteDefinition)
    assert sprite.id == 13
    assert_svg_matches(sprite.to_svg(), fixture("extractor", "sprite-13.svg"))


def test_exported_assets():
    swf = SwfFile(fixture("extractor", "1047", "1047.swf"))
    exported = swf.exported_assets

    assert all(isinstance(asset, SpriteDefinition) for asset in exported.values())
    assert {name: asset.id for name, asset in exported.items()} == EXPORTED_1047


def test_timeline():
    swf = SwfFile(fixture("extractor", "1", "1.swf"))

    for frame, svg in enumerate(swf.timeline(False).to_svg_all()):
        assert_svg_matches(svg, fixture("extractor", "1", f"frame_{frame}.svg"))
