from pixbox import Anchor, Box, Connection, Drawing, Point, TextBody
import drawsvg as dw


def test_drawing_bounds_include_figures_and_connections() -> None:
    box = Box(
        10.0,
        20.0,
        grid=[[TextBody("name"), Anchor("value")]],
        grid_size=([3.0, 1.0], 1.0),
    )
    connection = Connection([Point(8.0, 19.0), box.anchors["value"], Point(15.0, 25.0)])
    drawing = Drawing([box, connection])

    bounds = drawing.bounds()

    assert bounds.x_min == 8.0
    assert bounds.y_min == 19.0
    assert bounds.x_max == 15.0
    assert bounds.y_max == 25.0


def test_drawing_draw_uses_content_bounds_with_margin() -> None:
    box = Box(10.0, 20.0, grid=[[Anchor("value")]], grid_size=(2.0, 3.0))
    drawing = Drawing([box], margin=1.0, scale=50.0)

    dwg = drawing.draw()

    assert dwg.width == 4.0
    assert dwg.height == 5.0
    assert dwg.view_box == (9.0, 19.0, 4.0, 5.0)
    assert dwg.render_width == 200.0
    assert dwg.render_height == 250.0


def test_drawing_draw_adds_white_background_by_default() -> None:
    box = Box(10.0, 20.0, grid=[[Anchor("value")]], grid_size=(2.0, 3.0))
    drawing = Drawing([box], margin=1.0)

    dwg = drawing.draw()
    background = dwg.elements[0]

    assert isinstance(background, dw.Rectangle)
    assert background.args["x"] == 9.0
    assert background.args["y"] == 19.0
    assert background.args["width"] == 4.0
    assert background.args["height"] == 5.0
    assert background.args["fill"] == "white"
    assert background.args["stroke"] == "none"


def test_drawing_background_can_be_transparent() -> None:
    box = Box(10.0, 20.0, grid=[[Anchor("value")]], grid_size=(2.0, 3.0))
    drawing = Drawing([box], background=None)

    dwg = drawing.draw()

    assert not isinstance(dwg.elements[0], dw.Rectangle)
