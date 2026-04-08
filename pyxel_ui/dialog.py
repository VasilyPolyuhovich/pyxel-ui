"""Dialog and Tooltip widgets."""
import pyxel
from .core import Widget, get_ui
from .basic import Button, Label
from .layout import Row
from .utils import text_width, truncate_text


class Dialog(Widget):
    """Modal dialog popup.

    Centered on screen with title, content area, and action buttons.

    Args:
        title: Dialog title.
        message: Text message.
        buttons: List of button labels (e.g. ["OK", "Cancel"]).
        on_button: Callback ``fn(widget, button_index)``.
    """

    def __init__(self, title="", message="", buttons=None, **kw):
        self.title = title
        self.message = message
        self.button_labels = buttons or ["OK"]
        self.on_button = kw.get("on_button", None)
        self._btn_widgets = []
        w = kw.pop("width", max(80, text_width(message, None) + 16))
        chars_per_line = max(1, (w - 8) // 4)  # rough estimate for wrapping
        # Height will be recalculated in _build once theme is available
        h = kw.pop("height", 45 + (len(message) // chars_per_line + 1) * 8)
        x = (pyxel.width - w) // 2
        y = (pyxel.height - h) // 2
        kw.setdefault("focusable", True)
        super().__init__(x, y, w, h, **kw)
        self._build()

    def _build(self):
        # Center buttons
        fh = self.theme.font_height
        btn_h = fh + 6
        btn_w = 40
        btn_spacing = 8
        total_btn_w = len(self.button_labels) * btn_w + (len(self.button_labels) - 1) * btn_spacing
        bx = max(2, (self.width - total_btn_w) // 2)
        by = self.height - btn_h - 4
        for i, label in enumerate(self.button_labels):
            def make_handler(idx):
                return lambda w: self._on_btn(idx)
            btn = Button(label, x=bx + i * (btn_w + btn_spacing), y=by,
                         width=btn_w, height=btn_h, on_click=make_handler(i))
            self.add(btn)
            self._btn_widgets.append(btn)

    def _on_btn(self, idx):
        if self.on_button:
            self.on_button(self, idx)
        self.close()

    def show(self):
        """Show this dialog as a modal."""
        ui = get_ui()
        if ui:
            ui.show_modal(self)

    def close(self):
        """Close this dialog."""
        ui = get_ui()
        if ui:
            ui.close_modal()

    def content_x(self):
        return self.abs_x()

    def content_y(self):
        return self.abs_y()

    def draw(self):
        t = self.theme
        ax, ay = self.abs_x(), self.abs_y()
        font = t.font

        # Background
        pyxel.rect(ax, ay, self.width, self.height, t.dialog_bg)
        pyxel.rectb(ax, ay, self.width, self.height, t.dialog_border)

        # Title
        fh = t.font_height
        pad = max(2, fh // 4)
        title_h = fh + 3
        if self.title:
            pyxel.rect(ax + 1, ay + 1, self.width - 2, title_h - 2, t.panel_title_bg)
            pyxel.text(ax + pad, ay + (title_h - fh) // 2, self.title, t.panel_title_fg, font)

        # Message (word-wrapped)
        if self.message:
            available_px = self.width - pad * 2 - 4
            ty = ay + (title_h + 2 if self.title else 4)
            words = self.message.split(" ")
            line = ""
            for word in words:
                test = line + (" " if line else "") + word
                if text_width(test, font) > available_px:
                    pyxel.text(ax + 4, ty, line, t.text, font)
                    ty += t.font_height + 2
                    line = word
                else:
                    line = test
            if line:
                pyxel.text(ax + 4, ty, line, t.text, font)

        # Buttons
        for child in self.children:
            if child.visible:
                child.draw()

    def handle_key(self, key):
        if key == pyxel.KEY_ESCAPE:
            self.close()
        elif key == pyxel.KEY_RETURN:
            self._on_btn(0)


class Tooltip(Widget):
    """Tooltip overlay (usually managed by UI automatically via widget.tooltip).

    For manual tooltips, create and position yourself.

    Args:
        text: Tooltip text.
    """

    def __init__(self, text="", x=0, y=0, **kw):
        self.text = text
        w = text_width(text, None) + 4  # use default font for init sizing
        h = kw.pop("height", 0)
        super().__init__(x, y, w, h, **kw)

    def preferred_height(self):
        return self.height if self.height > 0 else self.theme.font_height + 3

    def draw(self):
        t = self.theme
        ax, ay = self.abs_x(), self.abs_y()
        fh = t.font_height
        pad = max(2, fh // 4)
        pyxel.rect(ax, ay, self.width, self.height, t.tooltip_bg)
        pyxel.rectb(ax, ay, self.width, self.height, t.tooltip_border)
        pyxel.text(ax + pad, ay + (self.height - fh) // 2, self.text, t.tooltip_fg, t.font)
