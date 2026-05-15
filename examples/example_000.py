import pixbox as px

drawing = px.Drawing()

main_ns = px.Fig.symbol_table(
    1.0, 1.0, name="__main__", elements=[("people", px.Anchor("people"))]
)
drawing.add(main_ns)

list_1 = px.Fig.sequence_box(
    *(main_ns.anchors["top_right"] + (2.0, 0.0)), elements=3, seq_type="list"
)

tuple_1 = px.Fig.sequence_box(
    *(list_1.anchors["top_right"] + (2.0, 0.0)),
    elements=[px.TextBody("Andrew"), px.TextBody("Ben"), px.TextBody("Charlie")],
    cell_width=3.0,
    seq_type="tuple",
)

drawing.add(list_1, tuple_1)

bend_1_1 = main_ns.anchors["people"] + (1.5, 0.0)
bend_1_2 = px.Point(bend_1_1.x, list_1.anchors["header_left"].y)
conn_1 = px.Connection(
    [main_ns.anchors["people"], bend_1_1, bend_1_2, list_1.anchors["header_left"]],
    begin_arrow=px.ArrowType.DOT,
    end_arrow=px.ArrowType.NARROW,
)
drawing.add(conn_1)

bend_2_1 = list_1.anchors["[0]"] + (0.0, 1.5)
bend_2_2 = bend_2_1 + (3.5, 0.0)
bend_2_3 = px.Point(bend_2_2.x, tuple_1.anchors["header_left"].y)
conn_2 = px.Connection(
    [
        list_1.anchors["[0]"],
        bend_2_1,
        bend_2_2,
        bend_2_3,
        tuple_1.anchors["header_left"],
    ],
    begin_arrow=px.ArrowType.DOT,
    end_arrow=px.ArrowType.NARROW,
)
drawing.add(conn_2)

px.cli.render(drawing)
