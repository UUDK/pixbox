from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TypeAlias

import drawsvg as dw

from .point import Point
from .style import FIELD_FILL, GHOST_STROKE_COLOR, STROKE_COLOR, STROKE_WIDTH
from .text import Text, TextAlign, TextBody, TextProp


SizeSpec: TypeAlias = float | list[float] | tuple[float, ...] | None
GridSizeSpec: TypeAlias = tuple[SizeSpec, SizeSpec] | None

TEXT_PADDING = 0.12


@dataclass
class Figure(ABC):
    x: float
    y: float
    w: float | None = None
    h: float | None = None
    ghost: bool = False

    @property
    def origin(self) -> Point:
        return Point(self.x, self.y)

    @property
    def xr(self) -> float:
        w, _ = self._size()
        return self.x + w

    @property
    def yb(self) -> float:
        _, h = self._size()
        return self.y + h

    @property
    def center(self) -> Point:
        w, h = self._size()
        return Point(self.x + w / 2.0, self.y + h / 2.0)

    def _size(self) -> tuple[float, float]:
        if self.w is None or self.h is None:
            raise ValueError("Figure size has not been calculated")
        return self.w, self.h

    @abstractmethod
    def draw(self) -> dw.DrawingElement: ...


@dataclass(frozen=True)
class Anchor:
    name: str


Cell: TypeAlias = TextBody | Anchor | None


