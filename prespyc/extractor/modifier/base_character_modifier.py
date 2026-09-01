"""Base class for character modifiers."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from prespyc.extractor.image.image_character import ImageCharacter
    from prespyc.extractor.morph_shape.morph_shape_definition import MorphShapeDefinition
    from prespyc.extractor.shape.shape_definition import ShapeDefinition
    from prespyc.extractor.sprite.sprite_definition import SpriteDefinition
    from prespyc.extractor.timeline.frame import Frame
    from prespyc.extractor.timeline.timeline import Timeline


class BaseCharacterModifier:
    """
    Default, no-op implementation of every `CharacterModifier` method.

    Subclass this rather than implementing the protocol directly: new methods may be added later.
    """

    __slots__ = ()

    def apply_on_sprite(self, sprite: SpriteDefinition) -> SpriteDefinition:
        return sprite

    def apply_on_timeline(self, timeline: Timeline) -> Timeline:
        return timeline

    def apply_on_frame(self, frame: Frame) -> Frame:
        return frame

    def apply_on_shape(self, shape: ShapeDefinition) -> ShapeDefinition:
        return shape

    def apply_on_morph_shape(self, morph_shape: MorphShapeDefinition) -> MorphShapeDefinition:
        return morph_shape

    def apply_on_image(self, image: ImageCharacter) -> ImageCharacter:
        return image
