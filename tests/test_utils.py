"""Tests for text measurement utilities."""
from pyxel_ui.utils import text_width, truncate_text, char_at_x, text_x_at


class TestTextWidth:
    def test_default_font(self):
        """Default (None) font: 4px per character."""
        assert text_width("", None) == 0
        assert text_width("A", None) == 4
        assert text_width("Hello", None) == 20

    def test_empty(self):
        assert text_width("", None) == 0


class TestTruncateText:
    def test_fits(self):
        assert truncate_text("Hi", 100, None) == "Hi"

    def test_truncates(self):
        result = truncate_text("Hello World", 20, None)  # 20px = 5 chars
        assert len(result) <= 5
        assert text_width(result, None) <= 20

    def test_empty(self):
        assert truncate_text("", 100, None) == ""


class TestCharAtX:
    def test_start(self):
        assert char_at_x("Hello", 0, None) == 0

    def test_middle(self):
        idx = char_at_x("Hello", 8, None)  # 8px = 2 chars
        assert idx == 2

    def test_end(self):
        idx = char_at_x("Hi", 100, None)
        assert idx == 2  # past end = len


class TestTextXAt:
    def test_start(self):
        assert text_x_at("Hello", 0, None) == 0

    def test_middle(self):
        x = text_x_at("Hello", 2, None)
        assert x == 8  # 2 * 4px

    def test_end(self):
        x = text_x_at("Hi", 2, None)
        assert x == 8
