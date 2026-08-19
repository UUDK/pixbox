from typing import Any

import drawsvg as dw
import pytest

from pixbox import ArrowType, Connection, Point
from pixbox.style import GHOST_STROKE_COLOR, STROKE_WIDTH


def _child(group: Any, index: int) -> Any:
    return group.children[index]


def test_connection_draws_polyline_path() -> None:
    connection = Connection([Point(0.0, 0.0), Point(2.0, 0.0), Point(2.0, 1.0)])

    group = connection.draw()
    line = _child(group, 0)

    assert isinstance(line, dw.Path)
    assert line.args["d"] == "M0.0,0.0 L2.0,0.0 L2.0,1.0"
    assert line.args["stroke"] == "black"
    assert line.args["stroke-width"] == STROKE_WIDTH
    assert line.args["fill"] == "none"


def test_connection_draws_dot_marker() -> None:
    connection = Connection(
        [Point(0.0, 0.0), Point(1.0, 0.0)],
        begin_arrow=ArrowType.DOT,
    )

    group = connection.draw()
    marker = _child(group, 1)

    assert isinstance(marker, dw.Circle)
    assert marker.args["cx"] == 0.0
    assert marker.args["cy"] == 0.0
    assert marker.args["stroke"] == "black"
    assert marker.args["stroke-width"] == STROKE_WIDTH
    assert marker.args["fill"] == "white"


def test_connection_draws_open_and_filled_narrow_markers() -> None:
    connection = Connection(
        [Point(0.0, 0.0), Point(1.0, 0.0)],
        begin_arrow=ArrowType.NARROW,
        end_arrow=ArrowType.NARROW_FILLED,
    )

    group = connection.draw()
    open_marker = _child(group, 1)
    filled_marker = _child(group, 2)

    assert isinstance(open_marker, dw.Path)
    assert open_marker.args["fill"] == "none"
    assert open_marker.args["stroke-width"] == STROKE_WIDTH
    assert isinstance(filled_marker, dw.Lines)
    assert filled_marker.args["fill"] == "black"
    assert filled_marker.args["stroke-width"] == STROKE_WIDTH


def test_unimplemented_arrow_types_fail_explicitly() -> None:
    connection = Connection(
        [Point(0.0, 0.0), Point(1.0, 0.0)],
        end_arrow=ArrowType.WIDE,
    )

    with pytest.raises(NotImplementedError):
        connection.draw()


def test_ghost_connection_draws_line_and_markers_in_ghost_color() -> None:
    connection = Connection(
        [Point(0.0, 0.0), Point(1.0, 0.0)],
        begin_arrow=ArrowType.DOT,
        end_arrow=ArrowType.NARROW_FILLED,
        ghost=True,
    )

    group = connection.draw()
    line = _child(group, 0)
    dot_marker = _child(group, 1)
    filled_marker = _child(group, 2)

    assert line.args["stroke"] == GHOST_STROKE_COLOR
    assert dot_marker.args["stroke"] == GHOST_STROKE_COLOR
    assert filled_marker.args["stroke"] == GHOST_STROKE_COLOR
    assert filled_marker.args["fill"] == GHOST_STROKE_COLOR
