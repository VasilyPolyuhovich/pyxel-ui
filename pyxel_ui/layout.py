"""Layout containers: Row, Column, Spacer."""
import pyxel
from .core import Widget


class _BoxLayout(Widget):
    """Base for Row and Column layouts."""

    HORIZONTAL = 0
    VERTICAL = 1

    def __init__(self, direction, x=0, y=0, width=0, height=0, **kw):
        super().__init__(x, y, width, height, **kw)
        self._dir = direction
        self.spacing = kw.get("spacing", None)  # None = use theme
        self.padding = kw.get("padding", None)
        self.align = kw.get("align", "start")  # start, center, end
        self.bg = kw.get("bg", None)  # background color, None = transparent

    def _get_spacing(self):
        return self.spacing if self.spacing is not None else self.theme.spacing

    def _get_padding(self):
        return self.padding if self.padding is not None else 0

    def content_x(self):
        return self.abs_x() + self._get_padding()

    def content_y(self):
        return self.abs_y() + self._get_padding()

    def content_width(self):
        return self.width - self._get_padding() * 2

    def content_height(self):
        return self.height - self._get_padding() * 2

    def layout(self):
        pad = self._get_padding()
        sp = self._get_spacing()
        is_h = self._dir == self.HORIZONTAL

        # Auto-size: compute dimensions from children if not explicitly set
        if is_h and self.width <= 0:
            self.width = self.preferred_width()
        if not is_h and self.height <= 0:
            self.height = self.preferred_height()
        # Also auto-size cross axis
        if is_h and self.height <= 0:
            self.height = self.preferred_height()
        if not is_h and self.width <= 0:
            self.width = self.preferred_width()

        avail_main = (self.content_width() if is_h else self.content_height())
        avail_cross = (self.content_height() if is_h else self.content_width())

        # Measure children
        visible = [c for c in self.children if c.visible]
        if not visible:
            self._dirty = False
            return

        total_fixed = 0
        total_flex = 0
        for c in visible:
            size = c.preferred_width() if is_h else c.preferred_height()
            if c.flex > 0:
                total_flex += c.flex
            else:
                total_fixed += size
        total_spacing = sp * max(0, len(visible) - 1)

        # Distribute flex space
        remaining = max(0, avail_main - total_fixed - total_spacing)

        # Position children
        pos = 0
        allocated_flex = 0
        flex_children = [c for c in visible if c.flex > 0]
        for c in visible:
            main_size = c.preferred_width() if is_h else c.preferred_height()
            if c.flex > 0 and total_flex > 0:
                if c is flex_children[-1]:
                    # Last flex child gets remainder to avoid pixel gaps
                    main_size = remaining - allocated_flex
                else:
                    main_size = int(remaining * c.flex / total_flex)
                    allocated_flex += main_size

            cross_size = c.preferred_height() if is_h else c.preferred_width()
            if cross_size <= 0:
                cross_size = avail_cross

            # Cross-axis alignment
            cross_pos = 0
            if self.align == "center":
                cross_pos = max(0, (avail_cross - cross_size) // 2)
            elif self.align == "end":
                cross_pos = max(0, avail_cross - cross_size)

            # Positions are relative to content area (content_x/y already adds padding)
            # Always set size for children with width/height=0 (auto-sized)
            if is_h:
                c.x = pos
                c.y = cross_pos
                if c.width <= 0 or c.flex > 0:
                    c.width = main_size
                if c.height <= 0:
                    c.height = cross_size
            else:
                c.x = cross_pos
                c.y = pos
                if c.width <= 0:
                    c.width = cross_size
                if c.height <= 0 or c.flex > 0:
                    c.height = main_size

            pos += main_size + sp

        self._dirty = False
        for c in visible:
            if c._dirty:
                c.layout()

    def preferred_width(self):
        if self.width > 0:
            return self.width
        pad = self._get_padding()
        sp = self._get_spacing()
        visible = [c for c in self.children if c.visible]
        if self._dir == self.HORIZONTAL:
            total = sum(c.preferred_width() for c in visible)
            total += sp * max(0, len(visible) - 1)
            return total + pad * 2
        else:
            return max((c.preferred_width() for c in visible), default=0) + pad * 2

    def preferred_height(self):
        if self.height > 0:
            return self.height
        pad = self._get_padding()
        sp = self._get_spacing()
        visible = [c for c in self.children if c.visible]
        if self._dir == self.VERTICAL:
            total = sum(c.preferred_height() for c in visible)
            total += sp * max(0, len(visible) - 1)
            return total + pad * 2
        else:
            return max((c.preferred_height() for c in visible), default=0) + pad * 2

    def draw(self):
        if self.bg is not None:
            ax, ay = self.abs_x(), self.abs_y()
            pyxel.rect(ax, ay, self.width, self.height, self.bg)
        super().draw()


class Row(_BoxLayout):
    """Horizontal layout container.

    Children are placed left-to-right with spacing.
    Use ``flex=1`` on children to make them expand.

    Args:
        spacing: Gap between children (default: theme.spacing).
        padding: Inner padding.
        align: Cross-axis alignment ("start", "center", "end").
        bg: Background color or None.
    """

    def __init__(self, x=0, y=0, width=0, height=0, **kw):
        super().__init__(_BoxLayout.HORIZONTAL, x, y, width, height, **kw)


class Column(_BoxLayout):
    """Vertical layout container.

    Children are placed top-to-bottom with spacing.
    Use ``flex=1`` on children to make them expand.
    """

    def __init__(self, x=0, y=0, width=0, height=0, **kw):
        super().__init__(_BoxLayout.VERTICAL, x, y, width, height, **kw)


class Spacer(Widget):
    """Flexible empty space for use inside Row/Column."""

    def __init__(self, width=0, height=0, flex=1):
        super().__init__(width=width, height=height, flex=flex)

    def preferred_width(self):
        return self.width

    def preferred_height(self):
        return self.height
