"""
CameraFeed — embeds an OpenCV MJPEG frame stream into a CTkLabel.
Runs frame pulls in a background thread so the UI stays responsive.
"""

import threading
import time
import customtkinter as ctk
from PIL import Image, ImageTk
import io
import requests as req_lib

from gui import theme


class CameraFeed(ctk.CTkFrame):
    """
    Pulls MJPEG frames from Flask's /api/admin/live_feed endpoint
    and renders them into a label at ~15 fps.
    """

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

        # Label that shows the frame
        self._feed_label = ctk.CTkLabel(
            self,
            text="",
            width=width,
            height=height,
            fg_color=theme.BG,
            corner_radius=theme.RADIUS_LG,
        )
        self._feed_label.pack(fill="both", expand=True)

        # Placeholder while stream is off
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
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._stream_worker, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._session:
            try:
                self._session.close()
            except Exception:
                pass

    def _stream_worker(self):
        """Background thread: reads MJPEG boundary chunks and updates the label."""
        try:
            self._session = req_lib.Session()
            response = self._session.get(self.STREAM_URL, stream=True, timeout=10)
            buffer = b""
            for chunk in response.iter_content(chunk_size=4096):
                if not self._running:
                    break
                buffer += chunk
                # Find JPEG start/end markers
                start = buffer.find(b"\xff\xd8")
                end   = buffer.find(b"\xff\xd9")
                if start != -1 and end != -1 and end > start:
                    jpeg_data = buffer[start:end + 2]
                    buffer = buffer[end + 2:]
                    try:
                        img = Image.open(io.BytesIO(jpeg_data))
                        img = img.resize((self._feed_width, self._feed_height), Image.LANCZOS)
                        ctk_img = ctk.CTkImage(img, size=(self._feed_width, self._feed_height))
                        # Update on main thread
                        self._feed_label.after(0, lambda i=ctk_img: self._feed_label.configure(image=i, text=""))
                    except Exception:
                        pass
        except Exception:
            # Stream not available — show placeholder
            self.after(0, self._placeholder)
