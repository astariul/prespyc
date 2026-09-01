"""Port of ArakneSwf's `tests/Parser/Structure/Record/ColorTransformTest.php`."""

from __future__ import annotations

from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.color_transform import ColorTransform
from tests.support import fixture, fixture_reader


def test_identity_transform():
    transform = ColorTransform()

    color = Color(255, 128, 64, 255)
    result = transform.transform(color)

    assert result == color


def test_add_transform():
    transform = ColorTransform(red_add=50, green_add=25, blue_add=50)

    color = Color(100, 150, 200, 255)
    expected = Color(150, 175, 250, 255)

    assert transform.transform(color) == expected


def test_multiply_transform():
    transform = ColorTransform(
        red_mult=128,  # 0.5
        green_mult=384,  # 1.5
        blue_mult=192,  # 0.75
    )

    color = Color(200, 100, 80, 255)
    expected = Color(100, 150, 60, 255)

    assert transform.transform(color) == expected


def test_combined_transform():
    transform = ColorTransform(
        red_mult=205,  # ~0.8
        green_mult=307,  # ~1.2
        blue_mult=128,  # 0.5
        red_add=10,
        green_add=5,
        blue_add=5,
    )

    color = Color(100, 100, 100, 255)
    expected = Color(90, 124, 55, 255)

    assert transform.transform(color) == expected


def test_upper_boundary():
    transform = ColorTransform(red_add=100, green_add=100, blue_add=100, alpha_add=100)

    color = Color(200, 200, 200, 200)
    expected = Color(255, 255, 255, 255)

    assert transform.transform(color) == expected


def test_lower_boundary():
    transform = ColorTransform(
        red_mult=128,
        green_mult=128,
        blue_mult=128,
        alpha_mult=128,
        red_add=-100,
        green_add=-100,
        blue_add=-100,
        alpha_add=-100,
    )

    color = Color(100, 100, 100, 200)
    expected = Color(0, 0, 0, 0)

    assert transform.transform(color) == expected


def test_alpha_transformation():
    transform = ColorTransform(alpha_mult=128, alpha_add=50)

    color = Color(100, 100, 100, 200)
    expected = Color(100, 100, 100, 150)

    assert transform.transform(color) == expected


def test_append():
    transform1 = ColorTransform(
        red_mult=123,
        green_mult=156,
        blue_mult=230,
        alpha_mult=256,
        red_add=42,
        green_add=66,
        blue_add=120,
        alpha_add=58,
    )

    transform2 = ColorTransform(
        red_mult=150,
        green_mult=200,
        blue_mult=120,
        alpha_mult=256,
        red_add=-50,
        green_add=-20,
        blue_add=5,
        alpha_add=0,
    )

    combined = transform1.append(transform2)

    assert combined.red_mult == 72
    assert combined.green_mult == 121
    assert combined.blue_mult == 107
    assert combined.alpha_mult == 256
    assert combined.red_add == -26
    assert combined.green_add == 31
    assert combined.blue_add == 61
    assert combined.alpha_add == 58


def test_read():
    reader = fixture_reader(fixture("1317.swf"), 2828)

    transform = ColorTransform.read(reader, True)

    assert transform.red_mult == 85
    assert transform.green_mult == 85
    assert transform.blue_mult == 85
    assert transform.alpha_mult == 256
    assert transform.red_add == 170
    assert transform.green_add == 170
    assert transform.blue_add == 170
    assert transform.alpha_add == 0
