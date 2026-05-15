from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, Flag, auto
from typing import TypeAlias

import drawsvg as dw


TextInput: TypeAlias = "str | Text"
TextBodyInput: TypeAlias = "TextInput | list[TextInput] | tuple[TextInput, ...]"
DEFAULT_FONT_FAMILY = "DejaVu Sans, Ubuntu, Arial, sans-serif"
TEXT_SIZE_TO_GRID = 0.4
LINE_HEIGHT = 1.25


class TextProp(Flag):
    NONE = 0
    BOLD = auto()
    ITALIC = auto()


class TextAlign(Enum):
    LEFT = auto()
    CENTER = auto()
    RIGHT = auto()


@dataclass(frozen=True, init=False)
class Text:
    text: str
    size: float = 1.0
    props: TextProp = TextProp.NONE
    align: TextAlign = TextAlign.LEFT
    font_family: str = DEFAULT_FONT_FAMILY

    def __init__(
        self,
        text: str,
        size: float = 1.0,
        props: TextProp = TextProp.NONE,
        align: TextAlign = TextAlign.LEFT,
        font_family: str = DEFAULT_FONT_FAMILY,
        *,
        prop: TextProp | None = None,
    ) -> None:
        object.__setattr__(self, "text", text)
        object.__setattr__(self, "size", size)
        object.__setattr__(self, "props", props if prop is None else prop)
        object.__setattr__(self, "align", align)
        object.__setattr__(self, "font_family", font_family)

    @property
    def font_size(self) -> float:
        return self.size * TEXT_SIZE_TO_GRID

    def draw(self) -> dw.DrawingElement:
        # Placement is normally handled by the containing field.
        return dw.Text(
            self.text,
            font_size=self.font_size,
            x=0,
            y=0,
            font_family=self.font_family,
            font_weight="bold" if TextProp.BOLD in self.props else "normal",
            font_style="italic" if TextProp.ITALIC in self.props else "normal",
        )


@dataclass(frozen=True)
class TextBody:
    content: TextBodyInput
    lines: tuple[Text, ...] = field(init=False)

    def __post_init__(self) -> None:
        if isinstance(self.content, (str, Text)):
            items = (self.content,)
        else:
            items = tuple(self.content)

        object.__setattr__(self, "lines", tuple(self._as_text(item) for item in items))

    @staticmethod
    def _as_text(item: TextInput) -> Text:
        if isinstance(item, Text):
            return item
        if isinstance(item, str):
            return Text(item)
        raise TypeError(
            "TextBody content must be str, Text, or a sequence of str | Text"
        )

    @property
    def max_size(self) -> float:
        return max((line.size for line in self.lines), default=1.0)

    @property
    def font_size(self) -> float:
        return self.max_size * TEXT_SIZE_TO_GRID

    @property
    def line_step(self) -> float:
        return self.font_size * LINE_HEIGHT

    def draw(self) -> dw.DrawingElement:
        # Placement is normally handled by the containing field.
        if len(self.lines) == 1:
            return self.lines[0].draw()

        group = dw.Group()
        for i, line in enumerate(self.lines):
            group.append(dw.Text(line.text, line.font_size, 0, -i * self.line_step))
        return group
