"""
Port of ArakneSwf's `tests/SwfFileTest.php`.

`variable()` / `execute()` live in `tests/test_swf_file_variables.py`; the asset accessors
(`assetByName()`, `assetById()`, `exportedAssets()`, `timeline()`) belong to the extractor phase.
"""

from __future__ import annotations

import pytest

from prespyc.errors import Errors, ExtraDataError
from prespyc.parser.structure.raw_tag import RawTag
from prespyc.parser.structure.record.rectangle import Rectangle
from prespyc.parser.structure.tag.do_action import DoActionTag
from prespyc.parser.structure.tag.end import EndTag
from prespyc.parser.structure.tag.file_attributes import FileAttributesTag
from prespyc.parser.structure.tag.set_background_color import SetBackgroundColorTag
from prespyc.parser.structure.tag.show_frame import ShowFrameTag
from prespyc.swf_file import SwfFile
from tests.support import fixture


def test_tags():
    file = SwfFile(fixture("lang_fr_801.swf"))

    tags = [parsed for _, parsed in file.tags()]
    assert len(tags) == 5
    assert isinstance(tags[0], FileAttributesTag)
    assert isinstance(tags[1], SetBackgroundColorTag)
    assert isinstance(tags[2], DoActionTag)
    assert isinstance(tags[3], ShowFrameTag)
    assert isinstance(tags[4], EndTag)

    tags = [parsed for _, parsed in file.tags(12)]
    assert len(tags) == 1
    assert isinstance(tags[0], DoActionTag)

    tags = [parsed for _, parsed in file.tags(12, 9)]
    assert len(tags) == 2
    assert isinstance(tags[0], SetBackgroundColorTag)
    assert isinstance(tags[1], DoActionTag)

    pairs = list(file.tags(12, 9))

    assert len(pairs) == 2
    assert pairs[0][0] == RawTag(9, 29, 3)
    assert isinstance(pairs[0][1], SetBackgroundColorTag)
    assert pairs[1][0] == RawTag(12, 38, 168338)
    assert isinstance(pairs[1][1], DoActionTag)


def test_tags_ignore_invalid():
    swf = SwfFile(fixture("corrupted.swf"), errors=Errors.IGNORE_INVALID_TAG)
    tags = [parsed for _, parsed in swf.tags()]

    assert len(tags) == 15


def test_valid():
    assert SwfFile(fixture("lang_fr_801.swf")).valid()
    assert not SwfFile(fixture("simple.sc")).valid()
    assert not SwfFile(fixture("invalid-signature")).valid()
    assert not SwfFile(fixture("invalid-too-small")).valid()
    assert not SwfFile(fixture("invalid-version-too-high")).valid()
    assert not SwfFile(fixture("invalid-length-too-high")).valid()


@pytest.mark.parametrize("name", ["Examples1.swf", "sunAndShadow.swf"])
def test_coverage(name):
    """
    Simply parse SWF files to check for exceptions.

    Some test files are from https://condor.depaul.edu/sjost/hci430/flash-examples.htm
    """
    swf = SwfFile(fixture(name))

    for _, tag in swf.tags():
        assert tag is not None


def test_with_extra_bytes_ignore_error():
    swf = SwfFile(fixture("1317.swf"), errors=Errors.NONE)

    for _, tag in swf.tags():
        assert tag is not None


def test_with_extra_bytes_throw_error():
    swf = SwfFile(fixture("1317.swf"))

    with pytest.raises(ExtraDataError) as info:
        for _, tag in swf.tags():
            assert tag is not None

    assert str(info.value).startswith("Extra data found after tag 26 at offset 37582 (length = 8)")
    assert info.value.offset == 37582
    assert info.value.length == 8


def test_header():
    swf = SwfFile(fixture("extractor", "1", "1.swf"))
    header = swf.header

    assert header.signature == "CWS"
    assert header.version == 7
    assert header.file_length == 2564
    assert header.frame_size == Rectangle(0, 20, 0, 20)
    assert header.frame_rate == 12.0
    assert header.frame_count == 1


def test_frame_rate():
    swf = SwfFile(fixture("extractor", "1", "1.swf"))

    assert swf.frame_rate == 12
