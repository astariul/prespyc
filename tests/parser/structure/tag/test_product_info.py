"""Port of ArakneSwf's `tests/Parser/Structure/Tag/ProductInfoTest.php`."""

from __future__ import annotations

from prespyc.parser.structure.tag.product_info import ProductInfo
from tests.support import fixture, fixture_reader


def test_read():
    reader = fixture_reader(fixture("parser", "TestFlex.swf"), 536)
    tag = ProductInfo.read(reader)

    assert tag.product_id == 3
    assert tag.edition == 6
    assert tag.major_version == 4
    assert tag.minor_version == 6
    assert tag.build_number == 23201
    assert tag.compilation_date == 1452749888546
