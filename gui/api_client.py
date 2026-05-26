"""
APCAS API Client — thin wrapper around requests.Session.
Talks to the Flask backend on http://127.0.0.1:5000.
"""

import requests
from typing import Optional

BASE_URL = "http://127.0.0.1:5000"


class APIClient:
    def __init__(self):
        self.session = requests.Session()

    # ── Auth ──────────────────────────────────────────────────────────────────
    def login(self, role: str, email: str, password: str) -> dict:
        """Returns dict with 'success' key; raises on network error."""
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
        except Exception:
            pass
        return None

    def logout(self) -> None:
        try:
            self.session.post(f"{BASE_URL}/api/v1/auth/logout", timeout=5)
        except Exception:
            pass

    # ── Dashboards ────────────────────────────────────────────────────────────
    def get_student_dashboard(self) -> dict:
        res = self.session.get(f"{BASE_URL}/api/v1/student/dashboard", timeout=10)
        res.raise_for_status()
        return res.json()

    def get_faculty_dashboard(self, cls: str = None, date: str = None, period: str = None) -> dict:
        params = {}
        if cls:
            params["class"] = cls
        if date:
            params["date"] = date
        if period:
            params["period"] = period
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

    # ── Faculty actions ───────────────────────────────────────────────────────
    def offline_attendance(self, photo_path: str, target_class: str,
                           period: str, date: str) -> dict:
        with open(photo_path, "rb") as f:
            res = self.session.post(
                f"{BASE_URL}/api/offline_attendance",
                files={"photo": f},
                data={"target_class": target_class, "period": period, "date": date},
                timeout=60,
            )
        res.raise_for_status()
        return res.json()

    def get_faculty_periods(self, date: str) -> list:
        res = self.session.get(f"{BASE_URL}/api/faculty_periods", params={"date": date}, timeout=10)
        res.raise_for_status()
        return res.json()

    # ── Admin actions ─────────────────────────────────────────────────────────
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

    # ── Attendance edit ───────────────────────────────────────────────────────
    def update_attendance(self, roll: str, date: str, updates: dict) -> dict:
        res = self.session.post(
            f"{BASE_URL}/api/admin_update_attendance",
            json={"roll": roll, "date": date, "updates": updates},
            timeout=10,
        )
        res.raise_for_status()
        return res.json()

    # ── Health ────────────────────────────────────────────────────────────────
    def ping(self) -> bool:
        try:
            self.session.get(f"{BASE_URL}/", timeout=3)
            return True
        except Exception:
            return False


# Shared singleton — import and use `api` everywhere
api = APIClient()
