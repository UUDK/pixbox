from __future__ import annotations

import argparse
import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .drawing import Drawing


@dataclass(frozen=True)
class RenderOptions:
    name: str
    destdir: Path
    png: bool = True
    svg: bool = True
    scale: float | None = None

    @property
    def png_path(self) -> Path:
        return self.destdir / f"{self.name}.png"

    @property
    def svg_path(self) -> Path:
        return self.destdir / f"{self.name}.svg"


def render(
    drawing: Drawing,
    *,
    argv: Sequence[str] | None = None,
    name: str | None = None,
    destdir: str | Path | None = None,
    png: bool | None = None,
    svg: bool | None = None,
    scale: float | None = None,
) -> RenderOptions:
    options = parse_render_options(
        argv=argv,
        default_name=name,
        default_destdir=destdir,
        default_png=True if png is None else png,
        default_svg=True if svg is None else svg,
        default_scale=scale,
    )

    options.destdir.mkdir(parents=True, exist_ok=True)
    if options.scale is not None:
        drawing.scale = options.scale
    if options.png:
        drawing.save_png(options.png_path)
    if options.svg:
        drawing.save_svg(options.svg_path)

    return options


def parse_render_options(
    *,
    argv: Sequence[str] | None = None,
    default_name: str | None = None,
    default_destdir: str | Path | None = None,
    default_png: bool = True,
    default_svg: bool = True,
    default_scale: float | None = None,
) -> RenderOptions:
    parser = _parser(
        default_name=default_name or _caller_stem(),
        default_destdir=Path(default_destdir)
        if default_destdir is not None
        else Path("."),
        default_png=default_png,
        default_svg=default_svg,
        default_scale=default_scale,
    )
    args = parser.parse_args(argv)

    if not args.png and not args.svg:
        parser.error("at least one output format must be enabled")

    return RenderOptions(
        name=args.name,
        destdir=args.destdir,
        png=args.png,
        svg=args.svg,
        scale=args.scale,
    )


def _parser(
    *,
    default_name: str,
    default_destdir: Path,
    default_png: bool,
    default_svg: bool,
    default_scale: float | None,
) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--name", default=default_name)
    parser.add_argument("--destdir", type=Path, default=default_destdir)
    parser.add_argument("--scale", type=float, default=default_scale)

    png_group = parser.add_mutually_exclusive_group()
    png_group.add_argument("--png", dest="png", action="store_true")
    png_group.add_argument("--no-png", dest="png", action="store_false")
    parser.set_defaults(png=default_png)

    svg_group = parser.add_mutually_exclusive_group()
    svg_group.add_argument("--svg", dest="svg", action="store_true")
    svg_group.add_argument("--no-svg", dest="svg", action="store_false")
    parser.set_defaults(svg=default_svg)

    return parser


def _caller_stem() -> str:
    for frame in inspect.stack()[2:]:
        path = Path(frame.filename)
        if path.name != Path(__file__).name:
            return path.stem
    return "drawing"
