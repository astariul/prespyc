"""A SWF sprite character."""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING

from prespyc.errors import CircularReferenceError, Errors
from prespyc.extractor.timeline.timeline import Timeline

if TYPE_CHECKING:
    from collections.abc import Iterator

    from prespyc.extractor.drawable import Drawable
    from prespyc.extractor.drawer.drawer import Drawer
    from prespyc.extractor.modifier.character_modifier import CharacterModifier
    from prespyc.extractor.timeline.timeline_processor import TimelineProcessor
    from prespyc.parser.structure.record.color_transform import ColorTransform
    from prespyc.parser.structure.record.rectangle import Rectangle
    from prespyc.parser.structure.tag.define_sprite import DefineSpriteTag


class SpriteDefinition:
    """A sprite character: a movie clip with its own timeline."""

    __slots__ = ("_processing", "_processor", "_timeline", "id", "tag")

    def __init__(self, processor: TimelineProcessor, id: int, tag: DefineSpriteTag) -> None:
        self._processor: TimelineProcessor | None = processor
        self._timeline: Timeline | None = None
        self._processing = False

        self.id = id
        """Character id of the sprite."""

        self.tag = tag
        """The raw SWF tag."""

    @property
    def timeline(self) -> Timeline:
        """The timeline of the sprite, processed on first access and cached afterwards."""
        if not self._timeline:
            if self._processing:
                if self._processor is not None and self._processor.error_enabled(Errors.CIRCULAR_REFERENCE):
                    raise CircularReferenceError(
                        f"Circular reference detected while processing sprite {self.id}", self.id
                    )

                self._timeline = Timeline.empty()

                return self._timeline

            self._processing = True

            try:
                assert self._processor is not None
                timeline = self._processor.process(self.tag.tags)

                # In case of ignored circular reference, a timeline object can already be assigned
                # here by the processor call, so we only assign it if it's not already set
                if self._timeline is None:
                    self._timeline = timeline
            finally:
                self._processing = False

            self._processor = None  # Remove the processor to remove cyclic reference

        return self._timeline

    def frames_count(self, recursive: bool = False) -> int:
        return self.timeline.frames_count(recursive)

    @property
    def bounds(self) -> Rectangle:
        return self.timeline.bounds

    def transform_colors(self, color_transform: ColorTransform) -> SpriteDefinition:
        return self._with_timeline(self.timeline.transform_colors(color_transform))

    def draw(self, drawer: Drawer, frame: int = 0) -> Drawer:
        return self.timeline.draw(drawer, frame)

    def modify(self, modifier: CharacterModifier, max_depth: int = -1) -> SpriteDefinition:
        result = self

        if max_depth != 0:
            old_timeline = self.timeline
            timeline = old_timeline.modify(modifier, max_depth - 1)

            if timeline is not old_timeline:
                result = self._with_timeline(timeline)

        return modifier.apply_on_sprite(result)

    def with_attachment(self, attachment: Drawable, depth: int, name: str | None) -> SpriteDefinition:
        """
        Attach an object at `depth` under `name` and return a new sprite.

        Equivalent to the "Attach Movie" action of SWF files. `name` is set on `FrameObject.name`.
        """
        return self._with_timeline(self.timeline.with_attachment(attachment, depth, name))

    def to_svg(self, frame: int = 0, subpixel_stroke_width: bool = True) -> str:
        """
        Render a single frame of the sprite to SVG.

        Without `subpixel_stroke_width`, the minimum stroke width is 1px, which approximates Flash
        rendering.
        """
        return self.timeline.to_svg(frame, subpixel_stroke_width)

    def to_svg_all(self, subpixel_stroke_width: bool = True) -> Iterator[str]:
        """
        Render every frame of the sprite to SVG, in play order.

        Without `subpixel_stroke_width`, the minimum stroke width is 1px, which approximates Flash
        rendering.
        """
        return self.timeline.to_svg_all(subpixel_stroke_width)

    def _with_timeline(self, timeline: Timeline) -> SpriteDefinition:
        """A copy of the sprite holding `timeline` instead of its own."""
        clone = copy.copy(self)
        clone._timeline = timeline

        return clone
