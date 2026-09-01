"""
Port of the `execute()` / `variables()` test methods of ArakneSwf's `tests/SwfFileTest.php`.

The rest of `SwfFileTest` lives elsewhere.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

import pytest

from prespyc._util import php_json_encode
from prespyc.avm.api.script_array import ScriptArray
from prespyc.avm.api.script_object import ScriptObject, to_json_value
from prespyc.swf_file import SwfFile
from tests.support import fixture


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        pytest.param(
            "objects",
            {
                "bag": ScriptObject({"a": 1, "b": False}),
                "arr": ScriptArray(1, 2),
                "inlined_object": ScriptObject({"d": "hello", "c": 1.3}),
                "inlined_array": [1, 2, 3],
                "get_member": 1,
                "array_access": 2,
                "get_member_str": False,
            },
            id="objects",
        ),
        pytest.param(
            "simple",
            {
                "simple_int": 123,
                "simple_string": "abc",
                "simple_float": 1.23,
                "simple_bool": True,
                "simple_null": None,
            },
            id="simple",
        ),
        pytest.param(
            "big",
            {
                "big_int": 1234567890,
                "negative_int": -1234567890,
                "big_float": 1234567890123.1235,
                "negative_float": -1234567890123.1235,
            },
            id="big",
        ),
        pytest.param(
            "cast",
            {
                "str_to_number": 1234.0,
                "float_to_str": "1234.5678",
                "int_to_bool": True,
            },
            id="cast",
        ),
    ],
)
def test_variables(name: str, expected: dict[str, Any]) -> None:
    swf = SwfFile(fixture(f"{name}.swf"))

    assert swf.variables == expected


def test_execute() -> None:
    file = SwfFile(fixture("lang_fr_801.swf"))

    state = file.execute()
    assert state.stack == []
    assert len(state.constants) == 1701

    assert state.variables["VERSION"] == 801
    assert isinstance(state.variables["VERSION"], int)
    assert state.variables["CHAT_MENU"] == "Menu du chat"
    assert state.variables["C"]["DEFAULT_COMMUNITY"] == "FR,0"
    assert state.variables["C"]["DELAY_RECO_START"] == 180000.0
    assert isinstance(state.variables["C"]["DELAY_RECO_START"], float)

    encoded = php_json_encode(to_json_value(state.variables))

    # Compared decoded, so that a failure points at the variable that differs. Going through JSON
    # also normalises the keys: PHP array keys — and so the port's — are ints when they look like
    # ints, while JSON object keys are always strings.
    expected = json.loads(fixture("lang_fr_801.json").read_text(encoding="utf-8"))

    assert json.loads(encoded) == expected

    # ArakneSwf's own assertion, which additionally pins key order and number formatting.
    assert hashlib.md5(encoded.encode()).hexdigest() == "44fada8d52329bcd9dddb9259c305897"
