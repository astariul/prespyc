# PORTING

File-by-file map from ArakneSwf (PHP) to `prespyc` (Python). This is the contract the port follows:
module paths and class names are fixed here so that work on different subsystems stays consistent.

Read [CONVENTIONS.md](CONVENTIONS.md) first — it holds the idiom, naming and fidelity rules.

`src/Console/**` (~720 LOC) is dropped: `prespyc` is a library, not a CLI.


## `src/`

| PHP file | Python module | Python name | PHP LOC |
|---|---|---|---|
| `SwfFile.php` | `prespyc/swf_file.py` | `SwfFile` | 336 |

## `src/Error/`

| PHP file | Python module | Python name | PHP LOC |
|---|---|---|---|
| `Errors.php` | `prespyc/errors.py` | `Errors` | 87 |
| `SwfExceptionInterface.php` | `prespyc/errors.py` | `SwfError` | 28 |

## `src/Util/`

| PHP file | Python module | Python name | PHP LOC |
|---|---|---|---|
| `Memory.php` | `prespyc/_util.py` | `Memory` | 102 |

## `src/Parser/`

| PHP file | Python module | Python name | PHP LOC |
|---|---|---|---|
| `Swf.php` | `prespyc/parser/swf.py` | `Swf` | 143 |
| `SwfReader.php` | `prespyc/parser/reader.py` | `Reader` | 864 |

## `src/Parser/Error/`

| PHP file | Python module | Python name | PHP LOC |
|---|---|---|---|
| `ParserExceptionInterface.php` | `prespyc/errors.py` | `ParserError` | 36 |
| `ParserExtraDataException.php` | `prespyc/errors.py` | `ExtraDataError` | 53 |
| `ParserInvalidDataException.php` | `prespyc/errors.py` | `InvalidDataError` | 65 |
| `ParserOutOfBoundException.php` | `prespyc/errors.py` | `OutOfBoundsError` | 77 |
| `UnknownTagException.php` | `prespyc/errors.py` | `UnknownTagError` | 49 |

## `src/Parser/Structure/`

| PHP file | Python module | Python name | PHP LOC |
|---|---|---|---|
| `SwfHeader.php` | `prespyc/parser/structure/header.py` | `Header` | 55 |
| `SwfTag.php` | `prespyc/parser/structure/raw_tag.py` | `RawTag` | 317 |

## `src/Parser/Structure/Record/`

| PHP file | Python module | Python name | PHP LOC |
|---|---|---|---|
| `ButtonCondAction.php` | `prespyc/parser/structure/record/button_cond_action.py` | `ButtonCondAction` | 128 |
| `ButtonRecord.php` | `prespyc/parser/structure/record/button_record.py` | `ButtonRecord` | 94 |
| `ClipActionRecord.php` | `prespyc/parser/structure/record/clip_action_record.py` | `ClipActionRecord` | 81 |
| `ClipActions.php` | `prespyc/parser/structure/record/clip_actions.py` | `ClipActions` | 53 |
| `ClipEventFlags.php` | `prespyc/parser/structure/record/clip_event_flags.py` | `ClipEventFlags` | 82 |
| `Color.php` | `prespyc/parser/structure/record/color.py` | `Color` | 99 |
| `ColorTransform.php` | `prespyc/parser/structure/record/color_transform.py` | `ColorTransform` | 157 |
| `EditTextLayout.php` | `prespyc/parser/structure/record/edit_text_layout.py` | `EditTextLayout` | 52 |
| `FontLayout.php` | `prespyc/parser/structure/record/font_layout.py` | `FontLayout` | 91 |
| `GlyphEntry.php` | `prespyc/parser/structure/record/glyph_entry.py` | `GlyphEntry` | 59 |
| `Gradient.php` | `prespyc/parser/structure/record/gradient.py` | `Gradient` | 144 |
| `GradientRecord.php` | `prespyc/parser/structure/record/gradient_record.py` | `GradientRecord` | 41 |
| `ImageBitmapType.php` | `prespyc/parser/structure/record/image_bitmap_type.py` | `ImageBitmapType` | 90 |
| `ImageDataType.php` | `prespyc/parser/structure/record/image_data_type.py` | `ImageDataType` | 68 |
| `KerningRecord.php` | `prespyc/parser/structure/record/kerning_record.py` | `KerningRecord` | 30 |
| `Matrix.php` | `prespyc/parser/structure/record/matrix.py` | `Matrix` | 170 |
| `Rectangle.php` | `prespyc/parser/structure/record/rectangle.py` | `Rectangle` | 234 |
| `SoundEnvelope.php` | `prespyc/parser/structure/record/sound_envelope.py` | `SoundEnvelope` | 30 |
| `SoundInfo.php` | `prespyc/parser/structure/record/sound_info.py` | `SoundInfo` | 85 |
| `TextRecord.php` | `prespyc/parser/structure/record/text_record.py` | `TextRecord` | 95 |
| `ZoneData.php` | `prespyc/parser/structure/record/zone_data.py` | `ZoneData` | 29 |
| `ZoneRecord.php` | `prespyc/parser/structure/record/zone_record.py` | `ZoneRecord` | 74 |

