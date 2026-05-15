from pixbox import Anchor, Box, Point, TextBody


def test_anchor_cell_center_uses_column_widths_and_row_heights() -> None:
    box = Box(
        10.0,
        20.0,
        grid=[
            [TextBody("name"), Anchor("name_value")],
            [TextBody("age"), Anchor("age_value")],
        ],
        grid_size=([3.0, 1.0], [1.0, 2.0]),
    )

    assert box.w == 4.0
    assert box.h == 3.0
    assert box.anchors["name_value"] == Point(13.5, 20.5)
    assert box.anchors["age_value"] == Point(13.5, 22.0)
