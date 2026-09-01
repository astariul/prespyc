"""A single object of a frame's display list."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from prespyc.extractor.timeline.blend_mode import BlendMode

if TYPE_CHECKING:
    from prespyc.extractor.drawable import Drawable
    from prespyc.parser.structure.record.color_transform import ColorTransform
    from prespyc.parser.structure.record.filter.filter import Filter
    from prespyc.parser.structure.record.matrix import Matrix
    from prespyc.parser.structure.record.rectangle import Rectangle


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
    """Transformation matrix to apply to the object."""

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

    _color_transforms: tuple[ColorTransform, ...] = ()
    """
    Color transformations to apply to the object, filled by `transform_colors()`.

    Only used to apply the transformations lazily, which matters because they can be applied
    recursively on sprites. Not to be confused with `color_transform`, which is always applied
    first and can be replaced by `with_()`, for a PlaceObjectX tag with the move flag set.
    """

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
    ) -> FrameObject:
        """
        Change some properties of the object and return a new instance.

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
            self._color_transforms,
        )
