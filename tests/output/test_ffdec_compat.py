"""
Phase 7 gate: a sprite comes out through the ffdec shim, in ffdec's on-disk layout.

A caller migrating off ffdec reads `{out}/DefineSprite_{id}_{name}/{frame + 1}.png`, so that layout
is the contract.
"""

from __future__ import annotations

import pytest
from PIL import Image

from prespyc.output.ffdec_compat import ZOOM, ffdec_export
from tests.support import fixture


def test_zoom_default():
    assert ZOOM == 2


def test_export_one_sprite(tmp_path):
    ffdec_export("sprite", fixture("extractor", "1047", "1047.swf"), tmp_path, chids=[62])

    directory = tmp_path / "DefineSprite_62_anim0R"
    assert directory.is_dir()

    frames = sorted(directory.iterdir(), key=lambda p: int(p.stem))
    assert [path.name for path in frames] == [f"{i}.png" for i in range(1, 41)]

    with Image.open(frames[0]) as image:
        assert image.format == "PNG"
        assert image.size > (0, 0)


def test_unnamed_sprite_has_no_name_suffix(tmp_path):
    ffdec_export("sprite", fixture("extractor", "1047", "1047.swf"), tmp_path, chids=[61])

    assert (tmp_path / "DefineSprite_61").is_dir()


def test_export_all_sprites(tmp_path):
    ffdec_export("sprite", fixture("extractor", "complex_sprite.swf"), tmp_path)

    directories = sorted(p.name for p in tmp_path.iterdir())
    assert directories
    assert all(name.startswith("DefineSprite_") for name in directories)
    assert all(any(p.iterdir()) for p in tmp_path.iterdir())


def test_export_shapes(tmp_path):
    ffdec_export("shape", fixture("extractor", "2.swf"), tmp_path)

    assert sorted(p.name for p in tmp_path.iterdir()) == ["DefineShape_1", "DefineShape_2"]
    assert (tmp_path / "DefineShape_1" / "1.png").is_file()


def test_single_frame_and_subframes(tmp_path):
    ffdec_export("sprite", fixture("extractor", "1047", "1047.swf"), tmp_path, chids=[62], frame_idx=3)
    assert [p.name for p in (tmp_path / "DefineSprite_62_anim0R").iterdir()] == ["1.png"]

    ffdec_export("sprite", fixture("extractor", "1047", "1047.swf"), tmp_path, chids=[62], frame_idx=3, subframes=4)
    assert sorted(p.name for p in (tmp_path / "DefineSprite_62_anim0R").iterdir()) == [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
    ]


def test_clean_folder(tmp_path):
    stale = tmp_path / "stale"
    stale.mkdir()
    (stale / "old.png").write_bytes(b"")

    ffdec_export("sprite", fixture("extractor", "2.swf"), tmp_path, clean_folder=True, chids=[1])

    assert not stale.exists()

    stale.mkdir()
    (stale / "old.png").write_bytes(b"")
    ffdec_export("sprite", fixture("extractor", "2.swf"), tmp_path, clean_folder=False, chids=[1])

    assert stale.exists()


def test_script_export_points_at_the_avm(tmp_path):
    with pytest.raises(NotImplementedError, match=r"SwfFile\.variables"):
        ffdec_export("script", fixture("simple.swf"), tmp_path)


def test_unknown_export_type(tmp_path):
    with pytest.raises(ValueError, match="Unsupported export type: movie"):
        ffdec_export("movie", fixture("simple.swf"), tmp_path)
