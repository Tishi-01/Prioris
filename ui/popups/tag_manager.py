import tkinter as tk
from tkinter import messagebox

from ui.utils import draw_rounded_rect
from database import queries


class TagManagerPopup:
    """Popup window for viewing and managing tags."""

    def __init__(self, app):
        self.app = app
        self.cursor = app.cursor
        self.connection = app.connection

        self.popup = tk.Toplevel(app.root)
        self.popup.title("Manage Tags")
        self.popup.geometry("500x350")
        self.popup.configure(bg="#FFFFFF")
        self.popup.grab_set()

        self._build_ui()

    def _build_ui(self):
        """Build the tag manager UI."""
        # ---- Title ----
        tk.Label(
            self.popup,
            text="Your Tags",
            font=("Poppins", 28, "bold"),
            bg="#FFFFFF",
            fg="#1555DC"
        ).pack(pady=(22, 12))

        # ---- Header ----
        header = tk.Frame(
            self.popup, bg="#F3F4F6",
            highlightbackground="#E0E0E0", highlightthickness=1
        )
        header.pack(fill="x", padx=35, pady=(0, 8))
        header.grid_columnconfigure(0, weight=3, uniform="col")
        header.grid_columnconfigure(1, weight=2, uniform="col")
        header.grid_columnconfigure(2, weight=1, uniform="col")

        tk.Label(
            header, text="Tag Name", font=("Poppins", 16, "bold"),
            bg="#F3F4F6", fg="#000000", anchor="w", padx=12
        ).grid(row=0, column=0, sticky="we")
        tk.Label(
            header, text="Type", font=("Poppins", 16, "bold"),
            bg="#F3F4F6", fg="#000000", anchor="center"
        ).grid(row=0, column=1, sticky="we")
        tk.Label(
            header, text="Delete", font=("Poppins", 16, "bold"),
            bg="#F3F4F6", fg="#000000", anchor="center"
        ).grid(row=0, column=2, sticky="we")

        # ---- Table container ----
        self.table_frame = tk.Frame(self.popup, bg="#FFFFFF")
        self.table_frame.pack(fill="both", expand=True, padx=35, pady=(0, 70))
        self.table_frame.grid_columnconfigure(0, weight=3, uniform="col")
        self.table_frame.grid_columnconfigure(1, weight=2, uniform="col")
        self.table_frame.grid_columnconfigure(2, weight=1, uniform="col")

        self._load_tags()
        self._create_add_button()

    def _load_tags(self):
        """Load and display all tags in the table."""
        for w in self.table_frame.winfo_children():
            w.destroy()

        tags = queries.get_all_tags_full(self.cursor)

        if not tags:
            tk.Label(
                self.table_frame, text="No tags defined yet.",
                font=("Poppins", 14), bg="#FFFFFF", fg="#888888"
            ).pack(pady=20)
            return

        for i, (tid, name, wifi, loc) in enumerate(tags):
            tag_type = "WiFi" if wifi else "Weather"
            bg_color = "#FAFAFA" if i % 2 == 0 else "#FFFFFF"

            name_lbl = tk.Label(
                self.table_frame, text=name, font=("Poppins", 15, "bold"),
                bg=bg_color, fg="#000000", anchor="w", padx=12
            )
            type_lbl = tk.Label(
                self.table_frame, text=tag_type, font=("Poppins", 14),
                bg=bg_color, fg="#000000", anchor="center"
            )
            del_btn = tk.Label(
                self.table_frame, text="✖", fg="#E11D48",
                font=("Poppins", 18, "bold"), bg=bg_color,
                anchor="center", cursor="hand2"
            )

            name_lbl.grid(row=i, column=0, sticky="we", pady=2, ipady=6)
            type_lbl.grid(row=i, column=1, sticky="we", pady=2, ipady=6)
            del_btn.grid(row=i, column=2, sticky="we", pady=2, ipady=6)

            def delete_tag(tid=tid, name=name):
                if messagebox.askyesno("Confirm Delete", f"Delete tag '{name}'?"):
                    queries.delete_tag_by_id(self.cursor, self.connection, tid)
                    self._load_tags()

            del_btn.bind(
                "<Button-1>",
                lambda e, tid=tid, name=name: delete_tag(tid, name)
            )

    def _create_add_button(self):
        """Create the floating Add Tag button."""
        add_btn_canvas = tk.Canvas(
            self.popup, width=100, height=35,
            bg="#FFFFFF", highlightthickness=0
        )
        add_btn_canvas.place(relx=0.88, rely=0.9, anchor="center")

        pill_id = draw_rounded_rect(
            add_btn_canvas, 0, 0, 100, 35,
            radius=35, color="#1555DC", outline="#1555DC"
        )
        text_id = add_btn_canvas.create_text(
            50, 17, text="+ Add Tag",
            fill="white", font=("Poppins", 18, "bold")
        )

        def open_add_tag(_=None):
            self.popup.destroy()
            from ui.popups.edit_tag import EditTagPopup
            EditTagPopup(self.app)

        for tag in (pill_id, text_id):
            add_btn_canvas.tag_bind(tag, "<Button-1>", open_add_tag)
