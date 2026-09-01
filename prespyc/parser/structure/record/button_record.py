"""Button record."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from prespyc.parser.structure.record.color_transform import ColorTransform
from prespyc.parser.structure.record.filter.filter import Filter
from prespyc.parser.structure.record.matrix import Matrix

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class ButtonRecord:
    """One character placed in a button state."""

    state_hit_test: bool
    state_down: bool
    state_over: bool
    state_up: bool
    character_id: int
    place_depth: int
    matrix: Matrix
    color_transform: ColorTransform | None = None
    filters: list[Filter] | None = None
    blend_mode: int | None = None

    @classmethod
    def read_collection(cls, reader: Reader, version: int) -> list[Self]:
        """
        Read a collection of button records.

        The end of the collection is marked by a record with a flags value of 0 (end character
        flag). `version` is the version of the define button tag.
        """
        records = []

        while reader.offset < reader.end:
            flags = reader.read_ui8()

            if flags == 0:
                break

            # 2 bits reserved
            has_blend_mode = (flags & 0b00100000) != 0
            has_filters = (flags & 0b00010000) != 0
            state_hit_test = (flags & 0b00001000) != 0
            state_down = (flags & 0b00000100) != 0
            state_over = (flags & 0b00000010) != 0
            state_up = (flags & 0b00000001) != 0

            character_id = reader.read_ui16()
            place_depth = reader.read_ui16()
            matrix = Matrix.read(reader)
            color_transform = ColorTransform.read(reader, True) if version >= 2 else None
            filters = Filter.read_collection(reader) if version >= 2 and has_filters else None
            blend_mode = reader.read_ui8() if version >= 2 and has_blend_mode else None

            records.append(
                cls(
                    state_hit_test=state_hit_test,
                    state_down=state_down,
                    state_over=state_over,
                    state_up=state_up,
                    character_id=character_id,
                    place_depth=place_depth,
                    matrix=matrix,
                    color_transform=color_transform,
                    filters=filters,
                    blend_mode=blend_mode,
                )
            )

        return records
