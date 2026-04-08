"""Extra widgets: Tags, MaskedInput, ColorPicker, Accordion, Pagination, SegmentedControl."""
import pyxel
from .core import Widget, get_ui
from .layout import Row
from .utils import text_width, text_x_at


class Tags(Widget):
    """Editable tag/chip list with add and remove.

    Args:
        tags: List of tag strings.
        on_change: Callback ``fn(widget, tags_list)``.
        max_tags: Maximum number of tags (0 = unlimited).
        removable: Whether tags can be removed by clicking X.
        color: Tag background color (None = theme.primary).
    """

    def __init__(self, tags=None, x=0, y=0, width=120, **kw):
        self._tags = list(tags or [])
        self.on_change = kw.get("on_change", None)
        self.max_tags = kw.get("max_tags", 0)
        self.removable = kw.get("removable", True)
        self.color = kw.get("color", None)
        h = kw.pop("height", 0)
        # Store width before super().__init__ so _calc_height can use it
        self._init_width = width
        super().__init__(x, y, width, h or self._calc_height(), **kw)

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, value):
        self._tags = list(value)
        self.height = self._calc_height()
        self.mark_dirty()

    def _tag_width(self, tag):
        font = self.theme.font if hasattr(self, '_theme') else None
        w = text_width(tag, font) + 4
        if self.removable:
            w += 8  # space for X
        return w

    def _tag_height(self):
        try:
            fh = self.theme.font_height
        except AttributeError:
            fh = 6
        return fh + 3

    def _calc_height(self):
        th = self._tag_height()
        if not self._tags:
            return th
        rows = 1
        x = 0
        sp = 2
        w = self.width if hasattr(self, 'width') and self.width > 0 else self._init_width
        for tag in self._tags:
            tw = self._tag_width(tag) + sp
            if x + tw > w and x > 0:
                rows += 1
                x = 0
            x += tw
        return rows * th + (rows - 1) * 2

    def preferred_width(self):
        return self.width

    def preferred_height(self):
        return self._calc_height()

    def add_tag(self, tag):
        if self.max_tags > 0 and len(self._tags) >= self.max_tags:
            return
        if tag and tag not in self._tags:
            self._tags.append(tag)
            self.height = self._calc_height()
            self.mark_dirty()
            if self.on_change:
                self.on_change(self, self._tags)

    def remove_tag(self, tag):
        if tag in self._tags:
            self._tags.remove(tag)
            self.height = self._calc_height()
            self.mark_dirty()
            if self.on_change:
                self.on_change(self, self._tags)

    def handle_release(self, mx, my):
        if self._pressed and self.removable and self.contains(mx, my):
            ax, ay = self.abs_x(), self.abs_y()
            th = self._tag_height()
            tx, ty = ax, ay
            sp = 2
            w = self.width if hasattr(self, 'width') and self.width > 0 else self._init_width
            for tag in self._tags:
                tw = self._tag_width(tag)
                if tx + tw + sp > ax + w and tx > ax:
                    tx = ax
                    ty += th + 2
                x_btn_x = tx + tw - 8
                if x_btn_x <= mx < tx + tw and ty <= my < ty + th:
                    self.remove_tag(tag)
                    super().handle_release(mx, my)
                    return
                tx += tw + sp
        super().handle_release(mx, my)

    def draw(self):
        t = self.theme
        ax, ay = self.abs_x(), self.abs_y()
        fh = t.font_height
        th = self._tag_height()
        pad = max(2, fh // 4)
        bg = self.color if self.color is not None else t.primary
        tx, ty = ax, ay
        sp = 2

        for tag in self._tags:
            tw = self._tag_width(tag)
            if tx + tw + sp > ax + self.width and tx > ax:
                tx = ax
                ty += th + 2
            pyxel.rect(tx, ty, tw, th, bg)
            pyxel.text(tx + pad, ty + (th - fh) // 2, tag, t.btn_fg, t.font)
            if self.removable:
                # X button
                xx = tx + tw - 7
                pyxel.text(xx, ty + (th - fh) // 2, "x", t.danger, t.font)
            tx += tw + sp


class MaskedInput(Widget):
    """Text input with display mask/formatting.

    The mask defines the display format. ``#`` = digit, ``A`` = letter,
    ``*`` = any char. Other chars are literals.

    Args:
        mask: Format mask, e.g. ``"####-####-####-####"`` for credit card.
        on_change: Callback ``fn(widget, raw_value)``.
        placeholder_char: Character shown for unfilled positions.
    """

    def __init__(self, mask="", x=0, y=0, **kw):
        self.mask = mask
        self.on_change = kw.get("on_change", None)
        self.placeholder_char = kw.get("placeholder_char", "_")
        self._raw = ""  # only user-entered chars (no literals)
        self._cursor_blink = 0
        w = kw.pop("width", 0)
        h = kw.pop("height", 0)
        kw.setdefault("focusable", True)
        super().__init__(x, y, w, h, **kw)

    @property
    def value(self):
        """The raw unmasked value (digits/letters only)."""
        return self._raw

    @value.setter
    def value(self, v):
        self._raw = v[:self._max_input_len()]

    def _max_input_len(self):
        return sum(1 for c in self.mask if c in "#A*")

    def _format_display(self):
        result = []
        ri = 0
        for mc in self.mask:
            if mc in "#A*":
                if ri < len(self._raw):
                    result.append(self._raw[ri])
                    ri += 1
                else:
                    result.append(self.placeholder_char)
            else:
                result.append(mc)
        return "".join(result)

    def _accepts_char(self, ch, mask_char):
        if mask_char == "#":
            return ch.isdigit()
        elif mask_char == "A":
            return ch.isalpha()
        elif mask_char == "*":
            return True
        return False

    def _current_mask_pos(self):
        """Find the mask position for the next input."""
        ri = 0
        for i, mc in enumerate(self.mask):
            if mc in "#A*":
                if ri == len(self._raw):
                    return i
                ri += 1
        return len(self.mask)

    def handle_text(self, ch):
        if len(self._raw) >= self._max_input_len():
            return
        # Find next input slot in mask
        ri = 0
        for mc in self.mask:
            if mc in "#A*":
                if ri == len(self._raw):
                    if self._accepts_char(ch, mc):
                        self._raw += ch
                        self._cursor_blink = 0
                        if self.on_change:
                            self.on_change(self, self._raw)
                    return
                ri += 1

    def handle_key(self, key):
        if key == pyxel.KEY_BACKSPACE and self._raw:
            self._raw = self._raw[:-1]
            self._cursor_blink = 0
            if self.on_change:
                self.on_change(self, self._raw)

    def update(self):
        if self._focused:
            self._cursor_blink += 1

    def preferred_width(self):
        return self.width if self.width > 0 else text_width(self.mask, self.theme.font) + 6

    def preferred_height(self):
        return self.height if self.height > 0 else self.theme.font_height + 6

    def draw(self):
        t = self.theme
        ax, ay = self.abs_x(), self.abs_y()
        font = t.font
        fh = t.font_height
        pad = max(2, fh // 4)
        ty = ay + (self.height - fh) // 2

        pyxel.rect(ax, ay, self.width, self.height, t.input_bg)
        pyxel.rectb(ax, ay, self.width, self.height,
                    t.input_focus if self._focused else t.input_border)

        display = self._format_display()
        pyxel.text(ax + pad, ty, display, t.input_fg, font)

        # Cursor at current position
        if self._focused and (self._cursor_blink % 30) < 20:
            # Find display position of cursor
            ri = 0
            cursor_idx = 0
            for mc in self.mask:
                if mc in "#A*":
                    if ri == len(self._raw):
                        break
                    ri += 1
                cursor_idx += 1
            cx = ax + pad + text_x_at(display, cursor_idx, font)
            pyxel.line(cx, ay + pad, cx, ay + self.height - pad - 1, t.input_cursor)


class ColorPicker(Widget):
    """Pyxel palette color picker (16 or 256 colors).

    Args:
        selected: Initially selected color index.
        colors: Number of colors to show (default 16).
        cell_size: Size of each color swatch.
        on_change: Callback ``fn(widget, color_index)``.
    """

    def __init__(self, x=0, y=0, **kw):
        self.selected = kw.get("selected", 0)
        self.num_colors = kw.get("colors", 16)
        self.cell_size = kw.get("cell_size", 8)
        self.on_change = kw.get("on_change", None)
        self._hover_color = -1
        cols = min(self.num_colors, 16)
        rows = (self.num_colors + cols - 1) // cols
        sp = 1
        w = kw.pop("width", cols * (self.cell_size + sp) + sp)
        h = kw.pop("height", rows * (self.cell_size + sp) + sp)
        kw.setdefault("focusable", True)
        super().__init__(x, y, w, h, **kw)

    def _cols(self):
        return min(self.num_colors, 16)

    def preferred_width(self):
        sp = 1
        return self._cols() * (self.cell_size + sp) + sp

    def preferred_height(self):
        sp = 1
        rows = (self.num_colors + self._cols() - 1) // self._cols()
        return rows * (self.cell_size + sp) + sp

    def _pos_to_color(self, mx, my):
        ax, ay = self.abs_x(), self.abs_y()
        sp = 1
        cs = self.cell_size
        cols = self._cols()
        col = (mx - ax - sp) // (cs + sp)
        row = (my - ay - sp) // (cs + sp)
        if 0 <= col < cols:
            idx = row * cols + col
            if 0 <= idx < self.num_colors:
                return idx
        return -1

    def handle_release(self, mx, my):
        if self._pressed and self.contains(mx, my):
            idx = self._pos_to_color(mx, my)
            if idx >= 0:
                self.selected = idx
                if self.on_change:
                    self.on_change(self, idx)
        super().handle_release(mx, my)

    def handle_key(self, key):
        old = self.selected
        cols = self._cols()
        if key == pyxel.KEY_RIGHT:
            self.selected = min(self.num_colors - 1, self.selected + 1)
        elif key == pyxel.KEY_LEFT:
            self.selected = max(0, self.selected - 1)
        elif key == pyxel.KEY_DOWN:
            self.selected = min(self.num_colors - 1, self.selected + cols)
        elif key == pyxel.KEY_UP:
            self.selected = max(0, self.selected - cols)
        if self.selected != old and self.on_change:
            self.on_change(self, self.selected)

    def update(self):
        if self._hovered:
            self._hover_color = self._pos_to_color(pyxel.mouse_x, pyxel.mouse_y)
        else:
            self._hover_color = -1

    def draw(self):
        t = self.theme
        ax, ay = self.abs_x(), self.abs_y()
        sp = 1
        cs = self.cell_size
        cols = self._cols()

        pyxel.rect(ax, ay, self.width, self.height, t.surface)

        for i in range(self.num_colors):
            col = i % cols
            row = i // cols
            cx = ax + sp + col * (cs + sp)
            cy = ay + sp + row * (cs + sp)
            pyxel.rect(cx, cy, cs, cs, i)

            if i == self.selected:
                pyxel.rectb(cx - 1, cy - 1, cs + 2, cs + 2, t.text)
            elif i == self._hover_color:
                pyxel.rectb(cx - 1, cy - 1, cs + 2, cs + 2, t.border_focus)


class Accordion(Widget):
    """Collapsible sections.

    Args:
        sections: List of (title, content_widget) tuples.
        multi_open: Allow multiple sections open at once.
        header_height: Height of each section header.
    """

    def __init__(self, x=0, y=0, width=120, **kw):
        self._sections = []
        self.multi_open = kw.get("multi_open", False)
        self._header_height_override = kw.get("header_height", 0)
        h = kw.pop("height", 0)
        super().__init__(x, y, width, h, **kw)

    @property
    def header_height(self):
        if self._header_height_override > 0:
            return self._header_height_override
        return self.theme.font_height + 5

    @header_height.setter
    def header_height(self, value):
        self._header_height_override = value

    def add_section(self, title, content, opened=False):
        content.parent = self
        content.visible = opened
        self._sections.append({"title": title, "content": content, "open": opened})
        self._recalc_height()
        self.mark_dirty()
        return content

    def _recalc_height(self):
        h = 0
        for s in self._sections:
            h += self.header_height
            if s["open"]:
                h += s["content"].preferred_height()
        self.height = max(self.header_height, h)

    def toggle_section(self, index):
        if not self.multi_open:
            for i, s in enumerate(self._sections):
                if i != index:
                    s["open"] = False
                    s["content"].visible = False
        s = self._sections[index]
        s["open"] = not s["open"]
        s["content"].visible = s["open"]
        self._recalc_height()
        self.mark_dirty()

    def preferred_height(self):
        self._recalc_height()
        return self.height

    def layout(self):
        y = 0
        for s in self._sections:
            y += self.header_height
            c = s["content"]
            c.x = 1
            c.y = y
            c.width = self.width - 2
            if s["open"]:
                if c._dirty:
                    c.layout()
                y += c.preferred_height()
        self._dirty = False

    def handle_press(self, mx, my):
        super().handle_press(mx, my)
        ax, ay = self.abs_x(), self.abs_y()
        y = ay
        for i, s in enumerate(self._sections):
            if y <= my < y + self.header_height and ax <= mx < ax + self.width:
                self.toggle_section(i)
                return
            y += self.header_height
            if s["open"]:
                y += s["content"].preferred_height()

    def hit_test(self, mx, my):
        if not self.visible or not self.contains(mx, my):
            return None
        # Check open section contents
        for s in self._sections:
            if s["open"] and s["content"].visible:
                hit = s["content"].hit_test(mx, my)
                if hit:
                    return hit
        return self

    def find_focusable(self, forward=True):
        result = []
        for s in self._sections:
            if s["open"] and s["content"].visible:
                result.extend(s["content"].find_focusable(forward))
        return result

    def update(self):
        for s in self._sections:
            if s["open"] and s["content"].visible:
                s["content"].update()

    def draw(self):
        t = self.theme
        ax, ay = self.abs_x(), self.abs_y()
        fh = t.font_height
        pad = max(2, fh // 4)
        hh = self.header_height
        text_y_off = (hh - fh) // 2
        y = ay

        for s in self._sections:
            # Header
            bg = t.panel_title_bg if s["open"] else t.surface
            pyxel.rect(ax, y, self.width, hh, bg)
            pyxel.rectb(ax, y, self.width, hh, t.panel_border)
            arrow = "v" if s["open"] else ">"
            pyxel.text(ax + pad, y + text_y_off, arrow, t.text_dim, t.font)
            pyxel.text(ax + pad + 8, y + text_y_off, s["title"], t.panel_title_fg if s["open"] else t.text, t.font)
            y += hh

            # Content
            if s["open"] and s["content"].visible:
                pyxel.rect(ax + 1, y, self.width - 2, s["content"].preferred_height(), t.panel_bg)
                s["content"].draw()
                y += s["content"].preferred_height()


class Pagination(Widget):
    """Page navigation control.

    Args:
        total_pages: Total number of pages.
        current: Current page (1-based).
        on_change: Callback ``fn(widget, page)``.
        max_visible: Max page buttons to show.
    """

    def __init__(self, total_pages=1, x=0, y=0, **kw):
        self.total_pages = max(1, total_pages)
        self.current = kw.get("current", 1)
        self.on_change = kw.get("on_change", None)
        self.max_visible = kw.get("max_visible", 5)
        w = kw.pop("width", 0)
        h = kw.pop("height", 0)
        kw.setdefault("focusable", True)
        super().__init__(x, y, w or self._calc_width_init(), h, **kw)

    def _btn_size(self):
        return self.theme.font_height + 5

    def _calc_width_init(self):
        # < [1] [2] [3] [4] [5] > (initial estimate with default font)
        n = min(self.total_pages, self.max_visible)
        return 12 + n * 12 + 12  # prev + pages + next

    def _calc_width(self):
        bs = self._btn_size()
        n = min(self.total_pages, self.max_visible)
        return (bs + 1) + n * (bs + 1) + (bs + 1)

    def _set_page(self, page):
        page = max(1, min(self.total_pages, page))
        if page != self.current:
            self.current = page
            if self.on_change:
                self.on_change(self, page)

    def _visible_range(self):
        half = self.max_visible // 2
        start = max(1, self.current - half)
        end = start + self.max_visible - 1
        if end > self.total_pages:
            end = self.total_pages
            start = max(1, end - self.max_visible + 1)
        return range(start, end + 1)

    def handle_release(self, mx, my):
        if self._pressed and self.contains(mx, my):
            ax, ay = self.abs_x(), self.abs_y()
            bs = self._btn_size()
            stride = bs + 1
            if ax <= mx < ax + bs:
                self._set_page(self.current - 1)
            else:
                pages = list(self._visible_range())
                next_x = ax + stride + len(pages) * stride
                if next_x <= mx < next_x + bs:
                    self._set_page(self.current + 1)
                else:
                    bx = ax + stride
                    for p in pages:
                        if bx <= mx < bx + bs:
                            self._set_page(p)
                            break
                        bx += stride
        super().handle_release(mx, my)

    def handle_key(self, key):
        if key == pyxel.KEY_LEFT:
            self._set_page(self.current - 1)
        elif key == pyxel.KEY_RIGHT:
            self._set_page(self.current + 1)

    def preferred_width(self):
        return self._calc_width()

    def preferred_height(self):
        return self.height if self.height > 0 else self._btn_size()

    def draw(self):
        t = self.theme
        ax, ay = self.abs_x(), self.abs_y()
        fh = t.font_height
        bs = self._btn_size()
        stride = bs + 1
        text_y = ay + (bs - fh) // 2
        pages = list(self._visible_range())
        font = t.font

        # Prev button
        prev_col = t.btn_bg if self.current > 1 else t.btn_disabled_bg
        pyxel.rect(ax, ay, bs, bs, prev_col)
        tw_arrow = text_width("<", font)
        pyxel.text(ax + (bs - tw_arrow) // 2, text_y, "<", t.btn_fg, font)

        # Page buttons
        bx = ax + stride
        for p in pages:
            is_current = p == self.current
            bg = t.primary if is_current else t.btn_bg
            pyxel.rect(bx, ay, bs, bs, bg)
            s = str(p)
            sw = text_width(s, font)
            pyxel.text(bx + (bs - sw) // 2, text_y, s, t.btn_fg, font)
            bx += stride

        # Next button
        next_col = t.btn_bg if self.current < self.total_pages else t.btn_disabled_bg
        pyxel.rect(bx, ay, bs, bs, next_col)
        tw_arrow = text_width(">", font)
        pyxel.text(bx + (bs - tw_arrow) // 2, text_y, ">", t.btn_fg, font)


class SegmentedControl(Widget):
    """Button group where exactly one segment is active.

    Args:
        options: List of segment labels.
        selected: Initially selected index.
        on_change: Callback ``fn(widget, index)``.
    """

    def __init__(self, options=None, x=0, y=0, **kw):
        self.options = options or []
        self.selected = kw.get("selected", 0)
        self.on_change = kw.get("on_change", None)
        w = kw.pop("width", 0)
        h = kw.pop("height", 0)
        kw.setdefault("focusable", True)
        super().__init__(x, y, w, h, **kw)

    def preferred_width(self):
        if self.width > 0:
            return self.width
        return sum(text_width(o, self.theme.font) + 8 for o in self.options) + 2

    def preferred_height(self):
        return self.height if self.height > 0 else self.theme.font_height + 5

    def _segment_widths(self):
        if not self.options:
            return []
        # Equal widths filling container
        sw = (self.width - 2) // len(self.options)
        widths = [sw] * len(self.options)
        # Give remainder to last segment
        widths[-1] = self.width - 2 - sw * (len(self.options) - 1)
        return widths

    def handle_release(self, mx, my):
        if self._pressed and self.contains(mx, my):
            ax = self.abs_x()
            bx = ax + 1
            for i, sw in enumerate(self._segment_widths()):
                if bx <= mx < bx + sw:
                    if i != self.selected:
                        self.selected = i
                        if self.on_change:
                            self.on_change(self, i)
                    break
                bx += sw
        super().handle_release(mx, my)

    def handle_key(self, key):
        if not self.options:
            return
        if key == pyxel.KEY_LEFT:
            self.selected = (self.selected - 1) % len(self.options)
            if self.on_change:
                self.on_change(self, self.selected)
        elif key == pyxel.KEY_RIGHT:
            self.selected = (self.selected + 1) % len(self.options)
            if self.on_change:
                self.on_change(self, self.selected)

    def draw(self):
        t = self.theme
        ax, ay = self.abs_x(), self.abs_y()
        fh = t.font_height
        font = t.font

        pyxel.rectb(ax, ay, self.width, self.height, t.border)
        if self._focused:
            pyxel.rectb(ax, ay, self.width, self.height, t.border_focus)

        bx = ax + 1
        widths = self._segment_widths()
        for i, (opt, sw) in enumerate(zip(self.options, widths)):
            is_active = i == self.selected
            bg = t.primary if is_active else t.surface
            fg = t.btn_fg if is_active else t.text
            pyxel.rect(bx, ay + 1, sw, self.height - 2, bg)
            tw = text_width(opt, font)
            pyxel.text(bx + (sw - tw) // 2, ay + (self.height - fh) // 2, opt, fg, font)
            # Separator
            if i > 0:
                pyxel.line(bx, ay + 1, bx, ay + self.height - 2, t.border)
            bx += sw
