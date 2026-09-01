"""Metadata tag: the RDF/XMP description of the file."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class MetadataTag:
    """An XML (RDF) description of the file, for search engines."""

    TYPE: ClassVar[int] = 77

    metadata: bytes

    @classmethod
    def read(cls, reader: Reader) -> Self:
        return cls(reader.read_null_terminated_string())
