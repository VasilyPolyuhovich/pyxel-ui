"""Tests for core UI manager and Widget base."""
from pyxel_ui import UI, Widget, THEME_DARK


class TestWidget:
    def test_create(self):
        w = Widget(x=10, y=20, width=50, height=30)
        assert w.x == 10
        assert w.y == 20
        assert w.width == 50
        assert w.height == 30

    def test_add_remove_children(self):
        parent = Widget(width=100, height=100)
        child = Widget(width=10, height=10)
        parent.add(child)
        assert child in parent.children
        assert child.parent is parent
        parent.remove(child)
        assert child not in parent.children
        assert child.parent is None

    def test_clear(self):
        parent = Widget(width=100, height=100)
        parent.add(Widget())
        parent.add(Widget())
        assert len(parent.children) == 2
        parent.clear()
        assert len(parent.children) == 0

    def test_contains(self):
        w = Widget(x=10, y=10, width=20, height=20)
        assert w.contains(15, 15) is True
        assert w.contains(5, 5) is False
        assert w.contains(30, 30) is False

    def test_hit_test_returns_deepest(self):
        parent = Widget(x=0, y=0, width=100, height=100)
        child = Widget(x=10, y=10, width=20, height=20)
        parent.add(child)
        hit = parent.hit_test(15, 15)
        assert hit is child

    def test_hit_test_returns_none_outside(self):
        w = Widget(x=0, y=0, width=50, height=50)
        assert w.hit_test(100, 100) is None

    def test_find_focusable(self):
        parent = Widget(x=0, y=0, width=100, height=100)
        a = Widget(focusable=True)
        b = Widget(focusable=False)
        c = Widget(focusable=True)
        parent.add(a)
        parent.add(b)
        parent.add(c)
        result = parent.find_focusable()
        assert a in result
        assert b not in result
        assert c in result

    def test_repr(self):
        w = Widget(x=1, y=2, width=3, height=4)
        r = repr(w)
        assert "Widget" in r
        assert "3x4" in r


class TestUI:
    def test_create(self):
        ui = UI(theme=THEME_DARK)
        assert ui.theme is THEME_DARK
        assert ui.root is not None

    def test_add_widget(self):
        ui = UI()
        w = Widget(x=0, y=0, width=10, height=10)
        ui.add(w)
        assert w in ui.root.children

    def test_focus(self):
        ui = UI()
        w = Widget(focusable=True)
        ui.add(w)
        ui.focus(w)
        assert w._focused is True
        ui.focus(None)
        assert w._focused is False

    def test_theme_setter_propagates(self):
        from pyxel_ui import THEME_LIGHT
        ui = UI(theme=THEME_DARK)
        ui.theme = THEME_LIGHT
        assert ui.root._theme is THEME_LIGHT
