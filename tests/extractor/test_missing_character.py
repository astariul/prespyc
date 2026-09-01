"""Port of ArakneSwf's tests/Extractor/MissingCharacterTest.php."""

from __future__ import annotations

from prespyc.extractor.missing_character import MissingCharacter
from prespyc.extractor.modifier.base_character_modifier import BaseCharacterModifier


def test_modify():
    char = MissingCharacter(1234)

    assert char.modify(BaseCharacterModifier()) is char
