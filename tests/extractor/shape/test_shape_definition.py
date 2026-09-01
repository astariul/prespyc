"""Port of `tests/Extractor/Shape/ShapeDefinitionTest.php`."""

from __future__ import annotations

import copy
from unittest.mock import Mock

from prespyc.swf_file import SwfFile
from tests.support import fixture


def test_modify():
    shape = SwfFile(fixture("extractor", "2.swf")).asset_by_id(1)
    new_shape = copy.copy(shape)

    modifier = Mock()
    modifier.apply_on_shape.return_value = new_shape

    assert shape.modify(modifier) is new_shape
    modifier.apply_on_shape.assert_called_once_with(shape)