## `src/Parser/Structure/Record/Filter/`

| PHP file | Python module | Python name | PHP LOC |
|---|---|---|---|
| `BevelFilter.php` | `prespyc/parser/structure/record/filter/bevel_filter.py` | `BevelFilter` | 67 |
| `BlurFilter.php` | `prespyc/parser/structure/record/filter/blur_filter.py` | `BlurFilter` | 45 |
| `ColorMatrixFilter.php` | `prespyc/parser/structure/record/filter/color_matrix_filter.py` | `ColorMatrixFilter` | 53 |
| `ConvolutionFilter.php` | `prespyc/parser/structure/record/filter/convolution_filter.py` | `ConvolutionFilter` | 80 |
| `DropShadowFilter.php` | `prespyc/parser/structure/record/filter/drop_shadow_filter.py` | `DropShadowFilter` | 60 |
| `Filter.php` | `prespyc/parser/structure/record/filter/filter.py` | `Filter` | 80 |
| `GlowFilter.php` | `prespyc/parser/structure/record/filter/glow_filter.py` | `GlowFilter` | 56 |
| `GradientBevelFilter.php` | `prespyc/parser/structure/record/filter/gradient_bevel_filter.py` | `GradientBevelFilter` | 90 |
| `GradientGlowFilter.php` | `prespyc/parser/structure/record/filter/gradient_glow_filter.py` | `GradientGlowFilter` | 86 |

## `src/Parser/Structure/Record/Shape/`

| PHP file | Python module | Python name | PHP LOC |
|---|---|---|---|
| `CurvedEdgeRecord.php` | `prespyc/parser/structure/record/shape/curved_edge_record.py` | `CurvedEdgeRecord` | 31 |
| `EndShapeRecord.php` | `prespyc/parser/structure/record/shape/end_shape_record.py` | `EndShapeRecord` | 23 |
| `FillStyle.php` | `prespyc/parser/structure/record/shape/fill_style.py` | `FillStyle` | 116 |
| `LineStyle.php` | `prespyc/parser/structure/record/shape/line_style.py` | `LineStyle` | 119 |
| `ShapeRecord.php` | `prespyc/parser/structure/record/shape/shape_record.py` | `ShapeRecord` | 153 |
| `ShapeWithStyle.php` | `prespyc/parser/structure/record/shape/shape_with_style.py` | `ShapeWithStyle` | 65 |
| `StraightEdgeRecord.php` | `prespyc/parser/structure/record/shape/straight_edge_record.py` | `StraightEdgeRecord` | 31 |
| `StyleChangeRecord.php` | `prespyc/parser/structure/record/shape/style_change_record.py` | `StyleChangeRecord` | 50 |

## `src/Parser/Structure/Record/MorphShape/`

| PHP file | Python module | Python name | PHP LOC |
|---|---|---|---|
| `MorphFillStyle.php` | `prespyc/parser/structure/record/morph_shape/morph_fill_style.py` | `MorphFillStyle` | 114 |
| `MorphGradient.php` | `prespyc/parser/structure/record/morph_shape/morph_gradient.py` | `MorphGradient` | 105 |
| `MorphGradientRecord.php` | `prespyc/parser/structure/record/morph_shape/morph_gradient_record.py` | `MorphGradientRecord` | 33 |
| `MorphLineStyle.php` | `prespyc/parser/structure/record/morph_shape/morph_line_style.py` | `MorphLineStyle` | 69 |
| `MorphLineStyle2.php` | `prespyc/parser/structure/record/morph_shape/morph_line_style2.py` | `MorphLineStyle2` | 117 |

## `src/Parser/Structure/Action/`

