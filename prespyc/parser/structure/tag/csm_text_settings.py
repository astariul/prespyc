"""CSMTextSettings tag."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class CSMTextSettingsTag:
    """Anti-aliasing settings applied to a text character."""

    TYPE: ClassVar[int] = 74

    text_id: int
    use_flash_type: int
    grid_fit: int
    thickness: float
    sharpness: float

    @classmethod
    def read(cls, reader: Reader) -> Self:
        """Read a CSMTextSettings tag from the reader."""
        text_id = reader.read_ui16()
        use_flash_type = reader.read_ub(2)
        grid_fit = reader.read_ub(3)
        reader.skip_bits(3)  # Reserved
        thickness = reader.read_float()
        sharpness = reader.read_float()
        reader.skip_bytes(1)  # Reserved

        return cls(
            text_id=text_id,
            use_flash_type=use_flash_type,
            grid_fit=grid_fit,
            thickness=thickness,
            sharpness=sharpness,
        )
