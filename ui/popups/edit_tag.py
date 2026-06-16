import tkinter as tk
from tkinter import ttk, messagebox

from config import GOOGLE_API_KEY, CITY_PICKER_PORT
from ui.utils import draw_rounded_rect
from services.wifi import get_local_ip
from services.city_picker import pick_city
from database import queries


class EditTagPopup:
    """Popup window for adding/editing a tag (WiFi or Weather based)."""

    def __init__(self, app):
        self.app = app
        self.cursor = app.cursor
        self.connection = app.connection

        self.popup = tk.Toplevel(app.root)
        self.popup.title("Add / Edit Tag")
        self.popup.geometry("500x400")
        self.popup.configure(bg="#DEDEDE")
        self.popup.grab_set()

        self._build_ui()

    def _build_ui(self):
        """Build the Add/Edit Tag form UI."""
        # ---- Tag Name ----
        tk.Label(
            self.popup, text="Enter Tag Name:",
            font=("Poppins", 22, "bold"),
            bg="#DEDEDE", fg="#1555DC"
        ).pack(pady=(30, 8))

        self.tag_entry = tk.Entry(
            self.popup, font=("Poppins", 18),
            width=25, bg="#5A565F"
        )
        self.tag_entry.pack(pady=(0, 20), ipady=6)

        # ---- Tag Type ----
        tk.Label(
            self.popup, text="Tag Type:",
            font=("Poppins", 22, "bold"),
            bg="#DEDEDE", fg="#1555DC"
        ).pack(pady=(10, 8))

        self.tag_type = ttk.Combobox(
            self.popup, values=["WiFi", "Weather"],
            state="readonly", font=("Poppins", 16)
        )
        self.tag_type.pack(pady=(0, 25))
        self.tag_type.set("Select Type")

        # ---- Save Button ----
        btn_holder = tk.Frame(self.popup, bg="#DEDEDE")
        btn_holder.pack(pady=16)

        pill_w, pill_h = 150, 50
        btn_canvas = tk.Canvas(
            btn_holder, width=pill_w, height=pill_h,
            bg="#DEDEDE", highlightthickness=0
        )
        btn_canvas.pack()

        pill_id = draw_rounded_rect(
            btn_canvas, 0, 0, pill_w, pill_h,
            radius=40, color="#1555DC", outline="#1555DC"
        )
        text_id = btn_canvas.create_text(
            pill_w / 2, pill_h / 2,
            text="Save", fill="white",
            font=("Poppins", 20, "bold")
        )

        for tag in (pill_id, text_id):
            btn_canvas.tag_bind(tag, "<Button-1>", lambda e: self._save_tag())

        self.popup.bind("<Return>", lambda e: self._save_tag())

    def _save_tag(self):
        """Validate and save the tag to the database."""
        tag = self.tag_entry.get().strip()
        tp = self.tag_type.get()

        if not tag or tp == "Select Type":
            messagebox.showerror("Error", "Please enter name and type.")
            return

        if tp == "WiFi":
            wifi = get_local_ip()
            if not wifi:
                messagebox.showerror("Error", "WiFi not detected!")
                return
            queries.insert_wifi_tag(self.cursor, self.connection, tag, wifi)
            messagebox.showinfo("Success", f"Tag '{tag}' added (WiFi linked).")
            self.popup.destroy()

        elif tp == "Weather":
            messagebox.showinfo("Info", "Select your city on the map.")
            city = pick_city(GOOGLE_API_KEY, port=CITY_PICKER_PORT)
            queries.insert_weather_tag(self.cursor, self.connection, tag, city)
            messagebox.showinfo("Success", f"Tag '{tag}' added for city: {city}")
            self.popup.destroy()
