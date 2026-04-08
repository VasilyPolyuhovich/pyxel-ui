"""Tests for layout system."""
from pyxel_ui import Row, Column, Spacer, Label, Button, Widget


class TestRow:
    def test_children_positioned_horizontally(self):
        row = Row(x=0, y=0, width=200, height=20)
        a = row.add(Label("AAA"))
        b = row.add(Label("BBB"))
        row.layout()
        assert a.x == 0
        assert b.x > a.x  # b is to the right of a

    def test_flex_child_expands(self):
        row = Row(x=0, y=0, width=200, height=20)
        fixed = row.add(Label("X"))
        flexy = row.add(Label("", flex=1))
        row.layout()
        assert flexy.width > fixed.width

    def test_spacing(self):
        row = Row(x=0, y=0, width=200, height=20, spacing=10)
        a = row.add(Label("A"))
        b = row.add(Label("B"))
        row.layout()
        gap = b.x - (a.x + a.width)
        assert gap == 10


class TestColumn:
    def test_children_positioned_vertically(self):
        col = Column(x=0, y=0, width=100, height=200)
        a = col.add(Label("AAA"))
        b = col.add(Label("BBB"))
        col.layout()
        assert a.y == 0
        assert b.y > a.y

    def test_auto_height(self):
        col = Column(x=0, y=0, width=100)
        col.add(Label("A"))
        col.add(Label("B"))
        col.layout()
        assert col.height > 0


class TestSpacer:
    def test_flex_default(self):
        s = Spacer()
        assert s.flex == 1

    def test_in_row(self):
        row = Row(x=0, y=0, width=200, height=20)
        a = row.add(Label("L"))
        row.add(Spacer())
        b = row.add(Label("R"))
        row.layout()
        # b should be pushed to the right
        assert b.x + b.width <= 200


class TestAutoSizing:
    def test_layout_sets_child_dimensions(self):
        """Children with width=0 get sized by layout."""
        row = Row(x=0, y=0, width=300, height=30)
        btn = row.add(Button("Test"))
        row.layout()
        assert btn.width > 0, "Button should have been auto-sized"
        assert btn.height > 0, "Button height should have been set"
