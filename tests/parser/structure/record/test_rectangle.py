"""Port of ArakneSwf's `tests/Parser/Structure/Record/RectangleTest.php`."""

from __future__ import annotations

import re

import pytest

from prespyc.errors import Errors, InvalidDataError
from prespyc.parser.reader import Reader
from prespyc.parser.structure.record.rectangle import Rectangle
from tests.support import fixture, fixture_reader


def test_read():
    reader = fixture_reader(fixture("parser", "Examples1.swf"), 3318)

    rectangle = Rectangle.read(reader)

    assert rectangle.xmin == -30
    assert rectangle.xmax == 3530
    assert rectangle.ymin == -30
    assert rectangle.ymax == 970


def test_read_invalid_x():
    reader = Reader(b"\x1b\x01\x80")

    with pytest.raises(InvalidDataError, match=re.escape("Invalid rectangle: xmin (3) is greater than xmax (0)")):
        Rectangle.read(reader)


def test_read_invalid_x_ignore_error():
    reader = Reader(b"\x1b\x01\x80", errors=Errors.NONE)
    rectangle = Rectangle.read(reader)

    assert rectangle.xmin == 0
    assert rectangle.xmax == 0
    assert rectangle.ymin == 0
    assert rectangle.ymax == 3


def test_read_invalid_y():
    reader = Reader(b"\x18\x6c\x00")

    with pytest.raises(InvalidDataError, match=re.escape("Invalid rectangle: ymin (3) is greater than ymax (0)")):
        Rectangle.read(reader)


def test_read_invalid_y_ignore_error():
    reader = Reader(b"\x18\x6c\x00", errors=Errors.NONE)
    rectangle = Rectangle.read(reader)

    assert rectangle.xmin == 0
    assert rectangle.xmax == 3
    assert rectangle.ymin == 0
    assert rectangle.ymax == 0


def test_union():
    rectangle = Rectangle(-5, 10, -3, 7)

    assert rectangle.union(rectangle) == rectangle
    assert rectangle.union(Rectangle(0, 0, 0, 0)) == rectangle
    assert rectangle.union(Rectangle(-10, 20, -10, 20)) == Rectangle(-10, 20, -10, 20)
    assert rectangle.union(Rectangle(0, 20, -10, 0)) == Rectangle(-5, 20, -10, 7)


def test_merge():
    assert Rectangle.merge([]) == Rectangle(0, 0, 0, 0)
    assert Rectangle.merge([Rectangle(-5, 10, -3, 7)]) == Rectangle(-5, 10, -3, 7)
    assert Rectangle.merge(
        [
            Rectangle(-5, 10, -3, 7),
            Rectangle(-10, 15, -5, 10),
            Rectangle(0, 20, 0, 20),
        ]
    ) == Rectangle(-10, 20, -5, 20)
