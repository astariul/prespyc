"""Facade over a parsed SWF file: header, tags and character dictionary."""

from __future__ import annotations

from typing import Self

from prespyc.errors import Errors
from prespyc.parser.reader import Reader
from prespyc.parser.structure.header import Header
from prespyc.parser.structure.raw_tag import RawTag
from prespyc.parser.structure.record.rectangle import Rectangle



class Swf:
    """A parsed SWF file. Tag *headers* are read eagerly, tag *bodies* on demand."""

    __slots__ = ("_reader", "dictionary", "header", "tags")

    def __init__(self, reader: Reader, header: Header, tags: list[RawTag], dictionary: dict[int, RawTag]) -> None:
        self._reader = reader

        self.header = header

        self.tags = tags
        """All tags contained in the SWF file."""

        self.dictionary = dictionary
        """All `DefineXxx` tags, indexed by character id."""

    def parse(self, tag: RawTag) -> object:
        """Parse the body of a tag."""
        return tag.parse(self._reader, self.header.version)

    @classmethod
    def from_bytes(cls, data: bytes, errors: int = Errors.ALL) -> Self:
        """Parse SWF data from a buffer."""
        return cls.read(Reader(data, errors=errors))

    @classmethod
    def read(cls, reader: Reader) -> Self:
        """Parse the header and all tag headers from a reader."""
        signature = reader.read_bytes(3)

        if signature == b"CWS":
            compressed = True
        elif signature == b"FWS":
            compressed = False
        else:
            raise ValueError(f"Unsupported SWF signature: {signature.decode('latin-1')}")

        version = reader.read_ui8()
        file_length = reader.read_ui32()

        if file_length < 8:
            raise ValueError(f"Invalid SWF file length: {file_length}")

        if compressed:
            reader = reader.uncompress(file_length)

        header = Header(
            signature=signature.decode("ascii"),
            version=version,
            file_length=file_length,
            frame_size=Rectangle.read(reader),
            frame_rate=reader.read_fixed8(),
            frame_count=reader.read_ui16(),
        )

        tags: list[RawTag] = []
        dictionary: dict[int, RawTag] = {}

        for tag in RawTag.read_all(reader):
            tags.append(tag)

            if tag.id is not None:
                dictionary[tag.id] = tag

        return cls(reader, header, tags, dictionary)
