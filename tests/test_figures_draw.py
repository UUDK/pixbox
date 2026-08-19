from typing import Any

import drawsvg as dw
import pytest

from pixbox import Box, Text, TextAlign, TextBody
from pixbox.style import FIELD_FILL, GHOST_STROKE_COLOR, STROKE_WIDTH


def _children_of_type(group: Any, cls: type) -> list[Any]:
    return [child for child in group.children if isinstance(child, cls)]


def test_box_draw_strokes_each_field_and_outer_border() -> None:
    box = Box(
        0.0,
        0.0,
        header=TextBody("dict"),
        grid=[[TextBody("short"), TextBody("much longer")]],
        grid_size=([3.0, 3.0], 1.0),
    )

    group = box.draw()

    rects = _children_of_type(group, dw.Rectangle)
    lines = _children_of_type(group, dw.Line)
    background = rects[0]
    outer_border = rects[-1]

    assert len(rects) == 2
    assert background.args["fill"] == FIELD_FILL
    assert background.args["stroke"] == "none"
    assert outer_border.args["stroke"] == "black"
    assert outer_border.args["stroke-width"] == STROKE_WIDTH
    assert outer_border.args["fill"] == "none"
    assert len(lines) == 2
    assert all(line.args["stroke-width"] == STROKE_WIDTH for line in lines)


def test_box_draw_uses_box_dimensions_for_header_text_and_outer_border() -> None:
    box = Box(
        1.0,
        1.0,
        header=TextBody(Text("dict", align=TextAlign.CENTER)),
        grid=[[TextBody("name"), TextBody("Andrew")]],
        grid_size=([3.0, 1.0], 1.0),
    )

    group = box.draw()
    rects = _children_of_type(group, dw.Rectangle)
    outer_border = rects[-1]
    text_groups = _children_of_type(group, dw.Group)
    header_text = text_groups[0].children[0]

    assert outer_border.args["x"] == 1.0
    assert outer_border.args["y"] == 1.0
    assert outer_border.args["width"] == 4.0
    assert outer_border.args["height"] == 2.0
    assert header_text.args["x"] == 3.0


def test_rounded_box_background_and_border_share_radius() -> None:
    box = Box(
        0.0,
        0.0,
        header=TextBody("list"),
        grid=[[TextBody("x")]],
        corners_radius=0.3,
    )

    group = box.draw()
    rects = _children_of_type(group, dw.Rectangle)
    background = rects[0]
    outer_border = rects[-1]

    assert background.args["rx"] == 0.3
    assert background.args["ry"] == 0.3
    assert outer_border.args["rx"] == 0.3
    assert outer_border.args["ry"] == 0.3


def test_left_aligned_text_uses_cell_geometry_not_text_bounds() -> None:
    box = Box(
        0.0,
        0.0,
        grid=[
            [TextBody(Text("a", align=TextAlign.LEFT))],
            [TextBody(Text("a much longer line", align=TextAlign.LEFT))],
        ],
        grid_size=(3.0, 1.0),
    )

    group = box.draw()
    text_groups = _children_of_type(group, dw.Group)
    text_elements = [
        child
        for text_group in text_groups
        for child in text_group.children
        if isinstance(child, dw.Text)
    ]

    assert len(text_elements) == 2
    assert text_elements[0].args["x"] == text_elements[1].args["x"] == 0.12
    assert text_elements[0].args["text-anchor"] == "start"
    assert text_elements[1].args["text-anchor"] == "start"


def test_multiline_text_spacing_uses_largest_line_size() -> None:
    box = Box(
        0.0,
        0.0,
        grid=[[TextBody([Text("small", size=0.5), Text("large", size=2.0)])]],
    )

    group = box.draw()
    text_groups = _children_of_type(group, dw.Group)
    text_elements = [
        child
        for text_group in text_groups
        for child in text_group.children
        if isinstance(child, dw.Text)
    ]

    assert text_elements[0].args["font-size"] == 0.2
    assert text_elements[1].args["font-size"] == 0.8
    assert text_elements[1].args["y"] - text_elements[0].args["y"] == pytest.approx(1.0)


def test_ghost_box_draws_strokes_and_text_in_ghost_color() -> None:
    box = Box(
        0.0,
        0.0,
        header=TextBody("dict"),
        grid=[[TextBody("value")]],
        ghost=True,
    )

    group = box.draw()
    rects = _children_of_type(group, dw.Rectangle)
    lines = _children_of_type(group, dw.Line)
    text_groups = _children_of_type(group, dw.Group)
    text_elements = [
        child
        for text_group in text_groups
        for child in text_group.children
        if isinstance(child, dw.Text)
    ]

    assert rects[-1].args["stroke"] == GHOST_STROKE_COLOR
    assert all(line.args["stroke"] == GHOST_STROKE_COLOR for line in lines)
    assert all(text.args["fill"] == GHOST_STROKE_COLOR for text in text_elements)
