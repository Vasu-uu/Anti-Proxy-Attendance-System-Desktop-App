import os
import sys
import time
import threading
import io
import datetime
from typing import Optional, List, Dict, Any
import requests
from PIL import Image
import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd

# ==============================================================================
# THEME (Dark/Light toggleable)
# ==============================================================================
class Theme:
    def __init__(self):
        self.mode = "dark" # dark or light
        
        # Colors (Modern Palette)
        self.PRIMARY = "#6366f1"     # Indigo
        self.PRIMARY_HOVER = "#4f46e5"
        self.ACCENT = "#14b8a6"      # Teal
        self.ACCENT_HOVER = "#0d9488"
        self.DANGER = "#f43f5e"      # Rose
        self.SUCCESS = "#10b981"     # Emerald
        self.WARNING = "#f59e0b"     # Amber
        
        # Typography
        self.H1 = ("Segoe UI", 32, "bold")
        self.H2 = ("Segoe UI", 24, "bold")
        self.H3 = ("Segoe UI", 18, "bold")
        self.BODY = ("Segoe UI", 14)
        self.BODY_BOLD = ("Segoe UI", 14, "bold")
        self.SMALL = ("Segoe UI", 12)
        
        self.RADIUS_SM = 8
        self.RADIUS_MD = 12
        self.RADIUS_LG = 16
        
        self.set_mode(self.mode)

    def set_mode(self, mode: str):
        self.mode = mode
        if mode == "dark":
            ctk.set_appearance_mode("dark")
            self.BG = "#0b0f19"         # Very dark blue-gray
            self.CARD_BG = "#1e293b"    # Slate 800
            self.SIDEBAR_BG = "#0f172a" # Slate 900
            self.BORDER = "#334155"     # Slate 700
            self.TEXT = "#f8fafc"       # Slate 50
            self.TEXT_DIM = "#94a3b8"   # Slate 400
        else:
            ctk.set_appearance_mode("light")
            self.BG = "#f8fafc"         # Slate 50
            self.CARD_BG = "#ffffff"    # White
            self.SIDEBAR_BG = "#f1f5f9" # Slate 100
            self.BORDER = "#e2e8f0"     # Slate 200
            self.TEXT = "#0f172a"       # Slate 900
            self.TEXT_DIM = "#64748b"   # Slate 500

theme = Theme()

# ==============================================================================
# API CLIENT
# ==============================================================================
BASE_URL = "http://127.0.0.1:5000"

class APIClient:
    def __init__(self):
        self.session = requests.Session()

    def login(self, role: str, email: str, password: str) -> dict:
        res = self.session.post(
            f"{BASE_URL}/auth",
            json={"role": role, "email": email, "password": password},
            timeout=10,
        )
        return res.json()

    def get_me(self) -> Optional[dict]:
        try:
            res = self.session.get(f"{BASE_URL}/api/v1/auth/me", timeout=5)
            if res.status_code == 200:
                return res.json()
        except:
            pass
        return None

    def logout(self):
        try:
            self.session.post(f"{BASE_URL}/api/v1/auth/logout", timeout=5)
        except:
            pass

    # Dashboard fetches
    def get_student_dashboard(self) -> dict:
        res = self.session.get(f"{BASE_URL}/api/v1/student/dashboard", timeout=10)
        res.raise_for_status()
        return res.json()

    def get_faculty_dashboard(self, cls: str = None, date: str = None, period: str = None) -> dict:
        params = {}
        if cls: params["class"] = cls
        if date: params["date"] = date
        if period: params["period"] = period
        res = self.session.get(f"{BASE_URL}/api/v1/faculty/dashboard", params=params, timeout=10)
        res.raise_for_status()
        return res.json()

    def get_admin_dashboard(self) -> dict:
        res = self.session.get(f"{BASE_URL}/api/v1/admin/dashboard", timeout=10)
        res.raise_for_status()
        return res.json()

    def get_system_status(self) -> dict:
        res = self.session.get(f"{BASE_URL}/api/system_status", timeout=15)
        res.raise_for_status()
        return res.json()

    # Admin Operations
    def add_faculty(self, name: str, email: str, password: str, department: str) -> dict:
        res = self.session.post(
            f"{BASE_URL}/auth",
            json={
                "auth_type": "admin_add_faculty",
                "fullname": name,
                "email": email,
                "password": password,
                "department": department,
            },
            timeout=10,
        )
        res.raise_for_status()
        return res.json()

    def update_attendance(self, roll: str, date: str, updates: dict) -> dict:
        res = self.session.post(
            f"{BASE_URL}/api/admin_update_attendance",
            json={"roll": roll, "date": date, "updates": updates},
            timeout=10,
        )
        res.raise_for_status()
        return res.json()
        
    def get_faculty_upload_day(self) -> dict:
        res = self.session.get(f"{BASE_URL}/api/admin_faculty_upload_day", timeout=10)
        res.raise_for_status()
        return res.json()

    def set_faculty_upload_day(self, enabled: bool) -> dict:
        res = self.session.post(
            f"{BASE_URL}/api/admin_faculty_upload_day",
            json={"enabled": enabled},
            timeout=10,
        )
        res.raise_for_status()
        return res.json()

    def get_classes(self) -> list:
        res = self.session.get(f"{BASE_URL}/api/classes", timeout=5)
        res.raise_for_status()
        return res.json()

    def get_class_students(self, cls: str) -> list:
        res = self.session.get(f"{BASE_URL}/api/class/{cls}/students", timeout=5)
        res.raise_for_status()
        return res.json()

    def get_timetable(self, cls: str) -> list:
        res = self.session.get(f"{BASE_URL}/api/timetable/{urllib.parse.quote(cls)}", timeout=5)
        res.raise_for_status()
        return res.json()

    def update_timetable_slot(self, tt_id: int, slot: str, faculty_name: str) -> dict:
        data = {"slot": slot, "faculty_name": faculty_name}
        res = self.session.put(f"{BASE_URL}/api/v1/timetable/{tt_id}", json=data, timeout=5)
        res.raise_for_status()
        return res.json()

    def get_admin_dashboard(self) -> dict:
        res = self.session.get(f"{BASE_URL}/api/v1/admin/dashboard", timeout=5)
        res.raise_for_status()
        return res.json()

    def get_system_status(self) -> dict:
        res = self.session.get(f"{BASE_URL}/api/v1/system_status", timeout=5)
        res.raise_for_status()
        return res.json()

    def get_faculty_dashboard(self) -> dict:
        res = self.session.get(f"{BASE_URL}/api/v1/faculty/dashboard", timeout=5)
        res.raise_for_status()
        return res.json()

    def get_faculty_timetable(self) -> list:
        res = self.session.get(f"{BASE_URL}/api/v1/faculty/timetable", timeout=5)
        res.raise_for_status()
        return res.json()

    def get_faculty_class_attendance(self, cls: str, date: str, period: str) -> dict:
        params = {"class": cls, "date": date, "period": period}
        res = self.session.get(f"{BASE_URL}/api/v1/faculty/dashboard", params=params, timeout=5)
        res.raise_for_status()
        return res.json()

    # Faculty Operations
    def offline_attendance(self, photo_path: str, target_class: str, period: str, date: str) -> dict:
        with open(photo_path, "rb") as f:
            res = self.session.post(
                f"{BASE_URL}/api/offline_attendance",
                files={"photo": f},
                data={"target_class": target_class, "period": period, "date": date},
                timeout=60,
            )
        res.raise_for_status()
        return res.json()

    # Student Operations
    def get_student_attendance_history(self, student_id: int, from_date: str, to_date: str) -> list:
        res = self.session.get(
            f"{BASE_URL}/api/student/attendance",
            params={"student_id": student_id, "from": from_date, "to": to_date},
            timeout=10
        )
        res.raise_for_status()
        return res.json()

