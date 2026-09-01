"""ImportAssets and ImportAssets2 tags: characters borrowed from another SWF."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class ImportAssetsTag:
    """Characters imported from another SWF file, by their exported name."""

    TYPE_V1: ClassVar[int] = 57
    TYPE_V2: ClassVar[int] = 71

    version: int
    """The version of the ImportAssets tag: either 1 or 2, depending on the tag type."""

    url: bytes
    """Path, or URL, of the SWF to import."""

    characters: dict[int, bytes]
    """
    Map of character ids to their names.

    The value is the exported name in the other SWF, and the key is the character id in the current
    SWF (it will be defined into the dictionary).
    """

    @classmethod
    def read(cls, reader: Reader, version: int) -> Self:
        url = reader.read_null_terminated_string()

        if version == 2:
            reader.skip_bytes(1)  # Reserved, must be 1
            reader.skip_bytes(1)  # Reserved, must be 0

        characters: dict[int, bytes] = {}
        count = reader.read_ui16()

        for _ in range(count):
            character_id = reader.read_ui16()
            characters[character_id] = reader.read_null_terminated_string()

        return cls(version=version, url=url, characters=characters)