| PHP file | Python module | Python name | PHP LOC |
|---|---|---|---|
| `ActionRecord.php` | `prespyc/parser/structure/action/action_record.py` | `ActionRecord` | 101 |
| `DefineFunction2Data.php` | `prespyc/parser/structure/action/define_function2_data.py` | `DefineFunction2Data` | 93 |
| `DefineFunctionData.php` | `prespyc/parser/structure/action/define_function_data.py` | `DefineFunctionData` | 49 |
| `GetURL2Data.php` | `prespyc/parser/structure/action/get_url2_data.py` | `GetURL2Data` | 44 |
| `GetURLData.php` | `prespyc/parser/structure/action/get_url_data.py` | `GetURLData` | 39 |
| `GotoFrame2Data.php` | `prespyc/parser/structure/action/goto_frame2_data.py` | `GotoFrame2Data` | 45 |
| `Opcode.php` | `prespyc/parser/structure/action/opcode.py` | `Opcode` | 197 |
| `Type.php` | `prespyc/parser/structure/action/type.py` | `Type` | 45 |
| `Value.php` | `prespyc/parser/structure/action/value.py` | `Value` | 99 |
| `WaitForFrameData.php` | `prespyc/parser/structure/action/wait_for_frame_data.py` | `WaitForFrameData` | 39 |

## `src/Parser/Structure/Tag/`

