"""
Faculty Dashboard View
"""

import threading
import customtkinter as ctk
from datetime import date, datetime
from tkinter import filedialog, messagebox

from gui import theme
from gui.api_client import api
from gui.widgets.stat_card import StatCard
from gui.widgets.badge import Badge, DotBadge
from gui.widgets.camera_feed import CameraFeed


class FacultyView(ctk.CTkFrame):

    def __init__(self, master, user: dict, **kwargs):
        super().__init__(master, fg_color=theme.BG, **kwargs)
        self._user = user
        self._data = None
        self._feed: CameraFeed | None = None
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self._build_skeleton()
        self._refresh()

    def on_destroy(self):
        if self._feed:
            self._feed.stop()

    # ── Skeleton ──────────────────────────────────────────────────────────────
    def _build_skeleton(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=theme.PAD_XL, pady=(theme.PAD_XL, 0))
        hdr.columnconfigure(0, weight=1)

        left = ctk.CTkFrame(hdr, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(left, text="Faculty Portal",
                     font=theme.font(26, "bold"), text_color=theme.TEXT).pack(anchor="w")
        ctk.CTkLabel(left, text=f"Welcome, {self._user.get('name', '')}  •  {self._user.get('department', '')}",
                     font=theme.BODY, text_color=theme.TEXT_MUTED).pack(anchor="w", pady=(4, 0))

        btn_row = ctk.CTkFrame(hdr, fg_color="transparent")
        btn_row.grid(row=0, column=1, sticky="e")
        self._upload_btn = ctk.CTkButton(
            btn_row,
            text="📤 Offline Upload",
            font=theme.SMALL,
            height=36, width=140,
            fg_color=theme.CARD,
            hover_color=theme.CARD_ALT,
            border_width=1, border_color=theme.BORDER,
            text_color=theme.TEXT,
            corner_radius=theme.RADIUS_MD,
            command=self._open_upload_dialog,
        )
        self._upload_btn.pack(side="left", padx=(0, 8))
        self._refresh_btn = ctk.CTkButton(
            btn_row, text="↻ Refresh", font=theme.SMALL, height=36, width=100,
            fg_color=theme.PRIMARY, hover_color=theme.PRIMARY_DARK,
            text_color=theme.TEXT, corner_radius=theme.RADIUS_MD,
            command=self._refresh,
        )
        self._refresh_btn.pack(side="left")

        # Scroll area
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        scroll.grid(row=1, column=0, sticky="nsew", padx=theme.PAD_XL, pady=theme.PAD_LG)
        scroll.columnconfigure(0, weight=1)
        self._scroll = scroll

        self._loading = ctk.CTkLabel(scroll, text="Loading…", font=theme.BODY,
                                     text_color=theme.TEXT_MUTED)
        self._loading.grid(row=0, column=0, pady=60)

    # ── Data ──────────────────────────────────────────────────────────────────
    def _refresh(self):
        self._refresh_btn.configure(state="disabled")
        threading.Thread(target=self._fetch, daemon=True).start()

    def _fetch(self):
        try:
            data = api.get_faculty_dashboard()
            self.after(0, lambda: self._render(data))
        except Exception as e:
            self.after(0, lambda: self._loading.configure(text=f"Error: {e}"))
        finally:
            self.after(0, lambda: self._refresh_btn.configure(state="normal"))

    # ── Render ────────────────────────────────────────────────────────────────
    def _render(self, data: dict):
        self._data = data
        for w in self._scroll.winfo_children():
            w.destroy()

        total   = data.get("total_students", 0)
        present = data.get("present_count", 0)
        absent  = data.get("absent_count", 0)
        cls     = data.get("selected_class", "—")
        sel_date = data.get("selected_date", date.today().isoformat())

        # ── Stat cards ────────────────────────────────────────────────────
        cards_row = ctk.CTkFrame(self._scroll, fg_color="transparent")
        cards_row.grid(row=0, column=0, sticky="ew")
        for i in range(3):
            cards_row.columnconfigure(i, weight=1)

        cards_info = [
            ("Total Students", str(total),   "👤", theme.BLUE),
            ("Present Today",  str(present), "✅", theme.EMERALD),
            ("Absent Today",   str(absent),  "❌", theme.RED),
        ]
        for i, (lbl, val, icon, color) in enumerate(cards_info):
            StatCard(cards_row, label=lbl, value=val, icon_char=icon, accent=color).grid(
                row=0, column=i, padx=(0, 12) if i < 2 else 0, sticky="nsew"
            )

        # ── Two-column lower ──────────────────────────────────────────────
        lower = ctk.CTkFrame(self._scroll, fg_color="transparent")
        lower.grid(row=1, column=0, sticky="ew", pady=(20, 0))
        lower.columnconfigure(0, weight=2)
        lower.columnconfigure(1, weight=1)

        self._build_camera_panel(lower, cls, sel_date, present, total)
        self._build_roster(lower, data.get("students_list", []))

    # ── Camera / session panel ────────────────────────────────────────────────
    def _build_camera_panel(self, parent, cls, sel_date, present, total):
        panel = ctk.CTkFrame(
            parent, fg_color=theme.CARD, corner_radius=theme.RADIUS_LG,
            border_width=1, border_color=theme.BORDER,
        )
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        panel.columnconfigure(0, weight=1)

        # Panel header
        ph = ctk.CTkFrame(panel, fg_color="transparent")
        ph.grid(row=0, column=0, sticky="ew", padx=theme.PAD_MD, pady=(theme.PAD_MD, 0))
        ph.columnconfigure(0, weight=1)
        ctk.CTkLabel(ph, text=f"Live Session: {cls}",
                     font=theme.font(14, "bold"), text_color=theme.TEXT, anchor="w").grid(
            row=0, column=0, sticky="w")
        DotBadge(ph, status="success", text="Camera Active").grid(row=0, column=1, sticky="e")

        # Camera feed
        self._feed = CameraFeed(panel, width=560, height=315)
        self._feed.grid(row=1, column=0, padx=theme.PAD_MD, pady=(12, 0), sticky="ew")
        self._feed.start()

        # Session footer
        footer = ctk.CTkFrame(
            panel, fg_color=theme.BG, corner_radius=theme.RADIUS_SM,
            border_width=1, border_color=theme.BORDER,
        )
        footer.grid(row=2, column=0, sticky="ew", padx=theme.PAD_MD, pady=theme.PAD_MD)
        footer.columnconfigure(1, weight=1)

        stats = ctk.CTkFrame(footer, fg_color="transparent")
        stats.grid(row=0, column=0, padx=theme.PAD_MD, pady=12, sticky="w")
        for label, val, color in [("Total", str(total), theme.TEXT),
                                    ("Detected", str(present), theme.EMERALD)]:
            col = ctk.CTkFrame(stats, fg_color="transparent")
            col.pack(side="left", padx=20)
            ctk.CTkLabel(col, text=label, font=theme.TINY,
                         text_color=theme.TEXT_DIM).pack()
            ctk.CTkLabel(col, text=val, font=theme.font(20, "bold"),
                         text_color=color).pack()

        ctk.CTkLabel(footer, text=f"Date: {sel_date}",
                     font=theme.SMALL, text_color=theme.TEXT_MUTED).grid(
            row=0, column=1, sticky="e", padx=theme.PAD_MD)

    # ── Class roster ──────────────────────────────────────────────────────────
    def _build_roster(self, parent, students: list):
        panel = ctk.CTkFrame(
            parent, fg_color=theme.CARD, corner_radius=theme.RADIUS_LG,
            border_width=1, border_color=theme.BORDER,
        )
        panel.grid(row=0, column=1, sticky="nsew")
        panel.columnconfigure(0, weight=1)

        ctk.CTkLabel(panel, text="Class Roster",
                     font=theme.font(14, "bold"), text_color=theme.TEXT, anchor="w").grid(
            row=0, column=0, sticky="w", padx=theme.PAD_MD, pady=(theme.PAD_MD, 0))

        scroll = ctk.CTkScrollableFrame(panel, fg_color="transparent", height=420)
        scroll.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        scroll.columnconfigure(0, weight=1)

        if not students:
            ctk.CTkLabel(scroll, text="No students found.",
                         font=theme.BODY, text_color=theme.TEXT_MUTED).grid(pady=40)
            return

        for i, s in enumerate(students):
            row = ctk.CTkFrame(
                scroll, fg_color=theme.BG, corner_radius=theme.RADIUS_SM,
                border_width=1, border_color=theme.BORDER,
            )
            row.grid(row=i, column=0, sticky="ew", pady=(0, 6))
            row.columnconfigure(1, weight=1)

            # Avatar
            av = ctk.CTkFrame(row, width=32, height=32, corner_radius=16,
                               fg_color=theme.PRIMARY_BADGE)
            av.grid(row=0, column=0, padx=(10, 0), pady=8)
            av.grid_propagate(False)
            ctk.CTkLabel(av, text=s.get("name", "?")[0].upper(),
                         font=theme.font(12, "bold"), text_color=theme.PRIMARY).place(
                relx=0.5, rely=0.5, anchor="center")

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.grid(row=0, column=1, sticky="w", padx=10)
            ctk.CTkLabel(info, text=s.get("name", "—"),
                         font=theme.font(12, "bold"), text_color=theme.TEXT).pack(anchor="w")
            ctk.CTkLabel(info, text=s.get("roll_no", ""),
                         font=theme.TINY, text_color=theme.TEXT_DIM).pack(anchor="w")

            status = s.get("status", "Absent")
            status_key = "present" if status == "Present" else "absent"
            Badge(row, status=status_key, text=status).grid(row=0, column=2, padx=10, pady=8)

    # ── Offline upload dialog ─────────────────────────────────────────────────
    def _open_upload_dialog(self):
        if not self._data:
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Offline Attendance Upload")
        dialog.geometry("420x380")
        dialog.configure(fg_color=theme.CARD)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Upload Class Photo",
                     font=theme.HEADING, text_color=theme.TEXT).pack(padx=24, pady=(24, 4), anchor="w")
        ctk.CTkLabel(dialog, text="Select a photo to mark attendance via face recognition.",
                     font=theme.SMALL, text_color=theme.TEXT_MUTED, wraplength=360).pack(padx=24, anchor="w")

        inner = ctk.CTkFrame(dialog, fg_color="transparent")
        inner.pack(padx=24, pady=16, fill="x")
        inner.columnconfigure(1, weight=1)

        # Class selector
        classes = self._data.get("available_classes", [])
        class_var = ctk.StringVar(value=classes[0] if classes else "")
        ctk.CTkLabel(inner, text="Class:", font=theme.SMALL,
                     text_color=theme.TEXT_MUTED).grid(row=0, column=0, sticky="w", pady=6)
        ctk.CTkOptionMenu(
            inner, variable=class_var, values=classes,
            fg_color=theme.BG, button_color=theme.PRIMARY,
            dropdown_fg_color=theme.CARD, font=theme.SMALL,
            text_color=theme.TEXT,
        ).grid(row=0, column=1, sticky="ew", padx=(12, 0), pady=6)

        # Period selector
        periods = [str(p["period_number"]) for p in self._data.get("faculty_today_periods", [])] or [str(i) for i in range(1, 7)]
        period_var = ctk.StringVar(value=periods[0] if periods else "1")
        ctk.CTkLabel(inner, text="Period:", font=theme.SMALL,
                     text_color=theme.TEXT_MUTED).grid(row=1, column=0, sticky="w", pady=6)
        ctk.CTkOptionMenu(
            inner, variable=period_var, values=periods,
            fg_color=theme.BG, button_color=theme.PRIMARY,
            dropdown_fg_color=theme.CARD, font=theme.SMALL,
            text_color=theme.TEXT,
        ).grid(row=1, column=1, sticky="ew", padx=(12, 0), pady=6)

        # Date
        date_var = ctk.StringVar(value=date.today().isoformat())
        ctk.CTkLabel(inner, text="Date:", font=theme.SMALL,
                     text_color=theme.TEXT_MUTED).grid(row=2, column=0, sticky="w", pady=6)
        ctk.CTkEntry(inner, textvariable=date_var, font=theme.SMALL,
                     fg_color=theme.BG, border_color=theme.BORDER,
                     text_color=theme.TEXT).grid(row=2, column=1, sticky="ew", padx=(12, 0), pady=6)

        # File picker
        file_var = ctk.StringVar(value="No file selected")
        ctk.CTkLabel(inner, text="Photo:", font=theme.SMALL,
                     text_color=theme.TEXT_MUTED).grid(row=3, column=0, sticky="w", pady=6)
        file_row = ctk.CTkFrame(inner, fg_color="transparent")
        file_row.grid(row=3, column=1, sticky="ew", padx=(12, 0), pady=6)
        file_row.columnconfigure(0, weight=1)

        file_lbl = ctk.CTkLabel(file_row, textvariable=file_var,
                                 font=theme.TINY, text_color=theme.TEXT_DIM, anchor="w")
        file_lbl.grid(row=0, column=0, sticky="w")

        selected_path = [None]

        def pick_file():
            path = filedialog.askopenfilename(
                title="Select class photo",
                filetypes=[("Images", "*.jpg *.jpeg *.png")],
            )
            if path:
                selected_path[0] = path
                file_var.set(path.split("/")[-1])

        ctk.CTkButton(file_row, text="Browse", font=theme.SMALL, height=28, width=70,
                      fg_color=theme.CARD, hover_color=theme.CARD_ALT,
                      border_width=1, border_color=theme.BORDER,
                      text_color=theme.TEXT, command=pick_file).grid(row=0, column=1, padx=(8, 0))

        # Result label
        result_lbl = ctk.CTkLabel(dialog, text="", font=theme.SMALL,
                                   text_color=theme.EMERALD, wraplength=360)
        result_lbl.pack(padx=24)

        def submit():
            if not selected_path[0]:
                result_lbl.configure(text="Please select a photo file.", text_color=theme.YELLOW)
                return
            submit_btn.configure(state="disabled", text="Processing…")
            threading.Thread(
                target=_do_upload,
                args=(selected_path[0], class_var.get(), period_var.get(), date_var.get()),
                daemon=True,
            ).start()

        def _do_upload(path, cls, period, dt):
            try:
                res = api.offline_attendance(path, cls, period, dt)
                if res.get("success"):
                    msg = f"✅ Done! Detected: {res.get('detected', 0)}, Absent: {res.get('absent', 0)}"
                    dialog.after(0, lambda: result_lbl.configure(text=msg, text_color=theme.EMERALD))
                    dialog.after(0, self._refresh)
                else:
                    dialog.after(0, lambda: result_lbl.configure(
                        text=f"❌ {res.get('error', 'Unknown error')}", text_color=theme.RED))
            except Exception as e:
                dialog.after(0, lambda: result_lbl.configure(text=f"Error: {e}", text_color=theme.RED))
            finally:
                dialog.after(0, lambda: submit_btn.configure(state="normal", text="Upload & Process"))

        submit_btn = ctk.CTkButton(
            dialog, text="Upload & Process",
            font=theme.font(13, "bold"), height=44,
            fg_color=theme.PRIMARY, hover_color=theme.PRIMARY_DARK,
            text_color=theme.TEXT, corner_radius=theme.RADIUS_MD,
            command=submit,
        )
        submit_btn.pack(padx=24, pady=(12, 24), fill="x")
