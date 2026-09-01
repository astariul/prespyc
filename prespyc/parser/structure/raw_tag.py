"""Unparsed tag header, and the dispatch to the 59 tag structures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from prespyc.errors import Errors, ExtraDataError
from prespyc.parser.structure.tag.csm_text_settings import CSMTextSettingsTag
from prespyc.parser.structure.tag.define_binary_data import DefineBinaryDataTag
from prespyc.parser.structure.tag.define_bits import DefineBitsTag
from prespyc.parser.structure.tag.define_bits_jpeg2 import DefineBitsJPEG2Tag
from prespyc.parser.structure.tag.define_bits_jpeg3 import DefineBitsJPEG3Tag
from prespyc.parser.structure.tag.define_bits_jpeg4 import DefineBitsJPEG4Tag
from prespyc.parser.structure.tag.define_bits_lossless import DefineBitsLosslessTag
from prespyc.parser.structure.tag.define_button import DefineButtonTag
from prespyc.parser.structure.tag.define_button2 import DefineButton2Tag
from prespyc.parser.structure.tag.define_button_cxform import DefineButtonCxformTag
from prespyc.parser.structure.tag.define_button_sound import DefineButtonSoundTag
from prespyc.parser.structure.tag.define_edit_text import DefineEditTextTag
from prespyc.parser.structure.tag.define_font import DefineFontTag
from prespyc.parser.structure.tag.define_font2_or3 import DefineFont2Or3Tag
from prespyc.parser.structure.tag.define_font4 import DefineFont4Tag
from prespyc.parser.structure.tag.define_font_align_zones import DefineFontAlignZonesTag
from prespyc.parser.structure.tag.define_font_info import DefineFontInfoTag
from prespyc.parser.structure.tag.define_font_name import DefineFontNameTag
from prespyc.parser.structure.tag.define_morph_shape import DefineMorphShapeTag
from prespyc.parser.structure.tag.define_morph_shape2 import DefineMorphShape2Tag
from prespyc.parser.structure.tag.define_scaling_grid import DefineScalingGridTag
from prespyc.parser.structure.tag.define_scene_and_frame_label_data import DefineSceneAndFrameLabelDataTag
from prespyc.parser.structure.tag.define_shape import DefineShapeTag
from prespyc.parser.structure.tag.define_shape4 import DefineShape4Tag
from prespyc.parser.structure.tag.define_sound import DefineSoundTag
from prespyc.parser.structure.tag.define_sprite import DefineSpriteTag
from prespyc.parser.structure.tag.define_text import DefineTextTag
from prespyc.parser.structure.tag.define_video_stream import DefineVideoStreamTag
from prespyc.parser.structure.tag.do_abc import DoABCTag
from prespyc.parser.structure.tag.do_action import DoActionTag
from prespyc.parser.structure.tag.do_init_action import DoInitActionTag
from prespyc.parser.structure.tag.enable_debugger import EnableDebuggerTag
from prespyc.parser.structure.tag.end import EndTag
from prespyc.parser.structure.tag.export_assets import ExportAssetsTag
from prespyc.parser.structure.tag.file_attributes import FileAttributesTag
from prespyc.parser.structure.tag.frame_label import FrameLabelTag
from prespyc.parser.structure.tag.import_assets import ImportAssetsTag
from prespyc.parser.structure.tag.jpeg_tables import JPEGTablesTag
from prespyc.parser.structure.tag.metadata import MetadataTag
from prespyc.parser.structure.tag.place_object import PlaceObjectTag
from prespyc.parser.structure.tag.place_object2 import PlaceObject2Tag
from prespyc.parser.structure.tag.place_object3 import PlaceObject3Tag
from prespyc.parser.structure.tag.product_info import ProductInfo
from prespyc.parser.structure.tag.protect import ProtectTag
from prespyc.parser.structure.tag.reflex import ReflexTag
from prespyc.parser.structure.tag.remove_object import RemoveObjectTag
from prespyc.parser.structure.tag.remove_object2 import RemoveObject2Tag
from prespyc.parser.structure.tag.script_limits import ScriptLimitsTag
from prespyc.parser.structure.tag.set_background_color import SetBackgroundColorTag
from prespyc.parser.structure.tag.set_tab_index import SetTabIndexTag
from prespyc.parser.structure.tag.show_frame import ShowFrameTag
from prespyc.parser.structure.tag.sound_stream_block import SoundStreamBlockTag
from prespyc.parser.structure.tag.sound_stream_head import SoundStreamHeadTag
from prespyc.parser.structure.tag.start_sound import StartSoundTag
from prespyc.parser.structure.tag.start_sound2 import StartSound2Tag
from prespyc.parser.structure.tag.symbol_class import SymbolClassTag
from prespyc.parser.structure.tag.unknown import UnknownTag
from prespyc.parser.structure.tag.video_frame import VideoFrameTag

if TYPE_CHECKING:
    from collections.abc import Iterator

    from prespyc.parser.reader import Reader

DEFINITION_TAG_TYPES: frozenset[int] = frozenset(
    {
        DefineShapeTag.TYPE_V1,
        DefineShapeTag.TYPE_V2,
        DefineShapeTag.TYPE_V3,
        DefineShape4Tag.TYPE_V4,
        DefineFontTag.TYPE_V1,
        DefineFont2Or3Tag.TYPE_V2,
        DefineFont2Or3Tag.TYPE_V3,
        DefineFont4Tag.TYPE_V4,
        DefineButtonTag.TYPE,
        DefineButton2Tag.TYPE,
        DefineSoundTag.TYPE,
        DefineSpriteTag.TYPE,
        DefineTextTag.TYPE_V1,
        DefineTextTag.TYPE_V2,
        DefineBitsLosslessTag.TYPE_V1,
        DefineBitsLosslessTag.TYPE_V2,
        DefineBitsTag.TYPE,
        DefineBitsJPEG2Tag.TYPE,
        DefineBitsJPEG3Tag.TYPE,
        DefineBitsJPEG4Tag.TYPE,
        DefineEditTextTag.TYPE,
        DefineMorphShapeTag.TYPE,
        DefineMorphShape2Tag.TYPE,
        DefineVideoStreamTag.TYPE,
        DefineBinaryDataTag.TYPE,
    }
)
"""Tag types that define a character, and therefore carry a character id."""

# One entry per tag type, taking (reader, swf_version, end). Mirrors ArakneSwf's `SwfTag::parse()`
# match, so the argument each tag actually needs stays visible.
_PARSERS: dict = {
    EndTag.TYPE: lambda reader, version, end: EndTag(),
    ShowFrameTag.TYPE: lambda reader, version, end: ShowFrameTag(),
    DefineShapeTag.TYPE_V1: lambda reader, version, end: DefineShapeTag.read(reader, 1),
    PlaceObjectTag.TYPE: lambda reader, version, end: PlaceObjectTag.read(reader, end),
    RemoveObjectTag.TYPE: lambda reader, version, end: RemoveObjectTag.read(reader),
    DefineBitsTag.TYPE: lambda reader, version, end: DefineBitsTag.read(reader, end),
    DefineButtonTag.TYPE: lambda reader, version, end: DefineButtonTag.read(reader, end),
    JPEGTablesTag.TYPE: lambda reader, version, end: JPEGTablesTag.read(reader, end),
    SetBackgroundColorTag.TYPE: lambda reader, version, end: SetBackgroundColorTag.read(reader),
    DefineFontTag.TYPE_V1: lambda reader, version, end: DefineFontTag.read(reader),
    DefineTextTag.TYPE_V1: lambda reader, version, end: DefineTextTag.read(reader, 1),
    DoActionTag.TYPE: lambda reader, version, end: DoActionTag.read(reader, end),
    DefineFontInfoTag.TYPE_V1: lambda reader, version, end: DefineFontInfoTag.read(reader, 1, end),
    DefineSoundTag.TYPE: lambda reader, version, end: DefineSoundTag.read(reader, end),
    StartSoundTag.TYPE: lambda reader, version, end: StartSoundTag.read(reader),
    DefineButtonSoundTag.TYPE: lambda reader, version, end: DefineButtonSoundTag.read(reader),
    SoundStreamHeadTag.TYPE_V1: lambda reader, version, end: SoundStreamHeadTag.read(reader, 1),
    SoundStreamBlockTag.TYPE: lambda reader, version, end: SoundStreamBlockTag.read(reader, end),
    DefineBitsLosslessTag.TYPE_V1: lambda reader, version, end: DefineBitsLosslessTag.read(reader, 1, end),
    DefineBitsJPEG2Tag.TYPE: lambda reader, version, end: DefineBitsJPEG2Tag.read(reader, end),
    DefineShapeTag.TYPE_V2: lambda reader, version, end: DefineShapeTag.read(reader, 2),
    DefineButtonCxformTag.TYPE: lambda reader, version, end: DefineButtonCxformTag.read(reader),
    ProtectTag.TYPE: lambda reader, version, end: ProtectTag.read(reader, end),
    PlaceObject2Tag.TYPE: lambda reader, version, end: PlaceObject2Tag.read(reader, version),
    RemoveObject2Tag.TYPE: lambda reader, version, end: RemoveObject2Tag.read(reader),
    DefineShapeTag.TYPE_V3: lambda reader, version, end: DefineShapeTag.read(reader, 3),
    DefineTextTag.TYPE_V2: lambda reader, version, end: DefineTextTag.read(reader, 2),
    DefineButton2Tag.TYPE: lambda reader, version, end: DefineButton2Tag.read(reader, end),
    DefineBitsJPEG3Tag.TYPE: lambda reader, version, end: DefineBitsJPEG3Tag.read(reader, end),
    DefineBitsLosslessTag.TYPE_V2: lambda reader, version, end: DefineBitsLosslessTag.read(reader, 2, end),
    DefineEditTextTag.TYPE: lambda reader, version, end: DefineEditTextTag.read(reader),
    DefineSpriteTag.TYPE: lambda reader, version, end: DefineSpriteTag.read(reader, version, end),
    ProductInfo.TYPE: lambda reader, version, end: ProductInfo.read(reader),
    FrameLabelTag.TYPE: lambda reader, version, end: FrameLabelTag.read(reader, end),
    SoundStreamHeadTag.TYPE_V2: lambda reader, version, end: SoundStreamHeadTag.read(reader, 2),
    DefineMorphShapeTag.TYPE: lambda reader, version, end: DefineMorphShapeTag.read(reader),
    DefineFont2Or3Tag.TYPE_V2: lambda reader, version, end: DefineFont2Or3Tag.read(reader, 2),
    ExportAssetsTag.TYPE: lambda reader, version, end: ExportAssetsTag.read(reader),
    ImportAssetsTag.TYPE_V1: lambda reader, version, end: ImportAssetsTag.read(reader, 1),
    EnableDebuggerTag.TYPE_V1: lambda reader, version, end: EnableDebuggerTag.read(reader, 1),
    DoInitActionTag.TYPE: lambda reader, version, end: DoInitActionTag.read(reader, end),
    DefineVideoStreamTag.TYPE: lambda reader, version, end: DefineVideoStreamTag.read(reader),
    VideoFrameTag.TYPE: lambda reader, version, end: VideoFrameTag.read(reader, end),
    DefineFontInfoTag.TYPE_V2: lambda reader, version, end: DefineFontInfoTag.read(reader, 2, end),
    EnableDebuggerTag.TYPE_V2: lambda reader, version, end: EnableDebuggerTag.read(reader, 2),
    ScriptLimitsTag.TYPE: lambda reader, version, end: ScriptLimitsTag.read(reader),
    SetTabIndexTag.TYPE: lambda reader, version, end: SetTabIndexTag.read(reader),
    FileAttributesTag.TYPE: lambda reader, version, end: FileAttributesTag.read(reader),
    PlaceObject3Tag.TYPE: lambda reader, version, end: PlaceObject3Tag.read(reader, version),
    ImportAssetsTag.TYPE_V2: lambda reader, version, end: ImportAssetsTag.read(reader, 2),
    DefineFontAlignZonesTag.TYPE: lambda reader, version, end: DefineFontAlignZonesTag.read(reader, end),
    CSMTextSettingsTag.TYPE: lambda reader, version, end: CSMTextSettingsTag.read(reader),
    DefineFont2Or3Tag.TYPE_V3: lambda reader, version, end: DefineFont2Or3Tag.read(reader, 3),
    SymbolClassTag.TYPE: lambda reader, version, end: SymbolClassTag.read(reader),
    MetadataTag.TYPE: lambda reader, version, end: MetadataTag.read(reader),
    DefineScalingGridTag.TYPE: lambda reader, version, end: DefineScalingGridTag.read(reader),
    DoABCTag.TYPE: lambda reader, version, end: DoABCTag.read(reader, end),
    DefineShape4Tag.TYPE_V4: lambda reader, version, end: DefineShape4Tag.read(reader),
    DefineMorphShape2Tag.TYPE: lambda reader, version, end: DefineMorphShape2Tag.read(reader),
    DefineSceneAndFrameLabelDataTag.TYPE: lambda reader, version, end: DefineSceneAndFrameLabelDataTag.read(reader),
    DefineBinaryDataTag.TYPE: lambda reader, version, end: DefineBinaryDataTag.read(reader, end),
    DefineFontNameTag.TYPE: lambda reader, version, end: DefineFontNameTag.read(reader),
    StartSound2Tag.TYPE: lambda reader, version, end: StartSound2Tag.read(reader),
    DefineBitsJPEG4Tag.TYPE: lambda reader, version, end: DefineBitsJPEG4Tag.read(reader, end),
    DefineFont4Tag.TYPE_V4: lambda reader, version, end: DefineFont4Tag.read(reader, end),
    ReflexTag.TYPE: lambda reader, version, end: ReflexTag.read(reader, end),
}


@dataclass(frozen=True, slots=True)
class RawTag:
    """
    A tag as it appears in the file: a type, a byte range, and — for definition tags — an id.

    Call `parse()` to get the actual tag structure.
    """

    type: int
    """Tag type, as defined in the SWF specification."""

    offset: int
    """
    Byte offset of the tag data, after the tag header (type and length). For an empty tag, this is
    past the end of the tag.
    """

    length: int
    """Length of the tag data in bytes, ignoring the tag header."""

    id: int | None = None
    """Character id, set only for definition tags (i.e. `DefineXxx`)."""

    def parse(self, reader: Reader, swf_version: int) -> object:
        """
        Parse the tag structure.

        `reader` is not modified: the tag data is read through a chunk of it.
        """
        byte_pos_end = self.offset + self.length
        reader = reader.chunk(self.offset, byte_pos_end)

        if byte_pos_end > reader.end:
            byte_pos_end = reader.end

        parser = _PARSERS.get(self.type)

        if parser is None:
            ret = UnknownTag.create(reader, self.type, byte_pos_end)
        else:
            ret = parser(reader, swf_version, byte_pos_end)

        if reader.offset < byte_pos_end and reader.errors & Errors.EXTRA_DATA:
            length = byte_pos_end - reader.offset
            assert length > 0

            raise ExtraDataError(
                f"Extra data found after tag {self.type} at offset {reader.offset} (length = {length})",
                reader.offset,
                length,
            )

        return ret

    @staticmethod
    def read_all(reader: Reader, end: int | None = None, parse_id: bool = True) -> Iterator[RawTag]:
        """Iterate over the tag headers, stopping at `end` or at the end of the buffer."""
        if end is None:
            end = reader.end

        while reader.offset < end:
            record_header = reader.read_ui16()
            tag_type = record_header >> 6
            tag_length = record_header & 0x3F

            if tag_length == 0x3F:
                tag_length = reader.read_ui32()

            if parse_id and tag_type in DEFINITION_TAG_TYPES and tag_length >= 2:
                # The two following bytes are the character id for definition tags
                yield RawTag(type=tag_type, offset=reader.offset, length=tag_length, id=reader.read_ui16())
                reader.skip_bytes(tag_length - 2)  # 2 bytes already consumed
            else:
                yield RawTag(type=tag_type, offset=reader.offset, length=tag_length)
                reader.skip_bytes(tag_length)