| PHP file | Python module | Python name | PHP LOC |
|---|---|---|---|
| `CSMTextSettingsTag.php` | `prespyc/parser/structure/tag/csm_text_settings.py` | `CSMTextSettingsTag` | 64 |
| `DefineBinaryDataTag.php` | `prespyc/parser/structure/tag/define_binary_data.py` | `DefineBinaryDataTag` | 53 |
| `DefineBitsJPEG2Tag.php` | `prespyc/parser/structure/tag/define_bits_jpeg2.py` | `DefineBitsJPEG2Tag` | 58 |
| `DefineBitsJPEG3Tag.php` | `prespyc/parser/structure/tag/define_bits_jpeg3.py` | `DefineBitsJPEG3Tag` | 86 |
| `DefineBitsJPEG4Tag.php` | `prespyc/parser/structure/tag/define_bits_jpeg4.py` | `DefineBitsJPEG4Tag` | 89 |
| `DefineBitsJPEGTagInterface.php` | `prespyc/parser/structure/tag/define_bits_jpeg.py` | `DefineBitsJPEGTag` | 48 |
| `DefineBitsLosslessTag.php` | `prespyc/parser/structure/tag/define_bits_lossless.py` | `DefineBitsLosslessTag` | 132 |
| `DefineBitsTag.php` | `prespyc/parser/structure/tag/define_bits.py` | `DefineBitsTag` | 51 |
| `DefineButton2Tag.php` | `prespyc/parser/structure/tag/define_button2.py` | `DefineButton2Tag` | 73 |
| `DefineButtonCxformTag.php` | `prespyc/parser/structure/tag/define_button_cxform.py` | `DefineButtonCxformTag` | 51 |
| `DefineButtonSoundTag.php` | `prespyc/parser/structure/tag/define_button_sound.py` | `DefineButtonSoundTag` | 65 |
| `DefineButtonTag.php` | `prespyc/parser/structure/tag/define_button.py` | `DefineButtonTag` | 62 |
| `DefineEditTextTag.php` | `prespyc/parser/structure/tag/define_edit_text.py` | `DefineEditTextTag` | 115 |
| `DefineFont2Or3Tag.php` | `prespyc/parser/structure/tag/define_font2_or3.py` | `DefineFont2Or3Tag` | 136 |
| `DefineFont4Tag.php` | `prespyc/parser/structure/tag/define_font4.py` | `DefineFont4Tag` | 71 |
| `DefineFontAlignZonesTag.php` | `prespyc/parser/structure/tag/define_font_align_zones.py` | `DefineFontAlignZonesTag` | 64 |
| `DefineFontInfoTag.php` | `prespyc/parser/structure/tag/define_font_info.py` | `DefineFontInfoTag` | 120 |
| `DefineFontNameTag.php` | `prespyc/parser/structure/tag/define_font_name.py` | `DefineFontNameTag` | 55 |
| `DefineFontTag.php` | `prespyc/parser/structure/tag/define_font.py` | `DefineFontTag` | 80 |
| `DefineMorphShape2Tag.php` | `prespyc/parser/structure/tag/define_morph_shape2.py` | `DefineMorphShape2Tag` | 103 |
| `DefineMorphShapeTag.php` | `prespyc/parser/structure/tag/define_morph_shape.py` | `DefineMorphShapeTag` | 82 |
| `DefineScalingGridTag.php` | `prespyc/parser/structure/tag/define_scaling_grid.py` | `DefineScalingGridTag` | 51 |
| `DefineSceneAndFrameLabelDataTag.php` | `prespyc/parser/structure/tag/define_scene_and_frame_label_data.py` | `DefineSceneAndFrameLabelDataTag` | 80 |
| `DefineShape4Tag.php` | `prespyc/parser/structure/tag/define_shape4.py` | `DefineShape4Tag` | 67 |
| `DefineShapeTag.php` | `prespyc/parser/structure/tag/define_shape.py` | `DefineShapeTag` | 62 |
| `DefineSoundTag.php` | `prespyc/parser/structure/tag/define_sound.py` | `DefineSoundTag` | 81 |
| `DefineSpriteTag.php` | `prespyc/parser/structure/tag/define_sprite.py` | `DefineSpriteTag` | 76 |
| `DefineTextTag.php` | `prespyc/parser/structure/tag/define_text.py` | `DefineTextTag` | 92 |
| `DefineVideoStreamTag.php` | `prespyc/parser/structure/tag/define_video_stream.py` | `DefineVideoStreamTag` | 71 |
| `DoABCTag.php` | `prespyc/parser/structure/tag/do_abc.py` | `DoABCTag` | 56 |
| `DoActionTag.php` | `prespyc/parser/structure/tag/do_action.py` | `DoActionTag` | 51 |
| `DoInitActionTag.php` | `prespyc/parser/structure/tag/do_init_action.py` | `DoInitActionTag` | 55 |
| `EnableDebuggerTag.php` | `prespyc/parser/structure/tag/enable_debugger.py` | `EnableDebuggerTag` | 66 |
| `EndTag.php` | `prespyc/parser/structure/tag/end.py` | `EndTag` | 26 |
| `ExportAssetsTag.php` | `prespyc/parser/structure/tag/export_assets.py` | `ExportAssetsTag` | 61 |
| `FileAttributesTag.php` | `prespyc/parser/structure/tag/file_attributes.py` | `FileAttributesTag` | 67 |
| `FrameLabelTag.php` | `prespyc/parser/structure/tag/frame_label.py` | `FrameLabelTag` | 61 |
| `ImportAssetsTag.php` | `prespyc/parser/structure/tag/import_assets.py` | `ImportAssetsTag` | 91 |
| `JPEGTablesTag.php` | `prespyc/parser/structure/tag/jpeg_tables.py` | `JPEGTablesTag` | 47 |
| `MetadataTag.php` | `prespyc/parser/structure/tag/metadata.py` | `MetadataTag` | 49 |
| `PlaceObject2Tag.php` | `prespyc/parser/structure/tag/place_object2.py` | `PlaceObject2Tag` | 82 |
| `PlaceObject3Tag.php` | `prespyc/parser/structure/tag/place_object3.py` | `PlaceObject3Tag` | 163 |
| `PlaceObjectTag.php` | `prespyc/parser/structure/tag/place_object.py` | `PlaceObjectTag` | 57 |
| `ProductInfo.php` | `prespyc/parser/structure/tag/product_info.py` | `ProductInfo` | 65 |
| `ProtectTag.php` | `prespyc/parser/structure/tag/protect.py` | `ProtectTag` | 57 |
| `ReflexTag.php` | `prespyc/parser/structure/tag/reflex.py` | `ReflexTag` | 53 |
| `RemoveObject2Tag.php` | `prespyc/parser/structure/tag/remove_object2.py` | `RemoveObject2Tag` | 46 |
| `RemoveObjectTag.php` | `prespyc/parser/structure/tag/remove_object.py` | `RemoveObjectTag` | 50 |
| `ScriptLimitsTag.php` | `prespyc/parser/structure/tag/script_limits.py` | `ScriptLimitsTag` | 50 |
| `SetBackgroundColorTag.php` | `prespyc/parser/structure/tag/set_background_color.py` | `SetBackgroundColorTag` | 47 |
| `SetTabIndexTag.php` | `prespyc/parser/structure/tag/set_tab_index.py` | `SetTabIndexTag` | 50 |
| `ShowFrameTag.php` | `prespyc/parser/structure/tag/show_frame.py` | `ShowFrameTag` | 26 |
| `SoundStreamBlockTag.php` | `prespyc/parser/structure/tag/sound_stream_block.py` | `SoundStreamBlockTag` | 47 |
| `SoundStreamHeadTag.php` | `prespyc/parser/structure/tag/sound_stream_head.py` | `SoundStreamHeadTag` | 83 |
| `StartSound2Tag.php` | `prespyc/parser/structure/tag/start_sound2.py` | `StartSound2Tag` | 54 |
| `StartSoundTag.php` | `prespyc/parser/structure/tag/start_sound.py` | `StartSoundTag` | 51 |
| `SymbolClassTag.php` | `prespyc/parser/structure/tag/symbol_class.py` | `SymbolClassTag` | 64 |
| `UnknownTag.php` | `prespyc/parser/structure/tag/unknown.py` | `UnknownTag` | 58 |
| `VideoFrameTag.php` | `prespyc/parser/structure/tag/video_frame.py` | `VideoFrameTag` | 53 |

