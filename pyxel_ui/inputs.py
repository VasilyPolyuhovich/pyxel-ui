"""Input widgets: TextInput, Slider, ProgressBar."""
import pyxel
from .core import Widget
from .utils import text_width, truncate_text, char_at_x, text_x_at


class TextInput(Widget):
    """Single-line text input field.

    Args:
        text: Initial text.
        placeholder: Placeholder when empty.
        max_length: Maximum characters (0 = unlimited).
        password: Show dots instead of text.
        on_change: Callback ``fn(widget, text)``.
        on_submit: Callback ``fn(widget, text)`` on Enter.
    """

    def __init__(self, x=0, y=0, width=60, **kw):
        self._text = kw.get("text", "")
        self.placeholder = kw.get("placeholder", "")
        self.max_length = kw.get("max_length", 0)
        self.password = kw.get("password", False)
        self.on_change = kw.get("on_change", None)
        self.on_submit = kw.get("on_submit", None)
        self._cursor = len(self._text)
        self._scroll_offset = 0
        self._cursor_blink = 0
        h = kw.pop("height", 0)
        kw.setdefault("focusable", True)
        super().__init__(x, y, width, h, **kw)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self._cursor = min(self._cursor, len(value))

    def preferred_width(self):
        return self.width if self.width > 0 else 60

    def preferred_height(self):
        return self.height if self.height > 0 else self.theme.font_height + 6

    def _visible_chars(self):
        """Number of characters that fit in the field (approximate for variable-width)."""
        font = self.theme.font
        fh = self.theme.font_height
        pad = max(2, fh // 4)
        available = self.width - pad * 2
        if font is None:
            return max(1, available // 4)
        # For variable-width fonts, estimate from average char width
        # We'll use the actual text for precise display in draw()
        avg = font.text_width("M") if font else 4
        return max(1, available // max(1, avg))

    def _ensure_cursor_visible(self):
        vis = self._visible_chars()
        if self._cursor < self._scroll_offset:
            self._scroll_offset = self._cursor
        elif self._cursor > self._scroll_offset + vis:
            self._scroll_offset = self._cursor - vis

    def handle_text(self, ch):
        if self.max_length > 0 and len(self._text) >= self.max_length:
            return
        self._text = self._text[:self._cursor] + ch + self._text[self._cursor:]
        self._cursor += 1
        self._ensure_cursor_visible()
        self._cursor_blink = 0
        if self.on_change:
            self.on_change(self, self._text)

    def handle_key(self, key):
        if key == pyxel.KEY_BACKSPACE:
            if self._cursor > 0:
                self._text = self._text[:self._cursor - 1] + self._text[self._cursor:]
                self._cursor -= 1
                self._ensure_cursor_visible()
                if self.on_change:
                    self.on_change(self, self._text)
        elif key == pyxel.KEY_DELETE:
            if self._cursor < len(self._text):
                self._text = self._text[:self._cursor] + self._text[self._cursor + 1:]
                if self.on_change:
                    self.on_change(self, self._text)
        elif key == pyxel.KEY_LEFT:
            self._cursor = max(0, self._cursor - 1)
            self._ensure_cursor_visible()
        elif key == pyxel.KEY_RIGHT:
            self._cursor = min(len(self._text), self._cursor + 1)
            self._ensure_cursor_visible()
        elif key == pyxel.KEY_HOME:
            self._cursor = 0
            self._scroll_offset = 0
        elif key == pyxel.KEY_END:
            self._cursor = len(self._text)
            self._ensure_cursor_visible()
        elif key == pyxel.KEY_RETURN:
            if self.on_submit:
                self.on_submit(self, self._text)
        self._cursor_blink = 0

    def handle_press(self, mx, my):
        super().handle_press(mx, my)
        # Position cursor by click
        fh = self.theme.font_height
        pad = max(2, fh // 4)
        ax = self.abs_x() + pad
        rel_x = mx - ax
        font = self.theme.font
        visible_text = self._text[self._scroll_offset:]
        char_pos = self._scroll_offset + char_at_x(visible_text, max(0, rel_x), font)
        self._cursor = min(len(self._text), char_pos)
        self._cursor_blink = 0

    def update(self):
        if self._focused:
            self._cursor_blink += 1

    def draw(self):
        t = self.theme
        ax, ay = self.abs_x(), self.abs_y()
        font = t.font
        fh = t.font_height
        pad = max(2, fh // 4)
        ty = ay + (self.height - fh) // 2

        # Background
        pyxel.rect(ax, ay, self.width, self.height, t.input_bg)
        border_col = t.input_focus if self._focused else t.input_border
        pyxel.rectb(ax, ay, self.width, self.height, border_col)

        # Text
        available = self.width - pad * 2
        if self._text:
            display = self._text
            if self.password:
                display = "*" * len(display)
            visible_text = display[self._scroll_offset:]
            visible_text = truncate_text(visible_text, available, font)
            pyxel.text(ax + pad, ty, visible_text, t.input_fg, font)
        elif self.placeholder and not self._focused:
            ph = truncate_text(self.placeholder, available, font)
            pyxel.text(ax + pad, ty, ph, t.input_placeholder, font)

        # Cursor
        if self._focused and (self._cursor_blink % 30) < 20:
            display = self._text
            if self.password:
                display = "*" * len(display)
            cursor_text = display[self._scroll_offset:self._cursor]
            cx = ax + pad + text_width(cursor_text, font)
            pyxel.line(cx, ay + pad, cx, ay + self.height - pad - 1, t.input_cursor)


class Slider(Widget):
    """Horizontal slider for numeric values.

    Args:
        value: Current value.
        min_val: Minimum value.
        max_val: Maximum value.
        step: Value step (0 = continuous).
        on_change: Callback ``fn(widget, value)``.
        show_value: Display current value text.
    """

    def __init__(self, x=0, y=0, width=60, **kw):
        self.value = kw.get("value", 0)
        self.min_val = kw.get("min_val", 0)
        self.max_val = kw.get("max_val", 100)
        self.step = kw.get("step", 0)
        self.on_change = kw.get("on_change", None)
        self.show_value = kw.get("show_value", True)
        self._dragging = False
        h = kw.pop("height", 0)
        kw.setdefault("focusable", True)
        super().__init__(x, y, width, h, **kw)

    def preferred_width(self):
        return self.width if self.width > 0 else 60

    def preferred_height(self):
        return self.height if self.height > 0 else self.theme.font_height + 4

    def _track_x(self):
        return self.abs_x() + 2

    def _track_w(self):
        w = self.width - 4
        if self.show_value:
            w -= 20
        return max(8, w)

    def _value_to_x(self, val):
        rng = self.max_val - self.min_val
        if rng <= 0:
            return 0
        frac = (val - self.min_val) / rng
        return int(frac * (self._track_w() - 3))

    def _x_to_value(self, rel_x):
        tw = self._track_w() - 3
        if tw <= 0:
            return self.min_val
        frac = max(0, min(1, rel_x / tw))
        val = self.min_val + frac * (self.max_val - self.min_val)
        if self.step > 0:
            val = round(val / self.step) * self.step
        return max(self.min_val, min(self.max_val, val))

    def _set_value_from_mouse(self, mx):
        rel_x = mx - self._track_x()
        new_val = self._x_to_value(rel_x)
        if new_val != self.value:
            self.value = new_val
            if self.on_change:
                self.on_change(self, self.value)

    def handle_press(self, mx, my):
        super().handle_press(mx, my)
        self._dragging = True
        self._set_value_from_mouse(mx)

    def handle_release(self, mx, my):
        self._dragging = False
        self._pressed = False

    def update(self):
        if self._dragging and pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
            self._set_value_from_mouse(pyxel.mouse_x)
        elif self._dragging:
            self._dragging = False

    def handle_key(self, key):
        delta = self.step if self.step > 0 else (self.max_val - self.min_val) / 20
        if key == pyxel.KEY_LEFT:
            self.value = max(self.min_val, self.value - delta)
            if self.on_change:
                self.on_change(self, self.value)
        elif key == pyxel.KEY_RIGHT:
            self.value = min(self.max_val, self.value + delta)
            if self.on_change:
                self.on_change(self, self.value)

    def draw(self):
        t = self.theme
        ax, ay = self.abs_x(), self.abs_y()
        tx = self._track_x()
        tw = self._track_w()
        track_y = ay + self.height // 2 - 1

        # Track
        pyxel.rect(tx, track_y, tw, 3, t.slider_track)

        # Fill
        fill_w = self._value_to_x(self.value)
        if fill_w > 0:
            pyxel.rect(tx, track_y, fill_w, 3, t.slider_fill)

        # Thumb
        thumb_x = tx + fill_w
        pyxel.rect(thumb_x, ay + 1, 3, self.height - 2, t.slider_thumb)
        if self._focused:
            pyxel.rectb(thumb_x - 1, ay, 5, self.height, t.border_focus)

        # Value text
        if self.show_value:
            fh = t.font_height
            val_str = str(int(self.value)) if self.step == 0 or self.step >= 1 else f"{self.value:.1f}"
            pyxel.text(tx + tw + 4, ay + (self.height - fh) // 2, val_str, t.text, t.font)


class ProgressBar(Widget):
    """Progress indicator.

    Args:
        value: Current progress (0.0 - 1.0).
        color: Fill color (None = theme.progress_fill).
        show_text: Show percentage text.
    """

    def __init__(self, x=0, y=0, width=60, **kw):
        self.value = kw.get("value", 0)
        self.color = kw.get("color", None)
        self.show_text = kw.get("show_text", False)
        h = kw.pop("height", 0)
        super().__init__(x, y, width, h, **kw)

    def preferred_width(self):
        return self.width if self.width > 0 else 60

    def preferred_height(self):
        return self.height if self.height > 0 else self.theme.font_height + 2

    def draw(self):
        t = self.theme
        ax, ay = self.abs_x(), self.abs_y()
        pyxel.rect(ax, ay, self.width, self.height, t.progress_bg)
        fill_w = int(self.width * max(0, min(1, self.value)))
        fill_col = self.color if self.color is not None else t.progress_fill
        if fill_w > 0:
            pyxel.rect(ax, ay, fill_w, self.height, fill_col)
        if self.show_text:
            fh = t.font_height
            pct = f"{int(self.value * 100)}%"
            tw = text_width(pct, t.font)
            pyxel.text(ax + (self.width - tw) // 2, ay + (self.height - fh) // 2, pct, t.text, t.font)
