from config import (
    BOX_WIDTH, BOX_HEIGHT, PADDING_X, PADDING_Y, GAP,
    CORNER_RADIUS, DEADLINE_RIGHT_PAD, ANIM_STEPS, ANIM_DELAY,
    PRIMARY_BLUE
)
from ui.utils import (
    draw_rounded_rect, animate_checkbox, animate_tick, format_deadline
)
from database import queries


class Matrix:
    """Eisenhower Matrix display with 4 quadrants and task rendering."""

    # Quadrant definitions: (x_offset, y_offset, label, color)
    QUADRANTS = [
        (PADDING_X, PADDING_Y,
         "➊ Urgent & Important", "#FC0001"),
        (PADDING_X + BOX_WIDTH + GAP, PADDING_Y,
         "➋ Not Urgent but Important", "#F37200"),
        (PADDING_X, PADDING_Y + BOX_HEIGHT + GAP,
         "➌ Urgent but Not Important", "#1964F4"),
        (PADDING_X + BOX_WIDTH + GAP, PADDING_Y + BOX_HEIGHT + GAP,
         "➍ Not Urgent & Not Important", "#2FBD54")
    ]

    def __init__(self, app):
        self.app = app
        self.canvas = app.canvas
        self.root = app.root
        self.cursor = app.cursor
        self.connection = app.connection

        # Task position origins for each category (1-4)
        self.positions = {
            1: (PADDING_X + 20, PADDING_Y + 80),
            2: (PADDING_X + BOX_WIDTH + GAP + 20, PADDING_Y + 80),
            3: (PADDING_X + 20, PADDING_Y + BOX_HEIGHT + GAP + 80),
            4: (PADDING_X + BOX_WIDTH + GAP + 20,
                PADDING_Y + BOX_HEIGHT + GAP + 80)
        }

        # Deadline X positions (right-aligned)
        self.deadline_x = {
            1: PADDING_X + BOX_WIDTH - DEADLINE_RIGHT_PAD,
            2: (PADDING_X + BOX_WIDTH + GAP) + BOX_WIDTH - DEADLINE_RIGHT_PAD,
            3: PADDING_X + BOX_WIDTH - DEADLINE_RIGHT_PAD,
            4: (PADDING_X + BOX_WIDTH + GAP) + BOX_WIDTH - DEADLINE_RIGHT_PAD,
        }

        # Canvas item ID tracking
        self.task_text_ids = {1: [], 2: [], 3: [], 4: []}
        self.deadline_text_ids = {1: [], 2: [], 3: [], 4: []}
        self.checkbox_ids = {}
        self.tick_ids = {}
        self.delete_icon_ids = {1: [], 2: [], 3: [], 4: []}

        self._draw_quadrants()

    def _draw_quadrants(self):
        """Draw the 4 Eisenhower matrix boxes with labels."""
        for (x, y, text, color) in self.QUADRANTS:
            draw_rounded_rect(
                self.canvas, x, y,
                x + BOX_WIDTH, y + BOX_HEIGHT,
                radius=CORNER_RADIUS, color="white",
                outline="#DEDEDE", width=2
            )
            self.canvas.create_text(
                x + 15, y + 30, text=text,
                font=("Poppins", 25, "bold"),
                fill=color, anchor="w"
            )

    def clear_matrix(self):
        """Remove all task-related canvas items."""
        for cat in self.task_text_ids:
            for tid in self.task_text_ids[cat]:
                self.canvas.delete(tid)
            self.task_text_ids[cat].clear()

        for cat in self.deadline_text_ids:
            for did in self.deadline_text_ids[cat]:
                self.canvas.delete(did)
            self.deadline_text_ids[cat].clear()

        for cat in self.checkbox_ids:
            for cid in self.checkbox_ids[cat]:
                self.canvas.delete(cid)
        self.checkbox_ids.clear()

        for cat in self.tick_ids:
            for kid in self.tick_ids[cat]:
                self.canvas.delete(kid)
        self.tick_ids.clear()

        for cat in self.delete_icon_ids:
            for did in self.delete_icon_ids[cat]:
                self.canvas.delete(did)
        self.delete_icon_ids.clear()

    def _toggle_status(self, task_name, current_status):
        """Toggle a task's completion status and refresh display."""
        queries.toggle_task_status(self.connection, task_name, current_status)
        current_filter = self.app.filters.get_active_filter()
        self.display_tasks(current_filter, smooth=True)

    def _delete_task(self, task_name):
        """Delete a task and refresh display."""
        queries.delete_task(self.connection, self.cursor, task_name)
        current_filter = self.app.filters.get_active_filter()
        self.display_tasks(current_filter, smooth=True)

    def _draw_category(self, cat, rows, filter_type, show_deadline=False):
        """Draw tasks for a single category quadrant."""
        x, y = self.positions[cat]
        self.checkbox_ids[cat] = []
        self.tick_ids[cat] = []
        self.deadline_text_ids[cat] = []
        self.delete_icon_ids[cat] = []

        for i, row in enumerate(rows):
            if len(row) == 3:
                task_name, status, dl = row
            else:
                task_name, status = row
                dl = None

            box_x, box_y = x, y + i * 28
            size = 14

            # Checkbox rectangle
            rect_id = self.canvas.create_rectangle(
                box_x, box_y - 6, box_x + size, box_y + size - 6,
                fill="#FFFFFF", outline=PRIMARY_BLUE, width=2
            )

            # Tick mark
            tick_fill = "#00AA00" if status == 1 else "#F3F4F6"
            tick_id = self.canvas.create_text(
                box_x + size / 2, box_y - 6 + size / 2,
                text="✓", font=("Poppins", 16, "bold"), fill=tick_fill
            )

            # Task name text
            tid = self.canvas.create_text(
                x + 25, y + i * 28,
                text=task_name,
                font=("Poppins", 20, "bold"),
                fill="gray" if status == 1 else "black",
                anchor="w"
            )

            # Deadline text
            if show_deadline and dl:
                dtext = format_deadline(dl)
                did = self.canvas.create_text(
                    self.deadline_x[cat], y + i * 28,
                    text=dtext, font=("Poppins", 16),
                    fill="#808080", anchor="e"
                )
                self.deadline_text_ids[cat].append(did)

            # Checkbox click handler with animation
            def make_cb(name=task_name, st=status, rid=rect_id, tkid=tick_id):
                def handler(event=None):
                    animate_checkbox(
                        self.canvas, self.root, rid,
                        PRIMARY_BLUE, PRIMARY_BLUE,
                        steps=ANIM_STEPS, delay=ANIM_DELAY
                    )
                    animate_tick(
                        self.canvas, self.root, tkid,
                        show=(st == 0),
                        steps=ANIM_STEPS // 2, delay=ANIM_DELAY
                    )
                    self.root.after(
                        ANIM_STEPS * ANIM_DELAY,
                        lambda: self._toggle_status(name, st)
                    )
                return handler

            cb = make_cb()
            self.canvas.tag_bind(rect_id, "<Button-1>", cb)
            self.canvas.tag_bind(tid, "<Button-1>", cb)
            self.canvas.tag_bind(tick_id, "<Button-1>", cb)

            # Delete icon for completed filter
            if filter_type.lower() == "completed":
                if cat in (1, 3):
                    col_left = PADDING_X
                else:
                    col_left = PADDING_X + BOX_WIDTH + GAP
                x_right = col_left + BOX_WIDTH - 25

                del_id = self.canvas.create_text(
                    x_right, y + i * 28,
                    text="✖", font=("Poppins", 20, "bold"),
                    fill="#E11D48", anchor="e"
                )
                self.canvas.tag_bind(
                    del_id, "<Button-1>",
                    lambda e, name=task_name: self._delete_task(name)
                )
                self.delete_icon_ids[cat].append(del_id)

            self.task_text_ids[cat].append(tid)
            self.checkbox_ids[cat].append(rect_id)
            self.tick_ids[cat].append(tick_id)

    def display_tasks(self, filter_type="All", smooth=False):
        """Fetch and display tasks based on the active filter."""
        self.clear_matrix()
        tag_list = queries.get_all_tag_names(self.cursor)

        if filter_type.lower() == "all":
            for c in range(1, 5):
                rows = queries.get_tasks_all(self.cursor, c)
                self._draw_category(c, rows, filter_type, show_deadline=True)

        elif filter_type.lower() == "today":
            for c in range(1, 5):
                rows = queries.get_tasks_today(self.cursor, c)
                self._draw_category(c, rows, filter_type, show_deadline=True)

        elif filter_type.lower() == "completed":
            for c in range(1, 5):
                rows = queries.get_tasks_completed(self.cursor, c)
                self._draw_category(c, rows, filter_type, show_deadline=False)

        elif filter_type in tag_list:
            for c in range(1, 5):
                rows = queries.get_tasks_by_tag(self.cursor, c, filter_type)
                self._draw_category(c, rows, filter_type, show_deadline=False)
