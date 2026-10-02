"""Movie timeline of a sprite or of a SWF file."""

from __future__ import annotations

from typing import TYPE_CHECKING

from prespyc.extractor.timeline.frame import Frame
from prespyc.extractor.timeline.frame_object import FrameObject
from prespyc.parser.structure.record.matrix import Matrix
from prespyc.parser.structure.record.rectangle import Rectangle

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator, Mapping

    from prespyc.extractor.drawable import Drawable
    from prespyc.extractor.drawer.drawer import Drawer
    from prespyc.extractor.modifier.character_modifier import CharacterModifier
    from prespyc.parser.structure.record.color_transform import ColorTransform


class Timeline:
    """
    Movie timeline of a sprite or of a SWF file. Always holds at least one frame.

    It plays like a movie clip: one frame per tick, back to the first one after the last unless a
    script stops it, and each child playing from the frame placing it.
    """

    __slots__ = ("_playback", "bounds", "frames")

    def __init__(self, bounds: Rectangle, *frames: Frame) -> None:
        assert len(frames) > 0

        self.bounds = bounds
        """Display rectangle of the timeline. Every frame should have the same one."""

        self.frames = frames
        """Frames of the timeline, in play order."""

        self._playback: _Playback | None = None

    def frames_count(self, recursive: bool = False) -> int:
        count = len(self.frames)

        if not recursive:
            return count

        for index, frame in enumerate(self.frames):
            frame_count = frame.frames_count(True) + index

            if frame_count > count:
                count = frame_count

        return count

    @property
    def loops(self) -> bool:
        """Whether the timeline starts over after its last frame: none of its frame scripts stops it."""
        return self._play().loops

    def draw(self, drawer: Drawer, frame: int = 0) -> Drawer:
        """
        Draw the timeline as it is after playing `frame` frames.

        Past the last frame, a looping timeline starts over and another one holds its last frame.
        """
        index, ticks = self._play().at(self.frames, frame)

        return self.frames[index].draw(drawer, frame, ticks)

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
        object = FrameObject.place(depth, attachment, name=name)
        frames = [frame.add_object(object) for frame in self.frames]

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

    def pad_to(self, count: int) -> Timeline:
        """Hold the last frame until the timeline is `count` frames long, and return a new timeline."""
        missing = max(0, count - len(self.frames))

        return Timeline(self.bounds, *self.frames, *([self.frames[-1]] * missing))

    def repeat(self, times: int) -> Timeline:
        """Play the frames `times` times in a row, and return a new timeline."""
        return Timeline(self.bounds, *(self.frames * times))

    def rotate(self, start: int) -> Timeline:
        """
        Start on the frame at position `start`, counting from 0, and play the frames before it last.

        The loop stays the same, from another frame: several instances of a clip get out of sync.
        """
        return Timeline(self.bounds, *self.frames[start:], *self.frames[:start])

    def hold(self, extra: Mapping[int, int]) -> Timeline:
        """
        Hold some frames longer and return a new timeline: the frame at position `i`, counting from
        0, plays `1 + extra[i]` times.
        """
        return Timeline(
            self.bounds,
            *(frame for index, frame in enumerate(self.frames) for _ in range(1 + extra.get(index, 0))),
        )

    def keep_ranges(self, ranges: Iterable[tuple[int, int]]) -> Timeline:
        """Play only the frames of the `[start, stop)` ranges, back to back, and return a new timeline."""
        return Timeline(self.bounds, *(frame for start, stop in ranges for frame in self.frames[start:stop]))

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

        index, _ = self._play().at(self.frames, frame)

        return self.draw(SvgCanvas(self.frames[index].bounds, subpixel_stroke_width), frame).render()

    def to_svg_all(self, subpixel_stroke_width: bool = True) -> Iterator[str]:
        """
        Render every frame to SVG, in play order.

        Without `subpixel_stroke_width`, the minimum stroke width is 1px, which approximates Flash
        rendering.
        """
        from prespyc.extractor.drawer.svg.svg_canvas import SvgCanvas

        for f, frame in enumerate(self.frames):
            yield self.draw(SvgCanvas(frame.bounds, subpixel_stroke_width), f).render()

    @classmethod
    def empty(cls) -> Timeline:
        """
        An empty timeline: one empty frame, sized 0x0.

        Used as the fallback value when an error occurs while parsing a timeline.
        """
        return Timeline(Rectangle(0, 0, 0, 0), Frame(Rectangle(0, 0, 0, 0), {}, [], None))

    @classmethod
    def sequence(cls, *drawables: Drawable, depth: int = 1, tag_matrix: Matrix | None = None) -> Timeline:
        """
        A timeline playing one drawable per frame, each placed at `depth` with `tag_matrix`.

        That is how a clip whose frames are states (full, harvested, empty...) is rebuilt out of other
        characters. The bounds hold every drawable.
        """
        objects = [FrameObject.place(depth, drawable, tag_matrix) for drawable in drawables]

        return cls.create(*(Frame(object.bounds, {depth: object}) for object in objects))

    @classmethod
    def create(cls, *frames: Frame) -> Timeline:
        """A timeline holding `frames`, with the same bounds fixed on every frame."""
        bounds = Rectangle.merge([frame.bounds for frame in frames])

        return Timeline(bounds, *[frame.with_bounds(bounds) for frame in frames])

    def _play(self) -> _Playback:
        if self._playback is None:
            self._playback = _Playback(self.frames)

        return self._playback

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Timeline):
            return NotImplemented

        return self.bounds == other.bounds and self.frames == other.frames

    def __repr__(self) -> str:
        return f"Timeline(bounds={self.bounds!r}, frames={len(self.frames)})"


class _Playback:
    """How the frames of a timeline play, worked out once: when each placement starts, and stops."""

    __slots__ = ("loops", "persistent", "starts", "stopped")

    def __init__(self, frames: tuple[Frame, ...]) -> None:
        from prespyc.avm.script import Script

        self.loops = not any(Script(tag.actions).halts for frame in frames for tag in frame.actions)

        self.starts: list[dict[int, int]] = []
        """For each frame, by depth: the frame the placement of the object started on."""

        self.stopped: set[int] = set()
        """Placements whose own clip event handlers stop their object."""

        current: dict[int, tuple[int, int]] = {}
        seen: set[int] = set()

        for index, frame in enumerate(frames):
            starts = {}

            for depth, object in frame.objects.items():
                placement = current.get(depth)

                if placement is None or placement[0] != object.placement:
                    placement = current[depth] = (object.placement, index)

                starts[depth] = placement[1]

                if object.placement not in seen:
                    seen.add(object.placement)

                    if object.stops:
                        self.stopped.add(object.placement)

            for depth in [depth for depth in current if depth not in frame.objects]:
                del current[depth]

            self.starts.append(starts)

        self.persistent = {depth for depth, start in self.starts[-1].items() if start == 0}
        """Depths placed once for the whole timeline: starting over does not place them again."""

    def at(self, frames: tuple[Frame, ...], frame: int) -> tuple[int, dict[int, int]]:
        """The frame to draw after `frame` ticks, and how many frames each of its objects has played."""
        count = len(frames)
        looped = frame >= count and self.loops
        index = frame % count if looped else min(frame, count - 1)
        ticks = {}

        for depth, object in frames[index].objects.items():
            start = self.starts[index][depth]

            if looped:
                tick = frame if depth in self.persistent else index - start
            else:
                tick = frame - start

            if object.placement in self.stopped:
                tick = min(tick, object.object.frames_count() - 1)

            ticks[depth] = tick

        return index, ticks
