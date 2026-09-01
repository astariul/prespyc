"""Morph gradient record."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.morph_shape.morph_gradient_record import MorphGradientRecord

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class MorphGradient:
    """
    A gradient of a morph shape.

    MorphGradient is not well documented in the SWF specification. Flags are not defined, but they
    are actually used, and seem to follow the same structure as `Gradient`.
    """

    SPREAD_MODE_PAD: ClassVar[int] = 0
    SPREAD_MODE_REFLECT: ClassVar[int] = 1
    SPREAD_MODE_REPEAT: ClassVar[int] = 2

    INTERPOLATION_MODE_NORMAL: ClassVar[int] = 0
    INTERPOLATION_MODE_LINEAR: ClassVar[int] = 1

    spread_mode: int
    """Undocumented flags: the two first bits."""

    interpolation_mode: int
    """Undocumented flags: the two following bits."""

    records: list[MorphGradientRecord]

    focal_point: float | None = None
    """Only used for a focal radial gradient."""

    @classmethod
    def read(cls, reader: Reader, focal: bool) -> Self:
        """
        Read a morph gradient from the given reader.

        `focal` tells whether the focal point is present in the data.
        """
        flags = reader.read_ui8()
        spread_mode = (flags >> 6) & 3  # 2bits
        interpolation_mode = (flags >> 4) & 3  # 2bits
        num_records = flags & 15  # 4bits

        return cls(
            spread_mode,
            interpolation_mode,
            cls._read_records(reader, num_records),
            focal_point=reader.read_fixed8() if focal else None,
        )

    @staticmethod
    def _read_records(reader: Reader, count: int) -> list[MorphGradientRecord]:
        return [
            MorphGradientRecord(
                start_ratio=reader.read_ui8(),
                start_color=Color.read_rgba(reader),
                end_ratio=reader.read_ui8(),
                end_color=Color.read_rgba(reader),
            )
            for _ in range(count)
        ]
