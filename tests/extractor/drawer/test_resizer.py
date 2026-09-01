"""Translated from ArakneSwf's `ScaleResizerTest.php` and `FitSizeResizerTest.php`."""

from __future__ import annotations

import pytest

from prespyc.extractor.drawer.resizer import FitSizeResizer, ScaleResizer


def test_scale_resizer():
    assert ScaleResizer(2.4).scale(100.0, 200.0) == (240.0, 480.0)


@pytest.mark.parametrize(
    ("width", "height", "expected"),
    [
        (200, 400, (100.0, 200.0)),
        (100, 200, (100.0, 200.0)),
        (50, 100, (100.0, 200.0)),
        (500, 100, (100.0, 20.0)),
        (0, 0, (100.0, 200.0)),
        (0, 50, (0.0, 200.0)),
        (50, 0, (100.0, 0.0)),
    ],
)
def test_fit_size_resizer(width, height, expected):
    assert FitSizeResizer(100, 200).scale(width, height) == expected
