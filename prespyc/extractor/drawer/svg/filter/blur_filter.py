"""Blur, as SVG filter primitives."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, ClassVar

from prespyc._util import num

if TYPE_CHECKING:
    from prespyc.extractor.drawer.svg.filter.filter_builder import SvgFilterBuilder
    from prespyc.parser.structure.record.filter.blur_filter import BlurFilter


class SvgBlurFilter:
    """
    Flash blurs with a box blur, not a Gaussian one, so `<feConvolveMatrix>` is the faithful
    primitive. Past a radius the kernel gets too big, and a Gaussian blur approximates it instead.
    """

    MAX_BOX_BLUR_RADIUS: ClassVar[int] = 9
    """
    Cap on the box blur radius, to avoid crashes and pathological render times.

    9 because RSVG only handles a 20x20 convolution kernel.
    """

    BLUR_BOX_RADIUS_TO_GAUSSIAN_BLUR_RATIO: ClassVar[float] = 1.732
    """sqrt(3), which approximates the variance of the blur box."""

    @staticmethod
    def apply(builder: SvgFilterBuilder, filter: BlurFilter, in_: str) -> str:
        return SvgBlurFilter.blur(builder, filter.blur_x, filter.blur_y, filter.passes, in_)

    @staticmethod
    def blur(builder: SvgFilterBuilder, blur_x: float, blur_y: float, passes: int, in_: str) -> str:
        """
        Append the blur primitives and return the id of the last result.

        Only the integer part of the radii is used. Three passes approximate a Gaussian blur.
        """
        if blur_x > SvgBlurFilter.MAX_BOX_BLUR_RADIUS or blur_y > SvgBlurFilter.MAX_BOX_BLUR_RADIUS:
            # The blur box is too large for a convolution kernel, so approximate it with a Gaussian.
            std_dev_x = blur_x / SvgBlurFilter.BLUR_BOX_RADIUS_TO_GAUSSIAN_BLUR_RATIO
            std_dev_y = blur_y / SvgBlurFilter.BLUR_BOX_RADIUS_TO_GAUSSIAN_BLUR_RATIO

            builder.add_offset(std_dev_x * 3, std_dev_y * 3)

            fe_gaussian_blur, result = builder.add_result_filter("feGaussianBlur", in_)
            fe_gaussian_blur.add_attribute("stdDeviation", f"{num(std_dev_x)} {num(std_dev_y)}")

            return result

        size_x = int(2 * math.ceil(blur_x) + 1)
        size_y = int(2 * math.ceil(blur_y) + 1)

        order = f"{size_x} {size_y}"
        divisor = size_x * size_y
        kernel_matrix = " ".join(["1"] * divisor)
        last_result = in_

        for _ in range(passes):
            fe_convolve_matrix, last_result = builder.add_result_filter("feConvolveMatrix", last_result)

            fe_convolve_matrix.add_attribute("order", order)
            fe_convolve_matrix.add_attribute("divisor", str(divisor))
            fe_convolve_matrix.add_attribute("kernelMatrix", kernel_matrix)

        return last_result
