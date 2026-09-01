"""Drop shadow, as SVG filter primitives."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from prespyc._util import num

if TYPE_CHECKING:
    from prespyc.extractor.drawer.svg.filter.filter_builder import SvgFilterBuilder
    from prespyc.parser.structure.record.color import Color
    from prespyc.parser.structure.record.filter.drop_shadow_filter import DropShadowFilter


class SvgDropShadowFilter:
    """A shadow: offset the source, recolor it, blur it, then merge it back under the source."""

    @staticmethod
    def apply(builder: SvgFilterBuilder, filter: DropShadowFilter, in_: str) -> str:
        if filter.inner_shadow:
            raise RuntimeError("Inner shadow is not supported")

        return SvgDropShadowFilter.outer(
            builder,
            filter.drop_shadow_color,
            filter.distance,
            filter.angle,
            filter.strength,
            filter.blur_x,
            filter.blur_y,
            filter.passes,
            filter.knockout,
            in_,
        )

    @staticmethod
    def outer(
        builder: SvgFilterBuilder,
        color: Color,
        distance: float,
        angle: float,
        strength: float,
        blur_x: float,
        blur_y: float,
        passes: int,
        knockout: bool,
        in_: str,
    ) -> str:
        from prespyc.extractor.drawer.svg.filter.blur_filter import SvgBlurFilter

        dx = distance * math.cos(angle)
        dy = distance * math.sin(angle)

        result_id = in_

        if dx != 0 or dy != 0:
            fe_offset, result_id = builder.add_result_filter("feOffset", in_)
            fe_offset.add_attribute("dx", num(dx))
            fe_offset.add_attribute("dy", num(dy))

        # Recolor the offset copy into the shadow color
        shadow_color, result_id = builder.add_result_filter("feColorMatrix", result_id)

        shadow_color.add_attribute("type", "matrix")
        shadow_color.add_attribute(
            "values",
            f"0 0 0 0 {num(color.red / 255)} "
            f"0 0 0 0 {num(color.green / 255)} "
            f"0 0 0 0 {num(color.blue / 255)} "
            f"0 0 0 {num(color.opacity * strength)} 0",
        )

        result_id = SvgBlurFilter.blur(builder, blur_x, blur_y, passes, result_id)

        if knockout:
            return result_id

        # Merge the shadow with the original shape
        fe_merge, merge_result = builder.add_result_filter("feMerge")

        fe_merge.add_child("feMergeNode").add_attribute("in", result_id)
        fe_merge.add_child("feMergeNode").add_attribute("in", in_)

        return merge_result
