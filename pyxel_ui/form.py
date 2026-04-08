"""Form utilities: validation, NumberInput, Link, Toast, Spinner."""
import pyxel
from .core import Widget, get_ui
from .basic import Label, Button
from .layout import Row
from .utils import text_width


class FormField(Widget):
    """Wraps any input widget with a label, error message, and validation.

    Args:
        label: Field label text.
        child: The input widget (TextInput, DropDown, etc.).
        required: Whether field is required.
        error: Initial error message (empty = no error).
        validator: Optional ``fn(value) -> str|None``. Returns error or None.
    """

    def __init__(self, label="", child=None, x=0, y=0, **kw):
        self.label_text = label
        self.child_widget = child
        self.required = kw.get("required", False)
        self._error = kw.get("error", "")
        self.validator = kw.get("validator", None)
        w = kw.pop("width", 0)
        h = kw.pop("height", 0)
        self._init_child_h = child.preferred_height() if child else 0
        super().__init__(x, y, w, h or 1, **kw)
        if child:
            self.add(child)
        # Recalc with theme available
        self._update_height()

    @property
    def error(self):
        return self._error

    @error.setter
    def error(self, value):
        self._error = value or ""
        self._update_height()

    def _update_height(self):
        ch = self.child_widget.preferred_height() if self.child_widget else (self.theme.font_height + 6)
        self.height = self.theme.font_height + 1 + 2 + ch + (self.theme.font_height + 2 if self._error else 0)
        self.mark_dirty()

    def validate(self):
        """Run validation. Returns True if valid."""
        if not self.child_widget:
            return True
        value = ""
        if hasattr(self.child_widget, "text"):
            value = self.child_widget.text
        elif hasattr(self.child_widget, "_text"):
            value = self.child_widget._text
        elif hasattr(self.child_widget, "selected_text"):
            value = self.child_widget.selected_text
        value = str(value or "")

        if self.required and not value.strip():
            self.error = "Required"
            return False
        if self.validator:
            err = self.validator(value)
            if err:
                self.error = err
                return False
        self.error = ""
        return True

    def preferred_width(self):
        return self.width if self.width > 0 else (self.child_widget.preferred_width() if self.child_widget else 60)

    def preferred_height(self):
        return self.height

    def content_x(self):
        return self.abs_x()

    def content_y(self):
        return self.abs_y()

    def layout(self):
        if self.child_widget:
            self.child_widget.x = 0
            self.child_widget.y = self.theme.font_height + 2
            if self.child_widget.width <= 0:
                self.child_widget.width = self.width
            if self.child_widget._dirty:
                self.child_widget.layout()
        self._dirty = False

    def draw(self):
        t = self.theme
        ax, ay = self.abs_x(), self.abs_y()

        # Label
        label = self.label_text
        if self.required:
            label += "*"
        col = t.danger if self._error else t.text
        pyxel.text(ax, ay, label, col, t.font)

        # Child widget
        if self.child_widget and self.child_widget.visible:
            self.child_widget.draw()
            # Draw error border overlay on top (without mutating theme)
            if self._error and hasattr(self.child_widget, 'abs_x'):
                cx, cy = self.child_widget.abs_x(), self.child_widget.abs_y()
                cw = self.child_widget.width
                ch = self.child_widget.preferred_height()
                pyxel.rectb(cx, cy, cw, ch, t.danger)

        # Error message
        if self._error:
            fh = t.font_height
            child_h = self.child_widget.preferred_height() if self.child_widget else (fh + 6)
            ey = ay + fh + 2 + child_h + 1
            pyxel.text(ax, ey, self._error, t.danger, t.font)

    def find_focusable(self, forward=True):
        if self.child_widget:
            return self.child_widget.find_focusable(forward)
        return []

    def hit_test(self, mx, my):
        if not self.visible or not self.contains(mx, my):
            return None
        if self.child_widget and self.child_widget.visible and self.child_widget.enabled:
            hit = self.child_widget.hit_test(mx, my)
            if hit:
                return hit
        return None