api = APIClient()

# ==============================================================================
# BASE CLASSES & WIDGETS
# ==============================================================================
class BaseView(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(
            master, 
            fg_color=theme.BG, 
            corner_radius=0, 
            **kwargs
        )
        self.app = app_controller
        
    def refresh(self):
        pass

class StatCard(ctk.CTkFrame):
    def __init__(self, master, title: str, value: str, icon: str = "", **kwargs):
        super().__init__(
            master,
            fg_color=theme.CARD_BG,
            border_color=theme.BORDER,
            border_width=1,
            corner_radius=theme.RADIUS_LG,
            **kwargs,
        )
        self.grid_columnconfigure(0, weight=1)
        lbl_title = ctk.CTkLabel(
            self, text=title.upper(), font=theme.SMALL, text_color=theme.TEXT_DIM, anchor="w"
        )
        lbl_title.grid(row=0, column=0, padx=24, pady=(24, 8), sticky="w")
        lbl_val = ctk.CTkLabel(
            self, text=f"{icon} {value}", font=theme.H1, text_color=theme.TEXT, anchor="w"
        )
        lbl_val.grid(row=1, column=0, padx=24, pady=(0, 24), sticky="w")

class CameraFeed(ctk.CTkFrame):
    STREAM_URL = "http://127.0.0.1:5000/api/admin/live_feed"

    def __init__(self, master, width: int = 640, height: int = 360, **kwargs):
        super().__init__(
            master,
            fg_color=theme.BG,
            corner_radius=theme.RADIUS_LG,
            border_width=1,
            border_color=theme.BORDER,
            **kwargs,
        )
        self._feed_width = width
        self._feed_height = height
        self._running = False
        self._thread = None
        self._session = None

        self._feed_label = ctk.CTkLabel(
            self,
            text="",
            width=width,
            height=height,
            fg_color=theme.BG,
            corner_radius=theme.RADIUS_LG,
        )
        self._feed_label.pack(fill="both", expand=True)
        self._placeholder()

    def _placeholder(self):
        placeholder = Image.new("RGB", (self._feed_width, self._feed_height), color="#0f0f0f")
        self._ph_img = ctk.CTkImage(placeholder, size=(self._feed_width, self._feed_height))
        self._feed_label.configure(
            image=self._ph_img,
            text="Camera stream not active",
            compound="bottom",
            font=theme.SMALL,
            text_color=theme.TEXT_DIM,
        )

    def start(self):
        if self._running: return
        self._running = True
        self._thread = threading.Thread(target=self._stream_worker, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._session:
            try: self._session.close()
            except: pass

    def _stream_worker(self):
        try:
            self._session = requests.Session()
            response = self._session.get(self.STREAM_URL, stream=True, timeout=10)
            buffer = b""
            for chunk in response.iter_content(chunk_size=4096):
                if not self._running: break
                buffer += chunk
                start = buffer.find(b"\xff\xd8")
                end = buffer.find(b"\xff\xd9")
                if start != -1 and end != -1 and end > start:
                    jpeg_data = buffer[start:end + 2]
                    buffer = buffer[end + 2:]
                    try:
                        img = Image.open(io.BytesIO(jpeg_data))
                        img = img.resize((self._feed_width, self._feed_height), Image.LANCZOS)
                        ctk_img = ctk.CTkImage(img, size=(self._feed_width, self._feed_height))
                        self._feed_label.after(0, lambda i=ctk_img: self._feed_label.configure(image=i, text=""))
                    except: pass
        except:
            self.after(0, self._placeholder)

# ==============================================================================
# LOGIN VIEW
# ==============================================================================
class LoginView(BaseView):
    def __init__(self, master, app_controller):
        super().__init__(master, app_controller)
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Left Side (Brand Area)
        left_frame = ctk.CTkFrame(self, fg_color=theme.PRIMARY, corner_radius=0)
        left_frame.grid(row=0, column=0, sticky="nsew")
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(0, weight=1)
        try:
            from PIL import Image
            img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "login img.jpg")
            if os.path.exists(img_path):
                img = Image.open(img_path)
                bg_image = ctk.CTkImage(img, size=(700, 900))
                bg_label = ctk.CTkLabel(left_frame, text="", image=bg_image)
                bg_label.place(relx=0.5, rely=0.5, anchor="center")
        except:
            pass
        
        brand_inner = ctk.CTkFrame(left_frame, fg_color="transparent")
        brand_inner.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(brand_inner, text="APCAS", font=("Segoe UI", 48, "bold"), text_color="#ffffff").pack(pady=(0,10))
        ctk.CTkLabel(brand_inner, text="Advanced Attendance\nPlatform System", font=("Segoe UI", 18), text_color="#e0e7ff", justify="center").pack()
        
        # Right Side (Login Form)
        right_frame = ctk.CTkFrame(self, fg_color=theme.BG, corner_radius=0)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(0, weight=1)
        
        form_container = ctk.CTkFrame(right_frame, fg_color="transparent", width=360)
        form_container.grid(row=0, column=0)
        form_container.grid_propagate(False)
        form_container.configure(height=480)
        
        ctk.CTkLabel(form_container, text="Welcome Back", font=theme.H1, text_color=theme.TEXT, anchor="w").pack(fill="x", pady=(20, 5))
        ctk.CTkLabel(form_container, text="Sign in to your account", font=theme.BODY, text_color=theme.TEXT_DIM, anchor="w").pack(fill="x", pady=(0, 40))
        
        self.role_var = ctk.StringVar(value="admin")
        roles = ctk.CTkSegmentedButton(
            form_container, values=["admin", "faculty", "student"], variable=self.role_var,
            selected_color=theme.PRIMARY, selected_hover_color=theme.PRIMARY_HOVER, height=36
        )
        roles.pack(fill="x", pady=(0, 25))
        
        self.email_ent = ctk.CTkEntry(form_container, placeholder_text="Email Address", height=45, font=theme.BODY, corner_radius=theme.RADIUS_SM, border_color=theme.BORDER)
        self.email_ent.pack(fill="x", pady=(0, 15))
        
        self.pass_ent = ctk.CTkEntry(form_container, placeholder_text="Password", show="•", height=45, font=theme.BODY, corner_radius=theme.RADIUS_SM, border_color=theme.BORDER)
        self.pass_ent.pack(fill="x", pady=(0, 20))
        
        self.err_lbl = ctk.CTkLabel(form_container, text="", text_color=theme.DANGER, font=theme.SMALL)
        self.err_lbl.pack(pady=(0, 15))
        
        self.btn = ctk.CTkButton(
            form_container, text="Sign In", height=45, font=theme.H3, corner_radius=theme.RADIUS_MD,
            fg_color=theme.PRIMARY, hover_color=theme.PRIMARY_HOVER,
            command=self._do_login
        )
        self.btn.pack(fill="x", pady=(0, 20))
        
        # Theme toggle on login screen
        self.theme_btn = ctk.CTkButton(
            right_frame, text="Toggle Theme", width=120, fg_color="transparent", 
            border_width=1, border_color=theme.BORDER, text_color=theme.TEXT, corner_radius=theme.RADIUS_SM,
            command=self.app.toggle_theme
        )
        self.theme_btn.place(relx=0.95, rely=0.95, anchor="se")

    def _do_login(self):
        role = self.role_var.get()
        email = self.email_ent.get().strip()
        pwd = self.pass_ent.get().strip()
        if not email or not pwd:
            self.err_lbl.configure(text="Email and password required.")
            return
            
        self.btn.configure(text="Signing in...", state="disabled")
        threading.Thread(target=self._auth_worker, args=(role, email, pwd), daemon=True).start()

    def _auth_worker(self, role, email, pwd):
        try:
            res = api.login(role, email, pwd)
            if res.get("error"):
                self.after(0, lambda: self.err_lbl.configure(text="Invalid credentials."))
            else:
                self.after(0, self.app.check_auth)
        except Exception as e:
            self.after(0, lambda: self.err_lbl.configure(text=f"Connection error: {e}"))
        finally:
            def _reset_btn():
                if self.winfo_exists() and self.btn.winfo_exists():
                    self.btn.configure(text="Sign In →", state="normal")
            self.after(0, _reset_btn)

# ==============================================================================
# MAIN APP
# ==============================================================================
class APCASApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("APCAS — Advanced Attendance Platform")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        self.configure(fg_color=theme.BG)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.current_view = None
        self.user = None
        
        self.check_auth()

    def toggle_theme(self):
        new_mode = "light" if theme.mode == "dark" else "dark"
        theme.set_mode(new_mode)
        # Redraw entirely
        if self.current_view:
            self.current_view.destroy()
        self.check_auth()

    def check_auth(self):
        self.user = api.get_me()
        if self.current_view:
            self.current_view.destroy()
            
        if not self.user:
            self.current_view = LoginView(self, self)
            self.current_view.grid(row=0, column=0, sticky="nsew")
        else:
            role = self.user.get("role")
            if role == "admin":
                self.current_view = AdminRootView(self, self)
            elif role == "faculty":
                self.current_view = FacultyRootView(self, self)
            elif role == "student":
                self.current_view = StudentRootView(self, self)
            else:
                self.user = None
                self.current_view = LoginView(self, self)
            self.current_view.grid(row=0, column=0, sticky="nsew")

    def logout(self):
        api.logout()
        self.check_auth()

# STUBS for root views
class SidebarView(BaseView):
    def __init__(self, master, app_controller, tabs: list):
        super().__init__(master, app_controller)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=theme.SIDEBAR_BG)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(len(tabs) + 2, weight=1)
        
        # Logo
        ctk.CTkLabel(self.sidebar, text="APCAS", font=theme.H2, text_color=theme.PRIMARY).grid(row=0, column=0, padx=25, pady=(30, 40), sticky="w")
        
        # Tabs
        self.tab_frames = {}
        self.tab_buttons = []
        for i, tab_name in enumerate(tabs):
            btn = ctk.CTkButton(
                self.sidebar, text=f"   {tab_name}", font=theme.BODY_BOLD, height=45, anchor="w",
                fg_color="transparent", text_color=theme.TEXT_DIM, hover_color=theme.BG,
                corner_radius=theme.RADIUS_SM,
                command=lambda name=tab_name: self.select_tab(name)
            )
            btn.grid(row=i+1, column=0, padx=15, pady=4, sticky="ew")
            self.tab_buttons.append(btn)
        
        # Bottom sidebar buttons
        self.theme_btn = ctk.CTkButton(
            self.sidebar, text="Toggle Theme", command=self.app.toggle_theme, height=40,
            fg_color="transparent", border_width=1, border_color=theme.BORDER, text_color=theme.TEXT, corner_radius=theme.RADIUS_SM
        )
        self.theme_btn.grid(row=len(tabs)+2, column=0, padx=15, pady=(0, 15), sticky="ew")
        
        self.logout_btn = ctk.CTkButton(
            self.sidebar, text="Logout", command=self.app.logout, height=40,
            fg_color="transparent", hover_color="#fef2f2", text_color=theme.DANGER, corner_radius=theme.RADIUS_SM,
            border_width=1, border_color="#fecaca" if theme.mode=="light" else theme.DANGER
        )
        self.logout_btn.grid(row=len(tabs)+3, column=0, padx=15, pady=(0, 30), sticky="ew")

        # Main Content Area
        self.main_content = ctk.CTkFrame(self, fg_color=theme.BG, corner_radius=0)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.main_content.grid_rowconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)
        
    def add_tab_frame(self, name: str, frame: ctk.CTkFrame):
        self.tab_frames[name] = frame
        
    def select_tab(self, name: str):
        for btn in self.tab_buttons:
            if btn.cget("text").strip() == name:
                btn.configure(fg_color=theme.PRIMARY, text_color="#ffffff", hover_color=theme.PRIMARY_HOVER)
            else:
                btn.configure(fg_color="transparent", text_color=theme.TEXT_DIM, hover_color=theme.BG)
        
        for frame in self.tab_frames.values():
            frame.grid_forget()
            
        if name in self.tab_frames:
            self.tab_frames[name].grid(row=0, column=0, sticky="nsew")

