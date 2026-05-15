from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TypeAlias

import drawsvg as dw

from .connection import Connection
from .figures import Figure


Drawable: TypeAlias = Figure | Connection
Filename: TypeAlias = str | Path


@dataclass(frozen=True)
class Bounds:
    x_min: float
    y_min: float
    x_max: float
    y_max: float

    @property
    def width(self) -> float:
        return self.x_max - self.x_min

    @property
    def height(self) -> float:
        return self.y_max - self.y_min

    def with_margin(self, margin: float) -> Bounds:
        return Bounds(
            self.x_min - margin,
            self.y_min - margin,
            self.x_max + margin,
            self.y_max + margin,
        )


@dataclass
class Drawing:
    elements: list[Drawable] = field(default_factory=list)
    margin: float = 1.0
    scale: float = 100.0
    background: str | None = "white"

    def add(self, *elements: Drawable) -> None:
        self.elements.extend(elements)

    def bounds(self) -> Bounds:
        if not self.elements:
            return Bounds(0.0, 0.0, 0.0, 0.0)

        x_values: list[float] = []
        y_values: list[float] = []

        for element in self.elements:
            if isinstance(element, Figure):
                x_values.extend([element.x, element.xr])
                y_values.extend([element.y, element.yb])
            elif isinstance(element, Connection):
                x_values.extend(point.x for point in element.path)
                y_values.extend(point.y for point in element.path)

        if not x_values or not y_values:
            return Bounds(0.0, 0.0, 0.0, 0.0)

        return Bounds(min(x_values), min(y_values), max(x_values), max(y_values))

    def draw(self) -> dw.Drawing:
        bounds = self.bounds().with_margin(self.margin)
        dwg = dw.Drawing(
            bounds.width, bounds.height, origin=(bounds.x_min, bounds.y_min)
        )
        dwg.set_render_size(bounds.width * self.scale, bounds.height * self.scale)

        if self.background is not None:
            dwg.append(
                dw.Rectangle(
                    bounds.x_min,
                    bounds.y_min,
                    bounds.width,
                    bounds.height,
                    fill=self.background,
                    stroke="none",
                )
            )

        for element in self.elements:
            dwg.append(element.draw())

        return dwg

    def save_svg(self, filename: Filename) -> None:
        self.draw().save_svg(str(filename))

    def save_png(self, filename: Filename) -> None:
        self.draw().save_png(str(filename))

    def svg_render(self, filename: Filename) -> None:
        self.save_svg(filename)

    def png_render(self, filename: Filename) -> None:
        self.save_png(filename)
