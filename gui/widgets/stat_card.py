"""
StatCard — a metric card widget with icon, value, and label.
Matches the card style from the React dashboard.
"""

import customtkinter as ctk
from gui import theme


class StatCard(ctk.CTkFrame):
    """
    A dark card displaying a metric:
      ┌─────────────────────────┐
      │  [icon_char]  Label     │
      │  Value                  │
      │  sub_label              │
      └─────────────────────────┘
    """

    def __init__(
        self,
        master,
        label: str = "Label",
        value: str = "—",
        icon_char: str = "◆",
        accent: str = theme.PRIMARY,
        sub_label: str = "",
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color=theme.CARD,
            corner_radius=theme.RADIUS_LG,
            border_width=1,
            border_color=theme.BORDER,
            **kwargs,
        )
        self._accent = accent
        self._build(label, value, icon_char, accent, sub_label)

    def _build(self, label, value, icon_char, accent, sub_label):
        self.columnconfigure(0, weight=1)

        # ── Icon badge row ───────────────────────────────────────────────
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=theme.PAD_MD, pady=(theme.PAD_MD, 4))
        top.columnconfigure(1, weight=1)

        icon_bg = ctk.CTkFrame(
            top,
            width=36, height=36,
            fg_color=self._make_bg(accent),
            corner_radius=10,
        )
        icon_bg.grid(row=0, column=0, sticky="w")
        icon_bg.grid_propagate(False)
        ctk.CTkLabel(
            icon_bg, text=icon_char, font=theme.font(16),
            text_color=accent, fg_color="transparent",
        ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            top, text=label, font=theme.SMALL,
            text_color=theme.TEXT_MUTED, anchor="w",
        ).grid(row=0, column=1, sticky="w", padx=(10, 0))

        # ── Value ────────────────────────────────────────────────────────
        self._value_lbl = ctk.CTkLabel(
            self, text=value, font=theme.font(28, "bold"),
            text_color=theme.TEXT, anchor="w",
        )
        self._value_lbl.grid(row=1, column=0, sticky="w", padx=theme.PAD_MD)

        # ── Sub-label ────────────────────────────────────────────────────
        if sub_label:
            ctk.CTkLabel(
                self, text=sub_label, font=theme.TINY,
                text_color=theme.TEXT_DIM, anchor="w",
            ).grid(row=2, column=0, sticky="w", padx=theme.PAD_MD, pady=(0, theme.PAD_MD))
        else:
            ctk.CTkFrame(self, height=theme.PAD_MD, fg_color="transparent").grid(row=2, column=0)

    @staticmethod
    def _make_bg(hex_color: str) -> str:
        """Return hex_color at ~12% opacity by blending with card bg."""
        # We simply return a slightly transparent version via a known dark-tinted hex
        palette = {
            theme.PRIMARY: "#0d2d29",
            theme.EMERALD: "#052e16",
            theme.RED: "#2d0a0a",
            theme.YELLOW: "#291b00",
            theme.BLUE: "#0c1c3b",
            theme.PURPLE: "#1e0a3b",
        }
        return palette.get(hex_color, "#1a1a1a")

    def update_value(self, value: str):
        self._value_lbl.configure(text=value)
