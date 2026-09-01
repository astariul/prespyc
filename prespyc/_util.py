"""
PHP semantics helpers.

The port must reproduce ArakneSwf's output byte for byte, and a few PHP operations do not behave
like their Python spelling. Every arithmetic or formatting operation listed in `CONVENTIONS.md`
§4 must go through this module.
"""

from __future__ import annotations

import json
import math
import os
import sys
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

__all__ = [
    "decode_swf_text",
    "memory_total",
    "memory_used",
    "num",
    "php_intdiv",
    "php_json_encode",
    "php_mod",
    "php_round",
    "round_int",
    "to_int32",
    "xxh128",
]


def php_round(value: float, precision: int = 0) -> float:
    """
    PHP `round()`: round half away from zero.

    Python's `round()` rounds half to even, and does it on the raw double. PHP first pre-rounds the
    value to the precision the double actually carries (~15 significant digits), so
    `round(2.675, 2)` is `2.68` in PHP but `2.67` in Python. Going through the shortest round-trip
    decimal representation reproduces that pre-rounding.
    """
    if not math.isfinite(value) or value == 0.0:
        return float(value)

    quantum = Decimal(1).scaleb(-precision)
    return float(Decimal(repr(float(value))).quantize(quantum, rounding=ROUND_HALF_UP))


def round_int(value: float) -> int:
    """
    PHP `(int) round($value)`.

    Hot path: called for every transformed coordinate. The fast path avoids `php_round()` and only
    falls back to it when the value sits close enough to a tie for the pre-rounding to matter.
    """
    negative = value < 0
    v = -value if negative else value

    i = int(v)  # truncation, so floor for a positive value
    frac = v - i

    if frac >= 0.5:
        i += 1
    elif frac > 0.49999999 and float(f"{v:.15g}") - i >= 0.5:
        # Close enough to a tie that PHP's pre-rounding pushed it over.
        i += 1

    return -i if negative else i


def php_intdiv(a: int, b: int) -> int:
    """PHP `intdiv()`: truncates toward zero, where Python's `//` floors."""
    q = abs(a) // abs(b)
    return -q if (a < 0) != (b < 0) else q


def php_mod(a: int, b: int) -> int:
    """PHP `%`: the sign follows the dividend, where Python's follows the divisor."""
    r = abs(a) % abs(b)
    return -r if a < 0 else r


def to_int32(value: int) -> int:
    """Wrap an integer to a signed 32 bit value, as ActionScript bitwise operators do."""
    value &= 0xFFFFFFFF
    return value - 0x100000000 if value >= 0x80000000 else value


def num(value: float | int) -> str:
    """
    Format a number the way PHP casts it to a string (`precision=14`).

    Trailing zeros and the decimal point are dropped, so `1.0` renders as `1` and `-0.0` as `-0`.
    Mandatory for every number written into SVG output.
    """
    if isinstance(value, int):
        return str(value)

    v = float(value)

    if math.isnan(v):
        return "NAN"
    if math.isinf(v):
        return "INF" if v > 0 else "-INF"

    text = f"{v:.14G}"

    if "E" in text:
        # PHP renders the exponent form as `1.0E+25`: a mantissa that always has a decimal part,
        # and an exponent without padding zeros.
        mantissa, _, exponent = text.partition("E")
        if "." not in mantissa:
            mantissa += ".0"
        e = int(exponent)
        return f"{mantissa}E{'+' if e >= 0 else '-'}{abs(e)}"

    return text


def decode_swf_text(raw: bytes, swf_version: int) -> str:
    """Decode a SWF string: UTF-8 from SWF 6 onwards, Latin-1 before."""
    if swf_version >= 6:
        return raw.decode("utf-8", errors="replace")

    return raw.decode("latin-1")


def php_json_encode(value: Any) -> str:
    r"""
    Serialise a value exactly as PHP's `json_encode()` does.

    Not interchangeable with `json.dumps`. The fill type ids that end up in SVG `id` attributes are
    `xxh128(json_encode($fillType))`, so any difference in the JSON text changes the id and breaks
    every gradient golden. Three PHP behaviours matter:

    - no spaces between tokens;
    - a float with no fractional part is written as an **integer** (`1.0` → `1`, `0.0` → `0`), since
      `JSON_PRESERVE_ZERO_FRACTION` is off by default;
    - `/` is escaped as `\/` and non-ASCII is escaped as `\uXXXX`.

    Mapping keys are emitted in insertion order, so a dict standing in for a PHP object must declare
    its keys in the same order as the PHP class declares its properties, with PHP's camelCase names.
    """
    if value is None:
        return "null"

    if value is True:
        return "true"

    if value is False:
        return "false"

    if isinstance(value, int):
        return str(value)

    if isinstance(value, float):
        return _php_json_float(value)

    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=True).replace("/", "\\/")

    if isinstance(value, dict):
        return "{" + ",".join(f"{php_json_encode(str(k))}:{php_json_encode(v)}" for k, v in value.items()) + "}"

    if isinstance(value, (list, tuple)):
        return "[" + ",".join(php_json_encode(item) for item in value) + "]"

    raise TypeError(f"Cannot JSON encode {type(value).__name__}")


def _php_json_float(value: float) -> str:
    if value == 0.0:
        return "-0" if math.copysign(1.0, value) < 0 else "0"

    if value.is_integer() and abs(value) < 1e15:
        return str(int(value))

    return repr(value)


def xxh128(data: bytes | str) -> str:
    """PHP `hash('xxh128', ...)`: the 128 bit XXH3 digest, as lowercase hex."""
    import xxhash

    if isinstance(data, str):
        data = data.encode("utf-8")

    return xxhash.xxh128_hexdigest(data)


def memory_used() -> int:
    """Resident memory of the current process, in bytes."""
    try:
        with open("/proc/self/statm") as statm:
            return int(statm.read().split()[1]) * os.sysconf("SC_PAGE_SIZE")
    except (OSError, IndexError, ValueError):
        import resource

        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024


def memory_total() -> int:
    """
    Total physical memory, in bytes.

    Stands in for PHP's `memory_limit`, which has no Python equivalent.
    """
    try:
        return os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")
    except (OSError, ValueError):
        return sys.maxsize
