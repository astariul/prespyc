"""Gradient record: one color stop of a gradient."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from prespyc.parser.structure.record.color import Color
    from prespyc.parser.structure.record.color_transform import ColorTransform


@dataclass(frozen=True, slots=True)
class GradientRecord:
    """A single color stop of a gradient."""

    ratio: int
    """
    The "distance" from the start of the gradient box.
    0 means the start of the gradient box, 255 means the end of the gradient box.
    """

    color: Color

    def transform_colors(self, color_transform: ColorTransform) -> GradientRecord:
        return GradientRecord(
            self.ratio,
            color_transform.transform(self.color),
        )

    def to_json(self) -> dict[str, object]:
        """
        JSON representation, matching PHP's `json_encode()` of the record.

        The keys are the PHP property names: the serialized form is hashed into the gradient ids of
        the generated SVG, so it must stay byte for byte identical.
        """
        return {
            "ratio": self.ratio,
            "color": asdict(self.color),
        }
