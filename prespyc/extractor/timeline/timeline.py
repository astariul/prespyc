"""Movie timeline of a sprite or of a SWF file."""

from __future__ import annotations

from typing import TYPE_CHECKING

from prespyc.extractor.timeline.frame import Frame
from prespyc.extractor.timeline.frame_object import FrameObject
from prespyc.parser.structure.record.matrix import Matrix
from prespyc.parser.structure.record.rectangle import Rectangle

if TYPE_CHECKING:
    from collections.abc import Iterator

    from prespyc.extractor.drawable import Drawable
    from prespyc.extractor.drawer.drawer import Drawer
    from prespyc.extractor.modifier.character_modifier import CharacterModifier
    from prespyc.parser.structure.record.color_transform import ColorTransform


class Timeline:
    """Movie timeline of a sprite or of a SWF file. Always holds at least one frame."""

    __slots__ = ("bounds", "frames")

    def __init__(self, bounds: Rectangle, *frames: Frame) -> None:
        assert len(frames) > 0

        self.bounds = bounds
        """Display rectangle of the timeline. Every frame should have the same one."""

        self.frames = frames
        """Frames of the timeline, in play order."""

    def frames_count(self, recursive: bool = False) -> int:
        count = len(self.frames)

        if not recursive:
            return count

        for index, frame in enumerate(self.frames):
            frame_count = frame.frames_count(True) + index

            if frame_count > count:
                count = frame_count

        return count

    def draw(self, drawer: Drawer, frame: int = 0) -> Drawer:
        frames = self.frames
        current_frame = min(frame, len(frames) - 1)

        return frames[current_frame].draw(drawer, frame)

    def transform_colors(self, color_transform: ColorTransform) -> Timeline:
        frames = []

        for frame in self.frames:
            frames.append(frame.transform_colors(color_transform))

        return Timeline(self.bounds, *frames)

    def modify(self, modifier: CharacterModifier, max_depth: int = -1) -> Timeline:
        result = self

        if max_depth != 0:
            frames = []
            is_modified = False

            for frame in self.frames:
                modified_frame = frame.modify(modifier, max_depth - 1)
                frames.append(modified_frame)
                is_modified = is_modified or (modified_frame is not frame)

            if is_modified:
                result = Timeline.create(*frames)

        return modifier.apply_on_timeline(result)

    def frame_by_label(self, label: str) -> Frame | None:
        """The frame labelled `label`, or `None` when there is none."""
        for frame in self.frames:
            if frame.label == label:
                return frame

        return None

    def with_attachment(self, attachment: Drawable, depth: int, name: str | None) -> Timeline:
        """
        Attach an object at `depth` under `name` and return a new timeline.

        Equivalent to the "Attach Movie" action of SWF files. `name` is set on
        `FrameObject.name`.
        """
        bounds = attachment.bounds
        frames = [
            frame.add_object(
                FrameObject(
                    depth=depth,
                    object=attachment,
                    bounds=bounds,
                    matrix=Matrix(
                        translate_x=bounds.xmin,
                        translate_y=bounds.ymin,
                    ),
                    name=name,
                )
            )
            for frame in self.frames
        ]

        return Timeline.create(*frames)

    def keep_frame_by_label(self, label: str) -> Timeline:
        """
        Keep only the frame labelled `label` and return a new timeline. Falls back to the first
        frame when the label is not found.

        Child timelines are left alone; use the `GotoAndStop` modifier for those.
        """
        if len(self.frames) == 1:
            return self

        frame = self.frame_by_label(label)

        return Timeline(
            self.bounds,
            frame if frame is not None else self.frames[0],
        )

    def keep_frame_by_number(self, number: int) -> Timeline:
        """
        Keep only the frame at position `number`, counting from 1, and return a new timeline. A
        number past the last frame keeps the last one.

        Child timelines are left alone; use the `GotoAndStop` modifier for those.
        """
        count = len(self.frames)

        if count == 1:
            return self

        if number < 1:
            number = 1
        elif number > count:
            number = count

        return Timeline(
            self.bounds,
            self.frames[number - 1],
        )

    def with_bounds(self, new_bounds: Rectangle) -> Timeline:
        """Change the display bounds of the timeline and of its frames, and return a new timeline."""
        frames = []

        for frame in self.frames:
            frames.append(frame.with_bounds(new_bounds))

        return Timeline(new_bounds, *frames)

    def to_svg(self, frame: int = 0, subpixel_stroke_width: bool = True) -> str:
        """
        Render a single frame to SVG. A `frame` past the last one renders the last frame.

        Without `subpixel_stroke_width`, the minimum stroke width is 1px, which approximates Flash
        rendering.
        """
        from prespyc.extractor.drawer.svg.svg_canvas import SvgCanvas

        max_frame = len(self.frames) - 1
        to_render = self.frames[min(frame, max_frame)]

        return to_render.draw(SvgCanvas(to_render.bounds, subpixel_stroke_width), frame).render()

    def to_svg_all(self, subpixel_stroke_width: bool = True) -> Iterator[str]:
        """
        Render every frame to SVG, in play order.

        Without `subpixel_stroke_width`, the minimum stroke width is 1px, which approximates Flash
        rendering.
        """
        from prespyc.extractor.drawer.svg.svg_canvas import SvgCanvas

        for f, frame in enumerate(self.frames):
            drawer = SvgCanvas(frame.bounds, subpixel_stroke_width)
            frame.draw(drawer, f)

            yield drawer.render()

    @classmethod
    def empty(cls) -> Timeline:
        """
        An empty timeline: one empty frame, sized 0x0.

        Used as the fallback value when an error occurs while parsing a timeline.
        """
        return Timeline(Rectangle(0, 0, 0, 0), Frame(Rectangle(0, 0, 0, 0), {}, [], None))

    @classmethod
    def create(cls, *frames: Frame) -> Timeline:
        """A timeline holding `frames`, with the same bounds fixed on every frame."""
        bounds = Rectangle.merge([frame.bounds for frame in frames])

        return Timeline(bounds, *[frame.with_bounds(bounds) for frame in frames])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Timeline):
            return NotImplemented

        return self.bounds == other.bounds and self.frames == other.frames

    def __repr__(self) -> str:
        return f"Timeline(bounds={self.bounds!r}, frames={len(self.frames)})"
