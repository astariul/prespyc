"""ActionScript `Object`: a property bag with optional computed properties."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

ScriptKey = str | int
"""An ActionScript property name, or an array index."""


def is_int(value: Any) -> bool:
    """
    PHP `is_int()`.

    Unlike `isinstance(value, int)`, a bool is **not** an integer: PHP's `is_int(false)` is false,
    and several AVM branches depend on it.
    """
    return isinstance(value, int) and not isinstance(value, bool)


def array_key(key: Any) -> Any:
    """
    Coerce a value the way PHP coerces an array key.

    PHP arrays only accept `int` and `string` keys: a bool or a float is cast to `int`, `null`
    becomes `''`, and a *canonical* decimal integer string becomes an `int` — so `$a['21']` and
    `$a[21]` are the same entry. The port keeps the same key space so that a property written as a
    string is read back as an int, and vice versa.
    """
    if isinstance(key, bool):
        return int(key)

    if isinstance(key, float):
        return int(key)

    if key is None:
        return ""

    if isinstance(key, str):
        try:
            as_int = int(key)
        except ValueError:
            return key

        # Only the canonical spelling is normalised: '021', ' 21' and '+21' stay strings.
        return as_int if str(as_int) == key else key

    return key


def php_array(array: dict[Any, Any]) -> list[Any] | dict[Any, Any]:
    """
    Render a PHP array the way `json_encode()` sees it.

    A PHP array is a single ordered map, and `json_encode()` writes it as a JSON array only when
    its keys are exactly `0..n-1` in that order; otherwise as a JSON object. Python has two
    separate types, so the decision has to be made explicitly.
    """
    if all(key == index for index, key in enumerate(array)):
        return list(array.values())

    return array


def to_json_value(value: Any) -> Any:
    """
    Convert a script value into something `php_json_encode()` accepts.

    Reproduces the recursion of PHP's `json_encode()`: `JsonSerializable` objects are replaced by
    `json_serialize()`, enums by their backing value, and other objects by their properties.
    """
    if isinstance(value, ScriptObject):
        return to_json_value(value.json_serialize())

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")

    if isinstance(value, dict):
        return php_array({key: to_json_value(item) for key, item in value.items()})

    if isinstance(value, (list, tuple)):
        return [to_json_value(item) for item in value]

    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: to_json_value(getattr(value, field.name)) for field in fields(value)}

    if callable(value):
        # PHP writes a closure as an empty object.
        return {}

    return value


def _keyed(mapping: dict[Any, Any] | None) -> dict[Any, Any]:
    """Copy a mapping, coercing its keys as PHP does — an array literal is already normalised."""
    if mapping is None:
        return {}

    return {array_key(key): value for key, value in mapping.items()}


class ScriptObject:
    """
    Base object for ActionScript objects.

    A property is reachable both as an attribute (`obj.foo`, PHP's `__get`/`__set`) and as an item
    (`obj["foo"]`, PHP's `ArrayAccess`); both hit the same store. `add_property()` registers a
    *computed* property, whose getter and setter shadow that store.
    """

    __slots__ = ("getters", "properties", "setters")

    _INTERNAL: ClassVar[frozenset[str]] = frozenset({"getters", "properties", "setters"})
    """Attribute names that hold real Python state, and so are not ActionScript properties."""

    def __init__(
        self,
        properties: dict[ScriptKey, Any] | None = None,
        getters: dict[ScriptKey, Callable[[], Any]] | None = None,
        setters: dict[ScriptKey, Callable[[Any], None]] | None = None,
    ) -> None:
        # Bypass __setattr__, which would treat these as ActionScript properties.
        object.__setattr__(self, "properties", _keyed(properties))
        object.__setattr__(self, "getters", _keyed(getters))
        object.__setattr__(self, "setters", _keyed(setters))

    def add_property(
        self,
        name: str,
        getter: Callable[[], Any],
        setter: Callable[[Any], None] | None = None,
    ) -> bool:
        """
        Define a computed property, overwriting any property of the same name.

        Without a `setter` the property is read-only: writing to it is silently ignored. Returns
        `False` when the name is invalid, i.e. empty.
        """
        if name == "":
            return False

        self.getters[array_key(name)] = getter

        if setter is not None:
            self.setters[array_key(name)] = setter

        return True

    def has_property(self, name: ScriptKey) -> bool:
        """
        Whether the property is set to a non-`None` value, i.e. PHP's `isset($obj->name)`.

        Beware: like `isset()`, a property explicitly set to `None` counts as missing.
        """
        key = array_key(name)

        return self.properties.get(key) is not None or self.getters.get(key) is not None

    def json_serialize(self) -> list[Any] | dict[Any, Any]:
        """The plain properties plus the computed ones, as PHP's `jsonSerialize()` returns them."""
        properties = dict(self.properties)

        for name, getter in self.getters.items():
            properties[name] = getter()

        return php_array(properties)

    def items(self) -> Iterator[tuple[ScriptKey, Any]]:
        """Iterate over `(name, value)` pairs, computed properties last."""
        yield from self.properties.items()

        for name, getter in self.getters.items():
            yield name, getter()

    def __len__(self) -> int:
        return len(self.properties) + len(self.getters)

    def __iter__(self) -> Iterator[ScriptKey]:
        return (name for name, _ in self.items())

    def __contains__(self, key: Any) -> bool:
        if not isinstance(key, str) and not is_int(key):
            return False

        return self.has_property(key)

    def __getitem__(self, key: Any) -> Any:
        return self._property_value(key)

    def __setitem__(self, key: Any, value: Any) -> None:
        self._set_property_value(key, value)

    def __delitem__(self, key: Any) -> None:
        self.properties.pop(array_key(key), None)

    def __getattr__(self, name: str) -> Any:
        # Internal slots read before __init__ ran, and every dunder, must keep raising: returning
        # None for `__deepcopy__` & co. would break the protocols that probe for them.
        if name in self._INTERNAL or (name.startswith("__") and name.endswith("__")):
            raise AttributeError(name)

        return self._property_value(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self._INTERNAL:
            object.__setattr__(self, name, value)
            return

        self._set_property_value(name, value)

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return NotImplemented

        return (
            self.properties == other.properties
            and self.getters.keys() == other.getters.keys()
            and self.setters.keys() == other.setters.keys()
        )

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.properties!r})"

    def _property_value(self, key: Any) -> Any:
        if not isinstance(key, str) and not is_int(key):
            return None

        key = array_key(key)
        getter = self.getters.get(key)

        if getter is not None:
            return getter()

        return self.properties.get(key)

    def _set_property_value(self, key: Any, value: Any) -> None:
        if not isinstance(key, str) and not is_int(key):
            return

        key = array_key(key)
        setter = self.setters.get(key)

        if setter is not None:
            setter(value)
            return

        self.properties[key] = value
