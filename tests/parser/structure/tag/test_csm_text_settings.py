"""Port of ArakneSwf's CSMTextSettingsTagTest."""

from __future__ import annotations

from prespyc.parser.structure.tag.csm_text_settings import CSMTextSettingsTag
from tests.support import fixture, fixture_reader


def test_read():
    reader = fixture_reader(fixture("extractor", "core", "core.swf"), 801399)

    tag = CSMTextSettingsTag.read(reader)

    assert tag.text_id == 536
    assert tag.use_flash_type == 1
    assert tag.grid_fit == 2
    assert tag.thickness == 0.0
    assert tag.sharpness == 0.0