## `src/Avm/`

| PHP file | Python module | Python name | PHP LOC |
|---|---|---|---|
| `Processor.php` | `prespyc/avm/processor.py` | `Processor` | 320 |
| `State.php` | `prespyc/avm/state.py` | `State` | 55 |

## `src/Avm/Api/`

| PHP file | Python module | Python name | PHP LOC |
|---|---|---|---|
| `ScriptArray.php` | `prespyc/avm/api/script_array.py` | `ScriptArray` | 130 |
| `ScriptObject.php` | `prespyc/avm/api/script_object.py` | `ScriptObject` | 205 |

## `src/Extractor/`

| PHP file | Python module | Python name | PHP LOC |
|---|---|---|---|
| `DrawableInterface.php` | `prespyc/extractor/drawable.py` | `Drawable` | 89 |
| `MissingCharacter.php` | `prespyc/extractor/missing_character.py` | `MissingCharacter` | 72 |
| `RatioDrawableInterface.php` | `prespyc/extractor/ratio_drawable.py` | `RatioDrawable` | 38 |
| `SwfExtractor.php` | `prespyc/extractor/extractor.py` | `Extractor` | 422 |

## `src/Extractor/Error/`

| PHP file | Python module | Python name | PHP LOC |
|---|---|---|---|
| `CircularReferenceException.php` | `prespyc/errors.py` | `CircularReferenceError` | 40 |
| `ExtractorExceptionInterface.php` | `prespyc/errors.py` | `ExtractorError` | 28 |
| `ProcessingInvalidDataException.php` | `prespyc/errors.py` | `ProcessingInvalidDataError` | 37 |

## `src/Extractor/Shape/`

| PHP file | Python module | Python name | PHP LOC |
|---|---|---|---|
| `CurvedEdge.php` | `prespyc/extractor/shape/curved_edge.py` | `CurvedEdge` | 72 |
| `EdgeInterface.php` | `prespyc/extractor/shape/edge.py` | `Edge` | 71 |
| `Path.php` | `prespyc/extractor/shape/path.py` | `Path` | 156 |
| `PathDrawerInterface.php` | `prespyc/extractor/shape/path_drawer.py` | `PathDrawer` | 50 |
| `PathStyle.php` | `prespyc/extractor/shape/path_style.py` | `PathStyle` | 134 |
| `PathsBuilder.php` | `prespyc/extractor/shape/paths_builder.py` | `PathsBuilder` | 162 |
| `Shape.php` | `prespyc/extractor/shape/shape.py` | `Shape` | 65 |
| `ShapeDefinition.php` | `prespyc/extractor/shape/shape_definition.py` | `ShapeDefinition` | 121 |
| `ShapeProcessor.php` | `prespyc/extractor/shape/shape_processor.py` | `ShapeProcessor` | 270 |
| `StraightEdge.php` | `prespyc/extractor/shape/straight_edge.py` | `StraightEdge` | 81 |

## `src/Extractor/Shape/FillType/`

| PHP file | Python module | Python name | PHP LOC |
|---|---|---|---|
| `Bitmap.php` | `prespyc/extractor/shape/fill_type/bitmap.py` | `Bitmap` | 96 |
| `FillTypeInterface.php` | `prespyc/extractor/shape/fill_type/fill_type.py` | `FillType` | 33 |
| `LinearGradient.php` | `prespyc/extractor/shape/fill_type/linear_gradient.py` | `LinearGradient` | 70 |
| `RadialGradient.php` | `prespyc/extractor/shape/fill_type/radial_gradient.py` | `RadialGradient` | 70 |
| `Solid.php` | `prespyc/extractor/shape/fill_type/solid.py` | `Solid` | 60 |

## `src/Extractor/MorphShape/`

