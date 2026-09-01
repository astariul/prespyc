"""DefineFontAlignZones tag."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.record.zone_record import ZoneRecord

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class DefineFontAlignZonesTag:
    """The glyph alignment zones of a font, used by the advanced text rendering engine."""

    TYPE: ClassVar[int] = 73

    font_id: int
    csm_table_hint: int
    zone_table: list[ZoneRecord]

    @classmethod
    def read(cls, reader: Reader, end: int) -> Self:
        """Read a DefineFontAlignZones tag, whose data ends at the `end` byte offset."""
        font_id = reader.read_ui16()
        flags = reader.read_ui8()

        csm_table_hint = (flags >> 6) & 3  # 2 bits CSMTableHint
        # 6 bits reserved

        zone_table = ZoneRecord.read_collection(reader, end)

        return cls(
            font_id=font_id,
            csm_table_hint=csm_table_hint,
            zone_table=zone_table,
        )
