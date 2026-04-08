"""Grid layout container."""
import pyxel
from .core import Widget


class Grid(Widget):
    """Auto-wrapping grid layout.

    Places children in a grid with fixed cell sizes. Cells wrap to
    the next row when the container width is exceeded.

    Args:
        col_width: Width of each cell.
        row_height: Height of each cell.
        cols: Fixed number of columns (0 = auto based on width).
        spacing_x: Horizontal gap between cells.
        spacing_y: Vertical gap between cells.
        padding: Inner padding.
        bg: Background color (None = transparent).
    """

    def __init__(self, x=0, y=0, width=0, height=0, **kw):
        self.col_width = kw.get("col_width", 40)
        self.row_height = kw.get("row_height", 20)
        self.cols = kw.get("cols", 0)
        self.spacing_x = kw.get("spacing_x", None)
        self.spacing_y = kw.get("spacing_y", None)
        self.padding = kw.get("padding", None)
        self.bg = kw.get("bg", None)
        super().__init__(x, y, width, height, **kw)

    def _pad(self):
        return self.padding if self.padding is not None else self.theme.padding

    def _sx(self):
        return self.spacing_x if self.spacing_x is not None else self.theme.spacing

    def _sy(self):
        return self.spacing_y if self.spacing_y is not None else self.theme.spacing

    def _num_cols(self):
        if self.cols > 0:
            return self.cols
        pad = self._pad()
        sx = self._sx()
        avail = self.width - pad * 2
        if avail <= 0:
            return 1
        return max(1, (avail + sx) // (self.col_width + sx))

    def content_x(self):
        return self.abs_x() + self._pad()

    def content_y(self):
        return self.abs_y() + self._pad()

    def layout(self):
        pad = self._pad()
        sx, sy = self._sx(), self._sy()
        ncols = self._num_cols()
        visible = [c for c in self.children if c.visible]

        for i, c in enumerate(visible):
            col = i % ncols
            row = i // ncols
            c.x = pad + col * (self.col_width + sx)
            c.y = pad + row * (self.row_height + sy)
            c.width = self.col_width
            c.height = self.row_height
            if c._dirty:
                c.layout()

        # Auto-size height
        if visible:
            nrows = (len(visible) + ncols - 1) // ncols
            computed_h = pad * 2 + nrows * self.row_height + max(0, nrows - 1) * sy
            if self.height <= 0 or self.height < computed_h:
                self.height = computed_h

        self._dirty = False

    def preferred_width(self):
        if self.width > 0:
            return self.width
        pad = self._pad()
        sx = self._sx()
        ncols = self._num_cols() if self.width > 0 else max(1, min(len(self.children), 4))
        return pad * 2 + ncols * self.col_width + max(0, ncols - 1) * sx

    def preferred_height(self):
        if self.height > 0:
            return self.height
        pad = self._pad()
        sy = self._sy()
        ncols = self._num_cols() if self.width > 0 else max(1, min(len(self.children), 4))
        visible = [c for c in self.children if c.visible]
        nrows = (len(visible) + ncols - 1) // ncols if ncols > 0 else 1
        return pad * 2 + nrows * self.row_height + max(0, nrows - 1) * sy

    def draw(self):
        if self.bg is not None:
            ax, ay = self.abs_x(), self.abs_y()
            pyxel.rect(ax, ay, self.width, self.height, self.bg)
        super().draw()
