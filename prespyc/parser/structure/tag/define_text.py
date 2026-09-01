"""DefineText and DefineText2 tags."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.errors import Errors, InvalidDataError
from prespyc.parser.structure.record.matrix import Matrix
from prespyc.parser.structure.record.rectangle import Rectangle
from prespyc.parser.structure.record.text_record import TextRecord

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class DefineTextTag:
    """A static text character: glyph runs positioned by a transformation matrix."""

    TYPE_V1: ClassVar[int] = 11
    TYPE_V2: ClassVar[int] = 33

    version: int
    character_id: int
    text_bounds: Rectangle
    text_matrix: Matrix
    glyph_bits: int
    advance_bits: int
    text_records: list[TextRecord]

    @classmethod
    def read(cls, reader: Reader, version: int) -> Self:
        """
        Read a DefineText or DefineText2 tag from the reader.

        `version` is the version of the tag, either 1 or 2. The version 2 handles the alpha channel
        in `TextRecord`.
        """
        character_id = reader.read_ui16()
        text_bounds = Rectangle.read(reader)
        text_matrix = Matrix.read(reader)
        glyph_bits = reader.read_ui8()
        advance_bits = reader.read_ui8()

        if glyph_bits > 32 or advance_bits > 32:
            if reader.errors & Errors.INVALID_DATA:
                raise InvalidDataError(
                    f"Glyph bits ({glyph_bits}) or advance bits ({advance_bits}) are out of bounds (0-32)",
                    reader.offset,
                )

            text_records: list[TextRecord] = []
        else:
            text_records = TextRecord.read_collection(reader, glyph_bits, advance_bits, with_alpha=version > 1)

        return cls(
            version=version,
            character_id=character_id,
            text_bounds=text_bounds,
            text_matrix=text_matrix,
            glyph_bits=glyph_bits,
            advance_bits=advance_bits,
            text_records=text_records,
        )
