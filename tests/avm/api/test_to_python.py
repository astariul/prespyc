"""`to_python()`: script values as plain Python values."""

from __future__ import annotations

import prespyc
from prespyc.avm.api.script_array import ScriptArray
from prespyc.avm.api.script_object import ScriptObject
from tests.support import fixture


def test_object_stays_a_dict_when_its_keys_are_indices() -> None:
    table = ScriptObject({0: "a", 1: "b"})

    assert prespyc.to_python(table) == {0: "a", 1: "b"}


def test_array_becomes_a_list() -> None:
    assert prespyc.to_python(ScriptArray(1, 2)) == [1, 2]


def test_nested_values_are_converted() -> None:
    value = ScriptObject({"name": b"well", "skills": [ScriptObject({0: 102})]})

    assert prespyc.to_python(value) == {"name": "well", "skills": [{0: 102}]}


def test_variables_of_a_file() -> None:
    variables = prespyc.open(fixture("objects.swf")).variables

    assert prespyc.to_python(variables) == {
        "bag": {"a": 1, "b": False},
        "arr": [1, 2],
        "inlined_object": {"d": "hello", "c": 1.3},
        "inlined_array": [1, 2, 3],
        "get_member": 1,
        "array_access": 2,
        "get_member_str": False,
    }
