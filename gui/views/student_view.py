"""
Student Dashboard View
"""

import threading
import customtkinter as ctk
from datetime import datetime

from gui import theme
from gui.api_client import api
from gui.widgets.stat_card import StatCard
from gui.widgets.badge import Badge


class StudentView(ctk.CTkFrame):

    def __init__(self, master, user: dict, **kwargs):
        super().__init__(master, fg_color=theme.BG, **kwargs)
        self._user = user
        self._data = None
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self._build_skeleton()
        self._refresh()

    # ── Skeleton layout ───────────────────────────────────────────────────────
    def _build_skeleton(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=theme.PAD_XL, pady=(theme.PAD_XL, 0))
        hdr.columnconfigure(0, weight=1)

        left = ctk.CTkFrame(hdr, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")
        self._greeting = ctk.CTkLabel(
            left,
            text=f"Hello, {self._user.get('name', 'Student')} 👋",
            font=theme.font(26, "bold"),
            text_color=theme.TEXT,
            anchor="w",
        )
        self._greeting.pack(anchor="w")
        ctk.CTkLabel(
            left,
            text="Here's your attendance overview for today.",
            font=theme.BODY,
            text_color=theme.TEXT_MUTED,
        ).pack(anchor="w", pady=(4, 0))

        right = ctk.CTkFrame(hdr, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e")
        self._date_lbl = ctk.CTkLabel(
            right,
            text=datetime.now().strftime("%A, %d %B %Y"),
            font=theme.SMALL,
            text_color=theme.TEXT_MUTED,
        )
        self._date_lbl.pack()
        self._refresh_btn = ctk.CTkButton(
            right, text="↻ Refresh", font=theme.SMALL, height=30, width=90,
            fg_color=theme.CARD, hover_color=theme.CARD_ALT,
            border_width=1, border_color=theme.BORDER,
            text_color=theme.TEXT_MUTED, corner_radius=8,
            command=self._refresh,
        )
        self._refresh_btn.pack(pady=(6, 0))

        # Scroll container
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        scroll.grid(row=1, column=0, sticky="nsew", padx=theme.PAD_XL, pady=theme.PAD_LG)
        scroll.columnconfigure(0, weight=1)
        self._scroll = scroll

        # Loading label
        self._loading = ctk.CTkLabel(
            scroll, text="Loading…", font=theme.BODY, text_color=theme.TEXT_MUTED
        )
        self._loading.grid(row=0, column=0, pady=60)

    # ── Data refresh ──────────────────────────────────────────────────────────
    def _refresh(self):
        self._refresh_btn.configure(state="disabled")
        threading.Thread(target=self._fetch, daemon=True).start()

    def _fetch(self):
        try:
            data = api.get_student_dashboard()
            self.after(0, lambda: self._render(data))
        except Exception as e:
            self.after(0, lambda: self._loading.configure(text=f"Error: {e}"))
        finally:
            self.after(0, lambda: self._refresh_btn.configure(state="normal"))

    # ── Render ────────────────────────────────────────────────────────────────
    def _render(self, data: dict):
        self._data = data
        # Clear scroll
        for w in self._scroll.winfo_children():
            w.destroy()

        # ── Stat cards row ────────────────────────────────────────────────
        cards_row = ctk.CTkFrame(self._scroll, fg_color="transparent")
        cards_row.grid(row=0, column=0, sticky="ew")
        for i in range(4):
            cards_row.columnconfigure(i, weight=1)

        overall_pct = data.get("overall_pct", 0)
        attended    = data.get("classes_attended", 0)
        missed      = data.get("classes_missed", 0)
        today_s     = data.get("today_status", "Not Marked")

        # Colour the attendance percentage
        if overall_pct >= 75:
            pct_color = theme.EMERALD
        elif overall_pct >= 60:
            pct_color = theme.YELLOW
        else:
            pct_color = theme.RED

        cards_info = [
            ("Overall Attendance", f"{overall_pct}%",   "📊", pct_color),
            ("Classes Attended",   str(attended),         "✅", theme.EMERALD),
            ("Classes Missed",     str(missed),           "❌", theme.RED),
            ("Today's Status",     today_s,               "🕐", theme.BLUE),
        ]
        self._stat_cards = []
        for i, (lbl, val, icon, color) in enumerate(cards_info):
            card = StatCard(cards_row, label=lbl, value=val, icon_char=icon, accent=color)
            card.grid(row=0, column=i, padx=(0, 12) if i < 3 else 0, sticky="nsew")
            self._stat_cards.append(card)

        # ── Attendance progress bar ───────────────────────────────────────
        prog_frame = ctk.CTkFrame(
            self._scroll,
            fg_color=theme.CARD,
            corner_radius=theme.RADIUS_LG,
            border_width=1,
            border_color=theme.BORDER,
        )
        prog_frame.grid(row=1, column=0, sticky="ew", pady=(20, 0))
        prog_frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(
            prog_frame,
            text="Attendance Progress",
            font=theme.font(13, "bold"),
            text_color=theme.TEXT,
            anchor="w",
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=theme.PAD_MD, pady=(theme.PAD_MD, 6))

        ctk.CTkLabel(
            prog_frame, text=f"{overall_pct}%",
            font=theme.font(11), text_color=pct_color,
        ).grid(row=1, column=0, sticky="w", padx=theme.PAD_MD)

        bar = ctk.CTkProgressBar(
            prog_frame,
            height=10,
            corner_radius=5,
            fg_color=theme.BG,
            progress_color=pct_color,
        )
        bar.set(overall_pct / 100)
        bar.grid(row=1, column=1, sticky="ew", padx=8, pady=(0, theme.PAD_MD))

        req_lbl = "75% required"
        ctk.CTkLabel(
            prog_frame, text=req_lbl, font=theme.TINY, text_color=theme.TEXT_DIM,
        ).grid(row=1, column=2, sticky="e", padx=theme.PAD_MD)

        # ── Two-column lower section ──────────────────────────────────────
        lower = ctk.CTkFrame(self._scroll, fg_color="transparent")
        lower.grid(row=2, column=0, sticky="ew", pady=(20, 0))
        lower.columnconfigure(0, weight=2)
        lower.columnconfigure(1, weight=1)

        self._build_schedule(lower, data.get("today_classes", []))
        self._build_summary(lower, data)

    # ── Today's schedule panel ────────────────────────────────────────────────
    def _build_schedule(self, parent, classes: list):
        panel = ctk.CTkFrame(
            parent,
            fg_color=theme.CARD,
            corner_radius=theme.RADIUS_LG,
            border_width=1,
            border_color=theme.BORDER,
        )
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        panel.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            panel, text="Today's Schedule",
            font=theme.font(14, "bold"), text_color=theme.TEXT, anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=theme.PAD_MD, pady=(theme.PAD_MD, 8))

        if not classes:
            ctk.CTkLabel(
                panel, text="No classes scheduled today.",
                font=theme.BODY, text_color=theme.TEXT_MUTED,
            ).grid(row=1, column=0, pady=30)
            return

        for i, cls in enumerate(classes):
            is_current = cls.get("current", False)
            row_bg = theme.PRIMARY_GLOW if is_current else theme.BG
            border  = theme.PRIMARY if is_current else theme.BORDER

            row_frame = ctk.CTkFrame(
                panel, fg_color=row_bg, corner_radius=theme.RADIUS_SM,
                border_width=1, border_color=border,
            )
            row_frame.grid(row=i + 1, column=0, sticky="ew", padx=theme.PAD_MD,
                           pady=(0, 8))
            row_frame.columnconfigure(1, weight=1)

            # Accent stripe
            stripe = ctk.CTkFrame(row_frame, width=4, fg_color=theme.PRIMARY, corner_radius=2)
            stripe.grid(row=0, column=0, sticky="ns", padx=(8, 0), pady=8)
            stripe.grid_propagate(False)

            info = ctk.CTkFrame(row_frame, fg_color="transparent")
            info.grid(row=0, column=1, sticky="w", padx=10, pady=10)

            subj_row = ctk.CTkFrame(info, fg_color="transparent")
            subj_row.pack(anchor="w")
            ctk.CTkLabel(
                subj_row, text=cls.get("subject", "—"),
                font=theme.font(13, "bold"), text_color=theme.TEXT,
            ).pack(side="left")
            if is_current:
                ctk.CTkLabel(
                    subj_row, text="  ● Ongoing",
                    font=theme.TINY, text_color=theme.PRIMARY,
                ).pack(side="left")

            ctk.CTkLabel(
                info, text=f"{cls.get('time', '')}  •  {cls.get('type', 'Lecture')}",
                font=theme.SMALL, text_color=theme.TEXT_MUTED,
            ).pack(anchor="w", pady=(2, 0))

            # Status badge
            status = cls.get("status", "Pending")
            status_map = {"Present": "present", "Absent": "absent",
                          "Not Marked": "neutral", "Pending": "pending"}
            Badge(
                row_frame, status=status_map.get(status, "neutral"), text=status
            ).grid(row=0, column=2, padx=12, pady=10, sticky="e")

    # ── Summary / recent activity ──────────────────────────────────────────────
    def _build_summary(self, parent, data: dict):
        panel = ctk.CTkFrame(
            parent,
            fg_color=theme.CARD,
            corner_radius=theme.RADIUS_LG,
            border_width=1,
            border_color=theme.BORDER,
        )
        panel.grid(row=0, column=1, sticky="nsew")
        panel.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            panel, text="Current Period",
            font=theme.font(14, "bold"), text_color=theme.TEXT, anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=theme.PAD_MD, pady=(theme.PAD_MD, 0))

        period_text = data.get("current_period", "No Active Period")
        ctk.CTkLabel(
            panel, text=period_text,
            font=theme.BODY, text_color=theme.PRIMARY, wraplength=200, justify="left",
        ).grid(row=1, column=0, sticky="w", padx=theme.PAD_MD, pady=(4, theme.PAD_MD))

        sep = ctk.CTkFrame(panel, height=1, fg_color=theme.BORDER)
        sep.grid(row=2, column=0, sticky="ew", padx=theme.PAD_MD)

        # Stats
        stats = [
            ("Total Classes", str(data.get("total_classes", 0))),
            ("Present",       str(data.get("classes_attended", 0))),
            ("Absent",        str(data.get("classes_missed", 0))),
        ]
        for i, (lbl, val) in enumerate(stats):
            r = ctk.CTkFrame(panel, fg_color="transparent")
            r.grid(row=3 + i, column=0, sticky="ew", padx=theme.PAD_MD, pady=6)
            r.columnconfigure(1, weight=1)
            ctk.CTkLabel(r, text=lbl, font=theme.SMALL,
                         text_color=theme.TEXT_MUTED).grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(r, text=val, font=theme.font(13, "bold"),
                         text_color=theme.TEXT).grid(row=0, column=1, sticky="e")

        ctk.CTkFrame(panel, fg_color="transparent", height=8).grid(row=99, column=0)
