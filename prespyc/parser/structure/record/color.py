"""Color record."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader
    from prespyc.parser.structure.record.color_transform import ColorTransform


@dataclass(frozen=True, slots=True)
class Color:
    """An RGB(A) color. All channels are integers between 0 and 255; alpha is optional."""

    red: int
    green: int
    blue: int
    alpha: int | None = None

    @property
    def hex(self) -> str:
        """The color as `#rrggbb`. Does not include the alpha channel."""
        return f"#{self.red:02x}{self.green:02x}{self.blue:02x}"

    @property
    def opacity(self) -> float:
        """Opacity between 0.0 and 1.0. Without an alpha channel, the color is fully opaque."""
        return self.alpha / 255 if self.alpha is not None else 1.0

    @property
    def has_transparency(self) -> bool:
        """Whether the alpha channel is set and not fully opaque."""
        return self.alpha is not None and self.alpha < 255

    def __str__(self) -> str:
        return self.hex

    def transform(self, color_transform: ColorTransform) -> Color:
        return color_transform.transform(self)

    @classmethod
    def read_rgb(cls, reader: Reader) -> Self:
        return cls(reader.read_ui8(), reader.read_ui8(), reader.read_ui8())

    @classmethod
    def read_rgba(cls, reader: Reader) -> Self:
        return cls(reader.read_ui8(), reader.read_ui8(), reader.read_ui8(), reader.read_ui8())
