"""A morph shape character."""

from __future__ import annotations

from copy import copy
from typing import TYPE_CHECKING

from prespyc.extractor.drawable import RatioDrawable

if TYPE_CHECKING:
    from prespyc.extractor.drawable import Drawable
    from prespyc.extractor.drawer.drawer import Drawer
    from prespyc.extractor.modifier.character_modifier import CharacterModifier
    from prespyc.extractor.morph_shape.morph_shape import MorphShape
    from prespyc.extractor.morph_shape.morph_shape_processor import MorphShapeProcessor
    from prespyc.parser.structure.record.color_transform import ColorTransform
    from prespyc.parser.structure.record.rectangle import Rectangle
    from prespyc.parser.structure.tag.define_morph_shape import DefineMorphShapeTag
    from prespyc.parser.structure.tag.define_morph_shape2 import DefineMorphShape2Tag


class MorphShapeDefinition(RatioDrawable):
    """
    A morph shape character.

    Use `with_ratio()` to change the morph "frame": the `frame` argument of `draw()` is ignored.
    """

    __slots__ = ("_morph_shape", "_processor", "_ratio", "id", "tag")

    id: int
    """The character id."""

    tag: DefineMorphShapeTag | DefineMorphShape2Tag
    """The tag the morph shape is built from."""

    _ratio: int
    """The morph ratio: 0 is the start shape, `MAX_RATIO` the end shape."""

    def __init__(
        self,
        id: int,
        tag: DefineMorphShapeTag | DefineMorphShape2Tag,
        processor: MorphShapeProcessor,
    ) -> None:
        self.id = id
        self.tag = tag
        self._processor: MorphShapeProcessor | None = processor
        self._morph_shape: MorphShape | None = None
        self._ratio = 0

    @property
    def morph_shape(self) -> MorphShape:
        """The morph shape of the tag, processed once and cached."""
        if self._morph_shape is None:
            assert self._processor is not None
            self._morph_shape = self._processor.process(self.tag)
            self._processor = None  # Free memory

        return self._morph_shape

    def with_ratio(self, ratio: int) -> Drawable:
        new = copy(self)
        new._ratio = ratio

        return new

    @property
    def bounds(self) -> Rectangle:
        return self.morph_shape.bounds(self._ratio)

    def frames_count(self, recursive: bool = False) -> int:
        return 1

    def draw(self, drawer: Drawer, frame: int = 0) -> Drawer:
        drawer.shape(self.morph_shape.interpolate(self._ratio))

        return drawer

    def transform_colors(self, color_transform: ColorTransform) -> Drawable:
        new = copy(self)
        new._morph_shape = self.morph_shape.transform_colors(color_transform)

        return new

    def modify(self, modifier: CharacterModifier, max_depth: int = -1) -> Drawable:
        return modifier.apply_on_morph_shape(self)
