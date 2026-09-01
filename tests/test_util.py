"""PHP semantics helpers: the traps that decide whether goldens match."""

from __future__ import annotations

import math

import pytest

from prespyc._util import decode_swf_text, num, php_intdiv, php_json_encode, php_mod, php_round, round_int, to_int32


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (1.0, "1"),
        (-0.0, "-0"),
        (0.5, "0.5"),
        (25.35, "25.35"),
        (0.1 + 0.2, "0.3"),
        (-0.3492, "-0.3492"),
        (0.0001, "0.0001"),
        (1e-5, "1.0E-5"),
        (1e25, "1.0E+25"),
        (3, "3"),
        (math.inf, "INF"),
        (-math.inf, "-INF"),
        (math.nan, "NAN"),
    ],
)
def test_num_matches_php_string_cast(value, expected):
    assert num(value) == expected


@pytest.mark.parametrize(
    ("value", "precision", "expected"),
    [
        (2.675, 2, 2.68),  # Python's round() gives 2.67
        (0.285, 2, 0.29),
        (2.5, 0, 3.0),  # half away from zero, not half to even
        (-2.5, 0, -3.0),
        (1.0, 4, 1.0),
        (0.0, 4, 0.0),
    ],
)
def test_php_round_rounds_half_away_from_zero(value, precision, expected):
    assert php_round(value, precision) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (2.5, 3),
        (-2.5, -3),
        (0.4, 0),
        (-0.6, -1),
        (2.4999999999999996, 3),  # PHP pre-rounds to 15 significant digits first
        (1e15, 10**15),
    ],
)
def test_round_int(value, expected):
    assert round_int(value) == expected


def test_php_intdiv_and_mod_truncate_toward_zero():
    assert php_intdiv(-7, 2) == -3
    assert php_mod(-7, 2) == -1
    assert php_mod(7, -2) == 1


def test_to_int32_wraps():
    assert to_int32(0xFFFFFFFF) == -1
    assert to_int32(0x80000000) == -2147483648
    assert to_int32(5) == 5


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, "null"),
        (True, "true"),
        (False, "false"),
        (3, "3"),
        (1.0, "1"),  # JSON_PRESERVE_ZERO_FRACTION is off by default
        (0.0, "0"),
        (-0.0, "-0"),
        (1.5, "1.5"),
        ("a/b", '"a\\/b"'),
        ("é", '"\\u00e9"'),
        ([1, 2.0], "[1,2]"),
        ({"b": 1, "a": 2}, '{"b":1,"a":2}'),  # insertion order, not sorted
    ],
)
def test_php_json_encode(value, expected):
    assert php_json_encode(value) == expected


def test_gradient_hash_matches_the_golden_svg():
    """
    The id in `tests/fixtures/extractor/shape_with_radial_gradient.svg`.

    Guards the whole hashing chain at once: PHP property order, PHP's integral-float rule and
    xxh128. Getting any of it wrong renames every gradient and fails 229 goldens.
    """
    from prespyc._util import xxh128

    payload = {
        "matrix": {
            "scaleX": 0.26959228515625,
            "scaleY": 0.26959228515625,
            "rotateSkew0": 0.0,
            "rotateSkew1": 0.0,
            "translateX": -5445,
            "translateY": -1990,
        },
        "gradient": {
            "spreadMode": 0,
            "interpolationMode": 0,
            "records": [
                {"ratio": 0, "color": {"red": 166, "green": 106, "blue": 47, "alpha": None}},
                {"ratio": 255, "color": {"red": 199, "green": 128, "blue": 56, "alpha": None}},
            ],
        },
    }

    assert "R" + xxh128(php_json_encode(payload)) == "R710d8a9e847219d07818370f16922e18"


def test_decode_swf_text():
    assert decode_swf_text(b"\xe9", 5) == "é"  # latin-1 before SWF 6
    assert decode_swf_text(b"\xc3\xa9", 6) == "é"  # utf-8 from SWF 6
