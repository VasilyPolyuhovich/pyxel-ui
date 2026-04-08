"""Basic widgets: Label, Button, Checkbox, RadioGroup, Toggle, Separator, Sprite."""
import pyxel
from .core import Widget
from .utils import text_width


class Label(Widget):
    """Text label.

    Args:
        text: Display text.
        color: Text color (None = theme.text).
        align: "left", "center", or "right".
    """

    def __init__(self, text="", x=0, y=0, **kw):
        self._text = text
        self.color = kw.get("color", None)
        self.align = kw.get("align", "left")
        w = kw.pop("width", 0)
        h = kw.pop("height", 0)
        super().__init__(x, y, w, h, **kw)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        if self.width <= 0:
            self.width = text_width(value, self.theme.font) + 1
        self.mark_dirty()

    def preferred_width(self):
        return self.width if self.width > 0 else text_width(self._text, self.theme.font) + 1

    def preferred_height(self):
        return self.height if self.height > 0 else self.theme.font_height + 1

    def draw(self):
        if not self._text:
            return
        t = self.theme
        col = self.color if self.color is not None else t.text
        if not self.enabled:
            col = t.text_disabled
        ax, ay = self.abs_x(), self.abs_y()
        tw = text_width(self._text, t.font)
        if self.align == "center":
            ax += (self.width - tw) // 2
        elif self.align == "right":
            ax += self.width - tw
        pyxel.text(ax, ay, self._text, col, self.theme.font)


class Button(Widget):
    """Clickable button.

    Args:
        text: Button label.
        on_click: Callback ``fn(widget)``.
        variant: "default", "primary", "success", "warning", "danger".
        icon: Optional icon char drawn before text.
    """

    def __init__(self, text="", x=0, y=0, **kw):
        self.text = text
        self.variant = kw.get("variant", "default")
        self.icon = kw.get("icon", None)
        pad = 4
        label = text
        if self.icon:
            label = self.icon + " " + text
        w = kw.pop("width", 0)
        h = kw.pop("height", 0)
        kw.setdefault("focusable", True)
        super().__init__(x, y, w, h, **kw)

    def _label(self):
        label = self.text
        if self.icon:
            label = self.icon + " " + self.text
        return label

    def preferred_width(self):
        if self.width > 0:
            return self.width
        return text_width(self._label(), self.theme.font) + 9

    def preferred_height(self):
        return self.height if self.height > 0 else self.theme.font_height + 6

    def _get_colors(self):
        t = self.theme
        if not self.enabled:
            return t.btn_disabled_bg, t.btn_disabled_fg
        # Variant accent
        accent = {
            "primary": t.primary,
            "success": t.success,
            "warning": t.warning,
            "danger": t.danger,
        }.get(self.variant, t.btn_bg)
        bg = accent
        fg = t.btn_fg
        if self._pressed:
            bg = t.btn_press
        elif self._hovered:
            bg = t.btn_hover
        return bg, fg

    def draw(self):
        ax, ay = self.abs_x(), self.abs_y()
        bg, fg = self._get_colors()
        pyxel.rect(ax, ay, self.width, self.height, bg)
        if self._focused:
            pyxel.rectb(ax, ay, self.width, self.height, self.theme.border_focus)
        label = self._label()
        tw = text_width(label, self.theme.font)
        tx = ax + (self.width - tw) // 2
        ty = ay + (self.height - self.theme.font_height) // 2
        pyxel.text(tx, ty, label, fg, self.theme.font)

    def handle_key(self, key):
        if key == pyxel.KEY_RETURN or key == pyxel.KEY_SPACE:
            if self.on_click:
                self.on_click(self)


