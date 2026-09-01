"""Port of ArakneSwf's `tests/Avm/Api/ScriptObjectTest.php`."""

from __future__ import annotations

from typing import Any

from prespyc._util import php_json_encode
from prespyc.avm.api.script_object import ScriptObject


def test_simple_properties() -> None:
    o = ScriptObject()

    assert o.foo is None
    assert o["foo"] is None
    assert o.has_property("foo") is False
    assert "foo" not in o
    assert False not in o

    o.foo = 123
    assert o.foo == 123
    assert o["foo"] == 123
    assert o.has_property("foo") is True
    assert "foo" in o

    args: list[Any] = []

    def bar(*arguments: Any) -> int:
        args[:] = arguments
        return 42

    o.bar = bar

    assert o.bar("a", "b", "c") == 42
    assert args == ["a", "b", "c"]

    o[False] = 123
    assert o[False] is None
    assert False not in o


def test_computed_property_read_only() -> None:
    o = ScriptObject()
    counter = 0

    def getter() -> int:
        nonlocal counter
        counter += 1
        return counter

    assert o.add_property("foo", getter) is True

    assert o.foo == 1
    assert o.foo == 2

    # Read-only: the write is dropped, so the getter keeps counting.
    o.foo = 42
    assert o.foo == 3


def test_computed_property_read_write() -> None:
    o = ScriptObject()

    def setter(value: Any) -> None:
        o.firstName, o.lastName = value.split(" ")

    # `or ''` stands in for PHP's concatenation of a null property.
    assert o.add_property("name", lambda: f"{o.firstName or ''} {o.lastName or ''}", setter) is True

    assert o.name == " "

    o.name = "John Doe"
    assert o.name == "John Doe"
    assert o.firstName == "John"
    assert o.lastName == "Doe"

    o.firstName = "Jane"
    assert o.name == "Jane Doe"
    assert o.firstName == "Jane"
    assert o.lastName == "Doe"


def test_add_property_invalid_name() -> None:
    o = ScriptObject()
    assert o.add_property("", lambda: 42) is False

    assert "" not in o


def test_to_json() -> None:
    o = ScriptObject()
    o.foo = 123
    o.add_property("bar", lambda: 42)
    o[21] = "hello"

    assert php_json_encode(o.json_serialize()) == '{"foo":123,"21":"hello","bar":42}'
