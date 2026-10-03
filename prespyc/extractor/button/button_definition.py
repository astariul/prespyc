"""A SWF button character."""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING

from prespyc.errors import CircularReferenceError, Errors
from prespyc.extractor.timeline.blend_mode import BlendMode
from prespyc.extractor.timeline.frame import Frame
from prespyc.extractor.timeline.frame_object import FrameObject
from prespyc.extractor.timeline.timeline import Timeline
from prespyc.parser.structure.record.rectangle import Rectangle

if TYPE_CHECKING:
    from prespyc.extractor.drawer.drawer import Drawer
    from prespyc.extractor.extractor import Extractor
    from prespyc.extractor.modifier.character_modifier import CharacterModifier
    from prespyc.parser.structure.record.color_transform import ColorTransform
    from prespyc.parser.structure.tag.define_button import DefineButtonTag
    from prespyc.parser.structure.tag.define_button2 import DefineButton2Tag


class ButtonDefinition:
    """
    A button character, drawn in its up state: how it looks until the mouse comes over it.

    A button state is a display list, so it is a one-frame timeline.
    """

    __slots__ = ("_extractor", "_processing", "_timeline", "id", "tag")

    def __init__(self, extractor: Extractor, id: int, tag: DefineButtonTag | DefineButton2Tag) -> None:
        self._extractor: Extractor | None = extractor
        self._timeline: Timeline | None = None
        self._processing = False

        self.id = id
        """Character id of the button."""

        self.tag = tag
        """The raw SWF tag."""

    @property
    def timeline(self) -> Timeline:
        """The up state, processed on first access and cached afterwards."""
        if self._timeline is None:
            if self._processing:
                if self._extractor is not None and self._extractor.error_enabled(Errors.CIRCULAR_REFERENCE):
                    raise CircularReferenceError(
                        f"Circular reference detected while processing button {self.id}", self.id
                    )

                return Timeline.empty()

            self._processing = True

            try:
                self._timeline = self._up_state()
            finally:
                self._processing = False

            self._extractor = None  # Remove the extractor to remove cyclic reference

        return self._timeline

    @property
    def bounds(self) -> Rectangle:
        return self.timeline.bounds

    def frames_count(self, recursive: bool = False) -> int:
        return self.timeline.frames_count(recursive)

    def draw(self, drawer: Drawer, frame: int = 0) -> Drawer:
        return self.timeline.draw(drawer, frame)

    def transform_colors(self, color_transform: ColorTransform) -> ButtonDefinition:
        return self._with_timeline(self.timeline.transform_colors(color_transform))

    def modify(self, modifier: CharacterModifier, max_depth: int = -1) -> ButtonDefinition:
        result = self

        if max_depth != 0:
            timeline = self.timeline.modify(modifier, max_depth - 1)

            if timeline is not self.timeline:
                result = self._with_timeline(timeline)

        return modifier.apply_on_button(result)

    def _up_state(self) -> Timeline:
        assert self._extractor is not None
        objects = {}

        for record in self.tag.characters:
            if not record.state_up:
                continue

            objects[record.place_depth] = FrameObject.place(
                record.place_depth,
                self._extractor.character(record.character_id),
                record.matrix,
                color_transform=record.color_transform,
                filters=record.filters or [],
                blend_mode=BlendMode.of(record.blend_mode),
            )

        if not objects:
            return Timeline.empty()

        objects = dict(sorted(objects.items()))
        bounds = Rectangle.merge(object.bounds for object in objects.values())

        return Timeline(bounds, Frame(bounds, objects))

    def _with_timeline(self, timeline: Timeline) -> ButtonDefinition:
        """A copy of the button drawing `timeline` instead of its own."""
        clone = copy.copy(self)
        clone._timeline = timeline

        return clone