| PHP file | Python module | Python name | PHP LOC |
|---|---|---|---|
| `MorphPath.php` | `prespyc/extractor/morph_shape/morph_path.py` | `MorphPath` | 124 |
| `MorphShape.php` | `prespyc/extractor/morph_shape/morph_shape.py` | `MorphShape` | 231 |
| `MorphShapeDefinition.php` | `prespyc/extractor/morph_shape/morph_shape_definition.py` | `MorphShapeDefinition` | 116 |
| `MorphShapeProcessor.php` | `prespyc/extractor/morph_shape/morph_shape_processor.py` | `MorphShapeProcessor` | 298 |

## `src/Extractor/Image/`

| PHP file | Python module | Python name | PHP LOC |
|---|---|---|---|
| `EmptyImage.php` | `prespyc/extractor/image/empty_image.py` | `EmptyImage` | 89 |
| `ImageBitsDefinition.php` | `prespyc/extractor/image/image_bits_definition.py` | `ImageBitsDefinition` | 115 |
| `ImageCharacterInterface.php` | `prespyc/extractor/image/image_character.py` | `ImageCharacter` | 87 |
| `ImageData.php` | `prespyc/extractor/image/image_data.py` | `ImageData` | 46 |
| `JpegImageDefinition.php` | `prespyc/extractor/image/jpeg_image_definition.py` | `JpegImageDefinition` | 222 |
| `LosslessImageDefinition.php` | `prespyc/extractor/image/lossless_image_definition.py` | `LosslessImageDefinition` | 278 |
| `TransformedImage.php` | `prespyc/extractor/image/transformed_image.py` | `TransformedImage` | 161 |

## `src/Extractor/Image/Util/`

| PHP file | Python module | Python name | PHP LOC |
|---|---|---|---|
| `GD.php` | `prespyc/extractor/image/pixels.py` | `Pixels` + module-level helpers | 424 |

## `src/Extractor/Sprite/`

| PHP file | Python module | Python name | PHP LOC |
|---|---|---|---|
| `SpriteDefinition.php` | `prespyc/extractor/sprite/sprite_definition.py` | `SpriteDefinition` | 182 |

## `src/Extractor/Timeline/`

| PHP file | Python module | Python name | PHP LOC |
|---|---|---|---|
| `BlendMode.php` | `prespyc/extractor/timeline/blend_mode.py` | `BlendMode` | 40 |
| `Frame.php` | `prespyc/extractor/timeline/frame.py` | `Frame` | 330 |
| `FrameObject.php` | `prespyc/extractor/timeline/frame_object.py` | `FrameObject` | 206 |
| `Timeline.php` | `prespyc/extractor/timeline/timeline.py` | `Timeline` | 312 |
| `TimelineProcessor.php` | `prespyc/extractor/timeline/timeline_processor.py` | `TimelineProcessor` | 386 |

## `src/Extractor/Modifier/`

| PHP file | Python module | Python name | PHP LOC |
|---|---|---|---|
| `AbstractCharacterModifier.php` | `prespyc/extractor/modifier/base_character_modifier.py` | `BaseCharacterModifier` | 70 |
| `CharacterModifierInterface.php` | `prespyc/extractor/modifier/character_modifier.py` | `CharacterModifier` | 42 |
| `GotoAndStop.php` | `prespyc/extractor/modifier/goto_and_stop.py` | `GotoAndStop` | 34 |

## `src/Extractor/Drawer/`

| PHP file | Python module | Python name | PHP LOC |
|---|---|---|---|
| `DrawerInterface.php` | `prespyc/extractor/drawer/drawer.py` | `Drawer` | 112 |

## `src/Extractor/Drawer/Svg/`

| PHP file | Python module | Python name | PHP LOC |
|---|---|---|---|
| `AbstractSvgCanvas.php` | `prespyc/extractor/drawer/svg/base_svg_canvas.py` | `BaseSvgCanvas` | 238 |
| `ClipPathBuilder.php` | `prespyc/extractor/drawer/svg/clip_path_builder.py` | `ClipPathBuilder` | 81 |
| `IncludedSvgCanvas.php` | `prespyc/extractor/drawer/svg/included_svg_canvas.py` | `IncludedSvgCanvas` | 91 |
| `SvgBuilder.php` | `prespyc/extractor/drawer/svg/svg_builder.py` | `SvgBuilder` | 293 |
| `SvgCanvas.php` | `prespyc/extractor/drawer/svg/svg_canvas.py` | `SvgCanvas` | 98 |
| `SvgPathDrawer.php` | `prespyc/extractor/drawer/svg/svg_path_drawer.py` | `SvgPathDrawer` | 65 |

