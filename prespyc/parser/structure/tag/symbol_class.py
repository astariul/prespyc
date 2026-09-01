"""SymbolClass tag: binds characters to ActionScript 3 classes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class SymbolClassTag:
    """The AS3 class bound to each exported character."""

    TYPE: ClassVar[int] = 76

    symbols: dict[int, bytes]
    """Map of symbol id (character id) to symbol name (AS3 class name)."""

    @classmethod
    def read(cls, reader: Reader) -> Self:
        symbols: dict[int, bytes] = {}
        count = reader.read_ui16()

        for _ in range(count):
            symbol_id = reader.read_ui16()
            name = reader.read_null_terminated_string()

            symbols[symbol_id] = name

        return cls(symbols)
