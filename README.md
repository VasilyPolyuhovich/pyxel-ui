# pyxel-ui

Themeable UI widget toolkit for the [Pyxel](https://github.com/kitao/pyxel) retro game engine.

Build pixel-art applications with 35+ widgets, auto-layout, custom fonts, and mouse/keyboard/touch support. Works out of the box with the [Cozette](https://github.com/slavfox/Cozette) pixel font.

## Features

- **35+ widgets** — buttons, inputs, sliders, tables, dropdowns, tabs, dialogs, and more
- **Theming** — 4 built-in themes + fully customizable colors and fonts
- **Auto-layout** — Row/Column/Grid with flex, spacing, alignment
- **Font-aware** — all widgets scale to any font size automatically
- **Input** — mouse, keyboard (Tab focus cycling), touch/drag scroll
- **Overlays** — dropdowns, tooltips, modal dialogs with backdrop
- **Built-in font** — Cozette 6x13 BDF included, zero setup needed

## Quick Start

```python
import pyxel
from pyxel_ui import UI, THEME_DARK, Button, Label, Column

pyxel.init(480, 360, title="My App", display_scale=2)
pyxel.mouse(True)

ui = UI(theme=THEME_DARK)
col = ui.add(Column(x=10, y=10, width=460, spacing=4))
col.add(Label("Hello, pyxel-ui!"))
col.add(Button("Click me", on_click=lambda w: print("Clicked!")))

pyxel.run(ui.update, ui.draw)
```

## Installation

```bash
pip install pyxel-ui
```

Or install from GitHub:

```bash
pip install git+https://github.com/VasilyPolyuhovich/pyxel-ui
```

Requires Python 3.8+ and Pyxel (`pip install pyxel`).

## Widgets

### Basic
| Widget | Description |
|--------|-------------|
| `Label` | Text display with color and alignment |
| `Button` | Clickable with variants: default, primary, success, warning, danger |
| `Checkbox` | Toggle with label |
| `RadioGroup` | Single selection (horizontal/vertical) |
| `Toggle` | On/off switch |
| `Separator` | Horizontal/vertical divider |
| `Sprite` | Image bank sprite display |

### Input
| Widget | Description |
|--------|-------------|
| `TextInput` | Single-line text with cursor, password mode |
| `TextArea` | Multi-line text editor with scroll |
| `Slider` | Numeric range with value display |
| `ProgressBar` | Progress indicator with percentage |
| `NumberInput` | Numeric +/- with prefix/suffix |
| `MaskedInput` | Formatted input (`####-####-####-####`) |
| `ColorPicker` | Pyxel palette color selector |

### Data
| Widget | Description |
|--------|-------------|
| `Table` | Sortable columns, row selection, scrolling |
| `ListView` | Scrollable selectable item list |
| `Tags` | Removable tag/chip labels |

### Containers
| Widget | Description |
|--------|-------------|
| `Panel` | Bordered box with title |
| `ScrollView` | Scrollable area with drag support |
| `TabView` | Tabbed panels |
| `DropDown` | Expandable select list |
| `Accordion` | Collapsible sections |

### Layout
| Widget | Description |
|--------|-------------|
| `Row` | Horizontal auto-layout with flex |
| `Column` | Vertical auto-layout with flex |
| `Grid` | Auto-wrapping cell grid |
| `Spacer` | Flexible empty space |

### Overlay
| Widget | Description |
|--------|-------------|
| `Dialog` | Modal popup with buttons |
| `Tooltip` | Hover text (set `tooltip="..."` on any widget) |
| `Toast` | Temporary notification message |

### Form
| Widget | Description |
|--------|-------------|
| `FormField` | Input wrapper with label, validation, error display |
| `Link` | Clickable underlined text |
| `Badge` | Small counter/status indicator |
| `DividerText` | Separator with centered text |
| `Spinner` | Loading animation |
| `Pagination` | Page navigation |
| `SegmentedControl` | Exclusive button group |

## Themes

All themes use Cozette font by default:

```python
from pyxel_ui import THEME_DARK, THEME_LIGHT, THEME_NES, THEME_GAMEBOY, Theme

ui = UI(theme=THEME_DARK)       # dark blue (default)
ui = UI(theme=THEME_LIGHT)      # light gray
ui = UI(theme=THEME_NES)        # NES/Famicom red
ui = UI(theme=THEME_GAMEBOY)    # Game Boy green

# Switch to Pyxel's built-in 4x6 font
ui = UI(theme=Theme.pyxel_default())

# Custom theme
my_theme = THEME_DARK.copy(primary=8, btn_bg=2)
```

## Fonts

pyxel-ui ships with [Cozette](https://github.com/slavfox/Cozette) (6x13 BDF) as the default font. All widget sizes adapt automatically to font dimensions.

```python
from pyxel_ui import load_bdf, THEME_DARK

# Use a different BDF font
ibm = load_bdf("ib8x8u.bdf")  # loads from assets/fonts/
ui = UI(theme=THEME_DARK.copy(font=ibm, font_height=8))

# Use Pyxel's built-in font
ui = UI(theme=Theme.pyxel_default())

# Use any TTF/OTF font
import pyxel
my_font = pyxel.Font("/path/to/font.ttf", 12)
ui = UI(theme=THEME_DARK.copy(font=my_font, font_height=12))
```

## Layout

```python
# Auto-layout with flex
row = Row(spacing=4, width=400)
row.add(Label("Name:"))
row.add(TextInput(flex=1))   # expands to fill
row.add(Button("OK"))

# Grid
grid = Grid(col_width=100, row_height=30, cols=3)
for item in items:
    grid.add(Button(item))
```

## Form Validation

```python
email = FormField("Email",
    TextInput(placeholder="user@example.com"),
    required=True,
    validator=lambda v: "Invalid" if "@" not in v else None)

if email.validate():
    print("Valid:", email.child_widget.text)
```

## Examples

```bash
pyxel run examples/showcase.py     # full widget showcase
pyxel run examples/font_demo.py    # font comparison
```

## License

MIT License. See [LICENSE](LICENSE).

### Bundled Fonts

- **Cozette** by Slavfox — MIT License ([source](https://github.com/slavfox/Cozette))
- **IBM BIOS Font** by VileR — CC BY-SA 4.0 ([source](https://github.com/farsil/ibmfonts))

See `pyxel_ui/fonts_data/` for font license files.
