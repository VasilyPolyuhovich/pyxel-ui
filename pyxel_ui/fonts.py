"""Built-in font loader for pyxel-ui.

Loads Cozette BDF as the default font. Falls back to Pyxel built-in
if the font file is not found.
"""
import os
import pyxel

_FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts_data")

# Cached font instances
_cache = {}


def _resolve(name):
    """Resolve a font filename to absolute path."""
    return os.path.abspath(os.path.join(_FONT_DIR, name))


def load_cozette():
    """Load Cozette 6x13 BDF font (default UI font)."""
    return load_bdf("cozette.bdf")


def load_bdf(filename):
    """Load a BDF font from assets/fonts/."""
    if filename in _cache:
        return _cache[filename]
    path = _resolve(filename)
    if os.path.exists(path):
        font = pyxel.Font(path)
        _cache[filename] = font
        return font
    return None


def cozette_font_height():
    """Return Cozette font line height."""
    return 13


# Default font and height for pyxel-ui themes
DEFAULT_FONT = None  # Set lazily in get_default_font()
DEFAULT_FONT_HEIGHT = 13


def get_default_font():
    """Get the default pyxel-ui font (Cozette). Loaded lazily."""
    global DEFAULT_FONT
    if DEFAULT_FONT is None:
        DEFAULT_FONT = load_cozette()
    return DEFAULT_FONT
