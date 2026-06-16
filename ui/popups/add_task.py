import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

from ui.utils import draw_rounded_rect
from database import queries


class AddTaskPopup:
    """Popup window for adding a new task."""

    def __init__(self, app):
        self.app = app
        self.cursor = app.cursor
        self.connection = app.connection

        self.popup = tk.Toplevel(app.root)
        self.popup.title("Add Task")
        self.popup.geometry("600x400")
        self.popup.configure(bg="#FFFFFF")
        self.popup.grab_set()

        self._build_ui()

    def _build_ui(self):
        """Build the complete Add Task form UI."""
        self._create_name_entry()
        self._create_form_fields()
        self._create_save_button()

    def _create_name_entry(self):
        """Create the task name entry with placeholder behavior."""
        self.name_entry = tk.Entry(
            self.popup,
            font=("Poppins", 50, "bold"),
            width=40,
            relief="flat",
            bd=0,
            highlightthickness=0,
            highlightbackground="#FFFFFF",
            highlightcolor="#FFFFFF",
            bg="#FFFFFF",
            fg="gray",
            insertbackground="black"
        )
        self.name_entry.insert(0, "Enter Task")
        self.name_entry.pack(padx=24, pady=(30, 12), ipady=6, ipadx=6)

        self.name_entry.bind("<FocusIn>", self._on_entry_click)
        self.name_entry.bind("<FocusOut>", self._on_focusout)

    def _on_entry_click(self, event):
        if self.name_entry.get() == "Enter Task":
            self.name_entry.delete(0, "end")
            self.name_entry.config(fg="black")

    def _on_focusout(self, event):
        if self.name_entry.get().strip() == "":
            self.name_entry.insert(0, "Enter Task")
            self.name_entry.config(fg="gray")

    def _create_form_fields(self):
        """Create deadline, category, and tag form fields."""
        form = tk.Frame(self.popup, bg="#FFFFFF")
        form.pack(fill="x", padx=24, pady=(4, 6))
        form.grid_columnconfigure(0, weight=0)
        form.grid_columnconfigure(1, weight=1, uniform="in")
        form.grid_columnconfigure(2, weight=1, uniform="in")

        # Style configuration
        style = ttk.Style(self.popup)
        style.theme_use("clam")
        style.configure(
            "Popup.TCombobox",
            padding=6,
            arrowsize=12,
            fieldbackground="#FFFFFF",
            background="#FFFFFF",
            foreground="#000000",
            arrowcolor="#000000"
        )
        self.popup.option_add("*TCombobox*Listbox.background", "#FFFFFF")
        self.popup.option_add("*TCombobox*Listbox.foreground", "#000000")
        self.popup.option_add("*TCombobox*Listbox.selectBackground", "#E5E7EB")
        self.popup.option_add("*TCombobox*Listbox.selectForeground", "#000000")

        CB_FONT = ("Poppins", 12)

        # ---- Deadline ----
        tk.Label(
            form, text="Deadline:", font=("Poppins", 25, "bold"),
            bg="#FFFFFF", fg="#000000"
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        today_date = datetime.today().date()
        date_options = ["Date"] + [
            (today_date + timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range(365)
        ]
        time_options = ["Time"] + [
            f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 30)
        ]

        self.date_var = tk.StringVar()
        self.time_var = tk.StringVar()

        date_box = ttk.Combobox(
            form, textvariable=self.date_var, state="readonly",
            font=CB_FONT, style="Popup.TCombobox", values=date_options
        )
        date_box.set("Date")
        date_box.grid(row=0, column=1, sticky="we", padx=(8, 4), pady=(0, 12))

        time_box = ttk.Combobox(
            form, textvariable=self.time_var, state="readonly",
            font=CB_FONT, style="Popup.TCombobox", values=time_options
        )
        time_box.set("Time")
        time_box.grid(row=0, column=2, sticky="we", padx=(4, 2), pady=(0, 12))

        # ---- Category ----
        tk.Label(
            form, text="Category:", font=("Poppins", 25, "bold"),
            bg="#FFFFFF", fg="#000000"
        ).grid(row=1, column=0, sticky="w", pady=(8, 10))

        self.cat_var = tk.StringVar()
        category_values = [
            "1 - Urgent & Important",
            "2 - Not Urgent but Important",
            "3 - Urgent but Not Important",
            "4 - Not Urgent & Not Important",
        ]
        cat_box = ttk.Combobox(
            form, textvariable=self.cat_var, state="readonly",
            font=CB_FONT, style="Popup.TCombobox", values=category_values
        )
        cat_box.set("Select Category")
        cat_box.grid(
            row=1, column=1, columnspan=2,
            sticky="we", padx=(8, 4), pady=(8, 12)
        )

        # ---- Tag ----
        tk.Label(
            form, text="Tag:", font=("Poppins", 25, "bold"),
            bg="#FFFFFF", fg="#000000"
        ).grid(row=2, column=0, sticky="w", pady=(8, 10))

        tags = queries.get_all_tags_with_ids(self.cursor)
        self.tag_map = {
            f"{tname} (#{tid})": tname for tname, tid in tags
        }
        tag_values = list(self.tag_map.keys())
        self.tag_var = tk.StringVar()

        tag_box = ttk.Combobox(
            form, textvariable=self.tag_var, state="readonly",
            font=CB_FONT, style="Popup.TCombobox", values=tag_values
        )
        tag_box.set("Select Tag")
        tag_box.grid(
            row=2, column=1, columnspan=2,
            sticky="we", padx=(8, 4), pady=(8, 12)
        )

    def _create_save_button(self):
        """Create the rounded blue Save button."""
        btn_holder = tk.Frame(self.popup, bg="#FFFFFF")
        btn_holder.pack(pady=16)

        pill_w, pill_h = 100, 30
        btn_canvas = tk.Canvas(
            btn_holder, width=pill_w, height=pill_h,
            bg="#FFFFFF", highlightthickness=0
        )
        btn_canvas.pack()

        pill_id = draw_rounded_rect(
            btn_canvas, 0, 0, pill_w, pill_h,
            radius=30, color="#1555DC", outline="#1555DC"
        )
        text_id = btn_canvas.create_text(
            50, pill_h // 2, text="Save",
            fill="white", font=("Poppins", 20, "bold")
        )

        for tag in (pill_id, text_id):
            btn_canvas.tag_bind(tag, "<Button-1>", lambda e: self._save_task())

        self.popup.bind("<Return>", lambda e: self._save_task())

    def _save_task(self):
        """Validate and save the new task to the database."""
        task_name = self.name_entry.get().strip()
        if not task_name or task_name == "Enter Task":
            messagebox.showerror("Error", "Please enter a task name.")
            return

        if self.cat_var.get() == "Select Category":
            messagebox.showerror("Error", "Please choose a category.")
            return

        try:
            category = int(self.cat_var.get().split(" - ")[0])
        except Exception:
            category = 1

        if self.tag_var.get() == "Select Tag":
            tag_name = ""
        else:
            tag_name = self.tag_map.get(self.tag_var.get(), "")

        sel_date = self.date_var.get()
        sel_time = self.time_var.get()
        if sel_date == "Date" or sel_time == "Time":
            messagebox.showerror("Error", "Please select both date and time.")
            return

        try:
            dl = datetime.strptime(
                f"{sel_date} {sel_time}:00", "%Y-%m-%d %H:%M:%S"
            )
        except ValueError:
            messagebox.showerror("Error", "Invalid date/time selected.")
            return

        queries.insert_task(
            self.cursor, self.connection,
            task_name, category, tag_name, dl
        )
        messagebox.showinfo("Success", f"Task '{task_name}' added.")
        self.popup.destroy()
        self.app.matrix.display_tasks(self.app.filters.get_active_filter())
