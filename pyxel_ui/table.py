"""Table widget with columns, sorting, and scrolling."""
import pyxel
from .core import Widget
from .utils import truncate_text


class Table(Widget):
    """Data table with column headers, sorting, and row selection.

    Args:
        columns: List of column defs: ``{"key": str, "title": str, "width": int}``.
        rows: List of dicts with keys matching column keys.
        on_select: Callback ``fn(widget, row_index)``.
        on_sort: Callback ``fn(widget, column_key, ascending)``.
        row_height: Height per data row.
        header_height: Height of header row.
        sortable: Enable click-to-sort on headers.
    """

    def __init__(self, columns=None, rows=None, x=0, y=0, width=160, height=60, **kw):
        self.columns = columns or []
        self.rows = rows or []
        self.on_select = kw.get("on_select", None)
        self.on_sort = kw.get("on_sort", None)
        self._row_height_override = kw.get("row_height", 0)
        self._header_height_override = kw.get("header_height", 0)
        self.sortable = kw.get("sortable", True)
        self.selected = -1
        self._sort_key = None
        self._sort_asc = True
        self._scroll = 0
        self._hover_row = -1
        kw.setdefault("focusable", True)
        super().__init__(x, y, width, height, **kw)

    @property
    def row_height(self):
        if self._row_height_override > 0:
            return self._row_height_override
        return self.theme.font_height + 3

    @row_height.setter
    def row_height(self, value):
        self._row_height_override = value

    @property
    def header_height(self):
        if self._header_height_override > 0:
            return self._header_height_override
        return self.theme.font_height + 3

    @header_height.setter
    def header_height(self, value):
        self._header_height_override = value

    def _visible_rows(self):
        return max(1, (self.height - self.header_height) // self.row_height)

    def _max_scroll(self):
        return max(0, len(self.rows) - self._visible_rows())

    def _total_col_width(self):
        return sum(c.get("width", 40) for c in self.columns)

    def sort_by(self, key, ascending=True):
        self._sort_key = key
        self._sort_asc = ascending
        try:
            self.rows.sort(key=lambda r: r.get(key, ""), reverse=not ascending)
        except TypeError:
            pass
        if self.on_sort:
            self.on_sort(self, key, ascending)

    def handle_press(self, mx, my):
        super().handle_press(mx, my)
        ax, ay = self.abs_x(), self.abs_y()

        # Header click -> sort
        if self.sortable and ay <= my < ay + self.header_height:
            cx = ax
            for col in self.columns:
                cw = col.get("width", 40)
                if cx <= mx < cx + cw:
                    key = col["key"]
                    if self._sort_key == key:
                        self.sort_by(key, not self._sort_asc)
                    else:
                        self.sort_by(key, True)
                    return
                cx += cw

    def handle_release(self, mx, my):
        if self._pressed and self.contains(mx, my):
            ax, ay = self.abs_x(), self.abs_y()
            data_y = ay + self.header_height
            if my >= data_y:
                idx = self._scroll + (my - data_y) // self.row_height
                if 0 <= idx < len(self.rows):
                    self.selected = idx
                    if self.on_select:
                        self.on_select(self, idx)
        super().handle_release(mx, my)

    def handle_scroll(self, dx, dy):
        if dy != 0:
            self._scroll = max(0, min(self._scroll - dy, self._max_scroll()))
            return True
        return False

    def handle_key(self, key):
        if self.selected == -1 and self.rows and key in (pyxel.KEY_UP, pyxel.KEY_DOWN):
            self.selected = 0
            if self.on_select:
                self.on_select(self, 0)
            return
        if key == pyxel.KEY_UP and self.selected > 0:
            self.selected -= 1
            if self.selected < self._scroll:
                self._scroll = self.selected
            if self.on_select:
                self.on_select(self, self.selected)
        elif key == pyxel.KEY_DOWN and self.selected < len(self.rows) - 1:
            self.selected += 1
            vis = self._visible_rows()
            if self.selected >= self._scroll + vis:
                self._scroll = self.selected - vis + 1
            if self.on_select:
                self.on_select(self, self.selected)

    def update(self):
        if self._hovered:
            ax, ay = self.abs_x(), self.abs_y()
            data_y = ay + self.header_height
            my = pyxel.mouse_y
            if my >= data_y:
                self._hover_row = self._scroll + (my - data_y) // self.row_height
            else:
                self._hover_row = -1
        else:
            self._hover_row = -1

    def draw(self):
        t = self.theme
        ax, ay = self.abs_x(), self.abs_y()
        font = t.font

        # Background
        pyxel.rect(ax, ay, self.width, self.height, t.list_bg)
        pyxel.rectb(ax, ay, self.width, self.height, t.panel_border)

        # Header
        fh = t.font_height
        pad = max(2, fh // 4)
        hdr_ty = ay + (self.header_height - fh) // 2
        pyxel.rect(ax + 1, ay + 1, self.width - 2, self.header_height - 1, t.panel_title_bg)
        cx = ax
        for col in self.columns:
            cw = col.get("width", 40)
            title = col.get("title", col["key"])
            display_title = truncate_text(title, cw - pad * 2, font)
            pyxel.text(cx + pad, hdr_ty, display_title, t.panel_title_fg, font)
            # Sort indicator
            if self._sort_key == col["key"]:
                arrow = "^" if self._sort_asc else "v"
                pyxel.text(cx + cw - 6, hdr_ty, arrow, t.primary, font)
            # Column separator
            if cx > ax:
                pyxel.line(cx, ay + 1, cx, ay + self.height - 2, t.panel_border)
            cx += cw

        # Data rows
        data_y = ay + self.header_height
        pyxel.clip(ax + 1, data_y, self.width - 2, self.height - self.header_height - 1)
        try:
            vis = self._visible_rows()
            for i in range(vis):
                idx = self._scroll + i
                if idx >= len(self.rows):
                    break
                ry = data_y + i * self.row_height
                row = self.rows[idx]

                # Row background
                if idx == self.selected:
                    pyxel.rect(ax + 1, ry, self.width - 2, self.row_height, t.list_selected_bg)
                    fg = t.list_selected_fg
                elif idx == self._hover_row:
                    pyxel.rect(ax + 1, ry, self.width - 2, self.row_height, t.list_hover_bg)
                    fg = t.list_item
                else:
                    fg = t.list_item

                # Cells
                cx = ax
                row_ty = ry + (self.row_height - fh) // 2
                for col in self.columns:
                    cw = col.get("width", 40)
                    val = str(row.get(col["key"], ""))
                    display_val = truncate_text(val, cw - pad * 2, font)
                    pyxel.text(cx + pad, row_ty, display_val, fg, font)
                    cx += cw

                # Row separator
                pyxel.line(ax + 1, ry + self.row_height - 1,
                           ax + self.width - 2, ry + self.row_height - 1, t.panel_border)
        finally:
            pyxel.clip()

        # Scrollbar
        if len(self.rows) > vis:
            sb_x = ax + self.width - 3
            ratio = vis / len(self.rows)
            thumb_h = max(4, int((self.height - self.header_height) * ratio))
            max_s = self._max_scroll()
            off = int(((self.height - self.header_height) - thumb_h) * self._scroll / max_s) if max_s > 0 else 0
            pyxel.rect(sb_x, data_y + off, 2, thumb_h, t.scroll_thumb)
