"""ActionScript `Array`: a `ScriptObject` with an indexed value store and a `length` property."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any, ClassVar

from prespyc.avm.api.script_object import ScriptObject, array_key, is_int, php_array

if TYPE_CHECKING:
    from collections.abc import Iterator


class ScriptArray(ScriptObject):
    """
    Emulates an ActionScript `Array` object.

    Indexed values live in their own store, so `arr[0]` and `arr.foo` do not collide, and the
    computed `length` property reads and resizes that store. Built with a single integer argument,
    the array is pre-filled with that many `None` values — as `new Array(5)` does in ActionScript.

    Beware: the store is a *sparse* map, not a list, because ActionScript (like PHP) lets an
    arbitrary index be written: `arr[42] = 'x'` on an empty array leaves `length` at 1.
    """

    __slots__ = ("values",)

    _INTERNAL: ClassVar[frozenset[str]] = ScriptObject._INTERNAL | frozenset({"values"})

    def __init__(self, *values: Any) -> None:
        super().__init__()

        if len(values) == 1 and is_int(values[0]):
            self.values: dict[int, Any] = dict.fromkeys(range(values[0]))
        else:
            self.values = dict(enumerate(values))

        self.add_property("length", lambda: len(self.values), self._set_length)

    def json_serialize(self) -> list[Any] | dict[Any, Any]:
        # Computed properties are ignored, so `length` is not part of the output.
        merged = dict(self.values)

        for key, value in self.properties.items():
            merged.setdefault(key, value)

        return php_array(merged)

    def items(self) -> Iterator[tuple[Any, Any]]:
        yield from self.values.items()

    def __contains__(self, key: Any) -> bool:
        return self.values.get(array_key(key)) is not None or super().__contains__(key)

    def __getitem__(self, key: Any) -> Any:
        value = self.values.get(array_key(key))

        if value is not None:
            return value

        return super().__getitem__(key)

    def __setitem__(self, key: Any, value: Any) -> None:
        if _is_index(key):
            self.values[int(key)] = value
            return

        # A non-index key — including a numeric *string* — lands in the property store instead.
        super().__setitem__(key, value)

    def __delitem__(self, key: Any) -> None:
        if _is_index(key):
            # Blanking the entry rather than removing it, so `length` does not change. The entry is
            # created when it does not exist yet, which does grow `length`.
            self.values[array_key(key)] = None
            return

        super().__delitem__(key)

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return NotImplemented

        return self.values == other.values and super().__eq__(other)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({list(self.values.values())!r})"

    def _set_length(self, length: int) -> None:
        if length == 0:
            self.values = {}
            return

        current_length = len(self.values)

        if length < current_length:
            # PHP's array_slice() drops the extra entries and reindexes from 0.
            self.values = dict(enumerate(list(self.values.values())[:length]))
            return

        for _ in range(current_length, length):
            self._append(None)

    def _append(self, value: Any) -> None:
        """PHP `$array[] = $value`: store under the next free integer key."""
        next_key = max((key for key in self.values if is_int(key)), default=-1) + 1
        self.values[next_key] = value


def _is_index(key: Any) -> bool:
    """Whether the key addresses the indexed store: an integer, or a float that is one."""
    return is_int(key) or (isinstance(key, float) and math.isfinite(key) and key == int(key))
