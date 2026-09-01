"""Canvas for the dependencies of an SVG drawing."""

from __future__ import annotations

from typing import TYPE_CHECKING

from prespyc.extractor.drawer.svg.base_svg_canvas import BaseSvgCanvas
from prespyc.extractor.drawer.svg.svg_builder import SvgBuilder

if TYPE_CHECKING:
    from prespyc.extractor.drawer.svg.xml import XmlElement
    from prespyc.parser.structure.record.rectangle import Rectangle


class IncludedSvgCanvas(BaseSvgCanvas):
    """
    Draws an included character into the root canvas' `<defs>`, to be referenced with `<use>`.

    Internal: only `SvgCanvas` and `BaseSvgCanvas.include()` create one.
    """

    __slots__ = ("_defs_element", "_root", "ids")

    def __init__(self, root: BaseSvgCanvas, defs: XmlElement, subpixel_stroke_width: bool = True) -> None:
        self._root = root
        self._defs_element = defs

        self.ids: list[str] = []
        """Ids of the objects drawn here. Each one is referenced by a `<use>` element."""

        super().__init__(SvgBuilder(defs, subpixel_stroke_width))

    def render(self):
        raise RuntimeError("This is an internal implementation, rendering is performed by the root canvas")

    def _next_object_id(self) -> str:
        return self._root._next_object_id()

    def _defs(self) -> XmlElement:
        return self._defs_element

    def _new_group(self, builder: SvgBuilder, bounds: Rectangle) -> XmlElement:
        group = builder.add_group(bounds)
        id = self._next_object_id()
        self.ids.append(id)
        group.add_attribute("id", id)

        return group

    def _new_group_with_offset(self, builder: SvgBuilder, offset_x: int, offset_y: int) -> XmlElement:
        group = builder.add_group_with_offset(offset_x, offset_y)
        id = self._next_object_id()
        self.ids.append(id)
        group.add_attribute("id", id)

        return group
