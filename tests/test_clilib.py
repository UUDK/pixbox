from pathlib import Path

import pytest

from pixbox import Drawing
from pixbox.clilib import parse_render_options, render


def test_parse_render_options_uses_script_name_defaults() -> None:
    options = parse_render_options(argv=[], default_name="example_001")

    assert options.name == "example_001"
    assert options.destdir == Path(".")
    assert options.png_path == Path("example_001.png")
    assert options.svg_path == Path("example_001.svg")
    assert options.png is True
    assert options.svg is True


def test_parse_render_options_accepts_makefile_friendly_overrides(tmp_path: Path) -> None:
    options = parse_render_options(
        argv=[
            "--name",
            "figure",
            "--destdir",
            str(tmp_path),
            "--no-svg",
            "--scale",
            "42",
        ],
        default_name="example_001",
    )

    assert options.name == "figure"
    assert options.destdir == tmp_path
    assert options.png is True
    assert options.svg is False
    assert options.scale == 42.0


def test_parse_render_options_rejects_no_outputs() -> None:
    with pytest.raises(SystemExit):
        parse_render_options(argv=["--no-png", "--no-svg"], default_name="example_001")


def test_render_writes_selected_outputs(tmp_path: Path) -> None:
    drawing = Drawing()

    options = render(
        drawing,
        argv=["--destdir", str(tmp_path), "--no-png", "--scale", "25"],
        name="example_001",
    )

    assert drawing.scale == 25.0
    assert options.svg_path == tmp_path / "example_001.svg"
    assert options.svg_path.exists()
    assert not options.png_path.exists()
