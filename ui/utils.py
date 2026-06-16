from datetime import datetime
from config import MONTH_FIX


def draw_rounded_rect(canvas, x1, y1, x2, y2, radius=25,
                      color="#1555DC", outline=None, width=2):
    """Draw a rounded rectangle on a Tkinter canvas."""
    points = [
        x1 + radius, y1, x2 - radius, y1,
        x2, y1, x2, y1 + radius,
        x2, y2 - radius, x2, y2,
        x2 - radius, y2, x1 + radius, y2,
        x1, y2, x1, y2 - radius,
        x1, y1 + radius, x1, y1
    ]
    return canvas.create_polygon(
        points, smooth=True, fill=color,
        outline=outline if outline else color, width=width
    )


def animate_checkbox(canvas, root, rect_id, start_color, end_color,
                     steps=10, delay=30):
    """Animate checkbox outline color transition."""
    def hex_lerp(a, b, t):
        return int(a + (b - a) * t)

    def lerp_color(c1, c2, t):
        c1 = canvas.winfo_rgb(c1)
        c2 = canvas.winfo_rgb(c2)
        return "#%02x%02x%02x" % (
            hex_lerp(c1[0] // 256, c2[0] // 256, t),
            hex_lerp(c1[1] // 256, c2[1] // 256, t),
            hex_lerp(c1[2] // 256, c2[2] // 256, t)
        )

    for i in range(steps + 1):
        color = lerp_color(start_color, end_color, i / steps)
        root.after(
            i * delay,
            lambda c=color: canvas.itemconfig(rect_id, outline=c)
        )


def animate_tick(canvas, root, tick_id, show=True, steps=10, delay=30):
    """Animate tick mark color fade in/out."""
    bg_rgb = (243, 244, 246)
    green_rgb = (0, 170, 0)
    start = bg_rgb if show else green_rgb
    end = green_rgb if show else bg_rgb

    def lerp(a, b, t):
        return int(a + (b - a) * t)

    for i in range(steps + 1):
        t = i / steps
        r = lerp(start[0], end[0], t)
        g = lerp(start[1], end[1], t)
        b = lerp(start[2], end[2], t)
        color = f"#{r:02x}{g:02x}{b:02x}"
        root.after(
            i * delay,
            lambda c=color: canvas.itemconfig(tick_id, fill=c)
        )


def format_deadline(d):
    """Format a date/datetime object as 'day Month' string."""
    if not d:
        return ""
    if isinstance(d, datetime):
        d = d.date()
    try:
        mon = d.strftime("%b")
    except Exception:
        months = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
        ]
        mon = months[d.month - 1]
    mon = MONTH_FIX.get(mon, mon)
    return f"{d.day} {mon}"
