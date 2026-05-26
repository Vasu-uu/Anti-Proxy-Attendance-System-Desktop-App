"""
Login View — split-panel professional login screen.

Left panel:  Branding / description
Right panel: Role tabs + email/password form
"""

import customtkinter as ctk
from gui import theme
from gui.api_client import api


class LoginView(ctk.CTkFrame):

    def __init__(self, master, on_login_success, **kwargs):
        super().__init__(master, fg_color=theme.BG, **kwargs)
        self._on_success = on_login_success
        self._role = "student"
        self._build()

    # ── Build ─────────────────────────────────────────────────────────────────
    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Outer centering frame
        center = ctk.CTkFrame(self, fg_color=theme.BG)
        center.grid(row=0, column=0)

        # Card container
        card = ctk.CTkFrame(
            center,
            fg_color=theme.CARD,
            corner_radius=theme.RADIUS_XL,
            border_width=1,
            border_color=theme.BORDER,
        )
        card.pack(padx=40, pady=40)
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)

        self._build_left(card)
        self._build_right(card)

    # ── Left branding panel ───────────────────────────────────────────────────
    def _build_left(self, card):
        left = ctk.CTkFrame(
            card,
            width=360,
            fg_color="#0d1f1c",
            corner_radius=0,
        )
        left.grid(row=0, column=0, sticky="nsew")
        left.grid_propagate(False)
        left.rowconfigure(2, weight=1)

        # Logo row
        logo_row = ctk.CTkFrame(left, fg_color="transparent")
        logo_row.pack(padx=40, pady=(40, 0), anchor="w")

        logo_bg = ctk.CTkFrame(logo_row, width=44, height=44, corner_radius=12,
                               fg_color=theme.PRIMARY_DARK)
        logo_bg.pack(side="left")
        logo_bg.pack_propagate(False)
        ctk.CTkLabel(logo_bg, text="◈", font=theme.font(22, "bold"),
                     text_color=theme.TEXT).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(logo_row, text="APCAS Platform",
                     font=theme.font(16, "bold"), text_color=theme.TEXT).pack(side="left", padx=10)

        # Hero text
        hero = ctk.CTkFrame(left, fg_color="transparent")
        hero.pack(padx=40, pady=(32, 0), anchor="w")

        ctk.CTkLabel(
            hero,
            text="Next-generation\nfacial recognition\nattendance.",
            font=theme.font(26, "bold"),
            text_color=theme.TEXT,
            justify="left",
        ).pack(anchor="w")

        ctk.CTkLabel(
            hero,
            text="Secure, seamless, and automated\nattendance tracking powered by AI.",
            font=theme.font(13),
            text_color=theme.TEXT_MUTED,
            justify="left",
        ).pack(anchor="w", pady=(14, 0))

        # Feature bullets
        bullets = ctk.CTkFrame(left, fg_color="transparent")
        bullets.pack(padx=40, pady=(36, 0), anchor="w")

        feats = [
            ("◆", theme.PRIMARY,  "Real-time face detection"),
            ("◆", theme.EMERALD,  "Anti-proxy verification"),
            ("◆", theme.BLUE,     "Automated period tracking"),
        ]
        for icon, color, text in feats:
            row = ctk.CTkFrame(bullets, fg_color="transparent")
            row.pack(anchor="w", pady=5)
            ctk.CTkLabel(row, text=icon, font=theme.font(10), text_color=color).pack(side="left")
            ctk.CTkLabel(row, text=f"  {text}", font=theme.SMALL,
                         text_color=theme.TEXT_MUTED).pack(side="left")

        # Bottom spacer + accent line
        ctk.CTkFrame(left, height=2, fg_color=theme.PRIMARY_DARK,
                     corner_radius=0).pack(side="bottom", fill="x")
        ctk.CTkFrame(left, fg_color="transparent").pack(expand=True)

    # ── Right form panel ──────────────────────────────────────────────────────
    def _build_right(self, card):
        right = ctk.CTkFrame(card, width=400, fg_color=theme.CARD, corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_propagate(False)
        right.columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(right, fg_color="transparent")
        inner.pack(padx=40, pady=40, fill="both", expand=True)
        inner.columnconfigure(0, weight=1)

        # Header
        ctk.CTkLabel(inner, text="Welcome Back",
                     font=theme.font(22, "bold"), text_color=theme.TEXT).pack(anchor="center")
        ctk.CTkLabel(inner, text="Sign in to your account to continue",
                     font=theme.SMALL, text_color=theme.TEXT_MUTED).pack(anchor="center", pady=(4, 0))

        # ── Role selector ────────────────────────────────────────────────
        role_bar = ctk.CTkFrame(inner, fg_color=theme.BG, corner_radius=theme.RADIUS_MD)
        role_bar.pack(fill="x", pady=(28, 0))
        role_bar.columnconfigure((0, 1, 2), weight=1)

        self._role_btns: dict[str, ctk.CTkButton] = {}
        roles = [
            ("student", "🎓 Student"),
            ("faculty", "👥 Faculty"),
            ("admin",   "⚙ Admin"),
        ]
        for i, (rid, label) in enumerate(roles):
            btn = ctk.CTkButton(
                role_bar,
                text=label,
                font=theme.SMALL,
                height=38,
                corner_radius=theme.RADIUS_SM,
                fg_color=theme.PRIMARY if rid == self._role else "transparent",
                hover_color=theme.PRIMARY_DARK if rid == self._role else theme.CARD_ALT,
                text_color=theme.TEXT,
                command=lambda r=rid: self._select_role(r),
            )
            btn.grid(row=0, column=i, padx=4, pady=4, sticky="ew")
            self._role_btns[rid] = btn

        # ── Email ────────────────────────────────────────────────────────
        ctk.CTkLabel(inner, text="Email Address", font=theme.LABEL,
                     text_color=theme.TEXT_MUTED, anchor="w").pack(fill="x", pady=(24, 4))
        self._email = ctk.CTkEntry(
            inner,
            placeholder_text="name@institution.edu",
            font=theme.BODY,
            height=44,
            fg_color=theme.BG,
            border_color=theme.BORDER,
            text_color=theme.TEXT,
            placeholder_text_color=theme.TEXT_DIM,
            corner_radius=theme.RADIUS_MD,
        )
        self._email.pack(fill="x")

        # ── Password ─────────────────────────────────────────────────────
        pw_row = ctk.CTkFrame(inner, fg_color="transparent")
        pw_row.pack(fill="x", pady=(16, 4))
        ctk.CTkLabel(pw_row, text="Password", font=theme.LABEL,
                     text_color=theme.TEXT_MUTED).pack(side="left")

        self._password = ctk.CTkEntry(
            inner,
            placeholder_text="••••••••",
            show="•",
            font=theme.BODY,
            height=44,
            fg_color=theme.BG,
            border_color=theme.BORDER,
            text_color=theme.TEXT,
            placeholder_text_color=theme.TEXT_DIM,
            corner_radius=theme.RADIUS_MD,
        )
        self._password.pack(fill="x")
        self._password.bind("<Return>", lambda _: self._submit())

        # ── Error label ──────────────────────────────────────────────────
        self._err_frame = ctk.CTkFrame(inner, fg_color=theme.RED_BG,
                                       corner_radius=theme.RADIUS_SM, height=0)
        self._err_lbl = ctk.CTkLabel(self._err_frame, text="", font=theme.SMALL,
                                     text_color=theme.RED, wraplength=300)

        # ── Submit button ─────────────────────────────────────────────────
        self._submit_btn = ctk.CTkButton(
            inner,
            text="Sign In  →",
            font=theme.font(14, "bold"),
            height=48,
            corner_radius=theme.RADIUS_MD,
            fg_color=theme.PRIMARY,
            hover_color=theme.PRIMARY_DARK,
            text_color=theme.TEXT,
            command=self._submit,
        )
        self._submit_btn.pack(fill="x", pady=(24, 0))

        # ── Version tag ───────────────────────────────────────────────────
        ctk.CTkLabel(inner, text="APCAS v1.0 · Powered by FaceNet",
                     font=theme.TINY, text_color=theme.TEXT_DIM).pack(pady=(20, 0))

    # ── Interactions ──────────────────────────────────────────────────────────
    def _select_role(self, role: str):
        self._role = role
        for rid, btn in self._role_btns.items():
            if rid == role:
                btn.configure(fg_color=theme.PRIMARY, hover_color=theme.PRIMARY_DARK)
            else:
                btn.configure(fg_color="transparent", hover_color=theme.CARD_ALT)

    def _submit(self):
        email = self._email.get().strip()
        password = self._password.get()

        if not email or not password:
            self._show_error("Please enter your email and password.")
            return

        self._submit_btn.configure(text="Signing in…", state="disabled")
        self._hide_error()

        # Run in background thread to avoid blocking UI
        import threading
        threading.Thread(target=self._do_login, args=(email, password), daemon=True).start()

    def _do_login(self, email: str, password: str):
        try:
            result = api.login(self._role, email, password)
            if result.get("success"):
                me = api.get_me()
                self.after(0, lambda: self._on_success(me))
            else:
                msg = result.get("error", "Invalid credentials")
                self.after(0, lambda: self._show_error(f"Login failed: {msg}"))
        except Exception as e:
            self.after(0, lambda: self._show_error(f"Connection error: {e}"))
        finally:
            def _reset_btn():
                if self.winfo_exists() and self._submit_btn.winfo_exists():
                    self._submit_btn.configure(text="Sign In  →", state="normal")
            self.after(0, _reset_btn)

    def _show_error(self, msg: str):
        self._err_lbl.configure(text=msg)
        self._err_frame.pack(fill="x", pady=(10, 0))
        self._err_lbl.pack(padx=10, pady=6)

    def _hide_error(self):
        self._err_frame.pack_forget()
