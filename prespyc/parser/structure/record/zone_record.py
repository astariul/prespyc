"""Font alignment zone record."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from prespyc.parser.structure.record.zone_data import ZoneData

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class ZoneRecord:
    """Alignment zones of a single glyph."""

    data: list[ZoneData]
    """Should have a length of 2."""

    mask_y: bool
    mask_x: bool

    @classmethod
    def read_collection(cls, reader: Reader, end: int) -> list[Self]:
        """Read zone records until the `end` byte offset is reached."""
        records = []

        chunk = reader.chunk(reader.offset, end)
        reader.skip_to(end)

        while chunk.offset < end:
            count = chunk.read_ui8()  # Should be 2
            data = []

            for _ in range(count):
                data.append(
                    ZoneData(
                        alignment_coordinate=chunk.read_float16(),
                        range=chunk.read_float16(),
                    )
                )

            flags = chunk.read_ui8()
            # 6 bits reserved
            mask_y = (flags & 0b00000010) != 0
            mask_x = (flags & 0b00000001) != 0

            records.append(cls(data, mask_y, mask_x))

        return records