class Checkbox(Widget):
    """Checkbox with label.

    Args:
        text: Label text.
        checked: Initial state.
        on_change: Callback ``fn(widget, checked)``.
    """

    def __init__(self, text="", x=0, y=0, **kw):
        self.text = text
        self.checked = kw.get("checked", False)
        self.on_change = kw.get("on_change", None)
        w = kw.pop("width", 0)
        h = kw.pop("height", 0)  # 0 = auto from font
        kw.setdefault("focusable", True)
        super().__init__(x, y, w, h, **kw)

    def preferred_width(self):
        fh = self.theme.font_height
        box = fh + 1
        return self.width if self.width > 0 else box + 4 + text_width(self.text, self.theme.font)

    def preferred_height(self):
        return self.height if self.height > 0 else self.theme.font_height + 2

    def _toggle(self):
        self.checked = not self.checked
        if self.on_change:
            self.on_change(self, self.checked)

    def handle_release(self, mx, my):
        if self._pressed and self.contains(mx, my):
            self._toggle()
        super().handle_release(mx, my)

    def handle_key(self, key):
        if key == pyxel.KEY_RETURN or key == pyxel.KEY_SPACE:
            self._toggle()

    def draw(self):
        t = self.theme
        ax, ay = self.abs_x(), self.abs_y()
        fh = t.font_height
        box = max(7, fh)
        box_col = t.check_on if self.checked else t.check_off
        if self._focused:
            box_col = t.border_focus
        pyxel.rectb(ax, ay, box, box, box_col)
        if self.checked:
            m = max(1, box // 4)
            pyxel.rect(ax + m + 1, ay + m + 1, box - m * 2 - 2, box - m * 2 - 2, t.check_mark)
        col = t.text if self.enabled else t.text_disabled
        pyxel.text(ax + box + 3, ay + (box - fh) // 2, self.text, col, t.font)


class RadioGroup(Widget):
    """Group of radio buttons (single selection).

    Args:
        options: List of label strings.
        selected: Initially selected index.
        on_change: Callback ``fn(widget, selected_index)``.
        horizontal: Layout direction.
    """

    def __init__(self, options=None, x=0, y=0, **kw):
        self.options = options or []
        self.selected = kw.get("selected", 0)
        self.on_change = kw.get("on_change", None)
        self.horizontal = kw.get("horizontal", False)
        kw.setdefault("focusable", True)
        if self.horizontal:
            w = kw.pop("width", 0)
            h = kw.pop("height", 0)
        else:
            w = kw.pop("width", 0)
            h = kw.pop("height", 0)
        super().__init__(x, y, w, h, **kw)

    def _opt_width(self, opt):
        return 10 + text_width(opt, self.theme.font) + 4

    def preferred_width(self):
        if self.width > 0:
            return self.width
        if self.horizontal:
            return sum(self._opt_width(o) + 2 for o in self.options)
        return max((self._opt_width(o) for o in self.options), default=20)

    def preferred_height(self):
        if self.height > 0:
            return self.height
        fh = self.theme.font_height
        row_h = fh + 3
        if self.horizontal:
            return row_h
        return len(self.options) * row_h

    def handle_release(self, mx, my):
        if not self._pressed or not self.contains(mx, my):
            self._pressed = False
            return
        self._pressed = False
        ax, ay = self.abs_x(), self.abs_y()
        fh = self.theme.font_height
        row_h = fh + 3
        for i, opt in enumerate(self.options):
            if self.horizontal:
                ox = ax + sum(self._opt_width(self.options[j]) + 2 for j in range(i))
                oy = ay
                ow = self._opt_width(opt)
                oh = row_h
            else:
                ox, oy = ax, ay + i * row_h
                ow = self.width
                oh = row_h
            if ox <= mx < ox + ow and oy <= my < oy + oh:
                self.selected = i
                if self.on_change:
                    self.on_change(self, i)
                return

    def handle_key(self, key):
        if not self.options:
            return
        if key == pyxel.KEY_UP or key == pyxel.KEY_LEFT:
            self.selected = (self.selected - 1) % len(self.options)
            if self.on_change:
                self.on_change(self, self.selected)
        elif key == pyxel.KEY_DOWN or key == pyxel.KEY_RIGHT:
            self.selected = (self.selected + 1) % len(self.options)
            if self.on_change:
                self.on_change(self, self.selected)

    def draw(self):
        t = self.theme
        ax, ay = self.abs_x(), self.abs_y()
        fh = t.font_height
        row_h = fh + 3
        r = max(3, fh // 3)  # radio circle radius
        ox_accum = 0
        for i, opt in enumerate(self.options):
            if self.horizontal:
                ox = ax + ox_accum
                oy = ay
                ox_accum += self._opt_width(opt) + 2
            else:
                ox, oy = ax, ay + i * row_h
            # Circle
            cx, cy = ox + r, oy + row_h // 2
            col = t.check_on if i == self.selected else t.check_off
            if self._focused and i == self.selected:
                col = t.border_focus
            pyxel.circb(cx, cy, r, col)
            if i == self.selected:
                pyxel.circ(cx, cy, max(1, r - 2), t.check_mark)
            pyxel.text(ox + r * 2 + 4, oy + (row_h - fh) // 2, opt,
                       t.text if self.enabled else t.text_disabled, t.font)


class Toggle(Widget):
    """On/off toggle switch.

    Args:
        text: Label text.
        value: Initial state.
        on_change: Callback ``fn(widget, value)``.
    """

    def __init__(self, text="", x=0, y=0, **kw):
        self.text = text
        self.value = kw.get("value", False)
        self.on_change = kw.get("on_change", None)
        w = kw.pop("width", 0)
        h = kw.pop("height", 0)  # 0 = auto from font
        kw.setdefault("focusable", True)
        super().__init__(x, y, w, h, **kw)

    def preferred_width(self):
        fh = self.theme.font_height
        track_w = max(12, fh * 2)
        return self.width if self.width > 0 else track_w + 4 + text_width(self.text, self.theme.font)

    def preferred_height(self):
        return self.height if self.height > 0 else self.theme.font_height + 2

    def _toggle(self):
        self.value = not self.value
        if self.on_change:
            self.on_change(self, self.value)

    def handle_release(self, mx, my):
        if self._pressed and self.contains(mx, my):
            self._toggle()
        super().handle_release(mx, my)

    def handle_key(self, key):
        if key == pyxel.KEY_RETURN or key == pyxel.KEY_SPACE:
            self._toggle()

    def draw(self):
        t = self.theme
        ax, ay = self.abs_x(), self.abs_y()
        fh = t.font_height
        track_w = max(12, fh * 2)
        track_h = max(5, fh // 2 + 1)
        thumb_w = max(5, track_w // 3)
        h = self.preferred_height()
        track_y = ay + (h - track_h) // 2
        # Track
        track_col = t.check_on if self.value else t.check_off
        pyxel.rect(ax, track_y, track_w, track_h, track_col)
        # Thumb
        thumb_x = ax + track_w - thumb_w if self.value else ax
        pyxel.rect(thumb_x, ay, thumb_w, h, t.check_mark)
        if self._focused:
            pyxel.rectb(thumb_x, ay, thumb_w, h, t.border_focus)
        # Label
        col = t.text if self.enabled else t.text_disabled
        pyxel.text(ax + track_w + 3, ay + (h - fh) // 2, self.text, col, t.font)


class Separator(Widget):
    """Visual separator line.

    Args:
        orientation: "horizontal" or "vertical".
        color: Line color (None = theme.border).
    """

    def __init__(self, orientation="horizontal", x=0, y=0, **kw):
        self.orientation = orientation
        self.color = kw.get("color", None)
        if orientation == "horizontal":
            w = kw.pop("width", 0)
            h = 3
        else:
            w = 3
            h = kw.pop("height", 0)
        super().__init__(x, y, w, h, **kw)

    def preferred_width(self):
        return self.width if self.width > 0 else 0

    def preferred_height(self):
        return 3 if self.orientation == "horizontal" else self.height

    def draw(self):
        col = self.color if self.color is not None else self.theme.border
        ax, ay = self.abs_x(), self.abs_y()
        if self.orientation == "horizontal":
            pyxel.line(ax, ay + 1, ax + self.width - 1, ay + 1, col)
        else:
            pyxel.line(ax + 1, ay, ax + 1, ay + self.height - 1, col)


class Sprite(Widget):
    """Display a sprite from a Pyxel image bank.

    Args:
        img: Image bank index (0-2).
        u, v: Source position in image bank.
        w, h: Sprite size.
        colkey: Transparent color key.
        scale: Scale multiplier.
    """

    def __init__(self, img=0, u=0, v=0, w=8, h=8, x=0, y=0, **kw):
        self.img = img
        self.u = u
        self.v = v
        self.sprite_w = w
        self.sprite_h = h
        self.colkey = kw.get("colkey", None)
        self.scale = kw.get("scale", 1)
        disp_w = kw.pop("width", w * self.scale)
        disp_h = kw.pop("height", h * self.scale)
        super().__init__(x, y, disp_w, disp_h, **kw)

    def preferred_width(self):
        return self.sprite_w * self.scale

    def preferred_height(self):
        return self.sprite_h * self.scale

    def draw(self):
        ax, ay = self.abs_x(), self.abs_y()
        pyxel.blt(ax, ay, self.img, self.u, self.v,
                  self.sprite_w, self.sprite_h, self.colkey,
                  scale=self.scale)
