"""Text measurement utilities for font-aware rendering."""


def text_width(text, font=None):
    """Get pixel width of text string.

    Args:
        text: The text to measure.
        font: A ``pyxel.Font`` instance, or None for the built-in font.

    Returns:
        Width in pixels.
    """
    if not text:
        return 0
    if font is None:
        return len(text) * 4
    return font.text_width(text)


def text_height(font_height):
    """Return the line height value directly.

    This is a convenience wrapper -- the actual height is stored as
    ``theme.font_height`` (default 6 for the built-in font).
    """
    return font_height


def truncate_text(text, max_px, font=None):
    """Truncate *text* so its rendered width fits within *max_px* pixels.

    Returns the truncated string (no ellipsis -- Pyxel UIs are tight on
    space).
    """
    if not text:
        return text
    if text_width(text, font) <= max_px:
        return text
    # For the default (monospace) font, fast path
    if font is None:
        n = max(0, max_px // 4)
        return text[:n]
    # Variable-width: binary search
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if font.text_width(text[:mid]) <= max_px:
            lo = mid
        else:
            hi = mid - 1
    return text[:lo]


def char_at_x(text, px_offset, font=None):
    """Return the character index in *text* closest to pixel offset *px_offset*.

    Useful for click-to-cursor in text input widgets.
    """
    if not text:
        return 0
    if font is None:
        return min(len(text), max(0, px_offset) // 4)
    # Variable-width: walk forward
    for i in range(1, len(text) + 1):
        w = font.text_width(text[:i])
        if w > px_offset:
            # Check if click is closer to i-1 or i
            prev_w = font.text_width(text[:i - 1]) if i > 1 else 0
            if px_offset - prev_w < w - px_offset:
                return i - 1
            return i
    return len(text)


def text_x_at(text, index, font=None):
    """Return the pixel X offset for character *index* in *text*.

    Useful for cursor rendering in text input widgets.
    """
    if index <= 0 or not text:
        return 0
    sub = text[:index]
    if font is None:
        return len(sub) * 4
    return font.text_width(sub)
