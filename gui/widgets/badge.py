"""
Badge — a small pill/tag widget for status indicators.
"""

import customtkinter as ctk
from gui import theme


STATUS_STYLES = {
    "present":    (theme.EMERALD, theme.EMERALD_BG),
    "absent":     (theme.RED,     theme.RED_BG),
    "partial":    (theme.YELLOW,  theme.YELLOW_BG),
    "warning":    (theme.YELLOW,  theme.YELLOW_BG),
    "success":    (theme.EMERALD, theme.EMERALD_BG),
    "danger":     (theme.RED,     theme.RED_BG),
    "operational":(theme.EMERALD, theme.EMERALD_BG),
    "degraded":   (theme.YELLOW,  theme.YELLOW_BG),
    "active":     (theme.EMERALD, theme.EMERALD_BG),
    "inactive":   (theme.TEXT_MUTED, theme.CARD_ALT),
    "neutral":    (theme.TEXT_MUTED, theme.CARD_ALT),
    "pending":    (theme.TEXT_MUTED, theme.CARD_ALT),
}


class Badge(ctk.CTkLabel):
    """
    A pill-shaped status badge.  Usage:
        Badge(parent, status="present")  →  green  "Present"
        Badge(parent, text="Custom", status="warning")
    """

    def __init__(self, master, status: str = "neutral", text: str = None, **kwargs):
        status_key = status.lower()
        fg, bg = STATUS_STYLES.get(status_key, (theme.TEXT_MUTED, theme.CARD_ALT))
        label = text if text is not None else status.capitalize()

        super().__init__(
            master,
            text=f"  {label}  ",
            font=theme.font(10, "bold"),
            text_color=fg,
            fg_color=bg,
            corner_radius=6,
            **kwargs,
        )

    def set_status(self, status: str, text: str = None):
        status_key = status.lower()
        fg, bg = STATUS_STYLES.get(status_key, (theme.TEXT_MUTED, theme.CARD_ALT))
        label = text if text is not None else status.capitalize()
        self.configure(text=f"  {label}  ", text_color=fg, fg_color=bg)


class DotBadge(ctk.CTkFrame):
    """A glowing dot + label for live status (e.g. 'Camera Active')."""

    def __init__(self, master, status: str = "success", text: str = "Active", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        status_key = status.lower()
        color, _ = STATUS_STYLES.get(status_key, (theme.TEXT_MUTED, theme.CARD_ALT))

        self._dot = ctk.CTkFrame(self, width=10, height=10, corner_radius=5, fg_color=color)
        self._dot.grid(row=0, column=0, padx=(0, 6))
        self._dot.grid_propagate(False)

        self._lbl = ctk.CTkLabel(self, text=text, font=theme.SMALL, text_color=color)
        self._lbl.grid(row=0, column=1)

    def set_status(self, status: str, text: str):
        status_key = status.lower()
        color, _ = STATUS_STYLES.get(status_key, (theme.TEXT_MUTED, theme.CARD_ALT))
        self._dot.configure(fg_color=color)
        self._lbl.configure(text=text, text_color=color)
