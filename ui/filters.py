from config import PRIMARY_BLUE
from ui.utils import draw_rounded_rect


class Filters:
    """Filter buttons (All, Today, Completed) for the Eisenhower matrix."""

    def __init__(self, app):
        self.app = app
        self.canvas = app.canvas
        self.active_button = 0

        self.filter_buttons = [
            {"text": "All", "x1": 425, "y1": 40, "x2": 520, "y2": 80},
            {"text": "Today", "x1": 530, "y1": 40, "x2": 630, "y2": 80},
            {"text": "Completed", "x1": 1140, "y1": 40, "x2": 1280, "y2": 80}
        ]

        self._draw_buttons()
        self._bind_events()

    def _draw_buttons(self):
        """Draw all filter buttons with initial state."""
        for i, btn in enumerate(self.filter_buttons):
            color = PRIMARY_BLUE if i == self.active_button else "#FFFFFF"
            text_color = "white" if i == self.active_button else "black"

            btn["shape_id"] = draw_rounded_rect(
                self.canvas,
                btn["x1"], btn["y1"], btn["x2"], btn["y2"],
                radius=35, color=color, outline="#DEDEDE"
            )
            btn["text_id"] = self.canvas.create_text(
                (btn["x1"] + btn["x2"]) / 2,
                (btn["y1"] + btn["y2"]) / 2,
                text=btn["text"],
                font=("Poppins", 20, "bold"),
                fill=text_color
            )

    def _bind_events(self):
        """Bind click events to filter buttons."""
        for i, btn in enumerate(self.filter_buttons):
            for tag in (btn["shape_id"], btn["text_id"]):
                self.canvas.tag_bind(
                    tag, "<Button-1>",
                    lambda e, idx=i: self.set_active(idx)
                )

    def set_active(self, index):
        """Set the active filter button and refresh matrix display."""
        self.active_button = index

        for i, btn in enumerate(self.filter_buttons):
            if i == index:
                self.canvas.itemconfig(
                    btn["shape_id"], fill=PRIMARY_BLUE, outline=PRIMARY_BLUE
                )
                self.canvas.itemconfig(btn["text_id"], fill="white")
            else:
                self.canvas.itemconfig(
                    btn["shape_id"], fill="#FFFFFF", outline="#DEDEDE"
                )
                self.canvas.itemconfig(btn["text_id"], fill="black")

        filter_type = self.filter_buttons[index]["text"]
        self.app.matrix.display_tasks(filter_type)
        print(f"Filter → {filter_type}")

    def get_active_filter(self):
        """Return the currently active filter text."""
        return self.filter_buttons[self.active_button]["text"]
