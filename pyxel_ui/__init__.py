"""pyxel-ui: A retro UI toolkit for Pyxel.

Comprehensive widget library with theming, layout system,
mouse/touch/keyboard support.

Usage::

    import pyxel
    from pyxel_ui import UI, Button, Label, Column, THEME_DARK

    ui = UI(theme=THEME_DARK)
    col = ui.add(Column(x=10, y=10, width=140, height=100, spacing=4))
    col.add(Label("Hello, pyxel-ui!"))
    col.add(Button("Click me", on_click=lambda w: print("Clicked!")))

    pyxel.init(160, 120)
    pyxel.run(ui.update, ui.draw)
"""

__version__ = "0.3.0"

# Core
from .core import UI, Widget, get_ui

# Theme
from .theme import (
    Theme,
    THEME_DARK,
    THEME_LIGHT,
    THEME_NES,
    THEME_GAMEBOY,
)

# Layout
from .layout import Row, Column, Spacer

# Basic widgets
from .basic import (
    Label,
    Button,
    Checkbox,
    RadioGroup,
    Toggle,
    Separator,
    Sprite,
)

# Input widgets
from .inputs import TextInput, Slider, ProgressBar

# Multi-line text
from .textarea import TextArea

# Containers
from .containers import (
    Panel,
    ScrollView,
    TabView,
    DropDown,
    ListView,
)

# Dialogs
from .dialog import Dialog, Tooltip

# Form utilities
from .form import (
    FormField,
    NumberInput,
    Link,
    Toast,
    Spinner,
    Badge,
    DividerText,
)

# Table
from .table import Table

# Grid layout
from .grid import Grid

# Font loader
from .fonts import load_cozette, load_bdf

# Text measurement utilities
from .utils import text_width, text_height, truncate_text, char_at_x, text_x_at

# Extras
from .extras import (
    Tags,
    MaskedInput,
    ColorPicker,
    Accordion,
    Pagination,
    SegmentedControl,
)

__all__ = [
    # Core
    "UI", "Widget", "get_ui",
    # Theme
    "Theme", "THEME_DARK", "THEME_LIGHT", "THEME_NES", "THEME_GAMEBOY",
    # Layout
    "Row", "Column", "Spacer",
    # Basic
    "Label", "Button", "Checkbox", "RadioGroup", "Toggle", "Separator", "Sprite",
    # Input
    "TextInput", "TextArea", "Slider", "ProgressBar",
    # Containers
    "Panel", "ScrollView", "TabView", "DropDown", "ListView",
    # Dialog
    "Dialog", "Tooltip",
    # Form
    "FormField", "NumberInput", "Link", "Toast", "Spinner", "Badge", "DividerText",
    # Table & Grid
    "Table", "Grid",
    # Extras
    "Tags", "MaskedInput", "ColorPicker", "Accordion", "Pagination", "SegmentedControl",
    # Fonts
    "load_cozette", "load_bdf",
    # Utils
    "text_width", "text_height", "truncate_text", "char_at_x", "text_x_at",
]
