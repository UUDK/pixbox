# pixbox

`pixbox` is a small Python helper library for drawing course-material figures about Python objects, namespaces, references, lists, tuples, dictionaries, and similar data-structure diagrams.

The library is intentionally modest. It does not try to solve layout. Instead, it gives you a few predictable, grid-based figure primitives with named anchors, so you can place boxes and route arrows explicitly in ordinary Python code.

## Basic Idea

Figures live in an abstract grid coordinate system:

- `x` grows to the right.
- `y` grows downward.
- Sizes are grid units, not pixels.
- A `Drawing` scales grid units to SVG/PNG output when rendered.
- Figures expose named anchors as `Point` objects.
- Connections are explicit lists of `Point`s.

That means a route can be written directly from anchors and ad hoc bend points:

```python
bend = source.anchors["value"] + (1.5, 0.0)

conn = px.Connection([
    source.anchors["value"],
    bend,
    px.Point(bend.x, target.anchors["header_left"].y),
    target.anchors["header_left"],
])
```

There is no hidden router. The geometry you write is the geometry you get.

## Example

```python
import pixbox as px

drawing = px.Drawing()

main_ns = px.Fig.symbol_table(
    1.0,
    1.0,
    name="__main__",
    elements=[("people", px.Anchor("people"))],
)

people = px.Fig.sequence_box(
    *(main_ns.anchors["top_right"] + (2.0, 0.0)),
    elements=3,
    seq_type="list",
)

drawing.add(main_ns, people)

bend_1 = main_ns.anchors["people"] + (1.5, 0.0)
bend_2 = px.Point(bend_1.x, people.anchors["header_left"].y)

drawing.add(
    px.Connection(
        [
            main_ns.anchors["people"],
            bend_1,
            bend_2,
            people.anchors["header_left"],
        ],
        begin_arrow=px.ArrowType.DOT,
        end_arrow=px.ArrowType.NARROW,
    )
)

px.cli.render(drawing)
```

If the file is named `example_001.py`, the default output files are:

- `example_001.svg`
- `example_001.png`

## Examples

See [`examples/`](examples/) for complete scripts.

The examples are meant to be read as normal Python programs. They construct a `Drawing`, add figures and connections, and finish with:

```python
px.cli.render(drawing)
```

Useful render options:

```bash
python examples/example_000.py --destdir build/figures
python examples/example_000.py --no-png
python examples/example_000.py --name memory-model --scale 120
```

This is deliberately suitable for Makefile rules, for example:

```make
build/figures/example_000.svg: examples/example_000.py
	python $< --destdir build/figures --no-png
```

## Figure Helpers

`px.Fig` is a namespace for common figure constructors:

```python
px.Fig.symbol_table(...)
px.Fig.dict_box(...)
px.Fig.sequence_box(...)
px.Fig.sequence_box_vert(...)
px.Fig.simple_box(...)
```

The lower-level `px.Box` is the common table-like primitive underneath many of these helpers. Cells can contain:

- `TextBody`
- `Anchor`
- `None`

An `Anchor` cell does not render text. It marks the center of that cell as a named point for connections.

## Text

Simple strings are automatically converted into `Text` objects:

```python
px.TextBody("Andrew")
px.TextBody(["line one", "line two"])
px.Text("important", props=px.TextProp.BOLD)
```

Text is positioned by the containing field, not by its own bounding box. This keeps left- and right-aligned text stable inside cells.

## Intentional Limits

`pixbox` is not a general diagramming engine.

The deliberate constraints are:

- no automatic layout
- no automatic arrow routing
- no collision detection
- no text fitting
- no attempt to draw every possible shape
- no new domain-specific language beyond a small set of Python helpers

You choose the positions, sizes, and routes. `pixbox` makes those choices easier to express consistently, but it does not make them for you.

This is by design: the target use case is small, precise teaching figures where manual control is more useful than a large layout system.
