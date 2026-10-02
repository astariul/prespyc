"""Swapping characters by id, as a character modifier."""

from __future__ import annotations

from typing import TYPE_CHECKING

from prespyc.extractor.modifier.base_character_modifier import BaseCharacterModifier

if TYPE_CHECKING:
    from collections.abc import Mapping

    from prespyc.extractor.drawable import Drawable


class Substitute(BaseCharacterModifier):
    """
    Draws another drawable in place of some characters, wherever the tree places them.

    `replacements` maps a character id to what to draw instead, e.g. a variant built out of the
    character's own timeline. Each placement keeps its matrix, and the bounds up the tree follow.
    """

    __slots__ = ("_replacements",)

    def __init__(self, replacements: Mapping[int, Drawable]) -> None:
        self._replacements = replacements

    def apply_on_sprite(self, sprite):
        return self._replacements.get(sprite.id, sprite)

    def apply_on_shape(self, shape):
        return self._replacements.get(shape.id, shape)

    def apply_on_morph_shape(self, morph_shape):
        return self._replacements.get(morph_shape.id, morph_shape)

    def apply_on_image(self, image):
        return self._replacements.get(image.character_id, image)

    def apply_on_button(self, button):
        return self._replacements.get(button.id, button)

    def apply_on_text(self, text):
        return self._replacements.get(text.id, text)
