"""Building an SVG `<clipPath>` from a drawable."""

from __future__ import annotations

from typing import TYPE_CHECKING

from prespyc._util import num
from prespyc.extractor.timeline.blend_mode import BlendMode
from prespyc.parser.structure.record.matrix import Matrix

if TYPE_CHECKING:
    from collections.abc import Sequence

    from prespyc.extractor.drawable import Drawable
    from prespyc.extractor.drawer.svg.svg_builder import SvgBuilder
    from prespyc.extractor.drawer.svg.xml import XmlElement
    from prespyc.extractor.image.image_character import ImageCharacter
    from prespyc.extractor.shape.path import Path
    from prespyc.extractor.shape.shape import Shape
    from prespyc.parser.structure.record.filter.filter import Filter
    from prespyc.parser.structure.record.rectangle import Rectangle


class ClipPathBuilder:
    """
    A `Drawer` that records only the geometry, into a `<clipPath>`.

    Images, filters, nested clips and blend modes are ignored: a clip path is a silhouette.
    """

    __slots__ = ("_builder", "_clip_path", "_transform")

    def __init__(self, clip_path: XmlElement, builder: SvgBuilder, transform: Sequence[Matrix] = ()) -> None:
        self._clip_path = clip_path
        self._builder = builder
        self._transform = tuple(transform)

    def area(self, bounds: Rectangle) -> None:
        # A placement matrix holds the bounds offset of what it places: undo it, as the group of a
        # drawn sprite does, or a sprite used as a mask lands off by its bounds.
        if bounds.xmin or bounds.ymin:
            self._transform = (*self._transform, Matrix(translate_x=-bounds.xmin, translate_y=-bounds.ymin))

    def shape(self, shape: Shape) -> None:
        for path in shape.paths:
            element = self._builder.add_path(self._clip_path, path)

            if element is None:
                continue

            transforms = [matrix.to_svg_transformation() for matrix in self._transform]
            transforms.append(f"translate({num(shape.x_offset / 20)},{num(shape.y_offset / 20)})")
            element.add_attribute("transform", " ".join(transforms))

    def image(self, image: ImageCharacter) -> None:
        pass

    def include(
        self,
        obj: Drawable,
        matrix: Matrix,
        frame: int = 0,
        filters: Sequence[Filter] = (),
        blend_mode: BlendMode = BlendMode.NORMAL,
        name: str | None = None,
    ) -> None:
        obj.draw(ClipPathBuilder(self._clip_path, self._builder, (*self._transform, matrix)), frame)

    def start_clip(self, obj: Drawable, matrix: Matrix, frame: int) -> str:
        return ""

    def end_clip(self, clip_id: str) -> None:
        pass

    def path(self, path: Path) -> None:
        pass

    def render(self) -> None:
        return None
