"""DefineFontInfo and DefineFontInfo2 tags."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class DefineFontInfoTag:
    """The name, style and code table of a `DefineFontTag` glyph set."""

    TYPE_V1: ClassVar[int] = 13
    TYPE_V2: ClassVar[int] = 62

    version: int
    font_id: int
    font_name: bytes
    font_flags_small_text: bool
    font_flags_shift_jis: bool
    font_flags_ansi: bool
    font_flags_italic: bool
    font_flags_bold: bool
    font_flags_wide_codes: bool
    code_table: list[int]
    language_code: int | None = None

    @classmethod
    def read(cls, reader: Reader, version: int, end: int) -> Self:
        """
        Read a DefineFontInfo or DefineFontInfo2 tag from the reader.

        `version` is the version of the tag, either 1 or 2. `end` is the end byte offset of the tag.
        """
        font_id = reader.read_ui16()
        font_name = reader.read_bytes(reader.read_ui8())

        flags = reader.read_ui8()
        # 2 bits reserved
        small_text = (flags & 0b00100000) != 0
        shift_jis = (flags & 0b00010000) != 0
        ansi = (flags & 0b00001000) != 0
        italic = (flags & 0b00000100) != 0
        bold = (flags & 0b00000010) != 0
        # Version 2 always has wide codes (i.e. use 16 bits for codes)
        wide_codes = (flags & 0b00000001) != 0 or version > 1

        language_code = reader.read_ui8() if version > 1 else None
        code_table = _read_wide_code_table(reader, end) if wide_codes else _read_ascii_code_table(reader, end)

        return cls(
            version=version,
            font_id=font_id,
            font_name=font_name,
            font_flags_small_text=small_text,
            font_flags_shift_jis=shift_jis,
            font_flags_ansi=ansi,
            font_flags_italic=italic,
            font_flags_bold=bold,
            font_flags_wide_codes=wide_codes,
            code_table=code_table,
            language_code=language_code,
        )


def _read_wide_code_table(reader: Reader, end: int) -> list[int]:
    code_table = []

    while reader.offset < end:
        code_table.append(reader.read_ui16())

    return code_table


def _read_ascii_code_table(reader: Reader, end: int) -> list[int]:
    code_table = []

    while reader.offset < end:
        code_table.append(reader.read_ui8())

    return code_table
