"""Protocol for in-place modification of character definitions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from prespyc.extractor.image.image_character import ImageCharacter
    from prespyc.extractor.morph_shape.morph_shape_definition import MorphShapeDefinition
    from prespyc.extractor.shape.shape_definition import ShapeDefinition
    from prespyc.extractor.sprite.sprite_definition import SpriteDefinition
    from prespyc.extractor.timeline.frame import Frame
    from prespyc.extractor.timeline.timeline import Timeline


@runtime_checkable
class CharacterModifier(Protocol):
    """
    Applies a modification to character definitions.

    Prefer subclassing `BaseCharacterModifier`, which implements every method as a no-op.
    """

    def apply_on_sprite(self, sprite: SpriteDefinition) -> SpriteDefinition: ...

    def apply_on_timeline(self, timeline: Timeline) -> Timeline: ...

    def apply_on_frame(self, frame: Frame) -> Frame: ...

    def apply_on_shape(self, shape: ShapeDefinition) -> ShapeDefinition: ...

    def apply_on_morph_shape(self, morph_shape: MorphShapeDefinition) -> MorphShapeDefinition: ...

    def apply_on_image(self, image: ImageCharacter) -> ImageCharacter: ...
