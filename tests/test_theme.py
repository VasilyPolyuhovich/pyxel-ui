"""Tests for the theme system."""
from pyxel_ui import Theme, THEME_DARK, THEME_LIGHT, THEME_NES, THEME_GAMEBOY


def test_default_theme_has_cozette():
    """Default theme loads Cozette font automatically."""
    t = Theme()
    assert t.font is not None, "Default font should be Cozette, not None"
    assert t.font_height == 13


def test_pyxel_default_theme():
    """Theme.pyxel_default() uses built-in 4x6 font."""
    t = Theme.pyxel_default()
    assert t.font is None
    assert t.font_height == 6


def test_theme_copy_preserves_font():
    """Copying a theme preserves font settings."""
    t = THEME_DARK.copy(primary=8)
    assert t.primary == 8
    assert t.font is not None  # still Cozette
    assert t.font_height == 13


def test_theme_copy_can_override_font():
    """Copying with font=None switches to Pyxel built-in."""
    t = THEME_DARK.copy(font=None, font_height=6)
    assert t.font is None
    assert t.font_height == 6


def test_preset_themes_exist():
    """All preset themes are valid Theme instances."""
    for theme in [THEME_DARK, THEME_LIGHT, THEME_NES, THEME_GAMEBOY]:
        assert isinstance(theme, Theme)
        assert theme.font is not None  # all use Cozette by default


def test_theme_colors_are_ints():
    """All color properties should be integers (palette indices)."""
    t = THEME_DARK
    for attr in ["bg", "surface", "text", "primary", "secondary",
                 "success", "warning", "danger", "border"]:
        assert isinstance(getattr(t, attr), int), f"{attr} should be int"
