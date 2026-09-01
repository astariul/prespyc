"""Gradient fills."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from prespyc._util import php_json_encode, xxh128

if TYPE_CHECKING:
    from prespyc.parser.structure.record.color_transform import ColorTransform
    from prespyc.parser.structure.record.gradient import Gradient as GradientRecordSet
    from prespyc.parser.structure.record.matrix import Matrix


def _matrix_json(matrix: Matrix) -> dict:
    """
    The matrix as PHP's `json_encode` sees it: public properties, in declaration order, camelCase.
    """
    return {
        "scaleX": matrix.scale_x,
        "scaleY": matrix.scale_y,
        "rotateSkew0": matrix.rotate_skew0,
        "rotateSkew1": matrix.rotate_skew1,
        "translateX": matrix.translate_x,
        "translateY": matrix.translate_y,
    }


@dataclass(frozen=True, slots=True)
class LinearGradient:
    """A linear gradient fill."""

    PREFIX: ClassVar[str] = "L"

    matrix: Matrix
    gradient: GradientRecordSet

    @property
    def hash(self) -> str:
        # PHP: hash('xxh128', json_encode($this)) over the public properties, in declaration order.
        payload = {"matrix": _matrix_json(self.matrix), "gradient": self.gradient.to_json()}

        return self.PREFIX + xxh128(php_json_encode(payload))

    def transform_colors(self, color_transform: ColorTransform):
        return type(self)(self.matrix, self.gradient.transform_colors(color_transform))

    def interpolate(self, other, ratio: int):
        from prespyc.extractor.morph_shape.interpolate import interpolate_gradient, interpolate_matrix

        return type(self)(
            interpolate_matrix(self.matrix, other.matrix, ratio),
            interpolate_gradient(self.gradient, other.gradient, ratio),
        )


@dataclass(frozen=True, slots=True)
class RadialGradient(LinearGradient):
    """A radial (or focal) gradient fill. Identical to a linear one but for the hash prefix."""

    PREFIX: ClassVar[str] = "R"
