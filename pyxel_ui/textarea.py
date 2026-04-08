"""Multi-line text input widget."""
import pyxel
from .core import Widget
from .utils import text_width, truncate_text, char_at_x, text_x_at


class TextArea(Widget):
    """Multi-line text editor.

    Args:
        text: Initial text (newlines allowed).
        placeholder: Placeholder text when empty.
        max_length: Maximum total characters (0 = unlimited).
        on_change: Callback ``fn(widget, text)``.
        line_height: Pixel height per line (default 8).
    """

    def __init__(self, x=0, y=0, width=100, height=40, **kw):
        self._text = kw.get("text", "")
        self.placeholder = kw.get("placeholder", "")
        self.max_length = kw.get("max_length", 0)
        self.on_change = kw.get("on_change", None)
        self._line_height_override = kw.get("line_height", 0)
        self._cursor = len(self._text)
        self._scroll_y = 0
        self._cursor_blink = 0
        kw.setdefault("focusable", True)
        super().__init__(x, y, width, height, **kw)

    @property
    def line_height(self):
        if self._line_height_override > 0:
            return self._line_height_override
        return self.theme.font_height + 2

    @line_height.setter
    def line_height(self, value):
        self._line_height_override = value

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self._cursor = min(self._cursor, len(value))

    def _chars_per_line(self):
        font = self.theme.font
        fh = self.theme.font_height
        pad = max(2, fh // 4)
        available = self.width - (pad + 1) * 2
        if font is None:
            return max(1, available // 4)
        # For variable-width fonts, estimate using average char width
        avg = font.text_width("M") if font else 4
        return max(1, available // max(1, avg))

    def _get_lines(self):
        """Split text into display lines (hard wraps at newlines, soft wraps at width)."""
        cpl = self._chars_per_line()
        lines = []
        for paragraph in self._text.split("\n"):
            if not paragraph:
                lines.append("")
            else:
                while len(paragraph) > cpl:
                    lines.append(paragraph[:cpl])
                    paragraph = paragraph[cpl:]
                lines.append(paragraph)
        return lines

    def _visible_lines(self):
        fh = self.theme.font_height
        pad = max(2, fh // 4)
        return max(1, (self.height - pad * 2) // self.line_height)

    def _cursor_to_line_col(self):
        """Convert flat cursor position to (line_index, col) in wrapped lines."""
        cpl = self._chars_per_line()
        lines = self._get_lines()
        pos = 0
        for i, line in enumerate(lines):
            line_len = len(line)
            # Account for newline character between paragraphs
            end = pos + line_len
            if self._cursor <= end:
                return i, self._cursor - pos
            pos = end
            # Check if next char is a newline (paragraph break)
            if pos < len(self._text) and self._text[pos] == "\n":
                pos += 1  # skip newline
            elif i + 1 < len(lines):
                pass  # soft wrap, no newline to skip
        return max(0, len(lines) - 1), len(lines[-1]) if lines else 0

    def _line_col_to_cursor(self, line_idx, col):
        """Convert (line_index, col) back to flat cursor position."""
        cpl = self._chars_per_line()
        lines = self._get_lines()
        line_idx = max(0, min(line_idx, len(lines) - 1))
        pos = 0
        for i, line in enumerate(lines):
            if i == line_idx:
                return pos + min(col, len(line))
            pos += len(line)
            if pos < len(self._text) and self._text[pos] == "\n":
                pos += 1
        return len(self._text)

    def _ensure_cursor_visible(self):
        line, _ = self._cursor_to_line_col()
        vis = self._visible_lines()
        if line < self._scroll_y:
            self._scroll_y = line
        elif line >= self._scroll_y + vis:
            self._scroll_y = line - vis + 1

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
        lines = self._get_lines()
        line, col = self._cursor_to_line_col()

        if key == pyxel.KEY_RETURN:
            self._text = self._text[:self._cursor] + "\n" + self._text[self._cursor:]
            self._cursor += 1
            self._ensure_cursor_visible()
            if self.on_change:
                self.on_change(self, self._text)

        elif key == pyxel.KEY_BACKSPACE:
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

        elif key == pyxel.KEY_UP:
            if line > 0:
                self._cursor = self._line_col_to_cursor(line - 1, col)
                self._ensure_cursor_visible()

        elif key == pyxel.KEY_DOWN:
            if line < len(lines) - 1:
                self._cursor = self._line_col_to_cursor(line + 1, col)
                self._ensure_cursor_visible()

        elif key == pyxel.KEY_HOME:
            self._cursor = self._line_col_to_cursor(line, 0)

        elif key == pyxel.KEY_END:
            self._cursor = self._line_col_to_cursor(line, len(lines[line]) if line < len(lines) else 0)

        self._cursor_blink = 0

    def handle_press(self, mx, my):
        super().handle_press(mx, my)
        ax, ay = self.abs_x(), self.abs_y()
        font = self.theme.font
        fh = self.theme.font_height
        pad = max(2, fh // 4)
        click_line = self._scroll_y + (my - ay - pad) // self.line_height
        lines = self._get_lines()
        if 0 <= click_line < len(lines):
            click_col = char_at_x(lines[click_line], max(0, mx - ax - pad - 1), font)
        else:
            click_col = 0
        self._cursor = self._line_col_to_cursor(click_line, click_col)
        self._cursor_blink = 0

    def handle_scroll(self, dx, dy):
        lines = self._get_lines()
        max_scroll = max(0, len(lines) - self._visible_lines())
        if dy != 0:
            self._scroll_y -= dy
            self._scroll_y = max(0, min(self._scroll_y, max_scroll))
            return True
        return False

    def update(self):
        if self._focused:
            self._cursor_blink += 1

    def preferred_width(self):
        return self.width if self.width > 0 else 100

    def preferred_height(self):
        return self.height if self.height > 0 else 40

    def draw(self):
        t = self.theme
        ax, ay = self.abs_x(), self.abs_y()
        font = t.font

        # Background
        pyxel.rect(ax, ay, self.width, self.height, t.input_bg)
        border_col = t.input_focus if self._focused else t.input_border
        pyxel.rectb(ax, ay, self.width, self.height, border_col)

        # Clip content
        fh = t.font_height
        pad = max(2, fh // 4)
        pyxel.clip(ax + 1, ay + 1, self.width - 2, self.height - 2)
        try:
            lines = self._get_lines()
            vis = self._visible_lines()
            cur_line, cur_col = self._cursor_to_line_col()

            if not self._text and self.placeholder and not self._focused:
                pyxel.text(ax + pad + 1, ay + pad, self.placeholder, t.input_placeholder, font)
            else:
                for i in range(vis):
                    li = self._scroll_y + i
                    if li >= len(lines):
                        break
                    ly = ay + pad + i * self.line_height
                    pyxel.text(ax + pad + 1, ly, lines[li], t.input_fg, font)

            # Cursor
            if self._focused and (self._cursor_blink % 30) < 20:
                ci = cur_line - self._scroll_y
                if 0 <= ci < vis:
                    cur_line_text = lines[cur_line] if cur_line < len(lines) else ""
                    cx = ax + pad + 1 + text_x_at(cur_line_text, cur_col, font)
                    cy = ay + pad + ci * self.line_height
                    pyxel.line(cx, cy, cx, cy + self.line_height - 2, t.input_cursor)
        finally:
            pyxel.clip()

        # Scroll indicator
        if len(lines) > vis:
            sb_x = ax + self.width - 2
            ratio = vis / len(lines)
            thumb_h = max(2, int(self.height * ratio))
            max_s = max(1, len(lines) - vis)
            thumb_y = ay + int((self.height - thumb_h) * self._scroll_y / max_s)
            pyxel.rect(sb_x, thumb_y, 1, thumb_h, t.scroll_thumb)
