"""Color matrix, as an SVG filter primitive."""

from __future__ import annotations

from typing import TYPE_CHECKING

from prespyc._util import num

if TYPE_CHECKING:
    from prespyc.extractor.drawer.svg.filter.filter_builder import SvgFilterBuilder
    from prespyc.parser.structure.record.filter.color_matrix_filter import ColorMatrixFilter


class SvgColorMatrixFilter:
    """
    A 4x5 color matrix. SWF stores the offset column in 0-255, SVG expects 0-1, so every fifth
    value is divided by 255.
    """

    @staticmethod
    def apply(builder: SvgFilterBuilder, filter: ColorMatrixFilter, in_: str) -> str:
        values = " ".join(num(v / 255 if i % 5 == 4 else v) for i, v in enumerate(filter.matrix))

        fe_color_matrix, result_id = builder.add_result_filter("feColorMatrix", in_)

        fe_color_matrix.add_attribute("type", "matrix")
        fe_color_matrix.add_attribute("values", values)
        fe_color_matrix.add_attribute("color-interpolation-filters", "sRGB")

        return result_id
