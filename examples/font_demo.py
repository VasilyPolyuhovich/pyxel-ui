"""Font demo — compare Cozette (default) vs Pyxel built-in.

Run: pyxel run examples/font_demo.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pyxel
from pyxel_ui import UI, THEME_DARK, Theme, Column, Label, Separator, TabView, load_bdf
from pyxel_ui.utils import text_width

FONT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "fonts"))

LOREM = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
    "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
    "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris."
)


def wrap_text(text, max_w, font):
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        line = ""
        for word in words:
            test = line + (" " if line else "") + word
            tw = text_width(test, font)
            if tw > max_w and line:
                lines.append(line)
                line = word
            else:
                line = test
        if line:
            lines.append(line)
    return lines


class App:
    def __init__(self):
        pyxel.init(300, 180, title="Font Demo", fps=30, display_scale=2)
        pyxel.mouse(True)

        ibm = load_bdf("ib8x8u.bdf")

        self.fonts = [
            ("Cozette", "Cozette 6x13 (default)", THEME_DARK),
            ("IBM", "IBM BIOS 8x8", THEME_DARK.copy(font=ibm, font_height=8)),
            ("Pyxel", "Pyxel built-in 4x6", Theme.pyxel_default()),
        ]

        self.ui = UI(theme=THEME_DARK)
        tabs = self.ui.add(TabView(x=2, y=2, width=296, height=176))

        for short, full, theme in self.fonts:
            col = Column(spacing=2, padding=4)
            tabs.add_tab(short, col)
            col.add(Label(full, color=10, width=280, theme=theme))
            col.add(Separator(width=280))
            for line in wrap_text(LOREM, 278, theme.font):
                col.add(Label(line, width=280, theme=theme))

        pyxel.run(self.ui.update, self.ui.draw)


App()
