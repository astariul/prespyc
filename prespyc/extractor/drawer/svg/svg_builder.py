"""Building the SVG elements of a drawing."""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING

from prespyc._util import num
from prespyc.extractor.drawer.svg.svg_path_drawer import SvgPathDrawer
from prespyc.extractor.shape.fill_type.bitmap import Bitmap
from prespyc.extractor.shape.fill_type.gradient import LinearGradient, RadialGradient
from prespyc.extractor.shape.fill_type.solid import Solid

if TYPE_CHECKING:
    from collections.abc import Sequence

    from prespyc.extractor.drawer.svg.xml import XmlElement
    from prespyc.extractor.shape.fill_type.fill_type import FillType
    from prespyc.extractor.shape.path import Path
    from prespyc.parser.structure.record.filter.filter import Filter
    from prespyc.parser.structure.record.rectangle import Rectangle

XLINK_NS = "http://www.w3.org/1999/xlink"


class SvgBuilder:
    """
    Creates the SVG elements a drawing is made of.

    Gradient and pattern definitions are deduplicated by their content hash, so several paths sharing
    a fill reference one definition.
    """

    __slots__ = ("_elements_by_id", "_svg", "subpixel_stroke_width")

    def __init__(self, svg: XmlElement, subpixel_stroke_width: bool = True) -> None:
        self._svg = svg
        """The element to draw on: the root `<svg>` or a `<defs>`."""

        self.subpixel_stroke_width = subpixel_stroke_width
        """
        Whether strokes keep their real, possibly sub-pixel, SWF width.

        When true, a stroke below 1px is left to the renderer's antialiasing, so it comes out blurry
        and not fully opaque — which is *not* what Flash does, as Flash always draws a stroke at
        least 1px wide. When false, the minimum width is 1px and `non-scaling-stroke` keeps the
        stroke from scaling with the SVG, which approximates Flash at native size but loses the
        relative stroke width when rescaled.
        """

        self._elements_by_id: dict[str, XmlElement] = {}

    def add_group(self, bounds: Rectangle) -> XmlElement:
        """A `<g>` translated so that the bounds start at the origin."""
        return self.add_group_with_offset(-bounds.xmin, -bounds.ymin)

    def add_group_with_offset(self, x_offset: int, y_offset: int) -> XmlElement:
        """A `<g>` translated by the given offset, in twips."""
        g = self._svg.add_child("g")
        g.add_attribute("transform", f"matrix(1, 0, 0, 1, {num(x_offset / 20)}, {num(y_offset / 20)})")

        return g

    def add_path(self, g: XmlElement, path: Path) -> XmlElement | None:
        """
        A `<path>` for `path`, or `None` when its style draws nothing.
        """
        style = path.style

        if style.is_empty:
            return None

        path_element = g.add_child("path")

        self.apply_fill_style(path_element, style.fill, "fill")

        if style.line_fill is not None:
            self.apply_fill_style(path_element, style.line_fill, "stroke")
        else:
            path_element.add_attribute("stroke", style.line_color.hex if style.line_color is not None else "none")

            if style.line_color is not None and style.line_color.has_transparency:
                path_element.add_attribute("stroke-opacity", num(style.line_color.opacity))

        if style.line_width > 0:
            width = style.line_width / 20

            if not self.subpixel_stroke_width and width < 1:
                width = 1
                path_element.add_attribute("vector-effect", "non-scaling-stroke")

            path_element.add_attribute("stroke-width", num(width))
            path_element.add_attribute("stroke-linecap", "round")  # TODO use the style from LINESTYLE2 when available
            path_element.add_attribute("stroke-linejoin", "round")

        path.draw(SvgPathDrawer(path_element))

        return path_element

    def add_filter(self, filters: Sequence[Filter], id: str, width: float, height: float) -> None:
        """A `<filter>` chaining the SWF filters."""
        from prespyc.extractor.drawer.svg.filter.filter_builder import SvgFilterBuilder

        filter_builder = SvgFilterBuilder.create(self._svg, id, width, height)

        for filter in filters:
            filter_builder.apply(filter)

        filter_builder.finalize()

    def apply_fill_style(self, path: XmlElement, style: FillType | None, attribute: str) -> None:
        """Set `attribute` (`fill` or `stroke`) on `path` from `style`."""
        if style is None:
            path.add_attribute(attribute, "none")

            return

        if attribute == "fill":
            path.add_attribute("fill-rule", "evenodd")

        if isinstance(style, Solid):
            self.apply_fill_solid(path, style, attribute)
        elif isinstance(style, RadialGradient):
            # Checked before LinearGradient: RadialGradient is a subclass of it.
            self.apply_fill_radial_gradient(path, style, attribute)
        elif isinstance(style, LinearGradient):
            self.apply_fill_linear_gradient(path, style, attribute)
        elif isinstance(style, Bitmap):
            self.apply_fill_clipped_bitmap(path, style, attribute)

    def apply_fill_solid(self, path: XmlElement, style: Solid, attribute: str) -> None:
        path.add_attribute(attribute, style.color.hex)

        if style.color.has_transparency:
            path.add_attribute(f"{attribute}-opacity", num(style.color.opacity))

    def apply_fill_linear_gradient(self, path: XmlElement, style: LinearGradient, attribute: str) -> None:
        id = "gradient-" + style.hash
        path.add_attribute(attribute, f"url(#{id})")

        if id in self._elements_by_id:
            return

        self._elements_by_id[id] = linear_gradient = self._svg.add_child("linearGradient")

        linear_gradient.add_attribute("gradientTransform", style.matrix.to_svg_transformation())
        linear_gradient.add_attribute("gradientUnits", "userSpaceOnUse")
        linear_gradient.add_attribute("spreadMethod", "pad")
        linear_gradient.add_attribute("id", id)

        # Gradients live in the "gradient square", centred on (0, 0) and spanning
        # (-16384, -16384) to (16384, 16384) in twips.
        linear_gradient.add_attribute("x1", "-819.2")
        linear_gradient.add_attribute("x2", "819.2")

        for record in style.gradient.records:
            stop = linear_gradient.add_child("stop")
            stop.add_attribute("offset", num(record.ratio / 255))
            stop.add_attribute("stop-color", record.color.hex)
            stop.add_attribute("stop-opacity", num(record.color.opacity))

    def apply_fill_radial_gradient(self, path: XmlElement, style: RadialGradient, attribute: str) -> None:
        id = "gradient-" + style.hash
        path.add_attribute(attribute, f"url(#{id})")

        if id in self._elements_by_id:
            return

        # Note: unlike the linear case, ArakneSwf does not register the element here, so a radial
        # gradient shared by several paths is emitted once per path. Kept as is — the goldens
        # contain those duplicates.
        radial_gradient = self._svg.add_child("radialGradient")

        radial_gradient.add_attribute("gradientTransform", style.matrix.to_svg_transformation())
        radial_gradient.add_attribute("gradientUnits", "userSpaceOnUse")
        radial_gradient.add_attribute("spreadMethod", "pad")
        radial_gradient.add_attribute("id", id)

        radial_gradient.add_attribute("cx", "0")
        radial_gradient.add_attribute("cy", "0")
        radial_gradient.add_attribute("r", "819.2")

        if style.gradient.focal_point:
            radial_gradient.add_attribute("fx", "0")
            radial_gradient.add_attribute("fy", num(style.gradient.focal_point * 819.2))

        for record in style.gradient.records:
            stop = radial_gradient.add_child("stop")
            stop.add_attribute("offset", num(record.ratio / 255))
            stop.add_attribute("stop-color", record.color.hex)

            if record.color.has_transparency:
                stop.add_attribute("stop-opacity", num(record.color.opacity))

    def apply_fill_clipped_bitmap(self, path: XmlElement, style: Bitmap, attribute: str) -> None:
        id = "pattern-" + style.hash
        path.add_attribute(attribute, f"url(#{id})")

        if id in self._elements_by_id:
            return

        self._elements_by_id[id] = pattern = self._svg.add_child("pattern")

        bounds = style.bitmap.bounds
        width = num(bounds.width / 20)
        height = num(bounds.height / 20)

        pattern.add_attribute("id", id)
        pattern.add_attribute("overflow", "visible")
        pattern.add_attribute("patternUnits", "userSpaceOnUse")
        pattern.add_attribute("width", width)
        pattern.add_attribute("height", height)
        pattern.add_attribute("viewBox", f"0 0 {width} {height}")
        pattern.add_attribute("patternTransform", style.matrix.to_svg_transformation(undo_twip_scale=True))

        if not style.smoothed:
            pattern.add_attribute("image-rendering", "optimizeSpeed")

        b64 = style.bitmap.to_base64_data()
        image_id = "image-" + hashlib.md5(b64.encode()).hexdigest()

        if image_id not in self._elements_by_id:
            self._elements_by_id[image_id] = image = pattern.add_child("image")
            image.add_attribute("xlink:href", b64)
            image.add_attribute("id", image_id)
        else:
            use = pattern.add_child("use")
            use.add_attribute("xlink:href", f"#{image_id}")
