"""ExportAssets tag: gives characters a name so another SWF, or the host, can reference them."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class ExportAssetsTag:
    """Names exported by this SWF, one entry per exported character."""

    TYPE: ClassVar[int] = 56

    characters: dict[int, bytes]
    """Map of exported character ids to their names."""

    @classmethod
    def read(cls, reader: Reader) -> Self:
        characters: dict[int, bytes] = {}
        count = reader.read_ui16()

        for _ in range(count):
            if reader.offset >= reader.end:
                break

            character_id = reader.read_ui16()
            characters[character_id] = reader.read_null_terminated_string()

        return cls(characters)
