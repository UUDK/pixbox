from pixbox import Anchor, Factory, Fig, Point, TextBody


def test_fig_sequence_box_with_count_creates_anchor_cells() -> None:
    box = Fig.sequence_box(1.0, 2.0, elements=3)

    assert box.w == 3.0
    assert box.h == 2.0
    assert box.anchors["[0]"] == Point(1.5, 3.5)
    assert box.anchors["[1]"] == Point(2.5, 3.5)
    assert box.anchors["[2]"] == Point(3.5, 3.5)


def test_fig_sequence_box_accepts_text_cells() -> None:
    box = Fig.sequence_box(0.0, 0.0, elements=["Andrew", TextBody("Ben")], cell_width=3.0)

    assert box.w == 6.0
    assert isinstance(box.grid[0][0], TextBody)
    assert isinstance(box.grid[0][1], TextBody)


def test_fig_mapping_box_builds_two_column_grid() -> None:
    box = Fig.dict_box(
        10.0,
        20.0,
        elements=[("name", Anchor("name_value")), ("age", Anchor("age_value"))],
        key_width=3.0,
        value_width=1.0,
    )

    assert box.w == 4.0
    assert box.anchors["name_value"] == Point(13.5, 21.5)
    assert box.anchors["age_value"] == Point(13.5, 22.5)
    assert box.corners_radius == 0.3


def test_fig_mapping_box_is_dict_box_compatibility_name() -> None:
    box = Fig.mapping_box(0.0, 0.0, elements=[("name", Anchor("value"))])

    assert box.corners_radius == 0.3
    assert box.anchors["value"] == Point(3.5, 1.5)


def test_fig_symbol_table_has_square_corners() -> None:
    box = Fig.symbol_table(
        10.0,
        20.0,
        name="__main__",
        elements=[("x", Anchor("x_value"))],
    )

    assert box.w == 4.0
    assert box.h == 2.0
    assert box.corners_radius == 0.0
    assert box.anchors["x_value"] == Point(13.5, 21.5)


def test_factory_is_compatibility_alias_for_fig() -> None:
    assert Factory is Fig
