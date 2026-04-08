"""Core module: UI manager, Widget base class, input handling."""
import pyxel
from .theme import Theme, THEME_DARK
from .utils import text_width

# Module-level reference to active UI instance
_active_ui = None


def get_ui():
    """Get the active UI instance."""
    return _active_ui


class Widget:
    """Base class for all UI widgets.

    Coordinates are relative to the parent's content area.
    Layout containers override x/y during layout passes.
    """

    _id_counter = 0

    def __init__(self, x=0, y=0, width=0, height=0, **kw):
        Widget._id_counter += 1
        self.id = Widget._id_counter
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = kw.get("visible", True)
        self.enabled = kw.get("enabled", True)
        self.focusable = kw.get("focusable", False)
        self.flex = kw.get("flex", 0)
        self.tooltip_text = kw.get("tooltip", None)
        self.parent = None
        self.children = []
        self._theme = kw.get("theme", None)
        self._hovered = False
        self._pressed = False
        self._focused = False
        self._dirty = True  # needs layout recalc

        # Callbacks
        self.on_click = kw.get("on_click", None)
        self.on_mouse_enter = kw.get("on_mouse_enter", None)
        self.on_mouse_leave = kw.get("on_mouse_leave", None)
        self.on_focus = kw.get("on_focus", None)
        self.on_blur = kw.get("on_blur", None)

    def __repr__(self):
        name = type(self).__name__
        return f"<{name} id={self.id} ({self.x},{self.y} {self.width}x{self.height})>"

    @property
    def theme(self):
        if self._theme:
            return self._theme
        if self.parent:
            return self.parent.theme
        ui = get_ui()
        return ui.theme if ui else THEME_DARK

    @theme.setter
    def theme(self, value):
        self._theme = value

    def abs_x(self):
        """Absolute screen X coordinate."""
        px = self.parent.content_x() if self.parent else 0
        return self.x + px

    def abs_y(self):
        """Absolute screen Y coordinate."""
        py = self.parent.content_y() if self.parent else 0
        return self.y + py

    def content_x(self):
        """X where children content starts (after padding)."""
        return self.abs_x()

    def content_y(self):
        """Y where children content starts (after padding)."""
        return self.abs_y()

    def content_width(self):
        """Available width for children."""
        return self.width

    def content_height(self):
        """Available height for children."""
        return self.height

    def contains(self, mx, my):
        """Check if screen point is inside this widget."""
        ax, ay = self.abs_x(), self.abs_y()
        return ax <= mx < ax + self.width and ay <= my < ay + self.height

    def add(self, child):
        """Add a child widget."""
        child.parent = self
        self.children.append(child)
        self.mark_dirty()
        return child

    def remove(self, child):
        """Remove a child widget."""
        if child in self.children:
            self.children.remove(child)
            child.parent = None
            self.mark_dirty()

    def clear(self):
        """Remove all children."""
        for c in self.children:
            c.parent = None
        self.children.clear()
        self.mark_dirty()

    def mark_dirty(self):
        """Mark this widget as needing layout recalculation."""
        self._dirty = True
        if self.parent:
            self.parent.mark_dirty()

    def layout(self):
        """Recalculate layout. Override in containers."""
        self._dirty = False
        for child in self.children:
            if child._dirty:
                child.layout()

    def preferred_width(self):
        """Preferred width for auto-sizing."""
        return self.width

    def preferred_height(self):
        """Preferred height for auto-sizing."""
        return self.height

    def update(self):
        """Update logic. Called each frame."""
        for child in self.children:
            if child.visible:
                child.update()

    def draw(self):
        """Draw this widget. Override in subclasses."""
        for child in self.children:
            if child.visible:
                child.draw()

    def handle_mouse_enter(self):
        self._hovered = True
        if self.on_mouse_enter:
            self.on_mouse_enter(self)

    def handle_mouse_leave(self):
        self._hovered = False
        self._pressed = False
        if self.on_mouse_leave:
            self.on_mouse_leave(self)

    def handle_press(self, mx, my):
        self._pressed = True

    def handle_release(self, mx, my):
        was_pressed = self._pressed
        self._pressed = False
        if was_pressed and self.contains(mx, my) and self.on_click:
            self.on_click(self)

    def handle_focus(self):
        self._focused = True
        if self.on_focus:
            self.on_focus(self)

    def handle_blur(self):
        self._focused = False
        if self.on_blur:
            self.on_blur(self)

    def handle_key(self, key):
        """Handle keyboard input when focused."""
        pass

    def handle_text(self, text):
        """Handle text input when focused."""
        pass

    def handle_scroll(self, dx, dy):
        """Handle scroll wheel. Return True if consumed."""
        return False

    def hit_test(self, mx, my):
        """Find the deepest visible+enabled widget at (mx, my).

        Returns the widget or None. Checks children in reverse order
        (last drawn = on top).
        """
        if not self.visible or not self.contains(mx, my):
            return None
        for child in reversed(self.children):
            if child.visible and child.enabled:
                hit = child.hit_test(mx, my)
                if hit:
                    return hit
        return self if self.enabled else None

    def find_focusable(self, forward=True):
        """Collect all focusable descendants in tree order."""
        result = []
        if self.focusable and self.visible and self.enabled:
            result.append(self)
        for child in self.children:
            result.extend(child.find_focusable(forward))
        return result


