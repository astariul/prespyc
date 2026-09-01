"""Port of ArakneSwf's `tests/Parser/Structure/Tag/DoInitActionTagTest.php`."""

from __future__ import annotations

from prespyc.parser.structure.action.action_record import ActionRecord
from prespyc.parser.structure.tag.do_init_action import DoInitActionTag
from tests.support import fixture, fixture_reader


def test_read():
    reader = fixture_reader(fixture("sunAndShadow.swf"), 459)
    tag = DoInitActionTag.read(reader, 1565)

    assert tag.sprite_id == 6
    assert len(tag.actions) == 194
    assert all(isinstance(action, ActionRecord) for action in tag.actions)