@dataclass
class Box(Figure):
    header: Cell = None
    header_height: float = 1.0
    grid: list[list[Cell]] = field(default_factory=list)
    grid_size: GridSizeSpec = None
    corners_radius: float = 0.0

    col_widths: tuple[float, ...] = field(init=False)
    row_heights: tuple[float, ...] = field(init=False)
    anchors: dict[str, Point] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        col_count = max((len(row) for row in self.grid), default=0)
        row_count = len(self.grid)

        col_spec, row_spec = (
            self.grid_size if self.grid_size is not None else (None, None)
        )
        self.col_widths = self._normalize_sizes(col_spec, col_count, "column")
        self.row_heights = self._normalize_sizes(row_spec, row_count, "row")

        width = sum(self.col_widths)
        if col_count == 0 and self.w is not None:
            width = self.w

        header_height = self.header_height if self.header is not None else 0.0
        self.w = width
        self.h = header_height + sum(self.row_heights)

        self._set_box_anchors()
        if self.header is not None:
            self._set_header_anchors()
        self._set_cell_anchors()

    @staticmethod
    def _normalize_sizes(
        spec: SizeSpec, count: int, axis_name: str
    ) -> tuple[float, ...]:
        if count == 0:
            return ()

        if spec is None:
            return (1.0,) * count

        if isinstance(spec, (int, float)):
            if spec <= 0:
                raise ValueError(f"{axis_name} size must be positive")
            return (float(spec),) * count

        sizes = tuple(float(size) for size in spec)
        if len(sizes) != count:
            raise ValueError(f"Expected {count} {axis_name} sizes, got {len(sizes)}")
        if any(size <= 0 for size in sizes):
            raise ValueError(f"{axis_name} sizes must be positive")
        return sizes

    @property
    def body_y(self) -> float:
        return self.y + (self.header_height if self.header is not None else 0.0)

    def cell_origin(self, row: int, col: int) -> Point:
        self._assert_cell_index(row, col)
        return Point(
            self.x + sum(self.col_widths[:col]),
            self.body_y + sum(self.row_heights[:row]),
        )

    def cell_center(self, row: int, col: int) -> Point:
        origin = self.cell_origin(row, col)
        return Point(
            origin.x + self.col_widths[col] / 2.0,
            origin.y + self.row_heights[row] / 2.0,
        )

    def cell_size(self, row: int, col: int) -> tuple[float, float]:
        self._assert_cell_index(row, col)
        return self.col_widths[col], self.row_heights[row]

    def _assert_cell_index(self, row: int, col: int) -> None:
        if row < 0 or row >= len(self.row_heights):
            raise IndexError(f"Row index out of range: {row}")
        if col < 0 or col >= len(self.col_widths):
            raise IndexError(f"Column index out of range: {col}")

    def _set_box_anchors(self) -> None:
        w, h = self._size()
        self.anchors.update(
            {
                "top_left": Point(self.x, self.y),
                "top_center": Point(self.x + w / 2.0, self.y),
                "top_right": Point(self.xr, self.y),
                "center_left": Point(self.x, self.y + h / 2.0),
                "center": self.center,
                "center_right": Point(self.xr, self.y + h / 2.0),
                "bottom_left": Point(self.x, self.yb),
                "bottom_center": Point(self.x + w / 2.0, self.yb),
                "bottom_right": Point(self.xr, self.yb),
            }
        )

    def _set_header_anchors(self) -> None:
        w, _ = self._size()
        header_center = Point(self.x + w / 2.0, self.y + self.header_height / 2.0)
        self.anchors.update(
            {
                "header_left": Point(self.x, header_center.y),
                "header_center": header_center,
                "header_right": Point(self.xr, header_center.y),
            }
        )
        if isinstance(self.header, Anchor):
            self.anchors[self.header.name] = header_center

    def _set_cell_anchors(self) -> None:
        for row_index, row in enumerate(self.grid):
            for col_index, cell in enumerate(row):
                if isinstance(cell, Anchor):
                    self.anchors[cell.name] = self.cell_center(row_index, col_index)

    def draw(self) -> dw.DrawingElement:
        g = dw.Group()
        box_width, box_height = self._size()
        stroke_color = self._stroke_color()

        g.append(self._draw_box_background(box_width, box_height))
        for line in self._draw_field_lines():
            g.append(line)

        if self.header is not None and isinstance(self.header, TextBody):
            g.append(
                self._draw_text_body(
                    self.header, self.origin, box_width, self.header_height
                )
            )

        for row_index, row in enumerate(self.grid):
            for col_index, cell in enumerate(row):
                if isinstance(cell, TextBody):
                    origin = self.cell_origin(row_index, col_index)
                    cell_width, cell_height = self.cell_size(row_index, col_index)
                    g.append(
                        self._draw_text_body(cell, origin, cell_width, cell_height)
                    )

        g.append(
            dw.Rectangle(
                self.x,
                self.y,
                box_width,
                box_height,
                stroke=stroke_color,
                stroke_width=STROKE_WIDTH,
                fill="none",
                rx=self.corners_radius,
                ry=self.corners_radius,
            )
        )

        return g

    def _draw_box_background(self, width: float, height: float) -> dw.DrawingElement:
        return dw.Rectangle(
            self.x,
            self.y,
            width,
            height,
            stroke="none",
            fill=FIELD_FILL,
            rx=self.corners_radius,
            ry=self.corners_radius,
        )

    def _draw_field_lines(self) -> list[dw.DrawingElement]:
        lines: list[dw.DrawingElement] = []

        if self.header is not None and self.row_heights:
            lines.append(self._line(self.x, self.body_y, self.xr, self.body_y))

        for col_index in range(1, len(self.col_widths)):
            x = self.x + sum(self.col_widths[:col_index])
            lines.append(self._line(x, self.body_y, x, self.yb))

        for row_index in range(1, len(self.row_heights)):
            y = self.body_y + sum(self.row_heights[:row_index])
            lines.append(self._line(self.x, y, self.xr, y))

        return lines

    def _line(self, x1: float, y1: float, x2: float, y2: float) -> dw.DrawingElement:
        return dw.Line(
            x1,
            y1,
            x2,
            y2,
            stroke=self._stroke_color(),
            stroke_width=STROKE_WIDTH,
        )

    def _draw_text_body(
        self,
        text_body: TextBody,
        origin: Point,
        width: float,
        height: float,
    ) -> dw.DrawingElement:
        group = dw.Group()
        line_step = text_body.line_step
        total_height = (
            line_step * (len(text_body.lines) - 1) if text_body.lines else 0.0
        )
        y_start = origin.y + height / 2.0 - total_height / 2.0

        for index, line in enumerate(text_body.lines):
            x, text_anchor = self._text_x_and_anchor(line, origin, width)
            y = y_start + index * line_step
            group.append(
                dw.Text(
                    line.text,
                    line.font_size,
                    x,
                    y,
                    text_anchor=text_anchor,
                    dominant_baseline="central",
                    font_family=line.font_family,
                    fill=self._stroke_color(),
                    font_weight="bold" if TextProp.BOLD in line.props else "normal",
                    font_style="italic" if TextProp.ITALIC in line.props else "normal",
                )
            )

        return group

    def _stroke_color(self) -> str:
        return GHOST_STROKE_COLOR if self.ghost else STROKE_COLOR

    @staticmethod
    def _text_x_and_anchor(
        line: Text, origin: Point, width: float
    ) -> tuple[float, str]:
        if line.align is TextAlign.RIGHT:
            return origin.x + width - TEXT_PADDING, "end"
        if line.align is TextAlign.CENTER:
            return origin.x + width / 2.0, "middle"
        return origin.x + TEXT_PADDING, "start"
