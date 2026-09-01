"""Port of ArakneSwf's `tests/Parser/Structure/Tag/SymbolClassTagTest.php`."""

from __future__ import annotations

from prespyc.parser.structure.tag.symbol_class import SymbolClassTag
from tests.support import fixture, fixture_reader


def test_read():
    reader = fixture_reader(fixture("parser", "TestFlex.swf"), 2275941)
    tag = SymbolClassTag.read(reader)

    assert tag.symbols == {
        4: b"mx.graphics.shaderClasses.ColorDodgeShader_ShaderClass",
        9: b"mx.graphics.shaderClasses.LuminosityMaskShader_ShaderClass",
        2: b"mx.graphics.shaderClasses.SaturationShader_ShaderClass",
        3: b"mx.graphics.shaderClasses.SoftLightShader_ShaderClass",
        6: b"mx.graphics.shaderClasses.ColorShader_ShaderClass",
        5: b"mx.graphics.shaderClasses.ExclusionShader_ShaderClass",
        8: b"mx.graphics.shaderClasses.ColorBurnShader_ShaderClass",
        1: b"mx.graphics.shaderClasses.LuminosityShader_ShaderClass",
        7: b"mx.graphics.shaderClasses.HueShader_ShaderClass",
        0: b"TestFlex",
    }
