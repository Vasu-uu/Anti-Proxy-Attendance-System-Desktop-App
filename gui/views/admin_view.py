"""
Admin Dashboard View
"""

import threading
import customtkinter as ctk
from gui import theme
from gui.api_client import api
from gui.widgets.stat_card import StatCard
from gui.widgets.badge import Badge


class AdminView(ctk.CTkFrame):

    def __init__(self, master, user: dict, on_nav=None, **kwargs):
        super().__init__(master, fg_color=theme.BG, **kwargs)
        self._user = user
        self._on_nav = on_nav  # callable(page_name) for sidebar nav
        self._data = None
        self._upload_day_enabled = False
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self._build_skeleton()
        self._refresh()

    # ── Skeleton ──────────────────────────────────────────────────────────────
    def _build_skeleton(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=theme.PAD_XL, pady=(theme.PAD_XL, 0))
        hdr.columnconfigure(0, weight=1)

        left = ctk.CTkFrame(hdr, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(left, text="Admin Overview",
                     font=theme.font(26, "bold"), text_color=theme.TEXT).pack(anchor="w")
        ctk.CTkLabel(left, text="System-wide metrics and configuration.",
                     font=theme.BODY, text_color=theme.TEXT_MUTED).pack(anchor="w", pady=(4, 0))

        btn_row = ctk.CTkFrame(hdr, fg_color="transparent")
        btn_row.grid(row=0, column=1, sticky="e")
        self._refresh_btn = ctk.CTkButton(
            btn_row, text="↻ Refresh", font=theme.SMALL, height=36, width=100,
            fg_color=theme.PRIMARY, hover_color=theme.PRIMARY_DARK,
            text_color=theme.TEXT, corner_radius=theme.RADIUS_MD,
            command=self._refresh,
        )
        self._refresh_btn.pack()

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
            data = api.get_admin_dashboard()
            try:
                upload_day = api.get_faculty_upload_day()
                enabled = upload_day.get("enabled", False)
            except Exception:
                enabled = False
            self.after(0, lambda: self._render(data, enabled))
        except Exception as e:
            self.after(0, lambda: self._loading.configure(text=f"Error: {e}"))
        finally:
            self.after(0, lambda: self._refresh_btn.configure(state="normal"))

    # ── Render ────────────────────────────────────────────────────────────────
    def _render(self, data: dict, upload_day: bool):
        self._data = data
        self._upload_day_enabled = upload_day
        for w in self._scroll.winfo_children():
            w.destroy()

        # ── Stat cards ────────────────────────────────────────────────────
        cards_row = ctk.CTkFrame(self._scroll, fg_color="transparent")
        cards_row.grid(row=0, column=0, sticky="ew")
        for i in range(4):
            cards_row.columnconfigure(i, weight=1)

        cards_info = [
            ("Total Students",  str(data.get("total_students", 0)),  "🎓", theme.PRIMARY),
            ("Active Classes",  str(data.get("active_classes", 0)),  "📚", theme.BLUE),
            ("Total Subjects",  str(data.get("total_subjects", 0)),  "📖", theme.PURPLE),
            ("Proxy Alerts",    str(data.get("proxy_alerts", 0)),    "⚠", theme.RED),
        ]
        for i, (lbl, val, icon, color) in enumerate(cards_info):
            StatCard(cards_row, label=lbl, value=val, icon_char=icon, accent=color).grid(
                row=0, column=i, padx=(0, 12) if i < 3 else 0, sticky="nsew"
            )

        # ── Two-column lower ──────────────────────────────────────────────
        lower = ctk.CTkFrame(self._scroll, fg_color="transparent")
        lower.grid(row=1, column=0, sticky="ew", pady=(20, 0))
        lower.columnconfigure(0, weight=1)
        lower.columnconfigure(1, weight=1)

        self._build_controls(lower, upload_day)
        self._build_actions(lower)

    # ── System controls panel ─────────────────────────────────────────────────
    def _build_controls(self, parent, upload_day: bool):
        panel = ctk.CTkFrame(
            parent, fg_color=theme.CARD, corner_radius=theme.RADIUS_LG,
            border_width=1, border_color=theme.BORDER,
        )
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        panel.columnconfigure(0, weight=1)

        ctk.CTkLabel(panel, text="System Controls",
                     font=theme.font(14, "bold"), text_color=theme.TEXT, anchor="w").grid(
            row=0, column=0, sticky="w", padx=theme.PAD_MD, pady=(theme.PAD_MD, 8))

        # ── Faculty upload day toggle ─────────────────────────────────────
        toggle_frame = ctk.CTkFrame(
            panel, fg_color=theme.BG, corner_radius=theme.RADIUS_SM,
            border_width=1, border_color=theme.BORDER,
        )
        toggle_frame.grid(row=1, column=0, sticky="ew", padx=theme.PAD_MD, pady=(0, 10))
        toggle_frame.columnconfigure(0, weight=1)

        info = ctk.CTkFrame(toggle_frame, fg_color="transparent")
        info.grid(row=0, column=0, padx=theme.PAD_MD, pady=theme.PAD_MD, sticky="w")
        ctk.CTkLabel(info, text="Classroom Upload Mode",
                     font=theme.font(12, "bold"), text_color=theme.TEXT).pack(anchor="w")
        ctk.CTkLabel(info, text="Faculty use class photos instead of live camera",
                     font=theme.TINY, text_color=theme.TEXT_DIM).pack(anchor="w", pady=(2, 0))

        self._toggle_var = ctk.BooleanVar(value=upload_day)
        self._toggle_lbl = ctk.CTkLabel(
            toggle_frame,
            text="ON" if upload_day else "OFF",
            font=theme.font(11, "bold"),
            text_color=theme.EMERALD if upload_day else theme.TEXT_DIM,
        )
        self._toggle_lbl.grid(row=0, column=1, padx=(0, 8))

        sw = ctk.CTkSwitch(
            toggle_frame,
            text="",
            variable=self._toggle_var,
            onvalue=True,
            offvalue=False,
            progress_color=theme.PRIMARY,
            button_color=theme.TEXT,
            button_hover_color=theme.PRIMARY,
            command=self._toggle_upload_day,
        )
        sw.grid(row=0, column=2, padx=(0, theme.PAD_MD), pady=theme.PAD_MD)

        self._toggle_result = ctk.CTkLabel(panel, text="", font=theme.SMALL,
                                            text_color=theme.TEXT_MUTED)
        self._toggle_result.grid(row=2, column=0, sticky="w", padx=theme.PAD_MD)

        # ── Add faculty button ────────────────────────────────────────────
        ctk.CTkFrame(panel, height=1, fg_color=theme.BORDER).grid(
            row=3, column=0, sticky="ew", padx=theme.PAD_MD, pady=12)

        ctk.CTkLabel(panel, text="Faculty Management",
                     font=theme.font(13, "bold"), text_color=theme.TEXT, anchor="w").grid(
            row=4, column=0, sticky="w", padx=theme.PAD_MD)

        ctk.CTkButton(
            panel,
            text="➕  Add New Faculty",
            font=theme.SMALL,
            height=40,
            fg_color=theme.CARD_ALT,
            hover_color=theme.BORDER,
            border_width=1, border_color=theme.BORDER,
            text_color=theme.TEXT,
            corner_radius=theme.RADIUS_MD,
            command=self._open_add_faculty,
        ).grid(row=5, column=0, sticky="ew", padx=theme.PAD_MD, pady=(10, theme.PAD_MD))

    # ── Quick actions panel ───────────────────────────────────────────────────
    def _build_actions(self, parent):
        panel = ctk.CTkFrame(
            parent, fg_color=theme.CARD, corner_radius=theme.RADIUS_LG,
            border_width=1, border_color=theme.BORDER,
        )
        panel.grid(row=0, column=1, sticky="nsew")
        panel.columnconfigure(0, weight=1)

        ctk.CTkLabel(panel, text="Quick Actions",
                     font=theme.font(14, "bold"), text_color=theme.TEXT, anchor="w").grid(
            row=0, column=0, sticky="w", padx=theme.PAD_MD, pady=(theme.PAD_MD, 8))

        actions = [
            ("🖥", theme.PRIMARY, "System Status",   "Camera, DB, and model health", "system_status"),
            ("📋", theme.BLUE,    "View Attendance",  "Per-class attendance records",  None),
            ("🗓", theme.EMERALD, "Edit Timetable",   "Update class schedules",        None),
            ("⚙", theme.PURPLE,  "System Config",    "Thresholds and camera settings",None),
        ]
        for i, (icon, color, title, sub, nav) in enumerate(actions):
            btn_frame = ctk.CTkFrame(
                panel, fg_color=theme.BG, corner_radius=theme.RADIUS_SM,
                border_width=1, border_color=theme.BORDER, cursor="hand2",
            )
            btn_frame.grid(row=i + 1, column=0, sticky="ew", padx=theme.PAD_MD,
                           pady=(0, 8))
            btn_frame.columnconfigure(1, weight=1)

            icon_bg = ctk.CTkFrame(btn_frame, width=38, height=38,
                                   corner_radius=10, fg_color=StatCard._make_bg(color))
            icon_bg.grid(row=0, column=0, padx=10, pady=10)
            icon_bg.grid_propagate(False)
            ctk.CTkLabel(icon_bg, text=icon, font=theme.font(16),
                         text_color=color, fg_color="transparent").place(
                relx=0.5, rely=0.5, anchor="center")

            info = ctk.CTkFrame(btn_frame, fg_color="transparent")
            info.grid(row=0, column=1, sticky="w", pady=10)
            ctk.CTkLabel(info, text=title, font=theme.font(12, "bold"),
                         text_color=theme.TEXT, anchor="w").pack(anchor="w")
            ctk.CTkLabel(info, text=sub, font=theme.TINY,
                         text_color=theme.TEXT_DIM, anchor="w").pack(anchor="w", pady=(2, 0))

            ctk.CTkLabel(btn_frame, text="›", font=theme.font(18),
                         text_color=theme.TEXT_DIM).grid(row=0, column=2, padx=12)

            if nav and self._on_nav:
                captured_nav = nav
                btn_frame.bind("<Button-1>", lambda e, n=captured_nav: self._on_nav(n))
                for child in btn_frame.winfo_children():
                    child.bind("<Button-1>", lambda e, n=captured_nav: self._on_nav(n))

    # ── Toggle upload day ─────────────────────────────────────────────────────
    def _toggle_upload_day(self):
        enabled = self._toggle_var.get()
        self._toggle_lbl.configure(
            text="ON" if enabled else "OFF",
            text_color=theme.EMERALD if enabled else theme.TEXT_DIM,
        )
        threading.Thread(target=self._do_toggle, args=(enabled,), daemon=True).start()

    def _do_toggle(self, enabled: bool):
        try:
            res = api.set_faculty_upload_day(enabled)
            msg = res.get("message", "Done")
            self.after(0, lambda: self._toggle_result.configure(text=msg))
        except Exception as e:
            self.after(0, lambda: self._toggle_result.configure(text=f"Error: {e}"))

    # ── Add faculty dialog ────────────────────────────────────────────────────
    def _open_add_faculty(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New Faculty")
        dialog.geometry("400x380")
        dialog.configure(fg_color=theme.CARD)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Add Faculty Member",
                     font=theme.HEADING, text_color=theme.TEXT).pack(padx=24, pady=(24, 4), anchor="w")

        inner = ctk.CTkFrame(dialog, fg_color="transparent")
        inner.pack(padx=24, fill="x")

        fields: dict[str, ctk.CTkEntry] = {}
        for label, ph in [("Full Name", "Dr. Jane Smith"),
                           ("Email", "faculty@college.edu"),
                           ("Password", "••••••••"),
                           ("Department", "Computer Science")]:
            ctk.CTkLabel(inner, text=label, font=theme.SMALL,
                         text_color=theme.TEXT_MUTED).pack(anchor="w", pady=(12, 2))
            e = ctk.CTkEntry(
                inner, placeholder_text=ph, font=theme.SMALL,
                height=40, fg_color=theme.BG, border_color=theme.BORDER,
                text_color=theme.TEXT, placeholder_text_color=theme.TEXT_DIM,
                show="•" if label == "Password" else "",
            )
            e.pack(fill="x")
            fields[label] = e

        result_lbl = ctk.CTkLabel(dialog, text="", font=theme.SMALL,
                                   text_color=theme.EMERALD)
        result_lbl.pack(pady=(8, 0), padx=24, anchor="w")

        def submit():
            name  = fields["Full Name"].get().strip()
            email = fields["Email"].get().strip()
            pw    = fields["Password"].get()
            dept  = fields["Department"].get().strip()
            if not all([name, email, pw, dept]):
                result_lbl.configure(text="All fields are required.", text_color=theme.YELLOW)
                return
            add_btn.configure(state="disabled", text="Adding…")
            threading.Thread(target=_do_add, daemon=True).start()

        def _do_add():
            try:
                res = api.add_faculty(
                    fields["Full Name"].get().strip(),
                    fields["Email"].get().strip(),
                    fields["Password"].get(),
                    fields["Department"].get().strip(),
                )
                if res.get("success"):
                    dialog.after(0, lambda: result_lbl.configure(
                        text="✅ Faculty added successfully.", text_color=theme.EMERALD))
                    dialog.after(0, self._refresh)
                else:
                    err = res.get("error", "Unknown error")
                    dialog.after(0, lambda: result_lbl.configure(
                        text=f"❌ {err}", text_color=theme.RED))
            except Exception as e:
                dialog.after(0, lambda: result_lbl.configure(text=f"Error: {e}", text_color=theme.RED))
            finally:
                dialog.after(0, lambda: add_btn.configure(state="normal", text="Add Faculty"))

        add_btn = ctk.CTkButton(
            dialog, text="Add Faculty",
            font=theme.font(13, "bold"), height=44,
            fg_color=theme.PRIMARY, hover_color=theme.PRIMARY_DARK,
            text_color=theme.TEXT, corner_radius=theme.RADIUS_MD,
            command=submit,
        )
        add_btn.pack(padx=24, pady=(16, 24), fill="x")
