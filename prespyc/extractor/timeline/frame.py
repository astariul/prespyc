"""A single frame of a timeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from prespyc.parser.structure.record.rectangle import Rectangle

if TYPE_CHECKING:
    from prespyc.avm.processor import Processor
    from prespyc.avm.state import State
    from prespyc.extractor.drawer.drawer import Drawer
    from prespyc.extractor.modifier.character_modifier import CharacterModifier
    from prespyc.extractor.timeline.frame_object import FrameObject
    from prespyc.parser.structure.record.color_transform import ColorTransform
    from prespyc.parser.structure.tag.do_action import DoActionTag


@dataclass(frozen=True, slots=True)
class Frame:
    """A single frame of a timeline."""

    bounds: Rectangle
    """Display rectangle of the frame. It should be the same for every frame of the timeline."""

    objects: dict[int, FrameObject]
    """Objects to display, by depth, in drawing order."""

    actions: list[DoActionTag] = field(default_factory=list)
    """Script actions attached to this frame."""

    label: str | None = None
    """Frame label, targeted by the "go to label" action."""

    def frames_count(self, recursive: bool = False) -> int:
        if not recursive:
            return 1

        count = 1

        for object in self.objects.values():
            object_frames_count = object.object.frames_count(True)

            if object_frames_count > count:
                count = object_frames_count

        return count

    def draw(self, drawer: Drawer, frame: int = 0) -> Drawer:
        drawer.area(self.bounds)

        # Active clips, as the drawer-generated clip id to the depth the clip applies up to.
        active_clips: dict[str, int] = {}

        for object in self.objects.values():
            if object.clip_depth is not None:
                id = drawer.start_clip(object.object, object.matrix, frame)
                active_clips[id] = object.clip_depth

                continue

            for id, depth in list(active_clips.items()):
                if depth < object.depth:
                    drawer.end_clip(id)
                    del active_clips[id]

            drawer.include(
                object.transformed_object,
                object.matrix,
                frame,
                object.filters,
                object.blend_mode,
                object.name,
            )

        return drawer

    def transform_colors(self, color_transform: ColorTransform) -> Frame:
        objects = {}

        for depth, object in self.objects.items():
            objects[depth] = object.transform_colors(color_transform)

        return Frame(
            self.bounds,
            objects,
            self.actions,
            self.label,
        )

    def object_by_name(self, name: str) -> FrameObject | None:
        """The object named `name`, or `None` when the frame has none."""
        for object in self.objects.values():
            if object.name == name:
                return object

        return None

    @property
    def objects_by_name(self) -> dict[str, FrameObject]:
        """
        Named objects, by name. Objects without a name are left out.

        When several objects share a name, only the last one is kept.
        """
        objects = {}

        for object in self.objects.values():
            if object.name is not None:
                objects[object.name] = object

        return objects

    def run(self, state: State | None = None, processor: Processor | None = None) -> State:
        """
        Execute the frame actions and return the resulting state.

        The execution context of the timeline (i.e. `this`, and the objects) is not provided, and
        the actions of nested timelines are not executed.
        """
        if state is None:
            from prespyc.avm.state import State as DefaultState

            state = DefaultState()

        if processor is None:
            from prespyc.avm.processor import Processor as DefaultProcessor

            processor = DefaultProcessor()

        for action in self.actions:
            processor.run(action.actions, state)

        return state

    def modify(self, modifier: CharacterModifier, max_depth: int = -1) -> Frame:
        result = self

        if max_depth != 0:
            objects = {}
            is_modified = False

            xmin = self.bounds.xmin
            ymin = self.bounds.ymin
            xmax = self.bounds.xmax
            ymax = self.bounds.ymax

            for depth, object in self.objects.items():
                new_object = object.object.modify(modifier, max_depth - 1)

                if new_object is object.object:
                    objects[depth] = object
                    continue

                is_modified = True
                old_object_bounds = object.object.bounds
                old_matrix = object.matrix.translate(-old_object_bounds.xmin, -old_object_bounds.ymin)

                new_bounds = new_object.bounds.transform(old_matrix)
                objects[depth] = object.with_(
                    object=new_object,
                    bounds=new_bounds,
                    matrix=old_matrix.translate(new_object.bounds.xmin, new_object.bounds.ymin),
                )

                if new_bounds.xmin < xmin:
                    xmin = new_bounds.xmin
                if new_bounds.ymin < ymin:
                    ymin = new_bounds.ymin
                if new_bounds.xmax > xmax:
                    xmax = new_bounds.xmax
                if new_bounds.ymax > ymax:
                    ymax = new_bounds.ymax

            if is_modified:
                result = Frame(
                    Rectangle(xmin, xmax, ymin, ymax),
                    objects,
                    self.actions,
                    self.label,
                )

        return modifier.apply_on_frame(result)

    def with_bounds(self, new_bounds: Rectangle) -> Frame:
        """
        Change the display bounds of the frame.

        Used to keep the same bounds on every frame of a sprite.
        """
        return Frame(
            new_bounds,
            self.objects,
            self.actions,
            self.label,
        )

    def compact(self) -> Frame:
        """
        Recompute the bounds of the frame from its objects.

        Useful to extract a frame out of a timeline and still get correct bounds.
        """
        return Frame(
            Rectangle.merge([object.bounds for object in self.objects.values()]),
            self.objects,
            self.actions,
            self.label,
        )

    def add_object(self, object: FrameObject) -> Frame:
        """
        Add an object at its depth and return a new frame with updated bounds. The timeline bounds
        should be updated accordingly.

        An object already at the same depth is replaced silently.
        """
        objects = dict(self.objects)
        objects[object.depth] = object
        objects = dict(sorted(objects.items()))
        bounds = self.bounds.union(object.bounds)

        return Frame(
            bounds,
            objects,
            self.actions,
            self.label,
        )
