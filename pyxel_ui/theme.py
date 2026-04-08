"""Theming system for pyxel-ui."""

# Sentinel for "use default font" — resolved lazily in Theme.resolve_font()
_USE_DEFAULT = object()


class Theme:
    """Customizable theme with colors, spacing, and style settings.

    All color values are Pyxel palette indices (0-15 default, 0-255 extended).
    Pass any property as a keyword argument to override defaults.
    """

    def __init__(self, **kw):
        # -- Background & surface --
        self.bg = kw.get("bg", 0)
        self.surface = kw.get("surface", 1)

        # -- Text --
        self.text = kw.get("text", 7)
        self.text_dim = kw.get("text_dim", 13)
        self.text_disabled = kw.get("text_disabled", 5)

        # -- Accent palette --
        self.primary = kw.get("primary", 6)
        self.secondary = kw.get("secondary", 12)
        self.success = kw.get("success", 11)
        self.warning = kw.get("warning", 9)
        self.danger = kw.get("danger", 8)

        # -- Borders --
        self.border = kw.get("border", 5)
        self.border_focus = kw.get("border_focus", 6)

        # -- Button --
        self.btn_bg = kw.get("btn_bg", 5)
        self.btn_fg = kw.get("btn_fg", 7)
        self.btn_hover = kw.get("btn_hover", 6)
        self.btn_press = kw.get("btn_press", 12)
        self.btn_disabled_bg = kw.get("btn_disabled_bg", 13)
        self.btn_disabled_fg = kw.get("btn_disabled_fg", 5)

        # -- Input field --
        self.input_bg = kw.get("input_bg", 0)
        self.input_fg = kw.get("input_fg", 7)
        self.input_border = kw.get("input_border", 5)
        self.input_focus = kw.get("input_focus", 6)
        self.input_selection = kw.get("input_selection", 5)
        self.input_cursor = kw.get("input_cursor", 7)
        self.input_placeholder = kw.get("input_placeholder", 13)

        # -- Checkbox / Radio / Toggle --
        self.check_on = kw.get("check_on", 11)
        self.check_off = kw.get("check_off", 5)
        self.check_mark = kw.get("check_mark", 7)

        # -- Slider --
        self.slider_track = kw.get("slider_track", 5)
        self.slider_fill = kw.get("slider_fill", 6)
        self.slider_thumb = kw.get("slider_thumb", 7)

        # -- Progress bar --
        self.progress_bg = kw.get("progress_bg", 5)
        self.progress_fill = kw.get("progress_fill", 11)

        # -- Scroll --
        self.scroll_track = kw.get("scroll_track", 1)
        self.scroll_thumb = kw.get("scroll_thumb", 5)
        self.scroll_thumb_hover = kw.get("scroll_thumb_hover", 6)

        # -- Panel --
        self.panel_bg = kw.get("panel_bg", 1)
        self.panel_border = kw.get("panel_border", 5)
        self.panel_title_bg = kw.get("panel_title_bg", 5)
        self.panel_title_fg = kw.get("panel_title_fg", 7)

        # -- Tab --
        self.tab_active_bg = kw.get("tab_active_bg", 1)
        self.tab_active_fg = kw.get("tab_active_fg", 7)
        self.tab_inactive_bg = kw.get("tab_inactive_bg", 0)
        self.tab_inactive_fg = kw.get("tab_inactive_fg", 13)

        # -- DropDown --
        self.dropdown_bg = kw.get("dropdown_bg", 0)
        self.dropdown_fg = kw.get("dropdown_fg", 7)
        self.dropdown_hover = kw.get("dropdown_hover", 5)
        self.dropdown_border = kw.get("dropdown_border", 5)

        # -- ListView --
        self.list_bg = kw.get("list_bg", 0)
        self.list_item = kw.get("list_item", 7)
        self.list_selected_bg = kw.get("list_selected_bg", 5)
        self.list_selected_fg = kw.get("list_selected_fg", 7)
        self.list_hover_bg = kw.get("list_hover_bg", 1)

        # -- Dialog / Modal --
        self.dialog_bg = kw.get("dialog_bg", 1)
        self.dialog_border = kw.get("dialog_border", 7)
        self.dialog_title = kw.get("dialog_title", 10)
        self.overlay = kw.get("overlay", 0)  # modal backdrop color

        # -- Tooltip --
        self.tooltip_bg = kw.get("tooltip_bg", 0)
        self.tooltip_fg = kw.get("tooltip_fg", 7)
        self.tooltip_border = kw.get("tooltip_border", 13)

        # -- Spacing & sizing --
        self.padding = kw.get("padding", 2)
        self.spacing = kw.get("spacing", 2)
        self.item_height = kw.get("item_height", 10)
        self._font = kw.get("font", _USE_DEFAULT)
        self._font_height = kw.get("font_height", 0)  # 0 = auto from font

    @property
    def font(self):
        """Current font. Returns Cozette by default, None for Pyxel built-in."""
        if self._font is _USE_DEFAULT:
            from .fonts import get_default_font
            return get_default_font()
        return self._font

    @font.setter
    def font(self, value):
        self._font = value

    @property
    def font_height(self):
        """Font line height in pixels."""
        if self._font_height > 0:
            return self._font_height
        if self._font is _USE_DEFAULT:
            from .fonts import DEFAULT_FONT_HEIGHT
            return DEFAULT_FONT_HEIGHT
        if self._font is None:
            return 6  # Pyxel built-in font
        # Estimate from font
        return max(6, self._font.text_width("M"))

    @font_height.setter
    def font_height(self, value):
        self._font_height = value

    def copy(self, **overrides):
        """Create a copy of this theme with overrides."""
        data = {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
        # Include private font/font_height as public keys
        data["font"] = overrides.pop("font", self._font)
        data["font_height"] = overrides.pop("font_height", self._font_height)
        data.update(overrides)
        return Theme(**data)

    @staticmethod
    def pyxel_default(**kw):
        """Create a theme using Pyxel's built-in 4x6 font."""
        kw.setdefault("font", None)
        kw.setdefault("font_height", 6)
        return Theme(**kw)


# ── Preset themes ──

THEME_DARK = Theme()

THEME_LIGHT = Theme(
    bg=7, surface=15, text=0, text_dim=5, text_disabled=13,
    primary=5, secondary=1, border=13, border_focus=5,
    btn_bg=13, btn_fg=0, btn_hover=5, btn_press=1,
    input_bg=7, input_fg=0, input_border=13, input_focus=5,
    input_cursor=0, input_placeholder=13,
    check_on=3, check_off=13, check_mark=7,
    slider_track=13, slider_fill=5, slider_thumb=0,
    progress_bg=13, progress_fill=3,
    panel_bg=15, panel_border=13, panel_title_bg=13, panel_title_fg=0,
    tab_active_bg=15, tab_active_fg=0, tab_inactive_bg=7, tab_inactive_fg=5,
    dropdown_bg=7, dropdown_fg=0, dropdown_hover=15, dropdown_border=13,
    list_bg=7, list_item=0, list_selected_bg=5, list_selected_fg=7,
    list_hover_bg=15,
    dialog_bg=15, dialog_border=0, dialog_title=1,
    tooltip_bg=0, tooltip_fg=7, tooltip_border=5,
)

THEME_NES = Theme(
    bg=0, surface=0, text=7, text_dim=6, text_disabled=1,
    primary=8, secondary=6, success=11, warning=9, danger=8,
    border=7, border_focus=8,
    btn_bg=8, btn_fg=7, btn_hover=9, btn_press=2,
    input_bg=0, input_fg=7, input_border=7, input_focus=8,
    check_on=8, check_off=7,
    panel_bg=0, panel_border=7, panel_title_bg=8, panel_title_fg=7,
)

THEME_GAMEBOY = Theme(
    bg=11, surface=3, text=0, text_dim=3, text_disabled=11,
    primary=0, secondary=3, success=3, warning=3, danger=0,
    border=0, border_focus=0,
    btn_bg=3, btn_fg=0, btn_hover=11, btn_press=0,
    btn_disabled_bg=11, btn_disabled_fg=3,
    input_bg=11, input_fg=0, input_border=0, input_focus=0,
    input_cursor=0, input_placeholder=3,
    check_on=0, check_off=3, check_mark=11,
    slider_track=3, slider_fill=0, slider_thumb=11,
    progress_bg=3, progress_fill=0,
    panel_bg=3, panel_border=0, panel_title_bg=0, panel_title_fg=11,
    tab_active_bg=3, tab_active_fg=0, tab_inactive_bg=11, tab_inactive_fg=0,
    dialog_bg=3, dialog_border=0, overlay=0,
)
