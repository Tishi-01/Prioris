import tkinter as tk
from PIL import Image, ImageTk

from config import (
    WINDOW_TITLE, WINDOW_SIZE, BG_COLOR, CANVAS_BG,
    LOGO_PATH, PRIMARY_BLUE
)
from database.connection import get_connection
from ui.utils import draw_rounded_rect
from ui.sidebar import Sidebar
from ui.filters import Filters
from ui.matrix import Matrix
from ui.popups.add_task import AddTaskPopup
from ui.popups.tag_manager import TagManagerPopup


class PriorisApp:
    """Main application class that orchestrates all UI components."""

    def __init__(self):
        # ---- Database ----
        self.connection, self.cursor = get_connection()

        # ---- Root Window ----
        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.config(bg=BG_COLOR)

        # ---- Main Canvas ----
        self.canvas = tk.Canvas(self.root, bg=CANVAS_BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # ---- Logo ----
        self._load_logo()

        # ---- UI Components ----
        self.sidebar = Sidebar(self)
        self.filters = Filters(self)
        self.matrix = Matrix(self)

        # ---- Bottom Buttons ----
        self._create_bottom_buttons()

        # ---- Initial Load ----
        self.matrix.display_tasks("All")
        self.sidebar.monitor_wifi()

    def _load_logo(self):
        """Load and display the Prioris logo."""
        img = Image.open(LOGO_PATH)
        img = img.resize((250, 110))
        self.photo = ImageTk.PhotoImage(img)
        self.canvas.create_image(25, 5, image=self.photo, anchor="nw")
        self.canvas.image = self.photo

    def _create_bottom_buttons(self):
        """Create the Edit Tags and Add Task buttons."""
        # ---- Edit Tags button ----
        draw_rounded_rect(
            self.canvas, 25, 670, 195, 730,
            radius=50, color="#FFFFFF", outline="#DEDEDE"
        )
        self.canvas.create_text(
            60, 697, text="✎", fill="black",
            font=("Poppins", 27, "bold")
        )
        self.canvas.create_text(
            130, 700, text="Edit Tags", fill="black",
            font=("Poppins", 22, "bold")
        )

        # ---- Add Task button ----
        draw_rounded_rect(
            self.canvas, 25, 750, 225, 810,
            radius=50, color=PRIMARY_BLUE
        )
        self.canvas.create_text(
            60, 777, text="+", fill="white",
            font=("Poppins", 36, "bold")
        )
        self.canvas.create_text(
            140, 780, text="Add Task", fill="white",
            font=("Poppins", 26, "bold")
        )

        # ---- Hotspots (invisible clickable areas) ----
        add_task_hotspot = self.canvas.create_rectangle(
            25, 750, 225, 810, outline="", fill=""
        )
        self.canvas.tag_bind(
            add_task_hotspot, "<Button-1>",
            lambda e: AddTaskPopup(self)
        )

        edit_tag_hotspot = self.canvas.create_rectangle(
            25, 670, 195, 730, outline="", fill=""
        )
        self.canvas.tag_bind(
            edit_tag_hotspot, "<Button-1>",
            lambda e: TagManagerPopup(self)
        )

    def run(self):
        """Start the Tkinter main loop."""
        self.root.mainloop()
