"""Port of ArakneSwf's `tests/Avm/Api/ScriptArrayTest.php`."""

from __future__ import annotations

from prespyc._util import php_json_encode
from prespyc.avm.api.script_array import ScriptArray


def _json(array: ScriptArray) -> str:
    return php_json_encode(array.json_serialize())


def test_empty() -> None:
    a = ScriptArray()

    assert a.length == 0
    assert _json(a) == "[]"

    assert a[0] is None
    assert a.foo is None
    assert 0 not in a
    assert a.has_property("0") is False


def test_single_constructor_parameter() -> None:
    a = ScriptArray(3)

    assert a.length == 3
    assert _json(a) == "[null,null,null]"


def test_array_constructor() -> None:
    a = ScriptArray(1, 2, 3)

    assert a.length == 3
    assert _json(a) == "[1,2,3]"
    assert a[0] == 1
    assert a[1] == 2
    assert a[2] == 3
    assert 0 in a
    assert 1 in a
    assert 2 in a
    assert 3 not in a


def test_set_length() -> None:
    a = ScriptArray(1, 2, 3)
    a.length = 5

    assert a.length == 5
    assert _json(a) == "[1,2,3,null,null]"

    a.length = 2
    assert a.length == 2
    assert _json(a) == "[1,2]"

    a.length = 0
    assert a.length == 0
    assert _json(a) == "[]"


def test_offset_set() -> None:
    a = ScriptArray()

    a[0] = "foo"
    a[1] = "bar"
    a[2] = "baz"

    assert a.length == 3
    assert _json(a) == '["foo","bar","baz"]'


def test_unset_should_not_modify_length() -> None:
    a = ScriptArray(1, 2, 3)

    del a[1]

    assert a.length == 3
    assert _json(a) == "[1,null,3]"


def test_integer_float_index() -> None:
    a = ScriptArray()

    a[0] = "foo"
    a[1.0] = "bar"

    assert a.length == 2
    assert _json(a) == '["foo","bar"]'

    assert a[0.0] == "foo"
    assert a[1] == "bar"


def test_invalid_index() -> None:
    a = ScriptArray()

    a["foo"] = "bar"
    a[42] = "baz"

    assert a.length == 1
    assert _json(a) == '{"42":"baz","foo":"bar"}'

    del a["foo"]
    assert a.length == 1
    assert _json(a) == '{"42":"baz"}'

    del a[42]
    assert a.length == 1
    assert _json(a) == '{"42":null}'
