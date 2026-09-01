"""Port of ArakneSwf's `tests/Parser/Structure/Tag/ScriptLimitsTagTest.php`."""

from __future__ import annotations

from prespyc.parser.structure.tag.script_limits import ScriptLimitsTag
from tests.support import fixture, fixture_reader


def test_read():
    reader = fixture_reader(fixture("parser", "TestFlex.swf"), 525)
    tag = ScriptLimitsTag.read(reader)

    assert tag.max_recursion_depth == 1000
    assert tag.script_timeout_seconds == 60
