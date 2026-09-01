"""Base type for all shape records."""

from __future__ import annotations

from typing import TYPE_CHECKING

from prespyc.parser.structure.record.shape.fill_style import FillStyle
from prespyc.parser.structure.record.shape.line_style import LineStyle

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader
    from prespyc.parser.structure.record.shape.curved_edge_record import CurvedEdgeRecord
    from prespyc.parser.structure.record.shape.end_shape_record import EndShapeRecord
    from prespyc.parser.structure.record.shape.straight_edge_record import StraightEdgeRecord
    from prespyc.parser.structure.record.shape.style_change_record import StyleChangeRecord


class ShapeRecord:
    """Base type for all shape records."""

    __slots__ = ()

    @staticmethod
    def read_collection(
        reader: Reader, version: int
    ) -> list[CurvedEdgeRecord | EndShapeRecord | StraightEdgeRecord | StyleChangeRecord]:
        """
        Read a collection of shape records from the reader until the end of the shape is reached
        (i.e. a record with no flags set).

        `version` is the shape record version, between 1 and 4.
        """
        # Imported here: the record classes inherit from this one.
        from prespyc.parser.structure.record.shape.curved_edge_record import CurvedEdgeRecord
        from prespyc.parser.structure.record.shape.end_shape_record import EndShapeRecord
        from prespyc.parser.structure.record.shape.straight_edge_record import StraightEdgeRecord
        from prespyc.parser.structure.record.shape.style_change_record import StyleChangeRecord

        num_fill_bits = reader.read_ub(4)
        num_line_bits = reader.read_ub(4)
        shape_records: list[CurvedEdgeRecord | EndShapeRecord | StraightEdgeRecord | StyleChangeRecord] = []

        assert num_fill_bits < 16
        assert num_line_bits < 16

        while reader.offset < reader.end:
            edge_record = reader.read_bool()

            if edge_record:
                straight_flag = reader.read_bool()
                num_bits = reader.read_ub(4)
                assert num_bits < 16

                if straight_flag:
                    general_line_flag = reader.read_bool()
                    vert_line_flag = not general_line_flag and reader.read_bool()

                    delta_x = reader.read_sb(num_bits + 2) if general_line_flag or not vert_line_flag else 0
                    delta_y = reader.read_sb(num_bits + 2) if general_line_flag or vert_line_flag else 0

                    shape_records.append(StraightEdgeRecord(general_line_flag, vert_line_flag, delta_x, delta_y))
                else:
                    shape_records.append(
                        CurvedEdgeRecord(
                            reader.read_sb(num_bits + 2),
                            reader.read_sb(num_bits + 2),
                            reader.read_sb(num_bits + 2),
                            reader.read_sb(num_bits + 2),
                        )
                    )

                continue

            # Style change record
            state_new_styles = reader.read_bool()
            state_line_style = reader.read_bool()
            state_fill_style1 = reader.read_bool()
            state_fill_style0 = reader.read_bool()
            state_move_to = reader.read_bool()

            # End of shape
            if (
                not state_new_styles
                and not state_line_style
                and not state_fill_style1
                and not state_fill_style0
                and not state_move_to
            ):
                shape_records.append(EndShapeRecord())
                break

            if state_move_to:
                move_bits = reader.read_ub(5)
                assert move_bits < 32

                move_delta_x = reader.read_sb(move_bits)
                move_delta_y = reader.read_sb(move_bits)
            else:
                move_delta_x = 0
                move_delta_y = 0

            fill_style0 = reader.read_ub(num_fill_bits) if state_fill_style0 else 0
            fill_style1 = reader.read_ub(num_fill_bits) if state_fill_style1 else 0
            line_style = reader.read_ub(num_line_bits) if state_line_style else 0

            if state_new_styles and version >= 2:
                reader.align_byte()
                new_fill_styles = FillStyle.read_collection(reader, version)
                new_line_styles = LineStyle.read_collection(reader, version)
                num_fill_bits = reader.read_ub(4)
                num_line_bits = reader.read_ub(4)

                assert num_fill_bits < 16
                assert num_line_bits < 16
            else:
                new_fill_styles = []
                new_line_styles = []

            shape_records.append(
                StyleChangeRecord(
                    state_new_styles,
                    state_line_style,
                    state_fill_style0,
                    state_fill_style1,
                    state_move_to,
                    move_delta_x,
                    move_delta_y,
                    fill_style0,
                    fill_style1,
                    line_style,
                    new_fill_styles,
                    new_line_styles,
                )
            )

        reader.align_byte()

        return shape_records
