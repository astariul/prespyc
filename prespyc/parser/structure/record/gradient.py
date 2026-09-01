"""Gradient record."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.gradient_record import GradientRecord

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader
    from prespyc.parser.structure.record.color_transform import ColorTransform


@dataclass(frozen=True, slots=True)
class Gradient:
    """A gradient: a spread mode, an interpolation mode and a list of color stops."""

    SPREAD_MODE_PAD: ClassVar[int] = 0
    SPREAD_MODE_REFLECT: ClassVar[int] = 1
    SPREAD_MODE_REPEAT: ClassVar[int] = 2

    INTERPOLATION_MODE_NORMAL: ClassVar[int] = 0
    INTERPOLATION_MODE_LINEAR: ClassVar[int] = 1

    spread_mode: int
    interpolation_mode: int
    records: list[GradientRecord]
    focal_point: float | None = None

    def to_json(self) -> dict[str, object]:
        """
        JSON representation, matching PHP's `jsonSerialize()`.

        The keys are the PHP property names: the serialized form is hashed into the gradient ids of
        the generated SVG, so it must stay byte for byte identical.
        """
        ret: dict[str, object] = {
            "spreadMode": self.spread_mode,
            "interpolationMode": self.interpolation_mode,
            "records": [record.to_json() for record in self.records],
        }

        if self.focal_point is not None:
            ret["focalPoint"] = self.focal_point

        return ret

    def transform_colors(self, color_transform: ColorTransform) -> Gradient:
        records = []

        for record in self.records:
            records.append(record.transform_colors(color_transform))

        return Gradient(
            self.spread_mode,
            self.interpolation_mode,
            records,
            self.focal_point,
        )

    @classmethod
    def read(cls, reader: Reader, with_alpha: bool) -> Self:
        """Read a simple gradient. `with_alpha` selects RGBA colors instead of RGB ones."""
        flags = reader.read_ui8()
        spread_mode = (flags >> 6) & 3  # 2bits
        interpolation_mode = (flags >> 4) & 3  # 2bits
        num_records = flags & 15  # 4bits

        return cls(
            spread_mode,
            interpolation_mode,
            cls._records(reader, num_records, with_alpha),
        )

    @classmethod
    def read_focal(cls, reader: Reader) -> Self:
        """Read a focal gradient. Focal gradients always use alpha colors (RGBA)."""
        flags = reader.read_ui8()
        spread_mode = (flags >> 6) & 3  # 2bits
        interpolation_mode = (flags >> 4) & 3  # 2bits
        num_records = flags & 15  # 4bits

        return cls(
            spread_mode,
            interpolation_mode,
            cls._records(reader, num_records, True),
            focal_point=reader.read_fixed8(),
        )

    @staticmethod
    def _records(reader: Reader, count: int, with_alpha: bool) -> list[GradientRecord]:
        gradient_records = []

        for _ in range(count):
            gradient_records.append(
                GradientRecord(
                    ratio=reader.read_ui8(),
                    color=Color.read_rgba(reader) if with_alpha else Color.read_rgb(reader),
                )
            )

        return gradient_records
