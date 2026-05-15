import pytest

from pixbox import Text, TextBody


def test_text_size_is_grid_oriented() -> None:
    text = Text("abcdef")

    assert text.font_size == 0.4
    assert "DejaVu Sans" in text.font_family
    assert "sans-serif" in text.font_family


def test_text_body_line_step_uses_largest_text_size() -> None:
    body = TextBody([Text("small", size=0.5), Text("large", size=2.0)])

    assert body.font_size == 0.8
    assert body.line_step == pytest.approx(1.0)
