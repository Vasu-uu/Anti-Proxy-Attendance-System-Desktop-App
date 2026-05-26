"""
System Status View — Admin only.
Auto-refreshes every 30 seconds.
"""

import threading
import customtkinter as ctk
from datetime import datetime

from gui import theme
from gui.api_client import api
from gui.widgets.badge import Badge, DotBadge


class SystemStatusView(ctk.CTkFrame):

    REFRESH_MS = 30_000  # 30 seconds

    def __init__(self, master, user: dict, **kwargs):
        super().__init__(master, fg_color=theme.BG, **kwargs)
        self._user = user
        self._after_id = None
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self._build_skeleton()
        self._refresh()

    def on_destroy(self):
        if self._after_id:
            self.after_cancel(self._after_id)

    # ── Skeleton ──────────────────────────────────────────────────────────────
    def _build_skeleton(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=theme.PAD_XL, pady=(theme.PAD_XL, 0))
        hdr.columnconfigure(0, weight=1)

        left = ctk.CTkFrame(hdr, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(left, text="System Status",
                     font=theme.font(26, "bold"), text_color=theme.TEXT).pack(anchor="w")
        ctk.CTkLabel(left, text="Real-time health check of all APCAS components.",
                     font=theme.BODY, text_color=theme.TEXT_MUTED).pack(anchor="w", pady=(4, 0))

        btn_row = ctk.CTkFrame(hdr, fg_color="transparent")
        btn_row.grid(row=0, column=1, sticky="e")

        self._last_checked = ctk.CTkLabel(btn_row, text="", font=theme.TINY,
                                           text_color=theme.TEXT_DIM)
        self._last_checked.pack(anchor="e")

        self._refresh_btn = ctk.CTkButton(
            btn_row, text="↻ Refresh Now", font=theme.SMALL, height=36,
            fg_color=theme.PRIMARY, hover_color=theme.PRIMARY_DARK,
            text_color=theme.TEXT, corner_radius=theme.RADIUS_MD,
            command=self._refresh,
        )
        self._refresh_btn.pack(pady=(6, 0))

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        scroll.grid(row=1, column=0, sticky="nsew", padx=theme.PAD_XL, pady=theme.PAD_LG)
        scroll.columnconfigure(0, weight=1)
        self._scroll = scroll

        self._loading = ctk.CTkLabel(scroll, text="Checking system status…",
                                      font=theme.BODY, text_color=theme.TEXT_MUTED)
        self._loading.grid(row=0, column=0, pady=60)

    # ── Data ──────────────────────────────────────────────────────────────────
    def _refresh(self):
        if self._after_id:
            self.after_cancel(self._after_id)
        self._refresh_btn.configure(state="disabled")
        threading.Thread(target=self._fetch, daemon=True).start()

    def _fetch(self):
        try:
            data = api.get_system_status()
            self.after(0, lambda: self._render(data))
        except Exception as e:
            self.after(0, lambda: self._loading.configure(text=f"Error fetching status: {e}"))
        finally:
            self.after(0, lambda: self._refresh_btn.configure(state="normal"))
            # Schedule next auto-refresh
            self._after_id = self.after(self.REFRESH_MS, self._refresh)

    # ── Render ────────────────────────────────────────────────────────────────
    def _render(self, data: dict):
        for w in self._scroll.winfo_children():
            w.destroy()

        ts = data.get("checked_at", "")
        if ts:
            try:
                dt = datetime.fromisoformat(ts)
                self._last_checked.configure(
                    text=f"Last checked: {dt.strftime('%H:%M:%S')}")
            except Exception:
                pass

        # ── Overall banner ────────────────────────────────────────────────
        overall = data.get("overall", {})
        o_state  = overall.get("state", "danger")
        o_label  = overall.get("label", "Unknown")

        banner_color = {
            "success": theme.EMERALD_BG,
            "warning": theme.YELLOW_BG,
            "danger":  theme.RED_BG,
        }.get(o_state, theme.CARD)

        banner_fg = {
            "success": theme.EMERALD,
            "warning": theme.YELLOW,
            "danger":  theme.RED,
        }.get(o_state, theme.TEXT)

        banner_icon = {"success": "✅", "warning": "⚠", "danger": "❌"}.get(o_state, "•")

        banner = ctk.CTkFrame(
            self._scroll, fg_color=banner_color,
            corner_radius=theme.RADIUS_LG,
            border_width=1,
            border_color=banner_fg + "30",
        )
        banner.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        banner.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            banner,
            text=f"  {banner_icon}  {o_label}",
            font=theme.font(16, "bold"),
            text_color=banner_fg,
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=theme.PAD_MD, pady=theme.PAD_MD)

        # ── Component cards ───────────────────────────────────────────────
        components = [
            ("database",       "🗄",  "Database"),
            ("face_embeddings","🧠",  "Face Embeddings"),
            ("camera",         "📷",  "Camera (Iriun)"),
            ("timetable",      "🗓",  "Timetable Data"),
        ]

        for row_idx, (key, icon, title) in enumerate(components):
            comp = data.get(key, {})
            state  = comp.get("state", "danger")
            label  = comp.get("label", "Unknown")
            detail = comp.get("detail", "")

            card = ctk.CTkFrame(
                self._scroll, fg_color=theme.CARD,
                corner_radius=theme.RADIUS_LG,
                border_width=1, border_color=theme.BORDER,
            )
            card.grid(row=row_idx + 1, column=0, sticky="ew", pady=(0, 12))
            card.columnconfigure(1, weight=1)

            # Icon badge
            icon_color = {
                "success": theme.EMERALD,
                "warning": theme.YELLOW,
                "danger":  theme.RED,
            }.get(state, theme.TEXT_MUTED)

            icon_bg = ctk.CTkFrame(
                card, width=44, height=44, corner_radius=12,
                fg_color=StatCard_bg(icon_color),
            )
            icon_bg.grid(row=0, column=0, rowspan=2, padx=theme.PAD_MD, pady=theme.PAD_MD)
            icon_bg.grid_propagate(False)
            ctk.CTkLabel(icon_bg, text=icon, font=theme.font(18),
                         text_color=icon_color, fg_color="transparent").place(
                relx=0.5, rely=0.5, anchor="center")

            # Title + detail
            ctk.CTkLabel(card, text=title, font=theme.font(13, "bold"),
                         text_color=theme.TEXT, anchor="w").grid(
                row=0, column=1, sticky="w", pady=(theme.PAD_MD, 2))
            ctk.CTkLabel(card, text=detail, font=theme.SMALL,
                         text_color=theme.TEXT_MUTED, anchor="w", wraplength=600).grid(
                row=1, column=1, sticky="w", pady=(0, theme.PAD_MD))

            # Status badge
            Badge(card, status=state, text=label).grid(
                row=0, column=2, rowspan=2, padx=theme.PAD_MD, pady=theme.PAD_MD, sticky="e")

        # ── Auto-refresh note ─────────────────────────────────────────────
        ctk.CTkLabel(
            self._scroll,
            text="Auto-refreshes every 30 seconds.",
            font=theme.TINY,
            text_color=theme.TEXT_DIM,
        ).grid(row=99, column=0, pady=(8, 0))


def StatCard_bg(hex_color: str) -> str:
    palette = {
        theme.PRIMARY: "#0d2d29",
        theme.EMERALD: "#052e16",
        theme.RED:     "#2d0a0a",
        theme.YELLOW:  "#291b00",
        theme.BLUE:    "#0c1c3b",
        theme.PURPLE:  "#1e0a3b",
    }
    return palette.get(hex_color, "#1a1a1a")
