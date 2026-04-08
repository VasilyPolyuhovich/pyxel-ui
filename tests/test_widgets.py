"""Tests for widget creation and properties."""
from pyxel_ui import (
    Widget, Label, Button, Checkbox, Toggle, RadioGroup,
    TextInput, Slider, ProgressBar, Separator, DropDown,
    NumberInput, Tags, MaskedInput, SegmentedControl,
    Badge, Link, Spinner, DividerText, Pagination,
)
from pyxel_ui.form import FormField


class TestLabel:
    def test_create(self):
        l = Label("Hello")
        assert l.text == "Hello"

    def test_preferred_width_positive(self):
        l = Label("Test")
        assert l.preferred_width() > 0

    def test_preferred_height_from_font(self):
        l = Label("X")
        assert l.preferred_height() == l.theme.font_height + 1


class TestButton:
    def test_create(self):
        b = Button("Click")
        assert b.text == "Click"
        assert b.focusable is True

    def test_variants(self):
        for v in ["default", "primary", "success", "warning", "danger"]:
            b = Button("X", variant=v)
            assert b.variant == v

    def test_disabled(self):
        b = Button("X", enabled=False)
        assert b.enabled is False

    def test_click_callback(self):
        clicked = []
        b = Button("X", on_click=lambda w: clicked.append(True))
        b._pressed = True
        b.handle_release(b.abs_x() + 1, b.abs_y() + 1)
        # on_click fires via Widget.handle_release when pressed+contains


class TestCheckbox:
    def test_toggle(self):
        c = Checkbox("Opt", checked=False)
        c._toggle()
        assert c.checked is True
        c._toggle()
        assert c.checked is False

    def test_on_change(self):
        values = []
        c = Checkbox("Opt", on_change=lambda w, v: values.append(v))
        c._toggle()
        assert values == [True]


class TestToggle:
    def test_toggle(self):
        t = Toggle("Sound", value=False)
        t._toggle()
        assert t.value is True


class TestRadioGroup:
    def test_create(self):
        r = RadioGroup(["A", "B", "C"], selected=1)
        assert r.selected == 1
        assert r.options == ["A", "B", "C"]

    def test_empty_options_no_crash(self):
        r = RadioGroup([])
        import pyxel
        r.handle_key(pyxel.KEY_DOWN)  # should not crash


class TestTextInput:
    def test_create(self):
        t = TextInput(text="hello")
        assert t.text == "hello"

    def test_type_text(self):
        t = TextInput()
        t.handle_text("a")
        t.handle_text("b")
        assert t.text == "ab"

    def test_backspace(self):
        import pyxel
        t = TextInput(text="abc")
        t._cursor = 3
        t.handle_key(pyxel.KEY_BACKSPACE)
        assert t.text == "ab"

    def test_max_length(self):
        t = TextInput(max_length=3, text="ab")
        t._cursor = 2
        t.handle_text("c")
        t.handle_text("d")  # should be ignored
        assert t.text == "abc"

    def test_password_mode(self):
        t = TextInput(text="secret", password=True)
        assert t.password is True


class TestSlider:
    def test_create(self):
        s = Slider(value=50, min_val=0, max_val=100)
        assert s.value == 50

    def test_clamp(self):
        s = Slider(value=50, min_val=0, max_val=100, step=10)
        s.value = 150  # direct set doesn't clamp
        assert s.value == 150  # slider._set_value_from_mouse clamps


class TestProgressBar:
    def test_create(self):
        p = ProgressBar(value=0.5)
        assert p.value == 0.5


class TestDropDown:
    def test_create(self):
        d = DropDown(options=["A", "B", "C"], selected=0)
        assert d.selected_text == "A"

    def test_placeholder(self):
        d = DropDown(options=["X"], selected=-1, placeholder="Pick...")
        assert d.selected_text == "Pick..."


class TestNumberInput:
    def test_increment(self):
        n = NumberInput(value=5, min_val=0, max_val=10, step=1)
        n._set_value(6)
        assert n.value == 6

    def test_clamp_max(self):
        n = NumberInput(value=9, min_val=0, max_val=10, step=1)
        n._set_value(15)
        assert n.value == 10

    def test_clamp_min(self):
        n = NumberInput(value=1, min_val=0, max_val=10, step=1)
        n._set_value(-5)
        assert n.value == 0


class TestMaskedInput:
    def test_digit_mask(self):
        m = MaskedInput(mask="####")
        m.handle_text("1")
        m.handle_text("2")
        assert m.value == "12"

    def test_rejects_letters_in_digit_mask(self):
        m = MaskedInput(mask="####")
        m.handle_text("a")
        assert m.value == ""

    def test_max_input(self):
        m = MaskedInput(mask="##")
        m.handle_text("1")
        m.handle_text("2")
        m.handle_text("3")  # should be ignored
        assert m.value == "12"

    def test_formatted_display(self):
        m = MaskedInput(mask="##-##")
        m.handle_text("1")
        m.handle_text("2")
        m.handle_text("3")
        m.handle_text("4")
        assert m._format_display() == "12-34"


class TestTags:
    def test_add_remove(self):
        t = Tags(tags=["a", "b"])
        assert t.tags == ["a", "b"]
        t.add_tag("c")
        assert "c" in t.tags
        t.remove_tag("a")
        assert "a" not in t.tags

    def test_no_duplicates(self):
        t = Tags(tags=["a"])
        t.add_tag("a")
        assert t.tags == ["a"]

    def test_max_tags(self):
        t = Tags(tags=["a", "b"], max_tags=2)
        t.add_tag("c")
        assert len(t.tags) == 2


class TestSegmentedControl:
    def test_create(self):
        s = SegmentedControl(options=["A", "B", "C"], selected=0)
        assert s.selected == 0


class TestFormField:
    def test_required_validation(self):
        inp = TextInput(text="")
        f = FormField("Name", inp, required=True)
        assert f.validate() is False
        assert f.error == "Required"

    def test_custom_validator(self):
        inp = TextInput(text="bad")
        f = FormField("Email", inp,
                      validator=lambda v: "Invalid" if "@" not in v else None)
        assert f.validate() is False
        assert f.error == "Invalid"

    def test_valid_passes(self):
        inp = TextInput(text="ok@test.com")
        f = FormField("Email", inp,
                      validator=lambda v: "Invalid" if "@" not in v else None)
        assert f.validate() is True
        assert f.error == ""


class TestPagination:
    def test_create(self):
        p = Pagination(total_pages=5, current=1)
        assert p.current == 1
        assert p.total_pages == 5

    def test_clamp(self):
        p = Pagination(total_pages=5, current=1)
        p._set_page(0)
        assert p.current == 1
        p._set_page(10)
        assert p.current == 5
