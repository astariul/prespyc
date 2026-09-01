"""Glow, as SVG filter primitives."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from prespyc.extractor.drawer.svg.filter.filter_builder import SvgFilterBuilder
    from prespyc.parser.structure.record.color import Color
    from prespyc.parser.structure.record.filter.glow_filter import GlowFilter


class SvgGlowFilter:
    """A glow is a drop shadow with no offset and full strength."""

    @staticmethod
    def apply(builder: SvgFilterBuilder, filter: GlowFilter, in_: str) -> str:
        if filter.inner_glow:
            raise RuntimeError("Not implemented: inner glow filter")

        return SvgGlowFilter.outer(
            builder, filter.glow_color, filter.blur_x, filter.blur_y, filter.passes, filter.knockout, in_
        )

    @staticmethod
    def outer(
        builder: SvgFilterBuilder, color: Color, blur_x: float, blur_y: float, passes: int, knockout: bool, in_: str
    ) -> str:
        from prespyc.extractor.drawer.svg.filter.drop_shadow_filter import SvgDropShadowFilter

        return SvgDropShadowFilter.outer(
            builder,
            color,
            0,  # distance
            0,  # angle
            1.0,  # strength
            blur_x,
            blur_y,
            passes,
            knockout,
            in_,
        )
