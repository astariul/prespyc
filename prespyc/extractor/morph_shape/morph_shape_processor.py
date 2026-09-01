"""Turns DefineMorphShape tags into morph shape objects."""

from __future__ import annotations

from typing import TYPE_CHECKING

from prespyc.extractor.morph_shape.morph_path import MorphPath
from prespyc.extractor.morph_shape.morph_shape import MorphShape
from prespyc.extractor.shape.shape_processor import ShapeProcessor
from prespyc.parser.structure.record.gradient import Gradient
from prespyc.parser.structure.record.gradient_record import GradientRecord
from prespyc.parser.structure.record.morph_shape.morph_line_style2 import MorphLineStyle2
from prespyc.parser.structure.record.shape.curved_edge_record import CurvedEdgeRecord
from prespyc.parser.structure.record.shape.end_shape_record import EndShapeRecord
from prespyc.parser.structure.record.shape.fill_style import FillStyle
from prespyc.parser.structure.record.shape.line_style import LineStyle
from prespyc.parser.structure.record.shape.straight_edge_record import StraightEdgeRecord
from prespyc.parser.structure.record.shape.style_change_record import StyleChangeRecord

if TYPE_CHECKING:
    from prespyc.extractor.extractor import Extractor
    from prespyc.parser.structure.record.morph_shape.morph_fill_style import MorphFillStyle
    from prespyc.parser.structure.record.morph_shape.morph_gradient import MorphGradient
    from prespyc.parser.structure.record.morph_shape.morph_line_style import MorphLineStyle
    from prespyc.parser.structure.tag.define_morph_shape import DefineMorphShapeTag
    from prespyc.parser.structure.tag.define_morph_shape2 import DefineMorphShape2Tag

    ShapeRecords = list[StraightEdgeRecord | CurvedEdgeRecord | StyleChangeRecord | EndShapeRecord]


