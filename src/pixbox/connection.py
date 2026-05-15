from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from math import atan2, cos, sin

import drawsvg as dw

from .point import Offset, Point
from .style import STROKE_COLOR, STROKE_WIDTH


ARROW_LENGTH = 0.28
ARROW_WIDTH = 0.18
DOT_RADIUS = 0.08


class ArrowType(Enum):
    NONE = auto()
    DOT = auto()
    NARROW = auto()
    NARROW_FILLED = auto()
    WIDE = auto()
    WIDE_FILLED = auto()
    WIDE_TRIANGLE = auto()
    DIAMOND = auto()
    DIAMOND_FILLED = auto()
    FORK = auto()


@dataclass
class Connection:
    path: list[Point] = field(default_factory=list)
    begin_arrow: ArrowType = ArrowType.NONE
    end_arrow: ArrowType = ArrowType.NONE

    def draw(self) -> dw.DrawingElement:
        group = dw.Group()

        line = dw.Path(stroke=STROKE_COLOR, stroke_width=STROKE_WIDTH, fill="none")
        if self.path:
            first = self.path[0]
            line.M(first.x, first.y)
            for point in self.path[1:]:
                line.L(point.x, point.y)
        group.append(line)

        if len(self.path) >= 2:
            begin_direction = self.path[0] - self.path[1]
            end_direction = self.path[-1] - self.path[-2]
            begin_marker = self._draw_arrow(
                self.begin_arrow, self.path[0], begin_direction
            )
            end_marker = self._draw_arrow(self.end_arrow, self.path[-1], end_direction)

            if begin_marker is not None:
                group.append(begin_marker)
            if end_marker is not None:
                group.append(end_marker)

        return group

    def _draw_arrow(
        self, arrow: ArrowType, tip: Point, direction: Offset
    ) -> dw.DrawingElement | None:
        if arrow is ArrowType.NONE:
            return None
        if arrow is ArrowType.DOT:
            return dw.Circle(
                tip.x,
                tip.y,
                DOT_RADIUS,
                stroke=STROKE_COLOR,
                stroke_width=STROKE_WIDTH,
                fill="white",
            )
        if arrow is ArrowType.NARROW:
            return self._draw_narrow_arrow(tip, direction, filled=False)
        if arrow is ArrowType.NARROW_FILLED:
            return self._draw_narrow_arrow(tip, direction, filled=True)

        raise NotImplementedError(f"Arrow type is not implemented yet: {arrow.name}")

    @staticmethod
    def _draw_narrow_arrow(
        tip: Point, direction: Offset, *, filled: bool
    ) -> dw.DrawingElement:
        left, right = _arrow_base_points(tip, direction, ARROW_LENGTH, ARROW_WIDTH)

        if filled:
            return dw.Lines(
                tip.x,
                tip.y,
                left.x,
                left.y,
                right.x,
                right.y,
                close=True,
                stroke=STROKE_COLOR,
                stroke_width=STROKE_WIDTH,
                fill=STROKE_COLOR,
            )

        path = dw.Path(stroke=STROKE_COLOR, stroke_width=STROKE_WIDTH, fill="none")
        path.M(left.x, left.y).L(tip.x, tip.y).L(right.x, right.y)
        return path


def _arrow_base_points(
    tip: Point,
    direction: Offset,
    length: float,
    width: float,
) -> tuple[Point, Point]:
    angle = atan2(direction.dy, direction.dx)
    back = Point(tip.x - cos(angle) * length, tip.y - sin(angle) * length)
    perp_x = -sin(angle)
    perp_y = cos(angle)
    half_width = width / 2.0

    return (
        Point(back.x + perp_x * half_width, back.y + perp_y * half_width),
        Point(back.x - perp_x * half_width, back.y - perp_y * half_width),
    )
