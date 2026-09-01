"""Port of `tests/Extractor/Shape/FillType/BitmapTest.php`."""

from __future__ import annotations

from dataclasses import astuple

import pytest

from prespyc.extractor.image.empty_image import EmptyImage
from prespyc.extractor.shape.fill_type.bitmap import Bitmap
from prespyc.parser.structure.record.matrix import Matrix


def test_interpolate():
    start = Bitmap(
        EmptyImage(0),
        Matrix(1.2, 0.7, 12.3, 4.5, 42, -21),
        True,
        False,
    )
    end = Bitmap(
        EmptyImage(0),
        Matrix(-0.5, 2.3, 7.8, -1.1, -33, 17),
        True,
        False,
    )

    assert start.interpolate(end, 0) == start
    assert start.interpolate(end, 65535) == end

    expected = Bitmap(
        EmptyImage(0),
        Matrix(0.35, 1.5, 10.05, 1.7, 4, -1),
        True,
        False,
    )
    actual = start.interpolate(end, 32768)

    # The matrix factors are interpolated as floats, so they only match within a delta.
    assert actual.bitmap == expected.bitmap
    assert astuple(actual.matrix) == pytest.approx(astuple(expected.matrix), abs=0.0001)
    assert actual.smoothed == expected.smoothed
    assert actual.repeat == expected.repeat