## `src/Extractor/Drawer/Svg/Filter/`

| PHP file | Python module | Python name | PHP LOC |
|---|---|---|---|
| `SvgBlurFilter.php` | `prespyc/extractor/drawer/svg/filter/blur_filter.py` | `SvgBlurFilter` | 98 |
| `SvgColorMatrixFilter.php` | `prespyc/extractor/drawer/svg/filter/color_matrix_filter.py` | `SvgColorMatrixFilter` | 60 |
| `SvgDropShadowFilter.php` | `prespyc/extractor/drawer/svg/filter/drop_shadow_filter.py` | `SvgDropShadowFilter` | 104 |
| `SvgFilterBuilder.php` | `prespyc/extractor/drawer/svg/filter/filter_builder.py` | `SvgFilterBuilder` | 143 |
| `SvgGlowFilter.php` | `prespyc/extractor/drawer/svg/filter/glow_filter.py` | `SvgGlowFilter` | 70 |

## `src/Extractor/Drawer/Converter/`

| PHP file | Python module | Python name | PHP LOC |
|---|---|---|---|
| `AnimationFormater.php` | **dropped** (no animated output) | `--` | 62 |
| `Converter.php` | `prespyc/extractor/drawer/converter.py` | `Converter` | 405 |
| `DrawableFormater.php` | **dropped** (it pairs a resizer with an output format; only WEBP is left) | `--` | 61 |
| `FitSizeResizer.php` | `prespyc/extractor/drawer/resizer.py` | `FitSizeResizer` | 67 |
| `ImageFormat.php` | **dropped** (WEBP is the only output format) | `--` | 80 |
| `ImageResizerInterface.php` | `prespyc/extractor/drawer/resizer.py` | `ImageResizer` | 39 |
| `ScaleResizer.php` | `prespyc/extractor/drawer/resizer.py` | `ScaleResizer` | 46 |

## `src/Extractor/Drawer/Converter/Renderer/`

| PHP file | Python module | Python name | PHP LOC |
|---|---|---|---|
| `AbstractCommandImagickSvgRenderer.php` | **dropped** (Imagick backend) | `--` | 98 |
| `ImagickSvgRendererInterface.php` | `prespyc/extractor/drawer/render/rasterizer.py` | `SvgRasterizer` | 47 |
| `ImagickSvgRendererResolver.php` | `prespyc/extractor/drawer/render/rasterizer.py` | `default_rasterizer()` | 57 |
| `InkscapeImagickSvgRenderer.php` | **dropped** (Imagick backend) | `--` | 101 |
| `NativeImagickSvgRenderer.php` | **dropped** (Imagick backend) | `--` | 51 |
| `RsvgImagickSvgRenderer.php` | `prespyc/extractor/drawer/render/resvg.py` | `ResvgRasterizer` | 40 |

## Notes

- **Tag type constants.** Every tag class carries `TYPE: ClassVar[int]`, or `TYPE_V1`/`TYPE_V2`/…
  when one class covers several tag codes. PHP's two `ID` constants (`CSMTextSettingsTag::ID`,
  `ExportAssetsTag::ID`) are normalised to `TYPE`.
- **Dispatch.** `prespyc/parser/structure/raw_tag.py` holds the type → parser table, one entry per
  arm of PHP's `SwfTag::parse()` match. It is already written: a tag module only has to provide the
  class and the `read()` signature this file expects.
- **Circular imports.** `DefineSpriteTag.read()` needs `RawTag.read_all()`, and `raw_tag.py`
  imports every tag module. Import `RawTag` *inside* the function body, not at module level. Same
  rule wherever a record needs a tag (`ImageBitmapType` needs `DefineBitsLosslessTag`): use
  `if TYPE_CHECKING` for the annotation and a local import for the runtime use.
- **`Memory.php`** has no faithful Python counterpart (there is no `memory_limit`). The extractor's
  `release_if_out_of_memory()` takes an explicit byte threshold and reads the process RSS.
- **Dropped**: `src/Console/**`, the Imagick/Inkscape/native renderer backends, animated output and
  every output format except WEBP (and PNG/JPEG on the image characters, which the fixtures assert
  on directly).

## Extractor contract (already written — build against it)

These files fix the shared surface of the extractor layer. Do not change them; implement against them.

