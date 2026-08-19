from __future__ import annotations

from typing import TypeAlias

from .figures import Anchor, Box, Cell
from .text import Text, TextAlign, TextBody, TextProp


CellInput: TypeAlias = str | Text | TextBody | Anchor | None
MappingInput: TypeAlias = tuple[CellInput, CellInput]

DATA_CORNERS_RADIUS = 0.3
META_CORNERS_RADIUS = 0.0


class Fig:
    @staticmethod
    def simple_box(
        x: float,
        y: float,
        element: CellInput = None,
        *,
        w: float = 3.0,
        simple_type: str = "int",
        ghost: bool = False,
    ) -> Box:
        value = _as_cell("..." if element is None else element)
        return Box(
            x=x,
            y=y,
            header=_header(simple_type),
            grid=[[value]],
            grid_size=(w, 1.0),
            corners_radius=DATA_CORNERS_RADIUS,
            ghost=ghost,
        )

    @staticmethod
    def sequence_box(
        x: float,
        y: float,
        elements: list[CellInput] | int | None = None,
        *,
        cell_width: float = 1.0,
        seq_type: str = "list",
        ghost: bool = False,
    ) -> Box:
        cells = _sequence_cells(elements)
        return Box(
            x=x,
            y=y,
            header=_header(seq_type),
            grid=[cells],
            grid_size=(cell_width, 1.0),
            corners_radius=DATA_CORNERS_RADIUS,
            ghost=ghost,
        )

    @staticmethod
    def sequence_box_vert(
        x: float,
        y: float,
        elements: list[CellInput] | int | None = None,
        *,
        cell_height: float = 1.0,
        seq_type: str = "list",
        ghost: bool = False,
    ) -> Box:
        rows = [[cell] for cell in _sequence_cells(elements)]
        return Box(
            x=x,
            y=y,
            header=_header(seq_type),
            grid=rows,
            grid_size=(1.0, cell_height),
            corners_radius=DATA_CORNERS_RADIUS,
            ghost=ghost,
        )

    @staticmethod
    def mapping_box(
        x: float,
        y: float,
        elements: list[MappingInput] | None = None,
        *,
        key_width: float = 3.0,
        value_width: float = 1.0,
        map_type: str = "dict",
        ghost: bool = False,
    ) -> Box:
        return Fig.dict_box(
            x,
            y,
            elements,
            key_width=key_width,
            value_width=value_width,
            dict_type=map_type,
            ghost=ghost,
        )

    mapping_box_vert = mapping_box

    @staticmethod
    def dict_box(
        x: float,
        y: float,
        elements: list[MappingInput] | None = None,
        *,
        key_width: float = 3.0,
        value_width: float = 1.0,
        dict_type: str = "dict",
        ghost: bool = False,
    ) -> Box:
        return _mapping_box(
            x,
            y,
            elements,
            key_width=key_width,
            value_width=value_width,
            header=dict_type,
            corners_radius=DATA_CORNERS_RADIUS,
            ghost=ghost,
        )

    @staticmethod
    def symbol_table(
        x: float,
        y: float,
        elements: list[MappingInput] | None = None,
        *,
        name_width: float = 3.0,
        value_width: float = 1.0,
        name: str = "__main__",
        ghost: bool = False,
    ) -> Box:
        return _mapping_box(
            x,
            y,
            elements,
            key_width=name_width,
            value_width=value_width,
            header=name,
            corners_radius=META_CORNERS_RADIUS,
            ghost=ghost,
        )


Factory = Fig


def _header(text: str) -> TextBody:
    return TextBody(Text(text, props=TextProp.BOLD, align=TextAlign.CENTER))


def _sequence_cells(elements: list[CellInput] | int | None) -> list[Cell]:
    if elements is None:
        elements = 3
    if isinstance(elements, int):
        return [Anchor(f"[{index}]") for index in range(elements)]
    return [_as_cell(element) for element in elements]


def _mapping_box(
    x: float,
    y: float,
    elements: list[MappingInput] | None,
    *,
    key_width: float,
    value_width: float,
    header: str,
    corners_radius: float,
    ghost: bool = False,
) -> Box:
    rows = [[_as_cell(key), _as_cell(value)] for key, value in (elements or [])]
    return Box(
        x=x,
        y=y,
        header=_header(header),
        grid=rows,
        grid_size=([key_width, value_width], 1.0),
        corners_radius=corners_radius,
        ghost=ghost,
    )


def _as_cell(value: CellInput) -> Cell:
    if value is None or isinstance(value, (TextBody, Anchor)):
        return value
    if isinstance(value, Text):
        return TextBody(value)
    if isinstance(value, str):
        return TextBody(value)
    raise TypeError("Expected str, Text, TextBody, Anchor, or None")