class AdminRootView(SidebarView):
    def __init__(self, master, app):
        super().__init__(master, app, ["Dashboard", "Manage Faculty", "Class & Attendance", "Timetables", "System Status"])
        
        # Build Frames
        self.build_dashboard()
        self.build_manage_faculty()
        self.build_class_attendance()
        self.build_timetables()
        self.build_system_status()
        
        self.select_tab("Dashboard")

    def build_dashboard(self):
        f = ctk.CTkFrame(self.main_content, fg_color="transparent")
        ctk.CTkLabel(f, text="Admin Dashboard", font=theme.H1, text_color=theme.TEXT).pack(anchor="w", padx=20, pady=20)
        
        stats_frame = ctk.CTkFrame(f, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20, pady=10)
        stats_frame.grid_columnconfigure((0,1,2), weight=1)
        
        self.stat_students = StatCard(stats_frame, "Total Students", "Loading...")
        self.stat_students.grid(row=0, column=0, padx=5, sticky="ew")
        self.stat_classes = StatCard(stats_frame, "Active Classes", "Loading...")
        self.stat_classes.grid(row=0, column=1, padx=5, sticky="ew")
        self.stat_subjects = StatCard(stats_frame, "Total Subjects", "Loading...")
        self.stat_subjects.grid(row=0, column=2, padx=5, sticky="ew")
        
        # Charts Area
        self.chart_frame = ctk.CTkFrame(f, fg_color=theme.CARD_BG, corner_radius=theme.RADIUS_LG)
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.add_tab_frame("Dashboard", f)
        
        # Fetch data
        threading.Thread(target=self._load_dashboard, daemon=True).start()
        
    def clear_main(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

    def build_system_status(self):
        f = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header = ctk.CTkFrame(f, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(40, 20))
        ctk.CTkLabel(header, text="System Health & Status", font=("Segoe UI", 32, "bold"), text_color=theme.TEXT).pack(anchor="w")
        ctk.CTkLabel(header, text="Monitor backend services, database connections, and AI model health.", font=("Segoe UI", 16), text_color=theme.TEXT_DIM).pack(anchor="w")
        
        container = ctk.CTkScrollableFrame(f, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=40, pady=(0, 40))
        
        self.status_widgets = {}
        
        # Overall Card
        overall_card = ctk.CTkFrame(container, fg_color=theme.CARD_BG, corner_radius=12)
        overall_card.pack(fill="x", pady=(0, 20), ipady=20)
        overall_card.grid_columnconfigure(1, weight=1)
        
        self.status_widgets['overall_title'] = ctk.CTkLabel(overall_card, text="Loading system status...", font=("Segoe UI", 24, "bold"), text_color=theme.TEXT)
        self.status_widgets['overall_title'].grid(row=0, column=0, sticky="w", padx=20, pady=(10,0))
        self.status_widgets['checked_at'] = ctk.CTkLabel(overall_card, text="Last checked: --", font=("Segoe UI", 14), text_color=theme.TEXT_DIM)
        self.status_widgets['checked_at'].grid(row=1, column=0, sticky="w", padx=20)
        
        self.status_widgets['overall_badge'] = ctk.CTkLabel(overall_card, text="Checking...", fg_color=theme.PRIMARY, text_color="white", corner_radius=8, padx=15, pady=8, font=("Segoe UI", 16, "bold"))
        self.status_widgets['overall_badge'].grid(row=0, column=2, rowspan=2, sticky="e", padx=20)
        
        # Grid for Services
        services_frame = ctk.CTkFrame(container, fg_color="transparent")
        services_frame.pack(fill="x")
        services_frame.grid_columnconfigure((0,1), weight=1, uniform="col")
        
        def create_service_card(parent, row, col, title, desc):
            card = ctk.CTkFrame(parent, fg_color=theme.CARD_BG, corner_radius=12)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            card.grid_columnconfigure(1, weight=1)
            
            ctk.CTkLabel(card, text=title, font=("Segoe UI", 18, "bold"), text_color=theme.TEXT).grid(row=0, column=0, sticky="w", padx=20, pady=(20,5))
            badge = ctk.CTkLabel(card, text="Checking...", fg_color=theme.PRIMARY, text_color="white", corner_radius=6, padx=10, pady=4, font=("Segoe UI", 12, "bold"))
            badge.grid(row=0, column=2, sticky="e", padx=20, pady=(20,5))
            
            ctk.CTkLabel(card, text=desc, font=("Segoe UI", 14), text_color=theme.TEXT_DIM).grid(row=1, column=0, columnspan=3, sticky="w", padx=20, pady=(0, 20))
            detail = ctk.CTkLabel(card, text="--", font=("Segoe UI", 14, "bold"), text_color=theme.TEXT)
            detail.grid(row=2, column=0, columnspan=3, sticky="w", padx=20, pady=(0, 20))
            return badge, detail, card
            
        b_db, d_db, c_db = create_service_card(services_frame, 0, 0, "Main Database", "Current connection health")
        b_emb, d_emb, c_emb = create_service_card(services_frame, 0, 1, "Face Embeddings", "Student recognition data readiness")
        b_cam, d_cam, c_cam = create_service_card(services_frame, 1, 0, "Classroom Camera Feed", "Latest camera health signal")
        b_tt, d_tt, c_tt = create_service_card(services_frame, 1, 1, "Timetable Data", "Academic schedule availability")
        
        self.status_widgets['database'] = {'badge': b_db, 'detail': d_db, 'card': c_db}
        self.status_widgets['face_embeddings'] = {'badge': b_emb, 'detail': d_emb, 'card': c_emb}
        self.status_widgets['camera'] = {'badge': b_cam, 'detail': d_cam, 'card': c_cam}
        self.status_widgets['timetable'] = {'badge': b_tt, 'detail': d_tt, 'card': c_tt}
        self.status_widgets['overall_card'] = overall_card

        self.add_tab_frame("System Status", f)
        threading.Thread(target=self._fetch_system_status, daemon=True).start()
        
    def _fetch_system_status(self):
        try:
            data = api.get_system_status()
            self.after(0, lambda: self._render_system_status(data))
        except:
            pass

    def _render_system_status(self, data):
        def apply_state(ui_dict, pld):
            c_color = "#10b981" if pld['state'] == "success" else ("#f59e0b" if pld['state'] == "warning" else "#ef4444")
            ui_dict['badge'].configure(text=pld['label'], fg_color=c_color)
            if 'detail' in ui_dict:
                ui_dict['detail'].configure(text=pld.get('detail', '--'))
            
        if not hasattr(self, 'status_widgets') or 'overall_title' not in self.status_widgets:
            return
            
        ovr_color = "#10b981" if data['overall']['state'] == "success" else ("#f59e0b" if data['overall']['state'] == "warning" else "#ef4444")
        self.status_widgets['overall_title'].configure(text=data['overall']['label'])
        self.status_widgets['overall_badge'].configure(text=data['overall']['label'], fg_color=ovr_color)
        
        self.status_widgets['checked_at'].configure(text=f"Last checked: {data.get('checked_at', '--')}")
            
        apply_state(self.status_widgets['database'], data['database'])
        apply_state(self.status_widgets['face_embeddings'], data['face_embeddings'])
        apply_state(self.status_widgets['camera'], data['camera'])
        apply_state(self.status_widgets['timetable'], data['timetable'])

    def _load_dashboard(self):
        try:
            data = api.get_admin_dashboard()
            self.after(0, lambda: self._update_dash_ui(data))
        except:
            pass

    def _update_dash_ui(self, data):
        self.stat_students.winfo_children()[1].configure(text=str(data.get("total_students", 0)))
        self.stat_classes.winfo_children()[1].configure(text=str(data.get("active_classes", 0)))
        self.stat_subjects.winfo_children()[1].configure(text=str(data.get("total_subjects", 0)))
        
        # Draw Chart
        fig = Figure(figsize=(5, 3), dpi=100, facecolor=theme.CARD_BG)
        ax = fig.add_subplot(111)
        ax.set_facecolor(theme.CARD_BG)
        ax.bar(["Students", "Classes", "Subjects"], [data.get("total_students", 0), data.get("active_classes", 0), data.get("total_subjects", 0)], color=theme.ACCENT)
        ax.tick_params(colors=theme.TEXT_DIM)
        ax.spines['bottom'].set_color(theme.BORDER)
        ax.spines['left'].set_color(theme.BORDER)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
            
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def build_manage_faculty(self):
        f = ctk.CTkFrame(self.main_content, fg_color="transparent")
        ctk.CTkLabel(f, text="Add New Faculty", font=theme.H1, text_color=theme.TEXT).pack(anchor="w", padx=20, pady=20)
        
        form = ctk.CTkFrame(f, fg_color=theme.CARD_BG, corner_radius=theme.RADIUS_LG)
        form.pack(fill="x", padx=20, pady=10)
        
        self.fac_name = ctk.CTkEntry(form, placeholder_text="Full Name", height=40)
        self.fac_name.pack(fill="x", padx=20, pady=(20, 10))
        self.fac_email = ctk.CTkEntry(form, placeholder_text="Email Address", height=40)
        self.fac_email.pack(fill="x", padx=20, pady=10)
        self.fac_dept = ctk.CTkEntry(form, placeholder_text="Department", height=40)
        self.fac_dept.pack(fill="x", padx=20, pady=10)
        self.fac_pass = ctk.CTkEntry(form, placeholder_text="Password", show="•", height=40)
        self.fac_pass.pack(fill="x", padx=20, pady=10)
        
        self.fac_msg = ctk.CTkLabel(form, text="")
        self.fac_msg.pack(pady=5)
        
        ctk.CTkButton(form, text="Add Faculty", height=40, command=self._submit_faculty).pack(pady=(10, 20))
        
        self.add_tab_frame("Manage Faculty", f)
        
    def _submit_faculty(self):
        name = self.fac_name.get()
        email = self.fac_email.get()
        dept = self.fac_dept.get()
        pwd = self.fac_pass.get()
        if not all([name, email, dept, pwd]):
            self.fac_msg.configure(text="All fields required.", text_color=theme.DANGER)
            return
        
        def worker():
            try:
                api.add_faculty(name, email, pwd, dept)
                self.after(0, lambda: self.fac_msg.configure(text="Faculty added successfully!", text_color=theme.SUCCESS))
                self.after(0, lambda: [w.delete(0, 'end') for w in (self.fac_name, self.fac_email, self.fac_dept, self.fac_pass)])
            except Exception as e:
                self.after(0, lambda: self.fac_msg.configure(text=f"Error: {e}", text_color=theme.DANGER))
        threading.Thread(target=worker, daemon=True).start()

    def build_class_attendance(self):
        f = ctk.CTkFrame(self.main_content, fg_color="transparent")
        ctk.CTkLabel(f, text="Class Roster & Attendance", font=theme.H1, text_color=theme.TEXT).pack(anchor="w", pady=(0, 20))
        
        # Top bar: Class Selector
        top_bar = ctk.CTkFrame(f, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))
        
        self.class_sel = ctk.CTkOptionMenu(top_bar, values=["Select Class"], width=200, height=35, command=self._load_class_data)
        self.class_sel.pack(side="left", padx=(0, 10))
        
        # Data container
        self.cls_scroll = ctk.CTkScrollableFrame(f, fg_color=theme.CARD_BG, corner_radius=theme.RADIUS_LG)
        self.cls_scroll.pack(fill="both", expand=True)
        self.add_tab_frame("Class & Attendance", f)
        
        threading.Thread(target=self._populate_classes, daemon=True).start()

    def _populate_classes(self):
        try:
            classes = api.get_classes()
            if classes:
                self.after(0, lambda: self.class_sel.configure(values=classes))
                self.after(0, lambda: self.class_sel.set(classes[0]))
                self.after(0, lambda: self._load_class_data(classes[0]))
        except: pass

    def _load_class_data(self, cls_name):
        def worker():
            try:
                students = api.get_class_students(cls_name)
                self.after(0, lambda: self._render_class(students))
            except: pass
        threading.Thread(target=worker, daemon=True).start()

    def _render_class(self, students):
        for widget in self.cls_scroll.winfo_children(): widget.destroy()
        
        header = ctk.CTkFrame(self.cls_scroll, fg_color=theme.BG, corner_radius=theme.RADIUS_SM)
        header.pack(fill="x", pady=(0, 5), padx=5)
        ctk.CTkLabel(header, text="Roll No", font=theme.BODY_BOLD, text_color=theme.TEXT_DIM, width=80).grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkLabel(header, text="Student Name", font=theme.BODY_BOLD, text_color=theme.TEXT_DIM, width=250, anchor="w").grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkLabel(header, text="Actions", font=theme.BODY_BOLD, text_color=theme.TEXT_DIM).grid(row=0, column=2, padx=10, pady=10)
        
        for i, s in enumerate(students):
            row_f = ctk.CTkFrame(self.cls_scroll, fg_color="transparent")
            row_f.pack(fill="x", pady=2, padx=5)
            
            ctk.CTkLabel(row_f, text=s.get("roll_no", ""), font=theme.BODY, text_color=theme.TEXT_DIM, width=80).grid(row=0, column=0, padx=10, pady=8)
            ctk.CTkLabel(row_f, text=s.get("name", ""), font=theme.BODY_BOLD, text_color=theme.TEXT, width=250, anchor="w").grid(row=0, column=1, padx=10, pady=8)
            
            btn = ctk.CTkButton(row_f, text="View Report", width=100, height=28, fg_color="transparent", border_width=1, border_color=theme.PRIMARY, text_color=theme.PRIMARY, hover_color=theme.BG)
            btn.grid(row=0, column=2, padx=10, pady=8)
            
            if i < len(students) - 1:
                div = ctk.CTkFrame(self.cls_scroll, fg_color=theme.BORDER, height=1)
                div.pack(fill="x", padx=15, pady=2)

    def build_timetables(self):
        f = ctk.CTkFrame(self.main_content, fg_color="transparent")
        ctk.CTkLabel(f, text="Timetable Viewer", font=theme.H1, text_color=theme.TEXT).pack(anchor="w", pady=(0, 20))
        
        top_bar = ctk.CTkFrame(f, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))
        
        self.tt_sel = ctk.CTkOptionMenu(top_bar, values=["Select Class"], width=200, height=35, command=self._load_tt_data)
        self.tt_sel.pack(side="left", padx=(0, 10))
        
        self.admin_tt_scroll = ctk.CTkScrollableFrame(f, fg_color=theme.CARD_BG, corner_radius=theme.RADIUS_LG)
        self.admin_tt_scroll.pack(fill="both", expand=True)
        self.add_tab_frame("Timetables", f)
        
        threading.Thread(target=self._populate_tt_classes, daemon=True).start()

    def _populate_tt_classes(self):
        try:
            classes = api.get_classes()
            if classes:
                self.after(0, lambda: self.tt_sel.configure(values=classes))
                self.after(0, lambda: self.tt_sel.set(classes[0]))
                self.after(0, lambda: self._load_tt_data(classes[0]))
        except: pass

    def _load_tt_data(self, cls_name):
        def worker():
            try:
                rows = api.get_timetable(cls_name)
                self.after(0, lambda: self._render_admin_tt(rows))
            except: pass
        threading.Thread(target=worker, daemon=True).start()

    def _render_admin_tt(self, rows):
        for widget in self.admin_tt_scroll.winfo_children(): widget.destroy()
        
        current_day = ""
        day_frame = None
        for r in rows:
            if r['day_of_week'] != current_day:
                current_day = r['day_of_week']
                
                day_frame = ctk.CTkFrame(self.admin_tt_scroll, fg_color="transparent")
                day_frame.pack(fill="x", pady=(20, 10), padx=10)
                ctk.CTkLabel(day_frame, text=current_day.upper(), font=theme.H3, text_color=theme.PRIMARY).pack(anchor="w", pady=(0, 5))
                
                h = ctk.CTkFrame(day_frame, fg_color=theme.BG, corner_radius=theme.RADIUS_SM)
                h.pack(fill="x")
                ctk.CTkLabel(h, text="Period", font=theme.BODY_BOLD, text_color=theme.TEXT_DIM, width=80).grid(row=0, column=0, padx=10, pady=8)
                ctk.CTkLabel(h, text="Subject", font=theme.BODY_BOLD, text_color=theme.TEXT_DIM, anchor="w").grid(row=0, column=1, padx=20, pady=8)
            
            row_f = ctk.CTkFrame(day_frame, fg_color="transparent")
            row_f.pack(fill="x", pady=2)
            row_f.grid_columnconfigure(1, weight=1)
            
            ctk.CTkLabel(row_f, text=str(r['period_number']), font=theme.BODY, text_color=theme.TEXT_DIM, width=80).grid(row=0, column=0, padx=10, pady=8)
            
            slot = r['slot'] or "Free"
            fac = r.get('faculty_name') or ""
            slot_text = f"{slot} ({fac})" if fac and slot != "Free" else slot
            slot_color = theme.TEXT_DIM if slot == "Free" else theme.TEXT
            ctk.CTkLabel(row_f, text=slot_text, font=theme.BODY, text_color=slot_color, anchor="w").grid(row=0, column=1, padx=20, pady=8, sticky="w")
            
            edit_btn = ctk.CTkButton(row_f, text="Edit", width=60, height=28, fg_color="transparent", text_color=theme.PRIMARY, hover_color=theme.BORDER,
                                     command=lambda rid=r['id'], o_s=slot, o_f=fac: self._prompt_edit_tt(rid, o_s, o_f))
            edit_btn.grid(row=0, column=2, padx=10)
            
            div = ctk.CTkFrame(day_frame, fg_color=theme.BORDER, height=1)
            div.pack(fill="x", padx=10)

    def _prompt_edit_tt(self, tt_id, old_slot, old_fac):
        dialog = ctk.CTkInputDialog(text="Enter new Subject:", title="Edit Subject")
        new_slot = dialog.get_input()
        if new_slot is not None:
            new_fac = ctk.CTkInputDialog(text="Enter Faculty Name:", title="Edit Faculty").get_input()
            if new_fac is not None:
                try:
                    api.update_timetable_slot(tt_id, new_slot, new_fac)
                    self.show_toast("Timetable updated successfully", "success")
                    self._load_admin_tt(None)
                except Exception as e:
                    self.show_toast(f"Error updating: {e}", "error")