class NumberInput(Widget):
    """Numeric input with +/- buttons.

    Args:
        value: Current numeric value.
        min_val: Minimum value.
        max_val: Maximum value.
        step: Increment step.
        on_change: Callback ``fn(widget, value)``.
        prefix: Text before number (e.g. "$").
        suffix: Text after number (e.g. "kg").
    """

    def __init__(self, x=0, y=0, width=60, **kw):
        self.value = kw.get("value", 0)
        self.min_val = kw.get("min_val", 0)
        self.max_val = kw.get("max_val", 999)
        self.step = kw.get("step", 1)
        self.on_change = kw.get("on_change", None)
        self.prefix = kw.get("prefix", "")
        self.suffix = kw.get("suffix", "")
        self._is_float = isinstance(self.step, float)
        h = kw.pop("height", 0)
        kw.setdefault("focusable", True)
        super().__init__(x, y, width, h, **kw)

    def preferred_width(self):
        return self.width if self.width > 0 else 60

    def preferred_height(self):
        return self.height if self.height > 0 else self.theme.font_height + 6

    def _set_value(self, v):
        v = max(self.min_val, min(self.max_val, v))
        if not self._is_float:
            v = int(v)
        if v != self.value:
            self.value = v
            if self.on_change:
                self.on_change(self, self.value)

    def handle_release(self, mx, my):
        if self._pressed and self.contains(mx, my):
            ax = self.abs_x()
            btn_w = self.height  # square buttons
            if ax <= mx < ax + btn_w:
                self._set_value(self.value - self.step)
            elif ax + self.width - btn_w <= mx < ax + self.width:
                self._set_value(self.value + self.step)
        super().handle_release(mx, my)

    def handle_key(self, key):
        if key == pyxel.KEY_UP or key == pyxel.KEY_RIGHT:
            self._set_value(self.value + self.step)
        elif key == pyxel.KEY_DOWN or key == pyxel.KEY_LEFT:
            self._set_value(self.value - self.step)

    def draw(self):
        t = self.theme
        ax, ay = self.abs_x(), self.abs_y()
        h = self.height
        fh = t.font_height
        btn_w = h  # square buttons
        text_y = ay + (h - fh) // 2

        # Background
        pyxel.rect(ax, ay, self.width, h, t.input_bg)
        pyxel.rectb(ax, ay, self.width, h, t.input_focus if self._focused else t.input_border)

        # Minus button
        minus_hover = self._hovered and pyxel.mouse_x < ax + btn_w
        pyxel.rect(ax + 1, ay + 1, btn_w - 1, h - 2, t.btn_hover if minus_hover else t.btn_bg)
        minus_tw = text_width("-", t.font)
        pyxel.text(ax + (btn_w - minus_tw) // 2, text_y, "-", t.btn_fg, t.font)

        # Plus button
        plus_hover = self._hovered and pyxel.mouse_x >= ax + self.width - btn_w
        pyxel.rect(ax + self.width - btn_w, ay + 1, btn_w - 1, h - 2, t.btn_hover if plus_hover else t.btn_bg)
        plus_tw = text_width("+", t.font)
        pyxel.text(ax + self.width - btn_w + (btn_w - plus_tw) // 2, text_y, "+", t.btn_fg, t.font)

        # Value
        if self._is_float:
            val_str = f"{self.prefix}{self.value:.1f}{self.suffix}"
        else:
            val_str = f"{self.prefix}{self.value}{self.suffix}"
        tw = text_width(val_str, t.font)
        tx = ax + (self.width - tw) // 2
        pyxel.text(tx, text_y, val_str, t.text, t.font)


class Link(Widget):
    """Clickable text link.

    Args:
        text: Link text.
        color: Normal color (None = theme.primary).
        hover_color: Hover color (None = theme.secondary).
        on_click: Callback ``fn(widget)``.
    """

    def __init__(self, text="", x=0, y=0, **kw):
        self.text = text
        self.color = kw.get("color", None)
        self.hover_color = kw.get("hover_color", None)
        w = kw.pop("width", 0)
        h = kw.pop("height", 0)
        super().__init__(x, y, w, h, **kw)

    def preferred_width(self):
        return text_width(self.text, self.theme.font) + 1

    def preferred_height(self):
        return self.theme.font_height + 1

    def draw(self):
        t = self.theme
        ax, ay = self.abs_x(), self.abs_y()
        col = self.color if self.color is not None else t.primary
        if self._hovered:
            col = self.hover_color if self.hover_color is not None else t.secondary
        if not self.enabled:
            col = t.text_disabled
        pyxel.text(ax, ay, self.text, col, t.font)
        # Underline
        if self._hovered and self.enabled:
            tw = text_width(self.text, t.font)
            pyxel.line(ax, ay + t.font_height, ax + tw - 1, ay + t.font_height, col)


class Toast:
    """Temporary notification message.

    Shows a text message at the top of the screen that fades after duration.

    Usage::

        Toast.show("Saved!", color=11, duration=60)
    """

    _active = []

    @classmethod
    def show(cls, text, color=None, bg=None, duration=60):
        """Show a toast message.

        Args:
            text: Message text.
            color: Text color (default: theme.text).
            bg: Background color (default: theme.surface).
            duration: Frames to show (30fps: 60 = 2 seconds).
        """
        cls._active.append({
            "text": text,
            "color": color,
            "bg": bg,
            "duration": duration,
            "timer": 0,
        })

    @classmethod
    def update(cls):
        """Call in your update loop (or let UI.update handle it)."""
        cls._active = [t for t in cls._active if t["timer"] < t["duration"]]
        for t in cls._active:
            t["timer"] += 1

    @classmethod
    def draw(cls):
        """Call after UI.draw()."""
        ui = get_ui()
        theme = ui.theme if ui else None
        font = theme.font if theme else None
        fh = theme.font_height if theme else 6
        toast_h = fh + 3
        pad = max(2, fh // 4)
        y = 2
        for t in cls._active:
            text = t["text"]
            tw = text_width(text, font) + pad * 2 + 4
            tx = (pyxel.width - tw) // 2
            bg = t["bg"] if t["bg"] is not None else (theme.surface if theme else 1)
            fg = t["color"] if t["color"] is not None else (theme.text if theme else 7)
            remaining = t["duration"] - t["timer"]
            # Slide up and fade via dither in last 15 frames
            if remaining < 15:
                alpha = remaining / 15
                pyxel.dither(alpha)
            pyxel.rect(tx, y, tw, toast_h, bg)
            pyxel.rectb(tx, y, tw, toast_h, fg)
            pyxel.text(tx + pad + 2, y + (toast_h - fh) // 2, text, fg, font)
            if remaining < 15:
                pyxel.dither(1.0)
            y += toast_h + 3

    @classmethod
    def clear(cls):
        cls._active.clear()


class Spinner(Widget):
    """Loading spinner animation.

    Args:
        text: Optional loading text.
        color: Spinner color (None = theme.primary).
        speed: Animation speed (frames per rotation step).
    """

    def __init__(self, x=0, y=0, **kw):
        self.label = kw.get("text", "")
        self.color = kw.get("color", None)
        self.speed = kw.get("speed", 4)
        self._frame = 0
        w = kw.pop("width", 0)
        h = kw.pop("height", 0)
        super().__init__(x, y, w, h, **kw)

    def preferred_width(self):
        return 8 + (text_width(self.label, self.theme.font) + 4 if self.label else 0)

    def preferred_height(self):
        return self.height if self.height > 0 else self.theme.font_height + 2

    def update(self):
        self._frame += 1

    def draw(self):
        t = self.theme
        ax, ay = self.abs_x(), self.abs_y()
        fh = t.font_height
        col = self.color if self.color is not None else t.primary

        # Rotating dots pattern
        cx, cy = ax + 3, ay + self.height // 2
        step = (self._frame // self.speed) % 8
        positions = [
            (0, -3), (2, -2), (3, 0), (2, 2),
            (0, 3), (-2, 2), (-3, 0), (-2, -2),
        ]
        for i, (dx, dy) in enumerate(positions):
            dist = (i - step) % 8
            if dist < 4:
                pyxel.pset(cx + dx, cy + dy, col)

        # Label
        if self.label:
            pyxel.text(ax + 10, ay + (self.height - fh) // 2, self.label, t.text, t.font)


class Badge(Widget):
    """Small badge/counter indicator.

    Args:
        text: Badge text (number or short string).
        color: Background color (None = theme.danger).
        text_color: Text color (None = theme.text).
    """

    def __init__(self, text="", x=0, y=0, **kw):
        self.text = str(text)
        self.color = kw.get("color", None)
        self.text_color = kw.get("text_color", None)
        w = 0  # auto-sized by preferred_width
        h = kw.pop("height", 0)
        super().__init__(x, y, w, h, **kw)

    def preferred_width(self):
        return max(7, text_width(self.text, self.theme.font) + 4)

    def preferred_height(self):
        return self.theme.font_height + 1

    def draw(self):
        t = self.theme
        ax, ay = self.abs_x(), self.abs_y()
        fh = t.font_height
        bg = self.color if self.color is not None else t.danger
        fg = self.text_color if self.text_color is not None else t.text
        pyxel.rect(ax, ay, self.width, self.height, bg)
        tw = text_width(self.text, t.font)
        pyxel.text(ax + (self.width - tw) // 2, ay + (self.height - fh) // 2, self.text, fg, t.font)


class DividerText(Widget):
    """Horizontal divider with centered text (e.g. "-- OR --").

    Args:
        text: Center text.
        color: Line and text color (None = theme.text_dim).
    """

    def __init__(self, text="", x=0, y=0, **kw):
        self.text = text
        self.color = kw.get("color", None)
        w = kw.pop("width", 0)
        h = kw.pop("height", 0)
        super().__init__(x, y, w, h, **kw)

    def preferred_width(self):
        return self.width

    def preferred_height(self):
        return self.height if self.height > 0 else self.theme.font_height + 3

    def draw(self):
        t = self.theme
        ax, ay = self.abs_x(), self.abs_y()
        fh = t.font_height
        col = self.color if self.color is not None else t.text_dim
        mid_y = ay + self.height // 2
        if self.text:
            tw = text_width(self.text, t.font) + 4
            tx = ax + (self.width - tw) // 2
            pyxel.line(ax, mid_y, tx - 2, mid_y, col)
            pyxel.text(tx + 2, ay + (self.height - fh) // 2, self.text, col, t.font)
            pyxel.line(tx + tw + 2, mid_y, ax + self.width - 1, mid_y, col)
        else:
            pyxel.line(ax, mid_y, ax + self.width - 1, mid_y, col)
