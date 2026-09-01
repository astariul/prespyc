"""Building a timeline out of the display tags of a SWF file or sprite."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any, ClassVar

from prespyc._util import decode_swf_text
from prespyc.errors import Errors, ProcessingInvalidDataError
from prespyc.extractor.drawable import RatioDrawable
from prespyc.extractor.timeline.blend_mode import BlendMode
from prespyc.extractor.timeline.frame import Frame
from prespyc.extractor.timeline.frame_object import FrameObject
from prespyc.extractor.timeline.timeline import Timeline
from prespyc.parser.structure.record.matrix import Matrix
from prespyc.parser.structure.record.rectangle import Rectangle
from prespyc.parser.structure.tag.do_action import DoActionTag
from prespyc.parser.structure.tag.end import EndTag
from prespyc.parser.structure.tag.frame_label import FrameLabelTag
from prespyc.parser.structure.tag.place_object import PlaceObjectTag
from prespyc.parser.structure.tag.place_object2 import PlaceObject2Tag
from prespyc.parser.structure.tag.place_object3 import PlaceObject3Tag
from prespyc.parser.structure.tag.remove_object import RemoveObjectTag
from prespyc.parser.structure.tag.remove_object2 import RemoveObject2Tag
from prespyc.parser.structure.tag.show_frame import ShowFrameTag
from prespyc.parser.structure.tag.sound_stream_head import SoundStreamHeadTag

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from prespyc.extractor.extractor import Extractor

_PLACE_TAGS = (PlaceObjectTag, PlaceObject2Tag, PlaceObject3Tag)


class TimelineProcessor:
    """Renders the frames of a timeline out of SWF display tags."""

    _MAX_BOUNDS: ClassVar[int] = 163_840
    """
    Maximum bounds size of a sprite, arbitrarily set to 8192 pixels.

    An object resulting in larger bounds is still added to the display list, but ignored when
    computing the sprite bounds.
    """

    TAG_TYPES: ClassVar[tuple[int, ...]] = (
        EndTag.TYPE,
        ShowFrameTag.TYPE,
        PlaceObjectTag.TYPE,
        RemoveObjectTag.TYPE,
        DoActionTag.TYPE,
        PlaceObject2Tag.TYPE,
        RemoveObject2Tag.TYPE,
        FrameLabelTag.TYPE,
        PlaceObject3Tag.TYPE,
    )
    """Tag types the processor consumes."""

    __slots__ = ("_extractor",)

    def __init__(self, extractor: Extractor) -> None:
        self._extractor = extractor

    def error_enabled(self, error: int) -> bool:
        """Whether the given error flag is enabled."""
        return self._extractor.error_enabled(error)

    def process(self, tags: Iterable[Any]) -> Timeline:
        """
        Process display tags into the frames of a timeline.

        `tags` is either the `(raw tag, parsed tag)` pairs of `SwfFile.tags()` or the already
        parsed tags of `DefineSpriteTag.tags`.
        """
        objects_by_depth: dict[int, FrameObject] = {}
        actions: list[DoActionTag] = []
        frame_label: str | None = None
        frames: list[Frame] = []

        empty = True

        # Bounds of the sprite
        xmin = sys.maxsize
        ymin = sys.maxsize
        xmax = -sys.maxsize - 1
        ymax = -sys.maxsize - 1

        for frame_display_tag in _parsed_tags(tags):
            if isinstance(frame_display_tag, EndTag):
                break

            if isinstance(frame_display_tag, ShowFrameTag):
                # Ensure that depths are respected
                objects_by_depth = dict(sorted(objects_by_depth.items()))

                frames.append(
                    Frame(
                        # An empty frame gets empty bounds
                        Rectangle(xmin, xmax, ymin, ymax) if objects_by_depth else Rectangle(0, 0, 0, 0),
                        # A snapshot: PHP arrays are values, so the frame keeps the display list as
                        # it is now, while the loop keeps mutating it for the next frames.
                        dict(objects_by_depth),
                        actions,
                        frame_label,
                    )
                )
                actions = []
                frame_label = None
                continue

            if isinstance(frame_display_tag, DoActionTag):
                actions.append(frame_display_tag)
                continue

            if isinstance(frame_display_tag, FrameLabelTag):
                frame_label = self._decode(frame_display_tag.label)
                continue

            if isinstance(frame_display_tag, (RemoveObject2Tag, RemoveObjectTag)):
                objects_by_depth.pop(frame_display_tag.depth, None)
                continue

            # Ignore sounds: we only care about display objects
            if isinstance(frame_display_tag, SoundStreamHeadTag):
                continue

            if not isinstance(frame_display_tag, _PLACE_TAGS):
                if self.error_enabled(Errors.UNPROCESSABLE_DATA):
                    raise ProcessingInvalidDataError(
                        f"Invalid tag type {type(frame_display_tag).__name__} in timeline",
                    )

                continue

            is_new_object = not getattr(frame_display_tag, "move", False)

            # New object without characterId is not allowed
            if is_new_object and frame_display_tag.character_id is None:
                if self.error_enabled(Errors.UNPROCESSABLE_DATA):
                    raise ProcessingInvalidDataError(
                        f"New object at depth {frame_display_tag.depth} without characterId",
                    )

                continue

            # TODO handle PlaceObject3Tag.class_name if present
            if is_new_object:
                # New character at the given depth
                object_properties = self._place_new_object(frame_display_tag)
            else:
                # Modify the character at the given depth
                object_properties = objects_by_depth.get(frame_display_tag.depth)

                if object_properties is None:
                    if self.error_enabled(Errors.UNPROCESSABLE_DATA):
                        raise ProcessingInvalidDataError(
                            f"Cannot modify object as depth {frame_display_tag.depth}: it was not found",
                        )

                    continue

                assert not isinstance(frame_display_tag, PlaceObjectTag)  # Modify is not possible with PlaceObjectTag
                object_properties = self._modify_object(frame_display_tag, object_properties)

            objects_by_depth[frame_display_tag.depth] = object_properties
            current_object_bounds = object_properties.bounds

            if current_object_bounds.width > self._MAX_BOUNDS or current_object_bounds.height > self._MAX_BOUNDS:
                # Do not use this object for computing the sprite bounds
                continue

            if not empty and (
                current_object_bounds.xmax - xmin > self._MAX_BOUNDS
                or current_object_bounds.ymax - ymin > self._MAX_BOUNDS
                or xmax - current_object_bounds.xmin > self._MAX_BOUNDS
                or ymax - current_object_bounds.ymin > self._MAX_BOUNDS
            ):
                # The placement of this object will result in a sprite that is too large,
                # so we ignore it for computing the sprite bounds
                continue

            empty = False

            if current_object_bounds.xmax > xmax:
                xmax = current_object_bounds.xmax

            if current_object_bounds.xmin < xmin:
                xmin = current_object_bounds.xmin

            if current_object_bounds.ymax > ymax:
                ymax = current_object_bounds.ymax

            if current_object_bounds.ymin < ymin:
                ymin = current_object_bounds.ymin

        if not frames:
            if self.error_enabled(Errors.UNPROCESSABLE_DATA):
                raise ProcessingInvalidDataError("No frames found in the timeline: ShowFrame tag is missing")

            return Timeline.empty()

        # An empty sprite gets empty bounds
        sprite_bounds = Rectangle(xmin, xmax, ymin, ymax) if not empty else Rectangle(0, 0, 0, 0)

        # Use same bounds on all frames
        for i, frame in enumerate(frames):
            if frame.bounds != sprite_bounds:
                frames[i] = frame.with_bounds(sprite_bounds)

        return Timeline(sprite_bounds, *frames)

    def _place_new_object(self, tag: PlaceObjectTag | PlaceObject2Tag | PlaceObject3Tag) -> FrameObject:
        """Handle the display of a new object."""
        assert tag.character_id is not None
        object = self._extractor.character(tag.character_id)

        ratio = getattr(tag, "ratio", None)

        if ratio is not None and isinstance(object, RatioDrawable):
            object = object.with_ratio(ratio)

        current_object_bounds = object.bounds

        if tag.matrix is not None:
            # Because the origin shape has already an offset, we need to apply the transformation
            # to the offset, and apply the new matrix to the shape
            new_matrix = tag.matrix.translate(current_object_bounds.xmin, current_object_bounds.ymin)
            current_object_bounds = current_object_bounds.transform(tag.matrix)
        else:
            new_matrix = Matrix(
                translate_x=current_object_bounds.xmin,
                translate_y=current_object_bounds.ymin,
            )

        filters = getattr(tag, "surface_filter_list", None)

        if filters is None:
            filters = []

        return FrameObject(
            tag.depth,
            object,
            current_object_bounds,
            new_matrix,
            tag.color_transform,
            getattr(tag, "clip_depth", None),
            self._decode(getattr(tag, "name", None)),
            filters=filters,
            blend_mode=_blend_mode(getattr(tag, "blend_mode", None)),
            ratio=ratio,
        )

    def _modify_object(
        self,
        tag: PlaceObject2Tag | PlaceObject3Tag,
        object_properties: FrameObject,
    ) -> FrameObject:
        """Handle the movement, or the property changes, of an already displayed object."""
        if tag.character_id is not None:
            # New object to display, so we need to modify the bounds and matrix according to the
            # new object bounds
            old_object_bounds = object_properties.object.bounds
            new_object = self._extractor.character(tag.character_id)
            matrix = tag.matrix
            if matrix is None:
                matrix = object_properties.matrix.translate(-old_object_bounds.xmin, -old_object_bounds.ymin)
            new_object_bounds = new_object.bounds

            object_properties = object_properties.with_(
                object=new_object,
                bounds=new_object_bounds.transform(matrix),
                matrix=matrix.translate(new_object_bounds.xmin, new_object_bounds.ymin),
            )
        elif tag.matrix is not None:
            current_object_bounds = object_properties.object.bounds
            object_properties = object_properties.with_(
                bounds=current_object_bounds.transform(tag.matrix),
                matrix=tag.matrix.translate(current_object_bounds.xmin, current_object_bounds.ymin),
            )

        # PlaceObject3Tag properties
        blend_mode = getattr(tag, "blend_mode", None)
        surface_filter_list = getattr(tag, "surface_filter_list", None)

        if blend_mode is not None or surface_filter_list is not None:
            object_properties = object_properties.with_(
                filters=surface_filter_list,
                blend_mode=_blend_mode(blend_mode) if blend_mode is not None else None,
            )

        if tag.color_transform is not None or tag.clip_depth is not None or tag.name is not None:
            object_properties = object_properties.with_(
                color_transform=tag.color_transform,
                clip_depth=tag.clip_depth,
                name=self._decode(tag.name),
                ratio=tag.ratio,
            )

        if tag.ratio is not None and isinstance(object_properties.object, RatioDrawable):
            old_object_bounds = object_properties.object.bounds
            matrix = tag.matrix
            if matrix is None:
                matrix = object_properties.matrix.translate(-old_object_bounds.xmin, -old_object_bounds.ymin)

            new_object = object_properties.object.with_ratio(tag.ratio)
            current_object_bounds = new_object.bounds

            object_properties = object_properties.with_(
                object=new_object,
                bounds=current_object_bounds.transform(matrix),
                matrix=matrix.translate(current_object_bounds.xmin, current_object_bounds.ymin),
                ratio=tag.ratio,
            )

        return object_properties

    def _decode(self, raw: bytes | None) -> str | None:
        """Decode a tag string with the SWF version of the file being extracted."""
        if raw is None:
            return None

        return decode_swf_text(raw, self._extractor.file.header.version)


def _blend_mode(value: int | None) -> BlendMode:
    """`BlendMode` for a raw blend mode value, defaulting to `NORMAL` for a missing or unknown one."""
    try:
        return BlendMode(value if value is not None else 1)
    except ValueError:
        return BlendMode.NORMAL


def _parsed_tags(tags: Iterable[Any]) -> Iterator[Any]:
    """
    Yield the parsed tags of `tags`.

    `SwfFile.tags()` yields `(raw tag, parsed tag)` pairs, while `DefineSpriteTag.tags` holds the
    parsed tags directly. The PHP counterpart takes both because it iterates a keyed generator by
    value.
    """
    for tag in tags:
        yield tag[1] if isinstance(tag, tuple) else tag
