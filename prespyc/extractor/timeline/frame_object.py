"""A single object of a frame's display list."""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from prespyc.extractor.timeline.blend_mode import BlendMode
from prespyc.parser.structure.record.clip_event_flags import ClipEventFlags
from prespyc.parser.structure.record.matrix import Matrix

if TYPE_CHECKING:
    from prespyc.extractor.drawable import Drawable
    from prespyc.parser.structure.record.clip_actions import ClipActions
    from prespyc.parser.structure.record.color_transform import ColorTransform
    from prespyc.parser.structure.record.filter.filter import Filter
    from prespyc.parser.structure.record.rectangle import Rectangle

_placements = itertools.count()

_UNPROMPTED_EVENTS = (
    ClipEventFlags.LOAD | ClipEventFlags.ENTER_FRAME | ClipEventFlags.INITIALIZE | ClipEventFlags.CONSTRUCT
)
"""Clip events that fire without the user."""


def new_placement() -> int:
    """A `FrameObject.placement` no object holds yet."""
    return next(_placements)


@dataclass(frozen=True, slots=True)
class FrameObject:
    """A single object displayed in a frame."""

    depth: int
    """
    Depth of the object.

    An object with a higher depth is drawn after one with a lower depth, i.e. on top of it.
    """

    object: Drawable
    """
    The object to draw.

    It may differ from the original character when a color transformation is applied.
    """

    bounds: Rectangle
    """Bounds of the object, after applying `matrix`."""

    matrix: Matrix
    """
    Transformation matrix to apply to the object.

    It is the matrix of the PlaceObject tag (`tag_matrix`) already translated by the bounds offset
    of `object`, because an object is drawn from the corner of its bounds.
    """

    color_transform: ColorTransform | None = None
    """Color transformation to apply to the object."""

    clip_depth: int | None = None
    """
    Use the object as a clipping mask, up to this depth.

    Every object from this object's depth to `clip_depth` is clipped to this object's shape, i.e.
    displayed only inside it. When set, the object itself must not be displayed.
    """

    name: str | None = None
    """
    Name of the object, unique in the frame.

    It can be used to retrieve the object and modify it later.
    """

    filters: list[Filter] = field(default_factory=list)
    """Graphic filters to apply to the object."""

    blend_mode: BlendMode = BlendMode.NORMAL

    ratio: int | None = None
    """
    Morphing ratio, between 0 and `RatioDrawable.MAX_RATIO`, where 0 is the start shape and 65535
    the end shape. Only meaningful for a morph shape.
    """

    clip_actions: ClipActions | None = None
    """The `onClipEvent()` handlers of the placement. Read them with `prespyc.avm.script.Script`."""

    placement: int = field(default_factory=new_placement, compare=False, repr=False)
    """
    Identifies the placement: a moved or modified object keeps it, a newly placed one gets another.

    A child plays from the frame it is placed on, so this is how a timeline knows since when.
    """

    _color_transforms: tuple[ColorTransform, ...] = ()
    """
    Color transformations to apply to the object, filled by `transform_colors()`.

    Only used to apply the transformations lazily, which matters because they can be applied
    recursively on sprites. Not to be confused with `color_transform`, which is always applied
    first and can be replaced by `with_()`, for a PlaceObjectX tag with the move flag set.
    """

    @classmethod
    def place(cls, depth: int, object: Drawable, tag_matrix: Matrix | None = None, **properties: Any) -> FrameObject:
        """
        `object` placed at `depth` the way a PlaceObject tag with `tag_matrix` places it.

        `properties` sets the other fields: `color_transform`, `name`, `filters`...
        """
        if tag_matrix is None:
            tag_matrix = Matrix()

        bounds = object.bounds

        return cls(
            depth,
            object,
            bounds.transform(tag_matrix),
            tag_matrix.translate(bounds.xmin, bounds.ymin),
            **properties,
        )

    @property
    def tag_matrix(self) -> Matrix:
        """The matrix of the PlaceObject tag: `matrix` without the bounds offset of `object`."""
        bounds = self.object.bounds

        return self.matrix.translate(-bounds.xmin, -bounds.ymin)

    def with_placement(self, object: Drawable | None = None, tag_matrix: Matrix | None = None) -> FrameObject:
        """
        Place another object, or the same one with another tag matrix, and return a new instance.

        The bounds and the matrix follow. The rest of the placement is kept: color transformation,
        mask, filters, blend mode, name, clip actions.
        """
        if tag_matrix is None:
            tag_matrix = self.tag_matrix

        if object is None:
            object = self.object

        bounds = object.bounds

        return self.with_(
            object=object,
            bounds=bounds.transform(tag_matrix),
            matrix=tag_matrix.translate(bounds.xmin, bounds.ymin),
        )

    @property
    def stops(self) -> bool:
        """
        Whether the clip event handlers of the placement stop the object, by a `stop()` or a
        `gotoAndStop()` run on load or on every frame.
        """
        if self.clip_actions is None:
            return False

        from prespyc.avm.script import Script

        return any(
            record.flags.flags & _UNPROMPTED_EVENTS and Script(record.actions).halts
            for record in self.clip_actions.records
        )

    @property
    def transformed_object(self) -> Drawable:
        """The object to display, after applying the color transformations."""
        object = self.object

        if self.color_transform:
            object = object.transform_colors(self.color_transform)

        # Apply each color transformation to the object.
        # Note: it's not possible to create a single composite color transformation because of
        # clamping values to [0-255] after each transformation.
        for transform in self._color_transforms:
            object = object.transform_colors(transform)

        return object

    def transform_colors(self, color_transform: ColorTransform) -> FrameObject:
        """Apply a color transformation and return the new object."""
        return FrameObject(
            self.depth,
            self.object,
            self.bounds,
            self.matrix,
            self.color_transform,
            self.clip_depth,
            self.name,
            self.filters,
            self.blend_mode,
            self.ratio,
            self.clip_actions,
            self.placement,
            (*self._color_transforms, color_transform),
        )

    def with_(
        self,
        object: Drawable | None = None,
        bounds: Rectangle | None = None,
        matrix: Matrix | None = None,
        color_transform: ColorTransform | None = None,
        filters: list[Filter] | None = None,
        blend_mode: BlendMode | None = None,
        clip_depth: int | None = None,
        name: str | None = None,
        ratio: int | None = None,
        clip_actions: ClipActions | None = None,
    ) -> FrameObject:
        """
        Change some properties of the object and return a new instance, of the same placement.

        `None` means "keep the current value", so a property cannot be cleared this way.
        """
        return FrameObject(
            self.depth,
            object if object is not None else self.object,
            bounds if bounds is not None else self.bounds,
            matrix if matrix is not None else self.matrix,
            color_transform if color_transform is not None else self.color_transform,
            clip_depth if clip_depth is not None else self.clip_depth,
            name if name is not None else self.name,
            filters if filters is not None else self.filters,
            blend_mode if blend_mode is not None else self.blend_mode,
            ratio if ratio is not None else self.ratio,
            clip_actions if clip_actions is not None else self.clip_actions,
            self.placement,
            self._color_transforms,
        )