| File | Holds |
|---|---|
| `prespyc/extractor/drawable.py` | `Drawable`, `RatioDrawable` protocols |
| `prespyc/extractor/drawer/drawer.py` | `Drawer` protocol (the draw-ops sink) |
| `prespyc/extractor/shape/path_drawer.py` | `PathDrawer` protocol |
| `prespyc/extractor/image/image_character.py` | `ImageCharacter` protocol |
| `prespyc/extractor/modifier/character_modifier.py` | `CharacterModifier` protocol |
| `prespyc/extractor/timeline/blend_mode.py` | `BlendMode` |

Accessor shapes (PHP method → Python), applied throughout the extractor:

| PHP | Python |
|---|---|
| `bounds()` | `@property bounds` |
| `shape()`, `timeline()`, `paths()`, `exported()`, `shapes()`, `sprites()`, `images()`, `morphShapes()` — no argument | `@property` (cached: compute once, store on the instance) |
| `framesCount(bool $recursive = false)` | `frames_count(recursive=False)` |
| `draw(DrawerInterface $d, int $frame = 0)` | `draw(drawer, frame=0)` |
| `transformColors(ColorTransform $t)` | `transform_colors(color_transform)` |
| `modify(CharacterModifierInterface $m, int $maxDepth = -1)` | `modify(modifier, max_depth=-1)` |
| `withRatio(int $ratio)` | `with_ratio(ratio)` |
| `toSvg(int $frame = 0, bool $subpixelStrokeWidth = true)` | `to_svg(frame=0, subpixel_stroke_width=True)` |
| `toSvgAll(bool $subpixelStrokeWidth = true)` | `to_svg_all(subpixel_stroke_width=True)` — a generator |
| `Extractor::character(int $id)` | `character(id)`, plus `__getitem__` accepting an `int` id or a `str` exported name |
| `Extractor::byName(string $name)` | `by_name(name)` |
| `Extractor::timeline(bool $useFileDisplayBounds = true)` | `timeline(use_file_display_bounds=True)` — takes an argument, so it stays a method |

Where PHP memoises with `$this->x ??= ...`, use the same lazy pattern (a `_x` slot, or
`functools.cached_property`). Tests assert identity (`assertSame($a->shape(), $a->shape())`), so the
cache must return the *same* object.

## `SwfFile.tags()`

PHP yields a keyed generator (`yield $rawTag => $parsedTag`) and callers read either side. The port
yields **pairs**:

```python
for raw, tag in swf.tags(DefineShapeTag.TYPE_V1, DefineShape4Tag.TYPE_V4):
    if raw.id is None:
        continue
    shapes[raw.id] = ShapeDefinition(processor, raw.id, tag)
```

With no arguments, every tag is yielded.

## `Extractor.exported`

`ExportAssetsTag.characters` and `SymbolClassTag.symbols` are **id → raw name** (`dict[int, bytes]`).
`Extractor.exported` flips them into **name → id** (`dict[str, int]`):

- decode the name with `decode_swf_text(raw, swf_version)` — the tag layer keeps `bytes`;
- PHP's `$exported += array_flip(...)` keeps the **first** occurrence of a duplicate key, so use
  `setdefault`, not `update`;
- PHP coerces a numeric name like `"1681"` to the **int** key `1681`. The port keeps `str` keys.
  `Extractor.__getitem__` accepts `int | str`, so the `int` branch (character id) must not shadow a
  numeric exported name: look names up only for `str` keys.

## `Extractor` surface (write against it before it exists)

`extractor.py` is ported last, because it depends on every definition class. The processors take it
as a constructor argument, so build against this surface and annotate it under `if TYPE_CHECKING:`:

```python
class Extractor:
    def __init__(self, file: SwfFile) -> None: ...

    file: SwfFile  # the SWF being extracted

    def error_enabled(self, error: int) -> bool: ...  # PHP errorEnabled()
    def character(self, character_id: int) -> Drawable: ...  # MissingCharacter when absent
    def by_name(self, name: str) -> Drawable: ...
    def __getitem__(self, key: int | str) -> Drawable: ...  # id, or exported name

    @property
    def shapes(self) -> dict[int, ShapeDefinition]: ...
    @property
    def morph_shapes(self) -> dict[int, MorphShapeDefinition]: ...
    @property
    def sprites(self) -> dict[int, SpriteDefinition]: ...
    @property
    def images(self) -> dict[int, ImageCharacter]: ...
    @property
    def exported(self) -> dict[str, int]: ...

    def timeline(self, use_file_display_bounds: bool = True) -> Timeline: ...
    def release(self) -> None: ...
    def release_if_out_of_memory(self, memory_limit: int | None = None) -> bool: ...
```

The processors only ever call `error_enabled()` and `character()`, plus read `file`.
