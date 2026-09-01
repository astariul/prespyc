"""Extracting drawable resources out of a SWF file."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from prespyc._util import decode_swf_text, memory_total, memory_used
from prespyc.extractor.missing_character import MissingCharacter

if TYPE_CHECKING:
    from prespyc.extractor.image.image_character import ImageCharacter
    from prespyc.extractor.morph_shape.morph_shape_definition import MorphShapeDefinition
    from prespyc.extractor.shape.shape_definition import ShapeDefinition
    from prespyc.extractor.sprite.sprite_definition import SpriteDefinition
    from prespyc.extractor.timeline.timeline import Timeline
    from prespyc.swf_file import SwfFile


class Extractor:
    """
    Pulls shapes, morph shapes, sprites, images and the timeline out of a SWF file.

    Everything is lazy and memoised: a character is processed the first time it is asked for, and the
    same instance is returned afterwards. `release()` drops the caches, which also breaks the
    reference cycles between sprites and their children.
    """

    __slots__ = ("_characters", "_exported", "_images", "_morph_shapes", "_shapes", "_sprites", "_timeline", "file")

    def __init__(self, file: SwfFile) -> None:
        self.file = file
        self._characters: dict[int, Any] | None = None
        self._shapes: dict[int, ShapeDefinition] | None = None
        self._morph_shapes: dict[int, MorphShapeDefinition] | None = None
        self._sprites: dict[int, SpriteDefinition] | None = None
        self._images: dict[int, ImageCharacter] | None = None
        self._exported: dict[str, int] | None = None
        self._timeline: Timeline | None = None

    def error_enabled(self, error: int) -> bool:
        """Whether the file was opened with the given error flag enabled."""
        return (self.file.errors & error) != 0

    @property
    def shapes(self) -> dict[int, ShapeDefinition]:
        """Every shape, by character id. Shapes are processed only when drawn."""
        if self._shapes is not None:
            return self._shapes

        from prespyc.extractor.shape.shape_definition import ShapeDefinition
        from prespyc.extractor.shape.shape_processor import ShapeProcessor
        from prespyc.parser.structure.tag.define_shape import DefineShapeTag
        from prespyc.parser.structure.tag.define_shape4 import DefineShape4Tag

        shapes: dict[int, ShapeDefinition] = {}
        processor = ShapeProcessor(self)

        types = (DefineShapeTag.TYPE_V1, DefineShapeTag.TYPE_V2, DefineShapeTag.TYPE_V3, DefineShape4Tag.TYPE_V4)

        for raw, tag in self.file.tags(*types):
            if raw.id is None:
                continue

            shapes[raw.id] = ShapeDefinition(processor, raw.id, tag)

        self._shapes = shapes

        return shapes

    @property
    def morph_shapes(self) -> dict[int, MorphShapeDefinition]:
        """Every morph shape, by character id."""
        if self._morph_shapes is not None:
            return self._morph_shapes

        from prespyc.extractor.morph_shape.morph_shape_definition import MorphShapeDefinition
        from prespyc.extractor.morph_shape.morph_shape_processor import MorphShapeProcessor
        from prespyc.parser.structure.tag.define_morph_shape import DefineMorphShapeTag
        from prespyc.parser.structure.tag.define_morph_shape2 import DefineMorphShape2Tag

        morph_shapes: dict[int, MorphShapeDefinition] = {}
        processor = MorphShapeProcessor(self)

        for raw, tag in self.file.tags(DefineMorphShapeTag.TYPE, DefineMorphShape2Tag.TYPE):
            if raw.id is None:
                continue

            morph_shapes[raw.id] = MorphShapeDefinition(raw.id, tag, processor)

        self._morph_shapes = morph_shapes

        return morph_shapes

    @property
    def sprites(self) -> dict[int, SpriteDefinition]:
        """Every sprite, by character id."""
        if self._sprites is not None:
            return self._sprites

        from prespyc.extractor.sprite.sprite_definition import SpriteDefinition
        from prespyc.extractor.timeline.timeline_processor import TimelineProcessor
        from prespyc.parser.structure.tag.define_sprite import DefineSpriteTag

        sprites: dict[int, SpriteDefinition] = {}
        processor = TimelineProcessor(self)

        for raw, tag in self.file.tags(DefineSpriteTag.TYPE):
            if raw.id is None:
                continue

            sprites[raw.id] = SpriteDefinition(processor, raw.id, tag)

        self._sprites = sprites

        return sprites

    @property
    def images(self) -> dict[int, ImageCharacter]:
        """Every raster image, by character id."""
        if self._images is None:
            # PHP's `+` on arrays keeps the left operand on a key clash, so lossless wins.
            self._images = {**self._extract_define_bits(), **self._extract_jpeg(), **self._extract_lossless_images()}

        return self._images

    def timeline(self, use_file_display_bounds: bool = True) -> Timeline:
        """
        The root timeline animation.

        With `use_file_display_bounds`, the timeline is sized to the file's display bounds;
        otherwise to the union of every frame's bounds.
        """
        from prespyc.extractor.timeline.timeline_processor import TimelineProcessor

        timeline = self._timeline

        if timeline is None:
            processor = TimelineProcessor(self)
            self._timeline = timeline = processor.process(self.file.tags(*TimelineProcessor.TAG_TYPES))

        if not use_file_display_bounds:
            return timeline

        return timeline.with_bounds(self.file.display_bounds)

    def character(self, character_id: int):
        """
        The character with the given id, or a `MissingCharacter` when the file has none.

        Id 0 is the root timeline.
        """
        if character_id == 0:
            return self.timeline()

        if self._characters is None:
            # Same left-wins semantics as PHP's array `+`: shapes, then sprites, then images.
            self._characters = {**self.morph_shapes, **self.images, **self.sprites, **self.shapes}

        return self._characters.get(character_id) or MissingCharacter(character_id)

    def by_name(self, name: str):
        """The character exported under `name`. Raises `KeyError` when it is not exported."""
        id = self.exported.get(name)

        if id is None:
            raise KeyError(f'The name "{name}" has not been exported')

        return self.character(id)

    def __getitem__(self, key: int | str):
        """A character by id (`int`) or by exported name (`str`)."""
        if isinstance(key, str):
            return self.by_name(key)

        return self.character(key)

    @property
    def exported(self) -> dict[str, int]:
        """Exported name to character id."""
        if self._exported is not None:
            return self._exported

        from prespyc.parser.structure.tag.export_assets import ExportAssetsTag
        from prespyc.parser.structure.tag.symbol_class import SymbolClassTag

        version = self.file.header.version
        exported: dict[str, int] = {}

        for _, tag in self.file.tags(ExportAssetsTag.TYPE, SymbolClassTag.TYPE):
            names = tag.characters if isinstance(tag, ExportAssetsTag) else tag.symbols

            for character_id, name in names.items():
                # PHP flips id => name into name => id with `+=`, which keeps the first occurrence.
                exported.setdefault(decode_swf_text(name, version), character_id)

        self._exported = exported

        return exported

    def release(self) -> None:
        """
        Drop every loaded resource.

        Frees memory and breaks the reference cycles between sprites and their children. The
        extractor stays usable; it just reloads what it needs.
        """
        self._characters = None
        self._sprites = None
        self._images = None
        self._shapes = None
        self._morph_shapes = None
        self._exported = None
        self._timeline = None

    def release_if_out_of_memory(self, memory_limit: int | None = None) -> bool:
        """
        Call `release()` if resident memory has reached `memory_limit` bytes.

        Without a limit, the threshold is 75% of the physical memory — PHP uses 75% of
        `memory_limit`, which has no Python equivalent.
        """
        if memory_limit is None:
            should_release = memory_used() / memory_total() >= 0.75
        else:
            should_release = memory_used() >= memory_limit

        if should_release:
            self.release()

        return should_release

    def _extract_lossless_images(self) -> dict[int, ImageCharacter]:
        from prespyc.extractor.image.lossless_image_definition import LosslessImageDefinition
        from prespyc.parser.structure.tag.define_bits_lossless import DefineBitsLosslessTag

        images: dict[int, ImageCharacter] = {}

        for raw, tag in self.file.tags(DefineBitsLosslessTag.TYPE_V1, DefineBitsLosslessTag.TYPE_V2):
            if raw.id is None:
                continue

            images[raw.id] = LosslessImageDefinition(tag)

        return images

    def _extract_define_bits(self) -> dict[int, ImageCharacter]:
        from prespyc.extractor.image.image_bits_definition import ImageBitsDefinition
        from prespyc.parser.structure.tag.define_bits import DefineBitsTag
        from prespyc.parser.structure.tag.jpeg_tables import JPEGTablesTag

        images: dict[int, ImageCharacter] = {}
        jpeg_tables = None

        for _, tag in self.file.tags(JPEGTablesTag.TYPE, DefineBitsTag.TYPE):
            if isinstance(tag, JPEGTablesTag):
                jpeg_tables = tag
                continue

            if jpeg_tables is None:
                continue  # A JPEGTables tag must come before the DefineBits tags

            images[tag.character_id] = ImageBitsDefinition(tag, jpeg_tables)

        return images

    def _extract_jpeg(self) -> dict[int, ImageCharacter]:
        from prespyc.extractor.image.jpeg_image_definition import JpegImageDefinition
        from prespyc.parser.structure.tag.define_bits_jpeg2 import DefineBitsJPEG2Tag
        from prespyc.parser.structure.tag.define_bits_jpeg3 import DefineBitsJPEG3Tag
        from prespyc.parser.structure.tag.define_bits_jpeg4 import DefineBitsJPEG4Tag

        images: dict[int, ImageCharacter] = {}

        for raw, tag in self.file.tags(DefineBitsJPEG2Tag.TYPE, DefineBitsJPEG3Tag.TYPE, DefineBitsJPEG4Tag.TYPE):
            if raw.id is None:
                continue

            images[raw.id] = JpegImageDefinition(tag)

        return images
