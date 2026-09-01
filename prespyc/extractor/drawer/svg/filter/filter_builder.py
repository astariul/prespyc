"""Turning SWF filters into an SVG `<filter>` chain."""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

from prespyc._util import num
from prespyc.parser.structure.record.filter.blur_filter import BlurFilter
from prespyc.parser.structure.record.filter.color_matrix_filter import ColorMatrixFilter
from prespyc.parser.structure.record.filter.drop_shadow_filter import DropShadowFilter
from prespyc.parser.structure.record.filter.glow_filter import GlowFilter

if TYPE_CHECKING:
    from prespyc.extractor.drawer.svg.xml import XmlElement
    from prespyc.parser.structure.record.filter.filter import Filter


class SvgFilterBuilder:
    """
    Builds one SVG `<filter>` element from a chain of SWF filters.

    Stateful and single use: each filter appends primitives and its result becomes the next one's
    input.
    """

    __slots__ = ("_filter", "_filter_count", "_height", "_last_result", "_width", "_x_offset", "_y_offset")

    def __init__(self, filter: XmlElement, width: float, height: float) -> None:
        self._filter = filter
        self._width = width
        self._height = height
        self._filter_count = 0
        self._last_result = "SourceGraphic"
        self._x_offset = 0.0
        self._y_offset = 0.0

    @classmethod
    def create(cls, root: XmlElement, id: str, width: float, height: float) -> Self:
        """A builder and the `<filter>` element it fills, appended to `root`."""
        filter = root.add_child("filter")
        filter.add_attribute("id", id)
        filter.add_attribute("filterUnits", "userSpaceOnUse")  # Allow overflow

        return cls(filter, width, height)

    def apply(self, filter: Filter) -> None:
        """Append one SWF filter to the chain."""
        from prespyc.extractor.drawer.svg.filter.blur_filter import SvgBlurFilter
        from prespyc.extractor.drawer.svg.filter.color_matrix_filter import SvgColorMatrixFilter
        from prespyc.extractor.drawer.svg.filter.drop_shadow_filter import SvgDropShadowFilter
        from prespyc.extractor.drawer.svg.filter.glow_filter import SvgGlowFilter

        if isinstance(filter, ColorMatrixFilter):
            self._last_result = SvgColorMatrixFilter.apply(self, filter, self._last_result)
        elif isinstance(filter, BlurFilter):
            self._last_result = SvgBlurFilter.apply(self, filter, self._last_result)
        elif isinstance(filter, GlowFilter):
            self._last_result = SvgGlowFilter.apply(self, filter, self._last_result)
        elif isinstance(filter, DropShadowFilter):
            self._last_result = SvgDropShadowFilter.apply(self, filter, self._last_result)
        else:
            raise RuntimeError(f"Unsupported filter type: {type(filter).__name__}")

    def add_filter(self, element: str, in_: str | None = None) -> XmlElement:
        """A new filter primitive, with an `in` attribute when given."""
        filter_element = self._filter.add_child(element)

        if in_:
            filter_element.add_attribute("in", in_)

        return filter_element

    def add_result_filter(self, element: str, in_: str | None = None) -> tuple[XmlElement, str]:
        """A new filter primitive plus its result id, to feed the next primitive."""
        filter_element = self.add_filter(element, in_)
        self._filter_count += 1
        result = f"filter{self._filter_count}"

        filter_element.add_attribute("result", result)
        filter_element.add_attribute("id", result)

        return filter_element, result

    def add_offset(self, x: float, y: float) -> None:
        """
        Grow the filter region.

        A blur or a shadow draws outside the source bounds, so the region has to expand or the
        result is clipped.
        """
        self._x_offset += x
        self._y_offset += y

    def finalize(self) -> None:
        """Write the accumulated filter region. Call once, after every filter is applied."""
        if self._x_offset > 0 or self._y_offset > 0:
            self._filter.add_attribute("width", num(self._width + self._x_offset * 2))
            self._filter.add_attribute("height", num(self._height + self._y_offset * 2))
            self._filter.add_attribute("x", num(-self._x_offset))
            self._filter.add_attribute("y", num(-self._y_offset))
