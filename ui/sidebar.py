import tkinter as tk
from tkinter import ttk

from config import PRIMARY_BLUE
from ui.utils import draw_rounded_rect
from services.wifi import get_local_ip
from services.weather import get_city_if_rain_predicted
from database import queries


class Sidebar:
    """Suggested Tasks sidebar with scrollable pill-style task cards."""

    def __init__(self, app):
        self.app = app
        self.canvas = app.canvas
        self.root = app.root
        self.cursor = app.cursor
        self.connection = app.connection

        self._draw_background()
        self._create_scrollable_area()

    def _draw_background(self):
        """Draw the blue rounded sidebar background."""
        draw_rounded_rect(
            self.canvas, 25, 125, 400, 550,
            radius=40, color=PRIMARY_BLUE
        )
        self.canvas.create_text(
            160, 160, text="Suggested Tasks",
            font=("Poppins", 28, "bold"), fill="white"
        )

    def _create_scrollable_area(self):
        """Set up the scrollable frame inside the sidebar."""
        self.suggested_box_frame = tk.Frame(self.root, bg=PRIMARY_BLUE)
        self.suggested_box_frame.place(x=45, y=200, width=340, height=320)

        # Canvas inside the blue sidebar
        self.suggested_canvas = tk.Canvas(
            self.suggested_box_frame,
            bg=PRIMARY_BLUE,
            highlightthickness=0,
            bd=0
        )
        self.suggested_canvas.pack(side="left", fill="both", expand=True)

        # Custom blue scrollbar
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Blue.Vertical.TScrollbar",
            gripcount=0,
            background=PRIMARY_BLUE,
            darkcolor=PRIMARY_BLUE,
            lightcolor=PRIMARY_BLUE,
            troughcolor=PRIMARY_BLUE,
            bordercolor=PRIMARY_BLUE,
            arrowcolor=PRIMARY_BLUE
        )

        self.scrollbar = ttk.Scrollbar(
            self.suggested_box_frame,
            orient="vertical",
            command=self.suggested_canvas.yview,
            style="Blue.Vertical.TScrollbar"
        )
        self.scrollbar.pack(side="right", fill="y")
        self.suggested_canvas.configure(yscrollcommand=self.scrollbar.set)

        # Inner frame to hold translucent pills
        self.scrollable_frame = tk.Frame(self.suggested_canvas, bg=PRIMARY_BLUE)
        self.suggested_canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )

        # Update scroll region automatically
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)

        # Mousewheel scrolling support
        self.scrollable_frame.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_frame_configure(self, event):
        self.suggested_canvas.configure(
            scrollregion=self.suggested_canvas.bbox("all")
        )

    def _on_mousewheel(self, event):
        if self.root.tk.call('tk', 'windowingsystem') == 'aqua':  # macOS
            self.suggested_canvas.yview_scroll(-1 * int(event.delta), "units")
        else:
            self.suggested_canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    def _create_task_pill(self, text):
        """Create a single pill-style task card."""
        pill_frame = tk.Frame(self.scrollable_frame, bg=PRIMARY_BLUE)
        pill_frame.pack(fill="x", padx=10, pady=8)

        canvas_pill = tk.Canvas(
            pill_frame,
            width=300,
            height=60,
            bg=PRIMARY_BLUE,
            highlightthickness=0,
            bd=0
        )
        canvas_pill.pack()

        # Rounded translucent pill
        x1, y1, x2, y2, r = 5, 5, 295, 55, 20
        canvas_pill.create_polygon(
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
            smooth=True,
            fill="#BFD3FF",
            outline="#BFD3FF"
        )
        canvas_pill.create_text(
            (x1 + x2) / 2,
            (y1 + y2) / 2,
            text=text,
            font=("Poppins", 20, "bold"),
            fill="#003366"
        )

    def update_suggested_tasks(self):
        """Fetch and display suggested tasks based on WiFi and Weather."""
        wifi = get_local_ip()

        # Get WiFi-based tags
        wifi_tags = queries.get_tags_by_wifi(self.cursor, wifi) if wifi else []

        # Clear existing pills
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        found_any = False
        total_tasks = 0

        # --- WiFi-based Suggested Tasks ---
        for tag_name in wifi_tags:
            tasks = queries.get_incomplete_tasks_by_tag(self.cursor, tag_name)
            for task in tasks:
                self._create_task_pill(task)
                total_tasks += 1
                found_any = True

        # --- Weather-based Suggested Tasks (rain prediction) ---
        rain_tags = []
        locations = queries.get_all_tag_locations(self.cursor)
        for location in locations:
            if get_city_if_rain_predicted(location):
                tags = queries.get_tags_by_location(self.cursor, location)
                rain_tags.extend(tags)

        rain_tags = list(dict.fromkeys(rain_tags))  # Remove duplicates

        for tag_name in rain_tags:
            tasks = queries.get_incomplete_tasks_by_tag(self.cursor, tag_name)
            for task in tasks:
                self._create_task_pill(task)
                total_tasks += 1
                found_any = True

        # --- No task message ---
        if not found_any:
            tk.Label(
                self.scrollable_frame,
                text="No suggested tasks",
                font=("Poppins", 16, "italic"),
                fg="white",
                bg=PRIMARY_BLUE
            ).pack(pady=20)

        # --- Enable scrollbar only if >4 tasks ---
        if total_tasks > 4:
            self.scrollbar.pack(side="right", fill="y")
            self.suggested_canvas.configure(yscrollcommand=self.scrollbar.set)
        else:
            self.scrollbar.pack_forget()
            self.suggested_canvas.configure(yscrollcommand=None)

    def monitor_wifi(self):
        """Refresh suggested tasks safely every 10 seconds using Tkinter's main thread."""
        from config import WIFI_MONITOR_INTERVAL
        self.update_suggested_tasks()
        self.root.after(WIFI_MONITOR_INTERVAL, self.monitor_wifi)
