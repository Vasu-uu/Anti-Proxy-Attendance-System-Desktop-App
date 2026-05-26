"""
APCAS Main Application Window
Handles sidebar navigation, page switching, and auth state.
"""

import customtkinter as ctk
from datetime import datetime
from gui import theme
from gui.api_client import api
from gui.views.login_view import LoginView
from gui.views.student_view import StudentView
from gui.views.faculty_view import FacultyView
from gui.views.admin_view import AdminView
from gui.views.system_status_view import SystemStatusView

# ── CustomTkinter global settings ─────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


class APCASApp(ctk.CTk):
    """
    Root window.  Layout:
      ┌──────────┬──────────────────────────────────────────┐
      │ Sidebar  │  Page frame (swapped on navigation)      │
      │ (fixed)  │                                          │
      └──────────┴──────────────────────────────────────────┘
    """

    TITLE = "APCAS — Attendance Platform"
    MIN_W, MIN_H = 1100, 680

    def __init__(self):
        super().__init__()
        self.title(self.TITLE)
        self.minsize(self.MIN_W, self.MIN_H)
        self.geometry("1280x760")
        self.configure(fg_color=theme.BG)

        self._user: dict | None = None
        self._current_view = None
        self._nav_btns: dict[str, ctk.CTkButton] = {}
        self._active_page: str = ""

        # Root grid: sidebar | content
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Build sidebar (hidden until logged in)
        self._sidebar = self._build_sidebar()
        self._sidebar.grid(row=0, column=0, sticky="nsew")
        self._sidebar.grid_remove()

        # Content area
        self._content = ctk.CTkFrame(self, fg_color=theme.BG, corner_radius=0)
        self._content.grid(row=0, column=1, sticky="nsew")
        self._content.columnconfigure(0, weight=1)
        self._content.rowconfigure(0, weight=1)

        # Start with login
        self._show_login()

        # Clock tick
        self._tick_clock()

    # ─────────────────────────────────────────────────────────────────────────
    # Sidebar
    # ─────────────────────────────────────────────────────────────────────────
    def _build_sidebar(self) -> ctk.CTkFrame:
        sb = ctk.CTkFrame(
            self,
            width=theme.SIDEBAR_W,
            fg_color=theme.SIDEBAR_BG,
            corner_radius=0,
            border_width=1,
            border_color=theme.BORDER,
        )
        sb.grid_propagate(False)
        sb.columnconfigure(0, weight=1)
        sb.rowconfigure(2, weight=1)  # nav list expands

        # ── Logo ─────────────────────────────────────────────────────────
        logo_row = ctk.CTkFrame(sb, fg_color="transparent")
        logo_row.grid(row=0, column=0, sticky="ew", padx=16, pady=(20, 0))
        logo_row.columnconfigure(1, weight=1)

        logo_bg = ctk.CTkFrame(logo_row, width=38, height=38, corner_radius=10,
                               fg_color=theme.PRIMARY_DARK)
        logo_bg.grid(row=0, column=0)
        logo_bg.grid_propagate(False)
        ctk.CTkLabel(logo_bg, text="◈", font=theme.font(18, "bold"),
                     text_color=theme.TEXT, fg_color="transparent").place(
            relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(logo_row, text="APCAS",
                     font=theme.font(16, "bold"), text_color=theme.TEXT).grid(
            row=0, column=1, sticky="w", padx=10)

        # ── User info card ────────────────────────────────────────────────
        self._user_card = ctk.CTkFrame(sb, fg_color=theme.CARD, corner_radius=theme.RADIUS_MD,
                                        border_width=1, border_color=theme.BORDER)
        self._user_card.grid(row=1, column=0, sticky="ew", padx=12, pady=16)
        self._user_card.columnconfigure(1, weight=1)

        self._avatar = ctk.CTkFrame(self._user_card, width=34, height=34, corner_radius=17,
                                     fg_color=theme.PRIMARY_BADGE)
        self._avatar.grid(row=0, column=0, padx=10, pady=10)
        self._avatar.grid_propagate(False)
        self._avatar_lbl = ctk.CTkLabel(self._avatar, text="?",
                                         font=theme.font(13, "bold"), text_color=theme.PRIMARY,
                                         fg_color="transparent")
        self._avatar_lbl.place(relx=0.5, rely=0.5, anchor="center")

        info_col = ctk.CTkFrame(self._user_card, fg_color="transparent")
        info_col.grid(row=0, column=1, sticky="w")
        self._name_lbl = ctk.CTkLabel(info_col, text="—",
                                       font=theme.font(12, "bold"), text_color=theme.TEXT, anchor="w")
        self._name_lbl.pack(anchor="w")
        self._role_lbl = ctk.CTkLabel(info_col, text="—",
                                       font=theme.TINY, text_color=theme.PRIMARY, anchor="w")
        self._role_lbl.pack(anchor="w")

        # ── Nav list ──────────────────────────────────────────────────────
        self._nav_container = ctk.CTkFrame(sb, fg_color="transparent")
        self._nav_container.grid(row=2, column=0, sticky="nsew", padx=8, pady=8)
        self._nav_container.columnconfigure(0, weight=1)

        # ── Clock ─────────────────────────────────────────────────────────
        bottom = ctk.CTkFrame(sb, fg_color="transparent")
        bottom.grid(row=3, column=0, sticky="ew", padx=12, pady=8)
        bottom.columnconfigure(0, weight=1)

        self._clock_lbl = ctk.CTkLabel(bottom, text="",
                                        font=theme.TINY, text_color=theme.TEXT_DIM)
        self._clock_lbl.grid(row=0, column=0, sticky="w")

        # ── Logout ────────────────────────────────────────────────────────
        ctk.CTkFrame(bottom, height=1, fg_color=theme.BORDER).grid(
            row=1, column=0, sticky="ew", pady=8)

        logout_btn = ctk.CTkButton(
            bottom,
            text="⎋  Sign Out",
            font=theme.SMALL,
            height=38,
            fg_color="transparent",
            hover_color="#2d0a0a",
            text_color=theme.RED,
            border_width=1,
            border_color="#2d1515",
            corner_radius=theme.RADIUS_MD,
            anchor="w",
            command=self._logout,
        )
        logout_btn.grid(row=2, column=0, sticky="ew")

        return sb

    def _build_nav(self, role: str):
        """Populate the sidebar nav links based on role."""
        for w in self._nav_container.winfo_children():
            w.destroy()
        self._nav_btns.clear()

        nav_items = {
            "student": [
                ("dashboard", "🏠", "Dashboard"),
            ],
            "faculty": [
                ("dashboard", "🏠", "Dashboard"),
            ],
            "admin": [
                ("dashboard",     "🏠", "Overview"),
                ("system_status", "🖥", "System Status"),
            ],
        }

        for i, (page, icon, label) in enumerate(nav_items.get(role, [])):
            btn = ctk.CTkButton(
                self._nav_container,
                text=f"  {icon}   {label}",
                font=theme.SMALL,
                height=40,
                anchor="w",
                fg_color="transparent",
                hover_color=theme.NAV_HOVER_BG,
                text_color=theme.NAV_FG,
                corner_radius=theme.RADIUS_MD,
                command=lambda p=page: self._navigate(p),
            )
            btn.grid(row=i, column=0, sticky="ew", pady=2)
            self._nav_btns[page] = btn

    def _set_active_nav(self, page: str):
        for p, btn in self._nav_btns.items():
            if p == page:
                btn.configure(fg_color=theme.NAV_ACTIVE_BG, text_color=theme.PRIMARY)
            else:
                btn.configure(fg_color="transparent", text_color=theme.NAV_FG)

    # ─────────────────────────────────────────────────────────────────────────
    # Navigation / page switching
    # ─────────────────────────────────────────────────────────────────────────
    def _show_login(self):
        self._sidebar.grid_remove()
        self._clear_content()
        login = LoginView(self._content, on_login_success=self._on_login)
        login.grid(row=0, column=0, sticky="nsew")
        self._current_view = login

    def _on_login(self, user: dict):
        self._user = user
        self._update_user_card(user)
        role = user.get("role", "student")
        self._build_nav(role)
        self._sidebar.grid()
        self._navigate("dashboard")

    def _navigate(self, page: str):
        if page == self._active_page and self._current_view is not None:
            return
        self._active_page = page
        self._set_active_nav(page)
        self._clear_content()

        role = self._user.get("role", "student")

        if page == "dashboard":
            if role == "student":
                view = StudentView(self._content, user=self._user)
            elif role == "faculty":
                view = FacultyView(self._content, user=self._user)
            else:
                view = AdminView(self._content, user=self._user, on_nav=self._navigate)

        elif page == "system_status":
            view = SystemStatusView(self._content, user=self._user)

        else:
            view = ctk.CTkLabel(self._content, text=f"Page '{page}' not found.",
                                 font=theme.BODY, text_color=theme.TEXT_MUTED)

        view.grid(row=0, column=0, sticky="nsew")
        self._current_view = view

    def _clear_content(self):
        if self._current_view and hasattr(self._current_view, "on_destroy"):
            try:
                self._current_view.on_destroy()
            except Exception:
                pass
        for w in self._content.winfo_children():
            w.destroy()
        self._current_view = None

    def _logout(self):
        api.logout()
        self._user = None
        self._active_page = ""
        self._show_login()

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────────
    def _update_user_card(self, user: dict):
        name = user.get("name", "User")
        role = user.get("role", "").capitalize()
        initial = name[0].upper() if name else "?"
        self._avatar_lbl.configure(text=initial)
        self._name_lbl.configure(text=name)
        self._role_lbl.configure(text=role)

    def _tick_clock(self):
        now = datetime.now().strftime("%a %d %b  %H:%M:%S")
        if hasattr(self, "_clock_lbl"):
            self._clock_lbl.configure(text=now)
        self.after(1000, self._tick_clock)