class MorphShapeProcessor:
    """Processes DefineMorphShape tags into `MorphShape` objects."""

    __slots__ = ("_shape_processor",)

    def __init__(self, extractor: Extractor) -> None:
        self._shape_processor = ShapeProcessor(extractor)

    def process(self, tag: DefineMorphShapeTag | DefineMorphShape2Tag) -> MorphShape:
        """Build the morph shape of a DefineMorphShape or DefineMorphShape2 tag."""
        start_fill_styles = []
        end_fill_styles = []
        start_line_styles = []
        end_line_styles = []

        for morph_fill_style in tag.fill_styles:
            start_fill_styles.append(self._morph_fill_style_to_fill_style(morph_fill_style, True))
            end_fill_styles.append(self._morph_fill_style_to_fill_style(morph_fill_style, False))

        for morph_line_style in tag.line_styles:
            start_line_styles.append(self._morph_line_style_to_line_style(morph_line_style, True))
            end_line_styles.append(self._morph_line_style_to_line_style(morph_line_style, False))

        start_records, end_records = self._inject_styles_on_end_records(tag.start_edges, tag.end_edges)

        # Do not ignore zero width lines in morph shapes to ensure proper morphing from 0 width to
        # non-zero width lines
        start_paths = self._shape_processor.process_records(
            start_records, start_fill_styles, start_line_styles, ignore_zero_with_line=False
        )
        end_paths = self._shape_processor.process_records(
            end_records, end_fill_styles, end_line_styles, ignore_zero_with_line=False
        )

        assert len(start_paths) == len(end_paths)

        morph_paths = []

        for index, start_path in enumerate(start_paths):
            end_path = end_paths[index]
            morph_paths.append(MorphPath(start_path, end_path))

        return MorphShape(
            tag.start_bounds,
            tag.end_bounds,
            morph_paths,
        )

    def _morph_fill_style_to_fill_style(self, morph_fill_style: MorphFillStyle, start: bool) -> FillStyle:
        """The fill style of the start (`start` is true) or the end shape."""
        return FillStyle(
            type=morph_fill_style.type,
            color=morph_fill_style.start_color if start else morph_fill_style.end_color,
            matrix=morph_fill_style.start_gradient_matrix if start else morph_fill_style.end_gradient_matrix,
            gradient=self._morph_gradient_to_gradient(morph_fill_style.gradient, start),
            bitmap_id=morph_fill_style.bitmap_id,
            bitmap_matrix=morph_fill_style.start_bitmap_matrix if start else morph_fill_style.end_bitmap_matrix,
        )

    def _morph_line_style_to_line_style(self, style: MorphLineStyle | MorphLineStyle2, start: bool) -> LineStyle:
        """The line style of the start (`start` is true) or the end shape."""
        # PHP reads `$style->xxx ?? null` on the union, which swallows the properties that only
        # MorphLineStyle2 declares. `MorphLineStyle` really does not have them, hence `getattr()`.
        fill_style = getattr(style, "fill_style", None)

        return LineStyle(
            width=style.start_width if start else style.end_width,
            color=style.start_color if start else style.end_color,
            start_cap_style=getattr(style, "start_cap_style", None),
            join_style=getattr(style, "join_style", None),
            has_fill_flag=(fill_style is not None) if isinstance(style, MorphLineStyle2) else None,
            no_h_scale_flag=getattr(style, "no_h_scale", None),
            no_v_scale_flag=getattr(style, "no_v_scale", None),
            pixel_hinting_flag=getattr(style, "pixel_hinting", None),
            no_close=getattr(style, "no_close", None),
            end_cap_style=getattr(style, "end_cap_style", None),
            miter_limit_factor=getattr(style, "miter_limit_factor", None),
            fill_type=self._morph_fill_style_to_fill_style(fill_style, start) if fill_style is not None else None,
        )

    def _morph_gradient_to_gradient(self, gradient: MorphGradient | None, start: bool) -> Gradient | None:
        if gradient is None:
            return None

        records = []

        for record in gradient.records:
            records.append(
                GradientRecord(record.start_ratio, record.start_color)
                if start
                else GradientRecord(record.end_ratio, record.end_color)
            )

        return Gradient(
            spread_mode=gradient.spread_mode,
            interpolation_mode=gradient.interpolation_mode,
            records=records,
        )

    def _inject_styles_on_end_records(
        self, start_records: ShapeRecords, end_records: ShapeRecords
    ) -> tuple[ShapeRecords, ShapeRecords]:
        """
        Copy the styles of the start records (i.e. from `StyleChangeRecord`) onto the end records.

        Styles are only defined on the start records, so they have to be copied to the end records
        for these to be processed. Both returned lists have the same length.
        """
        result_end_records: ShapeRecords = []
        result_start_records: ShapeRecords = []

        end_records_index = 0
        start_records_index = 0

        start_records_count = len(start_records)
        end_records_count = len(end_records)

        # We need to track the position of start records to properly inject moveTo commands
        start_x = 0
        start_y = 0

        while start_records_index < start_records_count and end_records_index < end_records_count:
            start_record = start_records[start_records_index]
            end_record = end_records[end_records_index]

            # Both are edge records
            if not isinstance(start_record, StyleChangeRecord) and not isinstance(end_record, StyleChangeRecord):
                result_start_records.append(start_record)
                start_records_index += 1

                result_end_records.append(end_record)
                end_records_index += 1

                if isinstance(start_record, StraightEdgeRecord):
                    start_x += start_record.delta_x
                    start_y += start_record.delta_y
                elif isinstance(start_record, CurvedEdgeRecord):
                    start_x += start_record.control_delta_x + start_record.anchor_delta_x
                    start_y += start_record.control_delta_y + start_record.anchor_delta_y
                continue

            # Merge style change records
            if isinstance(start_record, StyleChangeRecord) and isinstance(end_record, StyleChangeRecord):
                result_start_records.append(start_record)
                start_records_index += 1

                result_end_records.append(
                    StyleChangeRecord(
                        state_new_styles=start_record.state_new_styles,
                        state_line_style=start_record.state_line_style,
                        state_fill_style0=start_record.state_fill_style0,
                        state_fill_style1=start_record.state_fill_style1,
                        state_move_to=end_record.state_move_to,
                        move_delta_x=end_record.move_delta_x,
                        move_delta_y=end_record.move_delta_y,
                        fill_style0=start_record.fill_style0,
                        fill_style1=start_record.fill_style1,
                        line_style=start_record.line_style,
                        fill_styles=start_record.fill_styles,
                        line_styles=start_record.line_styles,
                    )
                )
                end_records_index += 1

                if start_record.state_move_to:
                    start_x = start_record.move_delta_x
                    start_y = start_record.move_delta_y
                continue

            # In this case, only the start record is a style change record
            # So we inject the style without moving the end records cursor
            if isinstance(start_record, StyleChangeRecord):
                result_start_records.append(start_record)
                start_records_index += 1

                result_end_records.append(start_record)

                if start_record.state_move_to:
                    start_x = start_record.move_delta_x
                    start_y = start_record.move_delta_y
                continue

            assert isinstance(end_record, StyleChangeRecord)

            # End record is a style change record, but not start record
            # This is used when there is a moveTo on the end shape only
            # So inject a "fake" move to style change record in start records
            result_start_records.append(
                StyleChangeRecord(
                    state_new_styles=end_record.state_new_styles,
                    state_line_style=end_record.state_line_style,
                    state_fill_style0=end_record.state_fill_style0,
                    state_fill_style1=end_record.state_fill_style1,
                    state_move_to=end_record.state_move_to,
                    move_delta_x=start_x,
                    move_delta_y=start_y,
                    fill_style0=end_record.fill_style0,
                    fill_style1=end_record.fill_style1,
                    line_style=end_record.line_style,
                    fill_styles=end_record.fill_styles,
                    line_styles=end_record.line_styles,
                )
            )

            result_end_records.append(end_record)
            end_records_index += 1

        start_size = len(result_start_records)
        # PHP reads the size of the *start* list here too. Every branch above appends to both lists,
        # so the two sizes are always equal and the typo is harmless. Kept as is.
        end_size = len(result_start_records)

        if start_size == 0 or not isinstance(result_start_records[start_size - 1], EndShapeRecord):
            result_start_records.append(EndShapeRecord())

        if end_size == 0 or not isinstance(result_end_records[end_size - 1], EndShapeRecord):
            result_end_records.append(EndShapeRecord())

        assert len(result_start_records) == len(result_end_records)

        return result_start_records, result_end_records