class FacultyRootView(SidebarView):
    def __init__(self, master, app):
        super().__init__(master, app, ["Dashboard", "My Timetable", "Live Camera", "Offline Upload"])
        
        self.build_dashboard()
        self.build_faculty_timetable()
        self.build_live_camera()
        self.build_offline_upload()
        
        self.select_tab("Dashboard")

    def build_dashboard(self):
        f = ctk.CTkFrame(self.main_content, fg_color="transparent")
        ctk.CTkLabel(f, text="Faculty Dashboard", font=theme.H1, text_color=theme.TEXT).pack(anchor="w", padx=20, pady=(20, 0))
        
        # Top bar filters
        top_bar = ctk.CTkFrame(f, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=(10, 10))
        
        self.fac_class_sel = ctk.CTkOptionMenu(top_bar, values=["Select Class"], width=150, height=35, command=self._fac_load_roster)
        self.fac_class_sel.pack(side="left", padx=(0, 10))
        
        self.fac_date_sel = ctk.CTkEntry(top_bar, placeholder_text="YYYY-MM-DD", width=120, height=35)
        self.fac_date_sel.insert(0, datetime.date.today().isoformat())
        self.fac_date_sel.pack(side="left", padx=(0, 10))
        
        self.fac_period_sel = ctk.CTkOptionMenu(top_bar, values=["All Periods", "1", "2", "3", "4", "5", "6"], width=120, height=35, command=self._fac_load_roster)
        self.fac_period_sel.pack(side="left", padx=(0, 10))
        
        btn = ctk.CTkButton(top_bar, text="Refresh", width=100, height=35, command=lambda: self._fac_load_roster(None))
        btn.pack(side="left")
        
        # Stats summary
        self.fac_stats_lbl = ctk.CTkLabel(f, text="", font=theme.BODY_BOLD, text_color=theme.PRIMARY)
        self.fac_stats_lbl.pack(anchor="w", padx=20, pady=(0, 10))
        
        # Roster
        self.fac_roster_scroll = ctk.CTkScrollableFrame(f, fg_color=theme.CARD_BG, corner_radius=theme.RADIUS_LG)
        self.fac_roster_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.add_tab_frame("Dashboard", f)
        
        threading.Thread(target=self._fac_init_dashboard, daemon=True).start()

    def _fac_init_dashboard(self):
        try:
            data = api.get_faculty_dashboard()
            classes = data.get("available_classes", [])
            if classes:
                self.after(0, lambda: self.fac_class_sel.configure(values=classes))
                self.after(0, lambda: self.fac_class_sel.set(classes[0]))
                self.after(0, lambda: self._fac_load_roster(None))
        except: pass

    def _fac_load_roster(self, _):
        cls = self.fac_class_sel.get()
        if cls == "Select Class": return
        date_val = self.fac_date_sel.get()
        per_val = self.fac_period_sel.get()
        if per_val == "All Periods": per_val = ""
        
        def worker():
            try:
                data = api.get_faculty_class_attendance(cls, date_val, per_val)
                self.after(0, lambda: self._fac_render_roster(data))
            except: pass
        self.fac_stats_lbl.configure(text="Loading...")
        threading.Thread(target=worker, daemon=True).start()

    def _fac_render_roster(self, data):
        for w in self.fac_roster_scroll.winfo_children(): w.destroy()
        
        tot = data.get("total_students", 0)
        pres = data.get("present_count", 0)
        absent = data.get("absent_count", 0)
        self.fac_stats_lbl.configure(text=f"Total: {tot} | Present: {pres} | Absent: {absent}")
        
        header = ctk.CTkFrame(self.fac_roster_scroll, fg_color=theme.BG, corner_radius=theme.RADIUS_SM)
        header.pack(fill="x", pady=(0, 5), padx=5)
        header.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(header, text="Roll No", font=theme.BODY_BOLD, text_color=theme.TEXT_DIM, width=80).grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkLabel(header, text="Student Name", font=theme.BODY_BOLD, text_color=theme.TEXT_DIM, width=250, anchor="w").grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkLabel(header, text="Status", font=theme.BODY_BOLD, text_color=theme.TEXT_DIM, width=100).grid(row=0, column=2, padx=10, pady=10)
        
        students = data.get("students_list", [])
        period_val = self.fac_period_sel.get()
        date_val = self.fac_date_sel.get()
        
        for i, s in enumerate(students):
            row_f = ctk.CTkFrame(self.fac_roster_scroll, fg_color="transparent")
            row_f.pack(fill="x", pady=2, padx=5)
            row_f.grid_columnconfigure(1, weight=1)
            
            ctk.CTkLabel(row_f, text=s.get("roll_no", ""), font=theme.BODY, text_color=theme.TEXT_DIM, width=80).grid(row=0, column=0, padx=10, pady=8)
            ctk.CTkLabel(row_f, text=s.get("name", ""), font=theme.BODY_BOLD, text_color=theme.TEXT, width=250, anchor="w").grid(row=0, column=1, padx=10, pady=8)
            
            is_present = (s.get("status") == "Present") if "status" in s else s.get("present", False)
            status_text = "Present" if is_present else "Absent"
            status_color = theme.SUCCESS if is_present else theme.DANGER
            
            lbl = ctk.CTkLabel(row_f, text=status_text, font=theme.BODY_BOLD, text_color=status_color, width=100)
            lbl.grid(row=0, column=2, padx=10, pady=8)
            
            if period_val != "All Periods":
                btn = ctk.CTkButton(row_f, text="Toggle", width=60, height=28, fg_color="transparent", text_color=theme.PRIMARY, hover_color=theme.BORDER,
                                    command=lambda sid=s.get("id"), dt=date_val, p=period_val, cur=status_text: self._toggle_attendance(sid, dt, p, cur))
                btn.grid(row=0, column=3, padx=10)
            
            if i < len(students) - 1:
                div = ctk.CTkFrame(self.fac_roster_scroll, fg_color=theme.BORDER, height=1)
                div.pack(fill="x", padx=15, pady=2)

    def _toggle_attendance(self, sid, dt, p, cur_status):
        new_status = "Absent" if cur_status == "Present" else "Present"
        try:
            api.update_attendance(sid, dt, p, new_status)
            self._fac_load_roster(None)
        except Exception as e:
            self.show_toast(f"Update failed: {e}", "error")

    def build_faculty_timetable(self):
        f = ctk.CTkFrame(self.main_content, fg_color="transparent")
        ctk.CTkLabel(f, text="My Timetable", font=theme.H1, text_color=theme.TEXT).pack(anchor="w", padx=40, pady=(40, 10))
        ctk.CTkLabel(f, text="Your assigned classes for the week.", font=theme.BODY, text_color=theme.TEXT_DIM).pack(anchor="w", padx=40, pady=(0, 20))
        
        self.fac_tt_scroll = ctk.CTkScrollableFrame(f, fg_color="transparent")
        self.fac_tt_scroll.pack(fill="both", expand=True, padx=40, pady=10)
        
        self.add_tab_frame("My Timetable", f)
        
        def worker():
            try:
                rows = api.get_faculty_timetable()
                self.after(0, lambda: self._render_fac_tt(rows))
            except Exception as e:
                pass
        threading.Thread(target=worker, daemon=True).start()

    def _render_fac_tt(self, rows):
        for widget in self.fac_tt_scroll.winfo_children(): widget.destroy()
        if not rows:
            ctk.CTkLabel(self.fac_tt_scroll, text="No classes assigned yet.", font=theme.H3, text_color=theme.TEXT_DIM).pack(pady=40)
            return
            
        current_day = ""
        day_frame = None
        for r in rows:
            if r['day_of_week'] != current_day:
                current_day = r['day_of_week']
                day_frame = ctk.CTkFrame(self.fac_tt_scroll, fg_color="transparent")
                day_frame.pack(fill="x", pady=(20, 10), padx=10)
                ctk.CTkLabel(day_frame, text=current_day.upper(), font=theme.H3, text_color=theme.PRIMARY).pack(anchor="w", pady=(0, 5))
                
                h = ctk.CTkFrame(day_frame, fg_color=theme.BG, corner_radius=theme.RADIUS_SM)
                h.pack(fill="x")
                ctk.CTkLabel(h, text="Period", font=theme.BODY_BOLD, text_color=theme.TEXT_DIM, width=80).grid(row=0, column=0, padx=10, pady=8)
                ctk.CTkLabel(h, text="Class", font=theme.BODY_BOLD, text_color=theme.TEXT_DIM, width=120).grid(row=0, column=1, padx=20, pady=8)
                ctk.CTkLabel(h, text="Subject", font=theme.BODY_BOLD, text_color=theme.TEXT_DIM, anchor="w").grid(row=0, column=2, padx=20, pady=8)
            
            row_f = ctk.CTkFrame(day_frame, fg_color="transparent")
            row_f.pack(fill="x", pady=2)
            ctk.CTkLabel(row_f, text=str(r['period_number']), font=theme.BODY, text_color=theme.TEXT_DIM, width=80).grid(row=0, column=0, padx=10, pady=8)
            ctk.CTkLabel(row_f, text=r['target_class'], font=theme.BODY_BOLD, text_color=theme.PRIMARY, width=120).grid(row=0, column=1, padx=20, pady=8)
            ctk.CTkLabel(row_f, text=r['slot'], font=theme.BODY, text_color=theme.TEXT, anchor="w").grid(row=0, column=2, padx=20, pady=8)
            
            div = ctk.CTkFrame(day_frame, fg_color=theme.BORDER, height=1)
            div.pack(fill="x", padx=10)

    def build_live_camera(self):
        f = ctk.CTkFrame(self.main_content, fg_color="transparent")
        ctk.CTkLabel(f, text="Auto-Capture Live Feed", font=theme.H1, text_color=theme.TEXT).pack(anchor="w", padx=20, pady=20)
        
        self.camera = CameraFeed(f, width=800, height=480)
        self.camera.pack(pady=10)
        
        btn_frame = ctk.CTkFrame(f, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(btn_frame, text="Start Stream", command=self.camera.start, fg_color=theme.SUCCESS).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Stop Stream", command=self.camera.stop, fg_color=theme.DANGER).pack(side="left", padx=10)
        
        self.add_tab_frame("Live Camera", f)

    def build_offline_upload(self):
        f = ctk.CTkFrame(self.main_content, fg_color="transparent")
        ctk.CTkLabel(f, text="Offline Photo Upload", font=theme.H1, text_color=theme.TEXT).pack(anchor="w", padx=20, pady=20)
        
        card = ctk.CTkFrame(f, fg_color=theme.CARD_BG, corner_radius=theme.RADIUS_LG)
        card.pack(fill="x", padx=20, pady=10)
        
        self.up_class = ctk.CTkEntry(card, placeholder_text="Target Class (e.g. S6 CSB)", height=40)
        self.up_class.pack(fill="x", padx=20, pady=(20, 10))
        
        self.up_period = ctk.CTkEntry(card, placeholder_text="Period (1-6)", height=40)
        self.up_period.pack(fill="x", padx=20, pady=10)
        
        self.up_date = ctk.CTkEntry(card, placeholder_text="Date (YYYY-MM-DD)", height=40)
        self.up_date.insert(0, datetime.date.today().isoformat())
        self.up_date.pack(fill="x", padx=20, pady=10)
        
        self.up_path = ctk.CTkEntry(card, placeholder_text="Path to Image File", height=40)
        self.up_path.pack(fill="x", padx=20, pady=10)
        
        self.up_msg = ctk.CTkLabel(card, text="")
        self.up_msg.pack(pady=5)
        
        ctk.CTkButton(card, text="Process Image & Mark Attendance", height=40, command=self._submit_upload).pack(pady=(10, 20))
        
        self.add_tab_frame("Offline Upload", f)

    def _submit_upload(self):
        cls = self.up_class.get()
        per = self.up_period.get()
        dt = self.up_date.get()
        pth = self.up_path.get()
        
        if not all([cls, per, dt, pth]):
            self.up_msg.configure(text="All fields required.", text_color=theme.DANGER)
            return
            
        def worker():
            try:
                res = api.offline_attendance(pth, cls, per, dt)
                if res.get("success"):
                    names = res.get("names", [])
                    msg = f"Success! Marked {len(names)} students present."
                    self.after(0, lambda: self.up_msg.configure(text=msg, text_color=theme.SUCCESS))
                else:
                    self.after(0, lambda: self.up_msg.configure(text=res.get("error", "Unknown error"), text_color=theme.DANGER))
            except Exception as e:
                self.after(0, lambda: self.up_msg.configure(text=f"Error: {e}", text_color=theme.DANGER))
                
        self.up_msg.configure(text="Processing... This may take a minute.", text_color=theme.WARNING)
        threading.Thread(target=worker, daemon=True).start()
        
class StudentRootView(SidebarView):
    def __init__(self, master, app):
        super().__init__(master, app, ["Dashboard", "Attendance History", "My Timetable"])
        
        self.build_dashboard()
        self.build_history()
        self.build_timetable()
        
        self.select_tab("Dashboard")

    def build_dashboard(self):
        f = ctk.CTkFrame(self.main_content, fg_color="transparent")
        ctk.CTkLabel(f, text="Student Dashboard", font=theme.H1, text_color=theme.TEXT).pack(anchor="w", padx=20, pady=20)
        
        stats_frame = ctk.CTkFrame(f, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20, pady=10)
        stats_frame.grid_columnconfigure((0,1), weight=1)
        
        self.stat_attended = StatCard(stats_frame, "Classes Attended", "Loading...")
        self.stat_attended.grid(row=0, column=0, padx=5, sticky="ew")
        self.stat_missed = StatCard(stats_frame, "Classes Missed", "Loading...")
        self.stat_missed.grid(row=0, column=1, padx=5, sticky="ew")
        
        self.chart_frame = ctk.CTkFrame(f, fg_color=theme.CARD_BG, corner_radius=theme.RADIUS_LG)
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.add_tab_frame("Dashboard", f)
        
        threading.Thread(target=self._load_dashboard, daemon=True).start()

    def _load_dashboard(self):
        try:
            data = api.get_student_dashboard()
            self.after(0, lambda: self._update_dash_ui(data))
        except:
            pass

    def _update_dash_ui(self, data):
        self.stat_attended.winfo_children()[1].configure(text=str(data.get("classes_attended", 0)))
        self.stat_missed.winfo_children()[1].configure(text=str(data.get("classes_missed", 0)))
        
        attended = data.get("classes_attended", 0)
        missed = data.get("classes_missed", 0)
        total = attended + missed
        if total == 0:
            return
            
        fig = Figure(figsize=(5, 3), dpi=100, facecolor=theme.CARD_BG)
        ax = fig.add_subplot(111)
        ax.set_facecolor(theme.CARD_BG)
        
        ax.pie(
            [attended, missed], 
            labels=["Attended", "Missed"],
            colors=[theme.SUCCESS, theme.DANGER],
            autopct='%1.1f%%',
            startangle=90,
            textprops={'color': theme.TEXT}
        )
        
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
            
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def build_history(self):
        f = ctk.CTkFrame(self.main_content, fg_color="transparent")
        ctk.CTkLabel(f, text="Attendance History", font=theme.H1, text_color=theme.TEXT).pack(anchor="w", pady=(0, 20))
        
        # Use a modern ScrollableFrame instead of a Textbox
        self.hist_scroll = ctk.CTkScrollableFrame(f, fg_color=theme.CARD_BG, corner_radius=theme.RADIUS_LG)
        self.hist_scroll.pack(fill="both", expand=True)
        self.add_tab_frame("Attendance History", f)
        
        threading.Thread(target=self._load_history, daemon=True).start()

    def _load_history(self):
        try:
            to_d = datetime.date.today()
            from_d = to_d - datetime.timedelta(days=30)
            uid = self.app.user.get("user_id")
            records = api.get_student_attendance_history(uid, from_d.isoformat(), to_d.isoformat())
            self.after(0, lambda: self._render_history(records))
        except: pass

    def _render_history(self, records):
        # Clear existing
        for widget in self.hist_scroll.winfo_children(): widget.destroy()
        
        # Header
        header = ctk.CTkFrame(self.hist_scroll, fg_color=theme.BG, corner_radius=theme.RADIUS_SM)
        header.pack(fill="x", pady=(0, 5), padx=5)
        cols = ["Date", "P1", "P2", "P3", "P4", "P5", "P6"]
        for i, c in enumerate(cols):
            w = 120 if i == 0 else 80
            ctk.CTkLabel(header, text=c, font=theme.BODY_BOLD, text_color=theme.TEXT_DIM, width=w, anchor="w" if i==0 else "center").grid(row=0, column=i, padx=10, pady=10)
        
        # Rows
        for i, r in enumerate(records):
            row_f = ctk.CTkFrame(self.hist_scroll, fg_color="transparent")
            row_f.pack(fill="x", pady=2, padx=5)
            
            ctk.CTkLabel(row_f, text=r.get("date", ""), font=theme.BODY, text_color=theme.TEXT, width=120, anchor="w").grid(row=0, column=0, padx=10, pady=8)
            
            for j in range(1, 7):
                status = r.get(f"hour{j}", "-")
                color = theme.SUCCESS if status == "Present" else (theme.DANGER if status == "Absent" else theme.TEXT_DIM)
                lbl = ctk.CTkLabel(row_f, text=status, font=theme.BODY, text_color=color, width=80, anchor="center")
                lbl.grid(row=0, column=j, padx=10, pady=8)
                
            # Divider
            if i < len(records) - 1:
                div = ctk.CTkFrame(self.hist_scroll, fg_color=theme.BORDER, height=1)
                div.pack(fill="x", padx=15, pady=2)

    def build_timetable(self):
        f = ctk.CTkFrame(self.main_content, fg_color="transparent")
        ctk.CTkLabel(f, text="My Timetable", font=theme.H1, text_color=theme.TEXT).pack(anchor="w", pady=(0, 20))
        
        self.tt_scroll = ctk.CTkScrollableFrame(f, fg_color=theme.CARD_BG, corner_radius=theme.RADIUS_LG)
        self.tt_scroll.pack(fill="both", expand=True)
        self.add_tab_frame("My Timetable", f)
        
        threading.Thread(target=self._load_tt, daemon=True).start()

    def _load_tt(self):
        try:
            cls = self.app.user.get("target_class")
            if not cls: return
            rows = api.get_timetable(cls)
            self.after(0, lambda: self._render_tt(rows))
        except: pass
        
    def _render_tt(self, rows):
        for widget in self.tt_scroll.winfo_children(): widget.destroy()
        
        current_day = ""
        day_frame = None
        for r in rows:
            if r['day_of_week'] != current_day:
                current_day = r['day_of_week']
                
                day_frame = ctk.CTkFrame(self.tt_scroll, fg_color="transparent")
                day_frame.pack(fill="x", pady=(20, 10), padx=10)
                
                ctk.CTkLabel(day_frame, text=current_day.upper(), font=theme.H3, text_color=theme.PRIMARY).pack(anchor="w", pady=(0, 5))
                
                # Header
                h = ctk.CTkFrame(day_frame, fg_color=theme.BG, corner_radius=theme.RADIUS_SM)
                h.pack(fill="x")
                ctk.CTkLabel(h, text="Period", font=theme.BODY_BOLD, text_color=theme.TEXT_DIM, width=80, anchor="center").grid(row=0, column=0, padx=10, pady=8)
                ctk.CTkLabel(h, text="Subject", font=theme.BODY_BOLD, text_color=theme.TEXT_DIM, anchor="w").grid(row=0, column=1, padx=20, pady=8)
            
            # Row
            row_f = ctk.CTkFrame(day_frame, fg_color="transparent")
            row_f.pack(fill="x", pady=2)
            ctk.CTkLabel(row_f, text=str(r['period_number']), font=theme.BODY, text_color=theme.TEXT_DIM, width=80, anchor="center").grid(row=0, column=0, padx=10, pady=8)
            
            slot = r['slot'] or "Free"
            slot_color = theme.TEXT_DIM if slot == "Free" else theme.TEXT
            ctk.CTkLabel(row_f, text=slot, font=theme.BODY, text_color=slot_color, anchor="w").grid(row=0, column=1, padx=20, pady=8)
            
            div = ctk.CTkFrame(day_frame, fg_color=theme.BORDER, height=1)
            div.pack(fill="x", padx=10)

if __name__ == "__main__":
    app = APCASApp()
    app.mainloop()

print('Testing append...')