class UI:
    """Main UI manager. Handles input, focus, and the widget tree.

    Usage::

        ui = UI(theme=THEME_DARK)
        ui.add(Button("Click me", on_click=my_handler))

        # In your Pyxel update/draw:
        def update(): ui.update()
        def draw(): ui.draw()
    """

    def __init__(self, theme=None):
        global _active_ui
        _active_ui = self
        self._theme = theme or THEME_DARK
        self.root = Widget(x=0, y=0, width=pyxel.width, height=pyxel.height)
        self.root._theme = self._theme
        self._focus = None
        self._hover = None
        self._pressed_widget = None
        self._overlays = []  # dropdowns, tooltips, modals
        self._prev_mx = 0
        self._prev_my = 0
        self._prev_btn = False
        self._tooltip_widget = None
        self._tooltip_timer = 0
        self._modal = None  # active modal blocks input to rest

    @property
    def theme(self):
        return self._theme

    @theme.setter
    def theme(self, value):
        """Set theme and propagate to root."""
        self._theme = value
        self.root._theme = value

    def add(self, widget):
        """Add a widget to the root."""
        return self.root.add(widget)

    def remove(self, widget):
        """Remove a widget from the root."""
        self.root.remove(widget)

    def focus(self, widget):
        """Set keyboard focus to a widget."""
        if self._focus is widget:
            return
        if self._focus:
            self._focus.handle_blur()
        self._focus = widget
        if widget:
            widget.handle_focus()

    def add_overlay(self, widget):
        """Add an overlay widget (dropdown, tooltip, modal)."""
        if widget not in self._overlays:
            self._overlays.append(widget)

    def remove_overlay(self, widget):
        """Remove an overlay."""
        if widget in self._overlays:
            self._overlays.remove(widget)
        if self._modal is widget:
            self._modal = None

    def show_modal(self, widget):
        """Show widget as a modal overlay."""
        self._modal = widget
        self.add_overlay(widget)
        self.focus(widget)

    def close_modal(self):
        """Close the current modal."""
        if self._modal:
            self.remove_overlay(self._modal)
            self._modal = None

    def update(self):
        """Process input and update all widgets. Call in pyxel update()."""
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        btn_now = pyxel.btn(pyxel.MOUSE_BUTTON_LEFT)
        btn_press = pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
        btn_release = pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT)
        scroll = pyxel.mouse_wheel

        # Hit test: overlays first, then root
        hit = None
        for overlay in reversed(self._overlays):
            hit = overlay.hit_test(mx, my)
            if hit:
                break
        if not hit and not self._modal:
            hit = self.root.hit_test(mx, my)

        # Hover tracking
        if hit is not self._hover:
            if self._hover:
                self._hover.handle_mouse_leave()
            self._hover = hit
            if hit:
                hit.handle_mouse_enter()
            self._tooltip_timer = 0
            self._tooltip_widget = None

        # Tooltip
        if self._hover and self._hover.tooltip_text:
            self._tooltip_timer += 1
            if self._tooltip_timer > 20:
                self._tooltip_widget = self._hover
        else:
            self._tooltip_timer = 0
            self._tooltip_widget = None

        # Press
        if btn_press:
            if hit:
                hit.handle_press(mx, my)
                self._pressed_widget = hit
                if hit.focusable:
                    self.focus(hit)
            else:
                self.focus(None)
                # Close overlays on outside click
                self._close_non_modal_overlays()

        # Release
        if btn_release:
            if self._pressed_widget:
                self._pressed_widget.handle_release(mx, my)
                self._pressed_widget = None

        # Scroll
        if scroll != 0 and self._hover:
            target = self._hover
            while target:
                if target.handle_scroll(0, scroll):
                    break
                target = target.parent

        # Tab navigation
        if pyxel.btnp(pyxel.KEY_TAB):
            self._cycle_focus(not pyxel.btn(pyxel.KEY_SHIFT))

        # Keyboard input to focused widget
        if self._focus:
            self._dispatch_keys()

        # Layout pass
        if self.root._dirty:
            self.root.width = pyxel.width
            self.root.height = pyxel.height
            self.root.layout()

        # Update widgets
        self.root.update()
        for overlay in self._overlays:
            overlay.update()

        self._prev_mx, self._prev_my = mx, my
        self._prev_btn = btn_now

    def draw(self):
        """Draw all widgets. Call in pyxel draw()."""
        self.root.draw()

        # Overlays
        for overlay in self._overlays:
            # Modal backdrop
            if overlay is self._modal:
                pyxel.dither(0.5)
                pyxel.rect(0, 0, pyxel.width, pyxel.height, self.theme.overlay)
                pyxel.dither(1.0)
            overlay.draw()

        # Tooltip
        if self._tooltip_widget:
            self._draw_tooltip()

    def _draw_tooltip(self):
        w = self._tooltip_widget
        text = w.tooltip_text
        tw = text_width(text, self.theme.font) + 4
        th = self.theme.font_height + 3
        tx = min(pyxel.mouse_x + 4, pyxel.width - tw - 1)
        ty = max(pyxel.mouse_y - th - 2, 0)
        t = self.theme
        pyxel.rect(tx, ty, tw, th, t.tooltip_bg)
        pyxel.rectb(tx, ty, tw, th, t.tooltip_border)
        pyxel.text(tx + 2, ty + 2, text, t.tooltip_fg)

    def _close_non_modal_overlays(self):
        to_remove = [o for o in self._overlays if o is not self._modal]
        for o in to_remove:
            self._overlays.remove(o)
            if hasattr(o, "close"):
                o.close()

    def _cycle_focus(self, forward):
        all_focusable = self.root.find_focusable(forward)
        # Also include modal focusables
        if self._modal:
            all_focusable = self._modal.find_focusable(forward)
        if not all_focusable:
            return
        if self._focus in all_focusable:
            idx = all_focusable.index(self._focus)
            next_idx = (idx + (1 if forward else -1)) % len(all_focusable)
        else:
            next_idx = 0 if forward else -1
        self.focus(all_focusable[next_idx])

    def _dispatch_keys(self):
        w = self._focus
        if not w:
            return

        # Check if focused widget accepts text input
        accepts_text = hasattr(w, "_cursor")  # TextInput signature

        # Printable characters — only sent to text-accepting widgets
        if accepts_text:
            shift = pyxel.btn(pyxel.KEY_SHIFT)
            for key in range(pyxel.KEY_A, pyxel.KEY_Z + 1):
                if pyxel.btnp(key, 8, 2):
                    ch = chr(ord("a") + key - pyxel.KEY_A)
                    if shift:
                        ch = ch.upper()
                    w.handle_text(ch)

            # Shift+digit symbols
            _SHIFT_DIGITS = ")!@#$%^&*("
            for key in range(pyxel.KEY_0, pyxel.KEY_9 + 1):
                if pyxel.btnp(key, 8, 2):
                    idx = key - pyxel.KEY_0
                    ch = _SHIFT_DIGITS[idx] if shift else chr(ord("0") + idx)
                    w.handle_text(ch)

            if pyxel.btnp(pyxel.KEY_SPACE, 8, 2):
                w.handle_text(" ")
            if pyxel.btnp(pyxel.KEY_PERIOD, 8, 2):
                w.handle_text(">" if shift else ".")
            if pyxel.btnp(pyxel.KEY_COMMA, 8, 2):
                w.handle_text("<" if shift else ",")
            if pyxel.btnp(pyxel.KEY_MINUS, 8, 2):
                w.handle_text("_" if shift else "-")
            if pyxel.btnp(pyxel.KEY_SLASH, 8, 2):
                w.handle_text("?" if shift else "/")
            if pyxel.btnp(pyxel.KEY_SEMICOLON, 8, 2):
                w.handle_text(":" if shift else ";")
            if pyxel.btnp(pyxel.KEY_QUOTE, 8, 2):
                w.handle_text('"' if shift else "'")
            if pyxel.btnp(pyxel.KEY_LEFTBRACKET, 8, 2):
                w.handle_text("{" if shift else "[")
            if pyxel.btnp(pyxel.KEY_RIGHTBRACKET, 8, 2):
                w.handle_text("}" if shift else "]")
            if pyxel.btnp(pyxel.KEY_BACKSLASH, 8, 2):
                w.handle_text("|" if shift else "\\")
            if pyxel.btnp(pyxel.KEY_EQUALS, 8, 2):
                w.handle_text("+" if shift else "=")
            if pyxel.btnp(pyxel.KEY_BACKQUOTE, 8, 2):
                w.handle_text("~" if shift else "`")

        # Special keys — always dispatched
        for key in [pyxel.KEY_BACKSPACE, pyxel.KEY_DELETE, pyxel.KEY_RETURN,
                     pyxel.KEY_LEFT, pyxel.KEY_RIGHT, pyxel.KEY_HOME,
                     pyxel.KEY_END, pyxel.KEY_ESCAPE, pyxel.KEY_UP,
                     pyxel.KEY_DOWN, pyxel.KEY_SPACE]:
            if pyxel.btnp(key, 8, 2):
                w.handle_key(key)
