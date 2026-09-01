"""Shared implementation of the SVG canvases."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from prespyc._util import num
from prespyc.extractor.timeline.blend_mode import BlendMode

if TYPE_CHECKING:
    from collections.abc import Sequence

    from prespyc.extractor.drawable import Drawable
    from prespyc.extractor.drawer.svg.svg_builder import SvgBuilder
    from prespyc.extractor.drawer.svg.xml import XmlElement
    from prespyc.extractor.image.image_character import ImageCharacter
    from prespyc.extractor.shape.path import Path
    from prespyc.extractor.shape.shape import Shape
    from prespyc.parser.structure.record.filter.filter import Filter
    from prespyc.parser.structure.record.matrix import Matrix
    from prespyc.parser.structure.record.rectangle import Rectangle


class BaseSvgCanvas(ABC):
    """
    A `Drawer` that emits SVG.

    Two things make this stateful. `_current_group` is the root `<g>` of the drawing, created on the
    first `area()`. `_current_target` is where the next element goes: with no active clip it is the
    root group, and with clips it is a nested `<g>` per active clip path. Setting it to `None` marks
    it as needing to be rebuilt, which is how `start_clip()`/`end_clip()` take effect.
    """

    __slots__ = ("_active_clip_paths", "_bounds", "_builder", "_current_group", "_current_target")

    def __init__(self, builder: SvgBuilder) -> None:
        self._builder = builder
        self._current_group: XmlElement | None = None
        self._current_target: XmlElement | None = None
        self._bounds: Rectangle | None = None
        self._active_clip_paths: dict[str, str] = {}

    def area(self, bounds: Rectangle) -> None:
        self._current_target = self._current_group = self._new_group(self._builder, bounds)
        self._bounds = bounds

    def shape(self, shape: Shape) -> None:
        self._current_target = self._new_group_with_offset(self._builder, shape.x_offset, shape.y_offset)

        for path in shape.paths:
            self.path(path)

    def image(self, image: ImageCharacter) -> None:
        g = self._current_target = self._new_group(self._builder, image.bounds)
        tag = g.add_child("image")
        tag.add_attribute("xlink:href", image.to_base64_data())

    def include(
        self,
        obj: Drawable,
        matrix: Matrix,
        frame: int = 0,
        filters: Sequence[Filter] = (),
        blend_mode: BlendMode = BlendMode.NORMAL,
        name: str | None = None,
    ) -> None:
        from prespyc.extractor.drawer.svg.included_svg_canvas import IncludedSvgCanvas

        included = IncludedSvgCanvas(self, self._defs(), self._builder.subpixel_stroke_width)

        obj.draw(included, frame)

        bounds = obj.bounds
        g = self._target(bounds)
        width = bounds.width / 20
        height = bounds.height / 20

        if filters and included.ids:
            filter_id = "filter-" + included.ids[0]
            self._builder.add_filter(filters, filter_id, width, height)
        else:
            filter_id = None

        css_blend_mode = blend_mode.css_value

        for id in included.ids:
            use = g.add_child("use")

            use.add_attribute("xlink:href", "#" + id)
            use.add_attribute("width", num(width))
            use.add_attribute("height", num(height))
            use.add_attribute("transform", matrix.to_svg_transformation())

            if name:
                use.add_attribute("id", name)

            if filter_id:
                use.add_attribute("filter", f"url(#{filter_id})")

            if css_blend_mode:
                use.add_attribute("style", f"mix-blend-mode: {css_blend_mode}")

    def start_clip(self, obj: Drawable, matrix: Matrix, frame: int) -> str:
        from prespyc.extractor.drawer.svg.clip_path_builder import ClipPathBuilder

        group = self._current_group

        if group is None:
            raise RuntimeError("No group defined for clipping")

        clip_path = group.add_child("clipPath")
        id = self._next_object_id()
        clip_path.add_attribute("id", id)
        clip_path.add_attribute("transform", matrix.to_svg_transformation())

        obj.draw(ClipPathBuilder(clip_path, self._builder), frame)
        self._active_clip_paths[id] = id

        # Force the next drawing to rebuild the target group, so it picks up the new clip path
        self._current_target = None

        return id

    def end_clip(self, clip_id: str) -> None:
        self._active_clip_paths.pop(clip_id, None)

        # Force the next drawing to rebuild the target group, so it drops the clip path
        self._current_target = None

    def path(self, path: Path) -> None:
        g = self._current_target

        if g is None:
            raise RuntimeError("No group defined")

        self._builder.add_path(g, path)

    def _target(self, bounds: Rectangle) -> XmlElement:
        target = self._current_target

        if target is not None:
            return target

        if self._current_group is None:
            self._current_group = self._new_group(self._builder, self._bounds if self._bounds is not None else bounds)

        root_group = self._current_group

        if not self._active_clip_paths:
            self._current_target = root_group

            return root_group

        # One nested <g> per active clip path, so nested clips compose
        target = root_group

        for id in self._active_clip_paths:
            target = target.add_child("g")
            target.add_attribute("clip-path", f"url(#{id})")

        self._current_target = target

        return target

    @abstractmethod
    def _next_object_id(self) -> str:
        """A fresh object id, unique across the whole drawing."""

    @abstractmethod
    def _defs(self) -> XmlElement:
        """The element holding this canvas' definitions."""

    @abstractmethod
    def _new_group(self, builder: SvgBuilder, bounds: Rectangle) -> XmlElement:
        """A new group for the given bounds. Must go through `SvgBuilder.add_group()`."""

    @abstractmethod
    def _new_group_with_offset(self, builder: SvgBuilder, offset_x: int, offset_y: int) -> XmlElement:
        """A new group at the given offset. Must go through `SvgBuilder.add_group_with_offset()`."""

    @abstractmethod
    def render(self):
        """Render the drawing."""
