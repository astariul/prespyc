"""Base type for graphic filters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Self

from prespyc.errors import Errors, InvalidDataError

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


class Filter(ABC):
    """Base type for graphic filters."""

    __slots__ = ()

    @staticmethod
    def read_collection(reader: Reader) -> list[Filter]:
        """
        Read a collection of filters from the reader.

        The collection size is provided by the first byte.
        """
        # Imported here because every filter module imports this one.
        from prespyc.parser.structure.record.filter.bevel_filter import BevelFilter
        from prespyc.parser.structure.record.filter.blur_filter import BlurFilter
        from prespyc.parser.structure.record.filter.color_matrix_filter import ColorMatrixFilter
        from prespyc.parser.structure.record.filter.convolution_filter import ConvolutionFilter
        from prespyc.parser.structure.record.filter.drop_shadow_filter import DropShadowFilter
        from prespyc.parser.structure.record.filter.glow_filter import GlowFilter
        from prespyc.parser.structure.record.filter.gradient_bevel_filter import GradientBevelFilter
        from prespyc.parser.structure.record.filter.gradient_glow_filter import GradientGlowFilter

        filters: list[Filter] = []
        count = reader.read_ui8()
        end = reader.end

        for _ in range(count):
            if reader.offset >= end:
                break

            filter_id = reader.read_ui8()

            match filter_id:
                case DropShadowFilter.FILTER_ID:
                    filters.append(DropShadowFilter._read(reader))
                case BlurFilter.FILTER_ID:
                    filters.append(BlurFilter._read(reader))
                case GlowFilter.FILTER_ID:
                    filters.append(GlowFilter._read(reader))
                case BevelFilter.FILTER_ID:
                    filters.append(BevelFilter._read(reader))
                case GradientGlowFilter.FILTER_ID:
                    filters.append(GradientGlowFilter._read(reader))
                case ConvolutionFilter.FILTER_ID:
                    filters.append(ConvolutionFilter._read(reader))
                case ColorMatrixFilter.FILTER_ID:
                    filters.append(ColorMatrixFilter._read(reader))
                case GradientBevelFilter.FILTER_ID:
                    filters.append(GradientBevelFilter._read(reader))
                case _:
                    if reader.errors & Errors.INVALID_DATA:
                        raise InvalidDataError(f"Unknown filter type {filter_id}", reader.offset)

        return filters

    @classmethod
    @abstractmethod
    def _read(cls, reader: Reader) -> Self:
        """
        Read a single filter from the reader.

        The filter type has already been determined by the caller, so this method only reads the
        filter data. Protected in the original: use `read_collection()`.
        """
