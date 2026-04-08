"""pyxel-ui Unified Showcase — all widgets, Cozette font, high resolution.

Run: pyxel run examples/showcase.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pyxel
from pyxel_ui import (
    UI, Theme, THEME_DARK, THEME_LIGHT, THEME_NES, THEME_GAMEBOY,
    Row, Column, Spacer, Grid,
    Label, Button, Checkbox, RadioGroup, Toggle, Separator,
    TextInput, TextArea, Slider, ProgressBar,
    Panel, ScrollView, TabView, DropDown, ListView,
    Dialog, Table, Tags, MaskedInput, ColorPicker,
    Accordion, Pagination, SegmentedControl,
)
from pyxel_ui.form import (
    FormField, NumberInput, Link, Toast, Badge, DividerText, Spinner,
)

# Themes use Cozette by default (loaded automatically by pyxel-ui)
THEMES = {
    "Dark": THEME_DARK,
    "Light": THEME_LIGHT,
    "NES": THEME_NES,
    "GameBoy": THEME_GAMEBOY,
    "Pyxel 4x6": Theme.pyxel_default(),
}

W, H = 480, 360
PAD = 4
CW = W - PAD * 2 - 4  # content width inside tabs


class ShowcaseApp:
    def __init__(self):
        pyxel.init(W, H, title="pyxel-ui Showcase", fps=30, display_scale=2)
        pyxel.mouse(True)
        self.ui = UI(theme=THEMES["Dark"])
        self.progress = None
        self.tags_w = None
        self.tag_input = None
        self.status = None
        self.build()
        pyxel.run(self.update, self.draw)

    def build(self):
        tabs = self.ui.add(TabView(x=PAD, y=PAD, width=W - PAD * 2, height=H - PAD * 2))
        self.build_basic(tabs)
        self.build_inputs(tabs)
        self.build_data(tabs)
        self.build_form(tabs)
        self.build_extras(tabs)

    # ── Tab 1: Basic ──
    def build_basic(self, tabs):
        t = Column(spacing=4, padding=4)
        tabs.add_tab("Basic", t)

        hdr = t.add(Row(spacing=6, height=16, width=CW))
        hdr.add(Label("pyxel-ui Showcase", color=10))
        hdr.add(Spacer())
        hdr.add(Label("Theme:"))
        hdr.add(DropDown(options=list(THEMES.keys()), selected=0, width=80, height=16,
                         on_change=lambda w, i: self.set_theme(i)))

        t.add(Separator(width=CW))

        t.add(Label("Buttons:"))
        br = t.add(Row(spacing=4, height=18, width=CW))
        br.add(Button("Default", on_click=lambda w: self.toast("Default"), height=18))
        br.add(Button("Primary", variant="primary", height=18,
                       on_click=lambda w: self.toast("Primary!")))
        br.add(Button("Success", variant="success", height=18,
                       on_click=lambda w: self.toast("Success!")))
        br.add(Button("Danger", variant="danger", height=18,
                       on_click=lambda w: self.toast("Danger!")))
        br.add(Button("Disabled", enabled=False, height=18))

        t.add(Label("Controls:"))
        cr = t.add(Row(spacing=10, height=14, width=CW))
        cr.add(Checkbox("Check A", checked=True))
        cr.add(Checkbox("Check B"))
        cr.add(Toggle("Sound", value=True))
        cr.add(Toggle("Music", value=True))

        t.add(RadioGroup(["Easy", "Normal", "Hard", "Nightmare"],
                         horizontal=True, selected=1))

        t.add(Label("SegmentedControl:"))
        t.add(SegmentedControl(
            options=["All", "Active", "Completed", "Archived"],
            selected=0, width=CW, height=18,
            on_change=lambda w, i: self.toast(f"Filter: {w.options[i]}")))

        pr = t.add(Row(spacing=4, height=14, width=CW))
        pr.add(Label("HP:"))
        self.progress = pr.add(ProgressBar(width=200, value=0.7, show_text=True, height=14))
        pr.add(Button("+", width=18, height=14, on_click=lambda w: self.adj_prog(0.1)))
        pr.add(Button("-", width=18, height=14, on_click=lambda w: self.adj_prog(-0.1)))

        self.status = t.add(Label("Ready. Click any button!", color=11))

    # ── Tab 2: Inputs ──
    def build_inputs(self, tabs):
        t = Column(spacing=4, padding=4)
        tabs.add_tab("Input", t)

        t.add(Label("Text Input:"))
        ir = t.add(Row(spacing=6, height=16, width=CW))
        ir.add(TextInput(width=180, height=16, placeholder="Type here..."))
        ir.add(TextInput(width=100, height=16, text="secret", password=True))
        ir.add(NumberInput(width=90, height=16, value=42, min_val=0, max_val=999))

        t.add(Label("Slider:"))
        t.add(Slider(width=350, value=50, min_val=0, max_val=100, step=5,
                     on_change=lambda w, v: self.toast(f"Volume: {int(v)}")))

        t.add(Label("TextArea:"))
        t.add(TextArea(width=CW, height=60,
                       text="Multi-line text editor with Cozette font.\n"
                            "Supports cursor navigation, scrolling,\n"
                            "and word wrap. Try typing here!"))

        t.add(DividerText("Masked Inputs", width=CW))

        mr = t.add(Row(spacing=8, height=16, width=CW))
        mr.add(Label("Card:"))
        mr.add(MaskedInput(mask="####-####-####-####", width=200, height=16))

        mr2 = t.add(Row(spacing=8, height=16, width=CW))
        mr2.add(Label("Phone:"))
        mr2.add(MaskedInput(mask="+## (###) ###-##-##", width=200, height=16))
        mr2.add(Label("Date:"))
        mr2.add(MaskedInput(mask="##/##/####", width=100, height=16))

        t.add(Label("ColorPicker:"))
        t.add(ColorPicker(selected=6, cell_size=14,
                          on_change=lambda w, c: self.toast(f"Color: {c}")))

    # ── Tab 3: Data ──
    def build_data(self, tabs):
        t = Column(spacing=4, padding=4)
        tabs.add_tab("Data", t)

        t.add(Label("Table (click headers to sort):"))
        self.orders = [
            {"id": "001", "item": "Enchanted Sword +2", "qty": "1", "gold": "50"},
            {"id": "002", "item": "HP Potion", "qty": "5", "gold": "25"},
            {"id": "003", "item": "Mithril Shield", "qty": "1", "gold": "35"},
            {"id": "004", "item": "Arrows x20", "qty": "3", "gold": "15"},
            {"id": "005", "item": "Mana Ring of Power", "qty": "1", "gold": "80"},
            {"id": "006", "item": "Torch", "qty": "10", "gold": "5"},
            {"id": "007", "item": "Silk Rope 50ft", "qty": "2", "gold": "10"},
            {"id": "008", "item": "Ancient Map", "qty": "1", "gold": "20"},
            {"id": "009", "item": "Dragon Scale", "qty": "1", "gold": "150"},
            {"id": "010", "item": "Healing Herb", "qty": "8", "gold": "12"},
        ]
        t.add(Table(
            columns=[
                {"key": "id", "title": "#", "width": 40},
                {"key": "item", "title": "Item Name", "width": 200},
                {"key": "qty", "title": "Qty", "width": 50},
                {"key": "gold", "title": "Gold", "width": 60},
            ],
            rows=self.orders, width=CW, height=150, sortable=True,
            row_height=16, header_height=16,
            on_select=lambda w, i: self.toast(f"Selected: {self.orders[i]['item']}"),
        ))
        t.add(Pagination(total_pages=12, current=1,
                         on_change=lambda w, p: self.toast(f"Page {p}")))

        t.add(Label("ListView:"))
        t.add(ListView(
            items=["Iron Sword +1", "Leather Armor", "HP Potion x3",
                   "MP Potion x1", "Antidote x2", "Gold Key",
                   "Dragon Scale", "Phoenix Feather", "Crystal Shard"],
            width=CW, height=80, selected=0, item_height=16,
            on_select=lambda w, i: self.toast(f"Item: {w.items[i]}"),
        ))

    # ── Tab 4: Form ──
    def build_form(self, tabs):
        t = Column(spacing=4, padding=4)
        tabs.add_tab("Form", t)

        hdr = t.add(Row(spacing=6, height=16, width=CW))
        hdr.add(Label("User Profile", color=10))
        hdr.add(Spacer())
        hdr.add(Badge("PRO", color=3))
        hdr.add(Badge("Lv.7", color=5))

        self.name_f = FormField("Display Name",
            TextInput(width=CW, height=16, text="Adventurer"),
            required=True, width=CW)
        t.add(self.name_f)

        self.email_f = FormField("Email",
            TextInput(width=CW, height=16, placeholder="user@example.com"),
            required=True, width=CW,
            validator=lambda v: "Invalid email" if v and "@" not in v else None)
        t.add(self.email_f)

        row1 = t.add(Row(spacing=8, height=16, width=CW))
        row1.add(Label("Class:"))
        row1.add(DropDown(
            options=["Warrior", "Mage", "Rogue", "Healer", "Ranger"],
            selected=0, width=120, height=16))
        row1.add(Label("Level:"))
        row1.add(NumberInput(width=80, height=16, value=7, min_val=1, max_val=99))
        row1.add(Label("Gold:"))
        row1.add(NumberInput(width=90, height=16, value=250, min_val=0, max_val=9999, step=10))

        cr = t.add(Row(spacing=10, height=14, width=CW))
        cr.add(Checkbox("Public profile"))
        cr.add(Checkbox("Notifications", checked=True))
        cr.add(Checkbox("Dark mode", checked=True))
        cr.add(Spacer())
        cr.add(Link("Terms of Service", on_click=lambda w: self.toast("Terms of Service")))

        br = t.add(Row(spacing=6, height=18, width=CW))
        br.add(Button("Save Profile", variant="success", width=100, height=18,
                       on_click=lambda w: self.save_form()))
        br.add(Button("Reset", width=70, height=18,
                       on_click=lambda w: self.toast("Reset!")))
        br.add(Button("Delete Account", variant="danger", width=120, height=18,
                       on_click=lambda w: self.toast("Are you sure?")))

    # ── Tab 5: Extras ──
    def build_extras(self, tabs):
        t = Column(spacing=4, padding=4)
        tabs.add_tab("Extra", t)

        t.add(Label("Tags (click x to remove):"))
        self.tags_w = t.add(Tags(
            tags=["python", "pyxel", "retro", "pixel-art", "gamedev", "open-source"],
            width=CW, removable=True))
        tr = t.add(Row(spacing=4, height=16, width=CW))
        self.tag_input = tr.add(TextInput(width=180, height=16, placeholder="New tag..."))
        tr.add(Button("Add Tag", width=70, height=16, on_click=self.add_tag))

        t.add(DividerText("Panels & Accordion", width=CW))

        panel = t.add(Panel("Character Stats", width=CW, height=40, padding=3))
        pc = panel.add(Row(spacing=16, height=14, width=CW - 12))
        pc.add(Label("HP: 30/30"))
        pc.add(Label("MP: 10/10"))
        pc.add(Label("ATK: 12"))
        pc.add(Label("DEF: 5"))
        pc.add(Label("SPD: 8"))

        acc = t.add(Accordion(width=CW))
        s1 = Column(spacing=3, padding=3)
        s1.add(Label("Destination: Castle Town, West District"))
        s1.add(Label("Estimated delivery: 3 days by griffin"))
        s1.add(Label("Tracking: #GT-2026-04-08-001"))
        acc.add_section("Shipping Details", s1, opened=True)
        s2 = Column(spacing=3, padding=3)
        s2.add(Label("Total: $250 gold"))
        s2.add(Label("Method: Royal Treasury Direct"))
        s2.add(Label("Status: Confirmed"))
        acc.add_section("Payment Info", s2)
        s3 = Column(spacing=3, padding=3)
        s3.add(Label("Gift wrapping: Enabled"))
        s3.add(Label("Message: 'For the brave hero!'"))
        acc.add_section("Additional Options", s3)

        t.add(Row(spacing=6, height=18, width=CW)).add(
            Button("Show Dialog", variant="primary", width=120, height=18,
                   on_click=lambda w: self.show_dialog()))

    # ── Helpers ──
    def toast(self, msg):
        Toast.show(msg, duration=50)
        if self.status:
            self.status.text = msg

    def set_theme(self, idx):
        name = list(THEMES.keys())[idx]
        self.ui.theme = THEMES[name]
        self.toast(f"Theme: {name}")

    def adj_prog(self, d):
        if self.progress:
            self.progress.value = max(0, min(1, self.progress.value + d))

    def add_tag(self, _):
        if self.tag_input and self.tags_w:
            text = self.tag_input.text.strip()
            if text:
                self.tags_w.add_tag(text)
                self.tag_input.text = ""
                self.tag_input._cursor = 0

    def save_form(self):
        ok = self.name_f.validate() & self.email_f.validate()
        if ok:
            Toast.show("Profile saved!", color=11, duration=60)
        else:
            Toast.show("Fix errors above", color=8, duration=60)

    def show_dialog(self):
        Dialog(
            title="Confirm Action",
            message="Do you want to save changes before leaving this page?",
            buttons=["Save", "Discard", "Cancel"],
            on_button=lambda w, i: self.toast(f"Dialog: {['Save','Discard','Cancel'][i]}"),
        ).show()

    def update(self):
        self.ui.update()
        Toast.update()

    def draw(self):
        pyxel.cls(self.ui.theme.bg)
        self.ui.draw()
        Toast.draw()


ShowcaseApp()
