"""
Phase 2 acceptance gate: every SWF fixture of the suite must go through the parser.

This has no PHPUnit counterpart. It fans the two useful error policies over the whole fixture tree,
so a regression in any of the 59 tag structures shows up as a failing fixture rather than as a
mysterious golden diff later on.
"""

from __future__ import annotations

import pytest

from prespyc.errors import Errors, InvalidDataError
from prespyc.parser.swf import Swf
from prespyc.swf_file import SwfFile
from tests.support import FIXTURES, fixture

SWF_FIXTURES = sorted(FIXTURES.rglob("*.swf"))
"""Every SWF of the fixture tree, discovered — never hardcoded."""

FIXTURE_IDS = [path.relative_to(FIXTURES).as_posix() for path in SWF_FIXTURES]

SCRIPT_ONLY = frozenset(
    {
        "array.swf",
        "big.swf",
        "cast.swf",
        "func_call.swf",
        "function.swf",
        "lang_fr_801.swf",
        "methods.swf",
        "objects.swf",
        "parser/alignment_fr_147.swf",
        "simple.swf",
        "undefined.swf",
    }
)
"""Fixtures that hold only `DoAction` scripts, so their character dictionary is legitimately empty."""

CORRUPT = {
    "corrupted.swf": 15,
}
"""Deliberately corrupt fixtures, and how many of their tags still parse. See `test_corrupted`."""

INVALID_HEADERS = ("invalid-signature", "invalid-too-small", "invalid-version-too-high", "invalid-length-too-high")
"""Deliberately truncated headers. Not `*.swf`, so they are outside the sweep below."""


def test_fixtures_discovered():
    assert len(SWF_FIXTURES) == 59
    assert SCRIPT_ONLY.issubset(FIXTURE_IDS)
    assert set(CORRUPT).issubset(FIXTURE_IDS)


@pytest.mark.slow
@pytest.mark.parametrize("path", SWF_FIXTURES, ids=FIXTURE_IDS)
def test_parses_fail_safe(path):
    """With every error flag off, no fixture may raise — corrupt bytes yield fallback values."""
    swf = Swf.from_bytes(path.read_bytes(), Errors.NONE)

    assert swf.header.signature in ("FWS", "CWS")

    count = 0

    for tag in swf.tags:
        assert swf.parse(tag) is not None
        count += 1

    assert count > 0


@pytest.mark.slow
@pytest.mark.parametrize("path", SWF_FIXTURES, ids=FIXTURE_IDS)
def test_parses_ignore_invalid_tag(path):
    """
    Same sweep with `Errors.IGNORE_INVALID_TAG`: every error is reported *except* on a tag that
    fails to read, which is skipped.

    Driven through `SwfFile.tags()` because — in the port as in ArakneSwf — `INVALID_TAG` is only
    honoured by the callers that catch (`SwfFile.tags()` and `DefineSpriteTag.read()`);
    `RawTag.parse()` itself always raises.
    """
    file = SwfFile(path, errors=Errors.IGNORE_INVALID_TAG)

    assert sum(1 for _ in file.tags()) > 0


@pytest.mark.parametrize("path", SWF_FIXTURES, ids=FIXTURE_IDS)
def test_tag_count_and_dictionary(path):
    """Every fixture holds tags, and every non-script fixture defines characters."""
    swf = Swf.from_bytes(path.read_bytes(), Errors.NONE)
    name = path.relative_to(FIXTURES).as_posix()

    assert len(swf.tags) > 0

    if name in SCRIPT_ONLY:
        assert len(swf.dictionary) == 0
    else:
        assert len(swf.dictionary) > 0


def test_corrupted():
    """
    `corrupted.swf` holds 19 tags, one of which has a broken zlib alpha channel.

    ArakneSwf's `SwfFileTest::tagsIgnoreInvalid()` pins the surviving count at 15; parsing the tag
    itself still raises, whatever the `INVALID_TAG` flag says.
    """
    path = fixture("corrupted.swf")
    swf = Swf.from_bytes(path.read_bytes(), Errors.IGNORE_INVALID_TAG)

    assert len(swf.tags) == 19

    with pytest.raises(InvalidDataError):
        for tag in swf.tags:
            swf.parse(tag)

    assert sum(1 for _ in SwfFile(path, errors=Errors.IGNORE_INVALID_TAG).tags()) == CORRUPT["corrupted.swf"]


@pytest.mark.parametrize("name", INVALID_HEADERS)
def test_invalid_header(name):
    """The `invalid-*` fixtures must be rejected by the header check, not by an exception."""
    assert not SwfFile(fixture(name)).valid()


def test_invalid_signature_fixture():
    with pytest.raises(ValueError, match="Unsupported SWF signature"):
        Swf.from_bytes(fixture("invalid-signature").read_bytes())
