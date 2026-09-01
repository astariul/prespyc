"""ProductInfo tag: which product generated the file."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class ProductInfo:
    """
    Attach information about the product that created the SWF file.

    Note: this tag is not documented in the official SWF documentation.

    See https://www.m2osw.com/swf_tag_productinfo
    """

    TYPE: ClassVar[int] = 41

    product_id: int
    edition: int
    major_version: int
    minor_version: int
    build_number: int
    compilation_date: int

    @classmethod
    def read(cls, reader: Reader) -> Self:
        return cls(
            product_id=reader.read_ui32(),
            edition=reader.read_ui32(),
            major_version=reader.read_ui8(),
            minor_version=reader.read_ui8(),
            build_number=reader.read_si64(),
            compilation_date=reader.read_si64(),
        )
