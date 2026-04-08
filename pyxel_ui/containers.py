"""Container widgets: Panel, ScrollView, TabView, DropDown, ListView."""
import pyxel
from .core import Widget, get_ui
from .utils import text_width, truncate_text

# Drag threshold in pixels before scroll starts (helps distinguish tap vs drag)
_DRAG_THRESHOLD = 3


class Panel(Widget):
    """Bordered container with optional title.

    Args:
        title: Panel title (shown in title bar).
        padding: Inner padding.
        bg: Background color (None = theme.panel_bg).
    """

    def __init__(self, title="", x=0, y=0, width=80, height=60, **kw):
        self.title = title
        self.padding = kw.get("padding", None)
        self.bg = kw.get("bg", None)
        super().__init__(x, y, width, height, **kw)

    def _pad(self):
        return self.padding if self.padding is not None else self.theme.padding

    def _title_h(self):
        return (self.theme.font_height + 3) if self.title else 0

    def content_x(self):
        return self.abs_x() + self._pad()

    def content_y(self):
        return self.abs_y() + self._title_h() + self._pad()

    def content_width(self):
        return self.width - self._pad() * 2

    def content_height(self):
        return self.height - self._title_h() - self._pad() * 2

    def draw(self):
        t = self.theme
        ax, ay = self.abs_x(), self.abs_y()
        bg = self.bg if self.bg is not None else t.panel_bg
        pyxel.rect(ax, ay, self.width, self.height, bg)
        pyxel.rectb(ax, ay, self.width, self.height, t.panel_border)
        if self.title:
            fh = t.font_height
            title_h = fh + 3
            pad = max(2, fh // 4)
            pyxel.rect(ax + 1, ay + 1, self.width - 2, title_h - 2, t.panel_title_bg)
            pyxel.text(ax + pad, ay + (title_h - fh) // 2, self.title, t.panel_title_fg, t.font)
        super().draw()


class ScrollView(Widget):
    """Scrollable content area.

    Add children that may be larger than the view.
    Supports mouse wheel and drag scrolling (touch-friendly).
    Drag only activates after moving beyond a threshold, so taps
    still propagate clicks to children.

    Args:
        scroll_x: Enable horizontal scrolling.
        scroll_y: Enable vertical scrolling.
        content_width: Total content width.
        content_height: Total content height.
    """

    def __init__(self, x=0, y=0, width=80, height=60, **kw):
        self.scroll_x_enabled = kw.get("scroll_x", False)
        self.scroll_y_enabled = kw.get("scroll_y", True)
        self._content_w = kw.get("content_width", 0)
        self._content_h = kw.get("content_height", 0)
        self._offset_x = 0
        self._offset_y = 0
        self._drag_start = None
        self._drag_offset = None
        self._dragging = False  # True once threshold exceeded
        self.scrollbar_w = 4
        super().__init__(x, y, width, height, **kw)

    def set_content_size(self, w, h):
        self._content_w = w
        self._content_h = h
        self._clamp_offset()

    def _clamp_offset(self):
        max_x = max(0, self._content_w - self.width + (self.scrollbar_w if self.scroll_y_enabled else 0))
        max_y = max(0, self._content_h - self.height + (self.scrollbar_w if self.scroll_x_enabled else 0))
        self._offset_x = max(0, min(self._offset_x, max_x))
        self._offset_y = max(0, min(self._offset_y, max_y))

    def content_x(self):
        return self.abs_x() - self._offset_x

    def content_y(self):
        return self.abs_y() - self._offset_y

    def handle_scroll(self, dx, dy):
        if self.scroll_y_enabled and dy != 0:
            self._offset_y -= dy * 8
            self._clamp_offset()
            return True
        if self.scroll_x_enabled and dx != 0:
            self._offset_x -= dx * 8
            self._clamp_offset()
            return True
        return False

    def handle_press(self, mx, my):
        super().handle_press(mx, my)
        self._drag_start = (mx, my)
        self._drag_offset = (self._offset_x, self._offset_y)
        self._dragging = False

    def handle_release(self, mx, my):
        if not self._dragging:
            # Was a tap, not a drag — propagate click to children
            super().handle_release(mx, my)
        self._drag_start = None
        self._dragging = False
        self._pressed = False

    def hit_test(self, mx, my):
        """Clip hit testing to the view bounds."""
        ax, ay = self.abs_x(), self.abs_y()
        if not self.visible or not (ax <= mx < ax + self.width and ay <= my < ay + self.height):
            return None
        for child in reversed(self.children):
            if child.visible and child.enabled:
                hit = child.hit_test(mx, my)
                # Only accept hits within the visible clip area
                if hit and ax <= mx < ax + self.width and ay <= my < ay + self.height:
                    return hit
        return self if self.enabled else None

    def update(self):
        # Drag scrolling (touch-friendly) with threshold
        if self._drag_start and pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
            mx, my = pyxel.mouse_x, pyxel.mouse_y
            dx = abs(mx - self._drag_start[0])
            dy = abs(my - self._drag_start[1])
            if not self._dragging and (dx > _DRAG_THRESHOLD or dy > _DRAG_THRESHOLD):
                self._dragging = True
            if self._dragging:
                if self.scroll_x_enabled:
                    self._offset_x = self._drag_offset[0] - (mx - self._drag_start[0])
                if self.scroll_y_enabled:
                    self._offset_y = self._drag_offset[1] - (my - self._drag_start[1])
                self._clamp_offset()
        elif self._drag_start:
            self._drag_start = None
            self._dragging = False
        super().update()

    def draw(self):
        ax, ay = self.abs_x(), self.abs_y()
        t = self.theme

        # Clip region with try/finally to always reset
        pyxel.clip(ax, ay, self.width, self.height)
        try:
            for child in self.children:
                if child.visible:
                    child.draw()
        finally:
            pyxel.clip()

        # Vertical scrollbar
        if self.scroll_y_enabled and self._content_h > self.height:
            sb_x = ax + self.width - self.scrollbar_w
            sb_h = self.height
            pyxel.rect(sb_x, ay, self.scrollbar_w, sb_h, t.scroll_track)
            vis_ratio = self.height / self._content_h
            thumb_h = max(4, int(sb_h * vis_ratio))
            max_off = self._content_h - self.height
            thumb_y = ay + int((sb_h - thumb_h) * self._offset_y / max_off) if max_off > 0 else ay
            col = t.scroll_thumb_hover if self._hovered else t.scroll_thumb
            pyxel.rect(sb_x, thumb_y, self.scrollbar_w, thumb_h, col)

        # Horizontal scrollbar
        if self.scroll_x_enabled and self._content_w > self.width:
            sb_y = ay + self.height - self.scrollbar_w
            sb_w = self.width
            pyxel.rect(ax, sb_y, sb_w, self.scrollbar_w, t.scroll_track)
            vis_ratio = self.width / self._content_w
            thumb_w = max(4, int(sb_w * vis_ratio))
            max_off = self._content_w - self.width
            thumb_x = ax + int((sb_w - thumb_w) * self._offset_x / max_off) if max_off > 0 else ax
            pyxel.rect(thumb_x, sb_y, thumb_w, self.scrollbar_w, t.scroll_thumb)


class TabView(Widget):
    """Tabbed container.

    Args:
        tabs: List of (title, content_widget) tuples.
        active: Initially active tab index.
        on_change: Callback ``fn(widget, tab_index)``.
    """

    def __init__(self, x=0, y=0, width=120, height=80, **kw):
        self._tabs = []
        self.active = kw.get("active", 0)
        self.on_change = kw.get("on_change", None)
        self._tab_height_override = None
        super().__init__(x, y, width, height, **kw)

    @property
    def tab_height(self):
        if self._tab_height_override is not None:
            return self._tab_height_override
        return self.theme.font_height + 4

    @tab_height.setter
    def tab_height(self, value):
        self._tab_height_override = value

    def add_tab(self, title, content):
        """Add a tab with title and content widget."""
        content.parent = self
        content.visible = len(self._tabs) == self.active
        self._tabs.append((title, content))
        self.mark_dirty()
        return content

    def set_active(self, index):
        if index == self.active or index < 0 or index >= len(self._tabs):
            return
        if self.active < len(self._tabs):
            self._tabs[self.active][1].visible = False
        self.active = index
        self._tabs[index][1].visible = True
        if self.on_change:
            self.on_change(self, index)

    def content_x(self):
        return self.abs_x() + 1

    def content_y(self):
        return self.abs_y() + self.tab_height + 1

    def content_width(self):
        return self.width - 2

    def content_height(self):
        return self.height - self.tab_height - 2

    def layout(self):
        cw, ch = self.content_width(), self.content_height()
        for _, content in self._tabs:
            # Positions relative to content area (content_x/y already offsets for tabs)
            content.x = 0
            content.y = 0
            content.width = cw
            content.height = ch
            if content._dirty:
                content.layout()
        self._dirty = False

    def handle_press(self, mx, my):
        super().handle_press(mx, my)
        ax, ay = self.abs_x(), self.abs_y()
        if ay <= my < ay + self.tab_height:
            fh = self.theme.font_height
            pad = max(2, fh // 4)
            tx = ax
            for i, (title, _) in enumerate(self._tabs):
                tw = text_width(title, self.theme.font) + pad * 2 + 4
                if tx <= mx < tx + tw:
                    self.set_active(i)
                    return
                tx += tw

    def hit_test(self, mx, my):
        if not self.visible or not self.contains(mx, my):
            return None
        # Check active tab content
        if self.active < len(self._tabs):
            content = self._tabs[self.active][1]
            if content.visible:
                hit = content.hit_test(mx, my)
                if hit:
                    return hit
        return self

    def find_focusable(self, forward=True):
        """Include active tab's focusable widgets in tab navigation."""
        result = []
        if self.focusable and self.visible and self.enabled:
            result.append(self)
        if self.active < len(self._tabs):
            content = self._tabs[self.active][1]
            if content.visible:
                result.extend(content.find_focusable(forward))
        return result

    def update(self):
        if self.active < len(self._tabs):
            content = self._tabs[self.active][1]
            if content.visible:
                content.update()

    def draw(self):
        t = self.theme
        ax, ay = self.abs_x(), self.abs_y()

        # Tab content area background
        pyxel.rect(ax, ay + self.tab_height, self.width,
                   self.height - self.tab_height, t.tab_active_bg)
        pyxel.rectb(ax, ay + self.tab_height, self.width,
                    self.height - self.tab_height, t.panel_border)

        # Tab headers
        fh = t.font_height
        pad = max(2, fh // 4)
        tx = ax
        for i, (title, _) in enumerate(self._tabs):
            tw = text_width(title, t.font) + pad * 2 + 4
            is_active = i == self.active
            bg = t.tab_active_bg if is_active else t.tab_inactive_bg
            fg = t.tab_active_fg if is_active else t.tab_inactive_fg
            pyxel.rect(tx, ay, tw, self.tab_height, bg)
            pyxel.rectb(tx, ay, tw, self.tab_height, t.panel_border)
            if is_active:
                pyxel.line(tx + 1, ay + self.tab_height, tx + tw - 2,
                           ay + self.tab_height, bg)
            pyxel.text(tx + pad + 2, ay + (self.tab_height - fh) // 2, title, fg, t.font)
            tx += tw

        # Draw active tab content
        if self.active < len(self._tabs):
            content = self._tabs[self.active][1]
            if content.visible:
                content.draw()


class DropDown(Widget):
    """Drop-down select list.

    Args:
        options: List of option strings.
        selected: Initially selected index.
        on_change: Callback ``fn(widget, index)``.
        placeholder: Text when nothing selected.
    """

    def __init__(self, options=None, x=0, y=0, width=60, **kw):
        self.options = options or []
        self.selected = kw.get("selected", -1)
        self.on_change = kw.get("on_change", None)
        self.placeholder = kw.get("placeholder", "Select...")
        self._open = False
        self._hover_idx = -1
        h = kw.pop("height", 0)
        kw.setdefault("focusable", True)
        super().__init__(x, y, width, h, **kw)

    @property
    def selected_text(self):
        if 0 <= self.selected < len(self.options):
            return self.options[self.selected]
        return self.placeholder

    def preferred_width(self):
        return self.width if self.width > 0 else 60

    def preferred_height(self):
        return self.height if self.height > 0 else self.theme.font_height + 6

    def _item_height(self):
        return self.theme.font_height + 3

    def _list_height(self):
        return len(self.options) * self._item_height() + 2

    def _open_dropdown(self):
        self._open = True
        ui = get_ui()
        if ui:
            ui.add_overlay(self)

    def _close_dropdown(self):
        self._open = False
        ui = get_ui()
        if ui:
            ui.remove_overlay(self)

    def handle_release(self, mx, my):
        if not self._pressed:
            return
        self._pressed = False
        ax, ay = self.abs_x(), self.abs_y()

        if self._open:
            list_y = ay + self.height
            list_h = self._list_height()
            if ax <= mx < ax + self.width and list_y <= my < list_y + list_h:
                idx = (my - list_y - 1) // self._item_height()
                if 0 <= idx < len(self.options):
                    self.selected = idx
                    if self.on_change:
                        self.on_change(self, idx)
            self._close_dropdown()
        else:
            if self.contains(mx, my):
                self._open_dropdown()

    def close(self):
        """Called when overlay is dismissed."""
        self._open = False

    def handle_key(self, key):
        if key == pyxel.KEY_RETURN or key == pyxel.KEY_SPACE:
            if self._open:
                self._close_dropdown()
            else:
                self._open_dropdown()
        elif key == pyxel.KEY_UP and self.selected > 0:
            self.selected -= 1
            if self.on_change:
                self.on_change(self, self.selected)
        elif key == pyxel.KEY_DOWN and self.selected < len(self.options) - 1:
            self.selected += 1
            if self.on_change:
                self.on_change(self, self.selected)
        elif key == pyxel.KEY_ESCAPE and self._open:
            self._close_dropdown()

    def contains(self, mx, my):
        ax, ay = self.abs_x(), self.abs_y()
        if ax <= mx < ax + self.width and ay <= my < ay + self.height:
            return True
        if self._open:
            list_y = ay + self.height
            list_h = self._list_height()
            if ax <= mx < ax + self.width and list_y <= my < list_y + list_h:
                return True
        return False

    def hit_test(self, mx, my):
        if self.contains(mx, my):
            return self
        return None

    def update(self):
        if self._open:
            ax, ay = self.abs_x(), self.abs_y()
            mx, my = pyxel.mouse_x, pyxel.mouse_y
            list_y = ay + self.height + 1
            if ax <= mx < ax + self.width:
                self._hover_idx = (my - list_y) // self._item_height()
            else:
                self._hover_idx = -1

    def draw(self):
        t = self.theme
        ax, ay = self.abs_x(), self.abs_y()
        fh = t.font_height
        pad = max(2, fh // 4)
        item_h = self._item_height()

        # Main box
        bg = t.dropdown_bg
        border = t.border_focus if self._focused else t.dropdown_border
        pyxel.rect(ax, ay, self.width, self.height, bg)
        pyxel.rectb(ax, ay, self.width, self.height, border)

        # Current value
        text = self.selected_text
        display = truncate_text(text, self.width - 12, t.font)
        pyxel.text(ax + pad, ay + (self.height - fh) // 2, display, t.dropdown_fg, t.font)

        # Arrow
        arrow_x = ax + self.width - 7
        arrow_y = ay + (self.height - 3) // 2
        if self._open:
            pyxel.tri(arrow_x, arrow_y + 2, arrow_x + 4, arrow_y + 2,
                      arrow_x + 2, arrow_y, t.dropdown_fg)
        else:
            pyxel.tri(arrow_x, arrow_y, arrow_x + 4, arrow_y,
                      arrow_x + 2, arrow_y + 2, t.dropdown_fg)

        # Expanded list
        if self._open:
            list_y = ay + self.height
            list_h = self._list_height()
            pyxel.rect(ax, list_y, self.width, list_h, t.dropdown_bg)
            pyxel.rectb(ax, list_y, self.width, list_h, t.dropdown_border)
            for i, opt in enumerate(self.options):
                iy = list_y + 1 + i * item_h
                if i == self._hover_idx:
                    pyxel.rect(ax + 1, iy, self.width - 2, item_h, t.dropdown_hover)
                col = t.primary if i == self.selected else t.dropdown_fg
                opt_display = truncate_text(opt, self.width - pad * 2, t.font)
                pyxel.text(ax + pad, iy + (item_h - fh) // 2, opt_display, col, t.font)


class ListView(Widget):
    """Scrollable list of selectable items.

    Args:
        items: List of display strings.
        selected: Selected index (-1 = none).
        multi_select: Allow multiple selection.
        on_select: Callback ``fn(widget, index)``.
        item_height: Height of each item row.
    """

    def __init__(self, items=None, x=0, y=0, width=80, height=60, **kw):
        self.items = items or []
        self.selected = kw.get("selected", -1)
        self.multi_select = kw.get("multi_select", False)
        self._selected_set = set()
        self.on_select = kw.get("on_select", None)
        self._item_h = kw.get("item_height", 0)
        self._scroll = 0
        self._hover_idx = -1
        kw.setdefault("focusable", True)
        super().__init__(x, y, width, height, **kw)
        if self.selected >= 0:
            self._selected_set.add(self.selected)

    def _get_item_h(self):
        if self._item_h > 0:
            return self._item_h
        return self.theme.font_height + 3

    def preferred_width(self):
        return self.width if self.width > 0 else 80

    def preferred_height(self):
        return self.height if self.height > 0 else 60

    def _visible_count(self):
        return max(1, self.height // self._get_item_h())

    def _max_scroll(self):
        return max(0, len(self.items) - self._visible_count())

    def handle_scroll(self, dx, dy):
        if dy != 0:
            self._scroll -= dy
            self._scroll = max(0, min(self._scroll, self._max_scroll()))
            return True
        return False

    def handle_release(self, mx, my):
        if not self._pressed or not self.contains(mx, my):
            self._pressed = False
            return
        self._pressed = False
        ax, ay = self.abs_x(), self.abs_y()
        idx = self._scroll + (my - ay) // self._get_item_h()
        if 0 <= idx < len(self.items):
            if self.multi_select:
                if idx in self._selected_set:
                    self._selected_set.discard(idx)
                else:
                    self._selected_set.add(idx)
            else:
                self.selected = idx
                self._selected_set = {idx}
            if self.on_select:
                self.on_select(self, idx)

    def handle_key(self, key):
        if key == pyxel.KEY_UP and self.selected > 0:
            self.selected -= 1
            if not self.multi_select:
                self._selected_set = {self.selected}
            if self.selected < self._scroll:
                self._scroll = self.selected
            if self.on_select:
                self.on_select(self, self.selected)
        elif key == pyxel.KEY_DOWN and self.selected < len(self.items) - 1:
            self.selected += 1
            if not self.multi_select:
                self._selected_set = {self.selected}
            if self.selected >= self._scroll + self._visible_count():
                self._scroll = self.selected - self._visible_count() + 1
            if self.on_select:
                self.on_select(self, self.selected)
        elif key == pyxel.KEY_SPACE and self.multi_select:
            # Toggle selection in multi-select mode
            if self.selected in self._selected_set:
                self._selected_set.discard(self.selected)
            else:
                self._selected_set.add(self.selected)

    def update(self):
        if self._hovered:
            ax, ay = self.abs_x(), self.abs_y()
            self._hover_idx = self._scroll + (pyxel.mouse_y - ay) // self._get_item_h()
        else:
            self._hover_idx = -1

    def draw(self):
        t = self.theme
        ax, ay = self.abs_x(), self.abs_y()
        pyxel.rect(ax, ay, self.width, self.height, t.list_bg)
        pyxel.rectb(ax, ay, self.width, self.height, t.panel_border)

        pyxel.clip(ax + 1, ay + 1, self.width - 2, self.height - 2)
        try:
            fh = t.font_height
            pad = max(2, fh // 4)
            ih = self._get_item_h()
            vis = self._visible_count()
            available_px = self.width - pad * 2 - 2
            for i in range(vis):
                idx = self._scroll + i
                if idx >= len(self.items):
                    break
                iy = ay + i * ih
                if idx in self._selected_set:
                    pyxel.rect(ax + 1, iy, self.width - 2, ih, t.list_selected_bg)
                    col = t.list_selected_fg
                elif idx == self._hover_idx:
                    pyxel.rect(ax + 1, iy, self.width - 2, ih, t.list_hover_bg)
                    col = t.list_item
                else:
                    col = t.list_item
                item_text = truncate_text(self.items[idx], available_px, t.font)
                pyxel.text(ax + pad + 1, iy + (ih - fh) // 2, item_text, col, t.font)
        finally:
            pyxel.clip()

        # Scrollbar
        if len(self.items) > vis:
            sb_x = ax + self.width - 3
            ratio = vis / len(self.items)
            thumb_h = max(4, int(self.height * ratio))
            max_s = self._max_scroll()
            thumb_y = ay + int((self.height - thumb_h) * self._scroll / max_s) if max_s > 0 else ay
            pyxel.rect(sb_x, ay, 2, self.height, t.scroll_track)
            pyxel.rect(sb_x, thumb_y, 2, thumb_h, t.scroll_thumb)
