import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# --- Window setup ---
root = tk.Tk()
root.title("Prioris - Task Manager")
root.geometry("1300x900")
root.config(bg="#DEDEDE")

canvas = tk.Canvas(root, bg="#F3F4F6", highlightthickness=0)
canvas.pack(fill="both", expand=True)

# --- Logo ---
img = Image.open("/Users/tanishk/Downloads/prioris_logo.png")
img = img.resize((250, 110))
photo = ImageTk.PhotoImage(img)
canvas.create_image(25, 5, image=photo, anchor="nw")
canvas.image = photo

# --- Rounded rectangle function ---
def draw_rounded_rect(canvas, x1, y1, x2, y2, radius=25, color="#1555DC", outline=None, width=2):
    points = [
        x1+radius, y1,
        x2-radius, y1,
        x2, y1,
        x2, y1+radius,
        x2, y2-radius,
        x2, y2,
        x2-radius, y2,
        x1+radius, y2,
        x1, y2,
        x1, y2-radius,
        x1, y1+radius,
        x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, fill=color,
                                 outline=outline if outline else color, width=width)

# --- Blue Sidebar ---
draw_rounded_rect(canvas, 25, 125, 400, 550, radius=40, color="#1555DC")
canvas.create_text(160, 160, text="Suggested Tasks",
                   font=("Poppins", 28, "bold"), fill="white")


# ==================== 🔵 FILTER BUTTONS ABOVE MATRIX ====================
filter_buttons = [
    {"text": "All", "x1": 425, "y1": 40, "x2": 520, "y2": 80},
    {"text": "Today", "x1": 530, "y1": 40, "x2": 630, "y2": 80},
    {"text": "Completed", "x1": 1140, "y1": 40, "x2": 1280, "y2": 80}
]

active_button = 0  # default = "All"

# Draw initial buttons and store shape IDs
for i, btn in enumerate(filter_buttons):
    color = "#1555DC" if i == active_button else "#FFFFFF"
    text_color = "white" if i == active_button else "black"
    btn["shape_id"] = draw_rounded_rect(
        canvas, btn["x1"], btn["y1"], btn["x2"], btn["y2"],
        radius=35, color=color, outline="#DEDEDE"
    )
    btn["text_id"] = canvas.create_text(
        (btn["x1"] + btn["x2"]) / 2,
        (btn["y1"] + btn["y2"]) / 2,
        text=btn["text"],
        font=("Poppins", 20, "bold"),
        fill=text_color
    )

def set_active(index):
    global active_button
    for i, btn in enumerate(filter_buttons):
        # Change color instead of redrawing
        if i == index:
            canvas.itemconfig(btn["shape_id"], fill="#1555DC", outline="#1555DC")
            canvas.itemconfig(btn["text_id"], fill="white")
        else:
            canvas.itemconfig(btn["shape_id"], fill="#FFFFFF", outline="#DEDEDE")
            canvas.itemconfig(btn["text_id"], fill="black")
    active_button = index
    print(f"{filter_buttons[index]['text']} selected")

# Bind click events to both shape and text
for i, btn in enumerate(filter_buttons):
    for tag in (btn["shape_id"], btn["text_id"]):
        canvas.tag_bind(tag, "<Button-1>", lambda e, idx=i: set_active(idx))
# =======================================================================



# --- Matrix Boxes ---
box_width, box_height = 420, 350
padding_x, padding_y, gap, corner_radius = 425, 100, 15, 30

boxes = [
    (padding_x, padding_y, "➊ Urgent & Important", "#FC0001"),
    (padding_x + box_width + gap, padding_y, "➋ Not Urgent but Important", "#F37200"),
    (padding_x, padding_y + box_height + gap, "➌ Urgent but Not Important", "#1964F4"),
    (padding_x + box_width + gap, padding_y + box_height + gap, "➍ Not Urgent & Not Important", "#2FBD54")
]

for (x, y, text, color) in boxes:
    draw_rounded_rect(canvas, x, y, x + box_width, y + box_height,
                      radius=corner_radius, color="white", outline="#DEDEDE", width=2)
    canvas.create_text(x + 15, y + 30, text=text, font=("Poppins", 25, "bold"),
                       fill=color, justify="left", anchor="w")

# --- Edit Tags Button (just above Add Task) ---
draw_rounded_rect(canvas, 25, 670, 195, 730, radius=50, color="#FFFFFF",outline="#DEDEDE")
text_edit_icon = canvas.create_text(60, 697, text="✎", fill="black", font=("Poppins", 27, "bold"))
text_edit_label = canvas.create_text(130, 700, text="Edit Tags", fill="black", font=("Poppins", 22, "bold"))

def on_edit_click(event):
    print("Edit Tags clicked!")

for tag in (text_edit_icon, text_edit_label):
    canvas.tag_bind(tag, "<Button-1>", on_edit_click)

# --- Add Task Button (bottom-left) ---
draw_rounded_rect(canvas, 25, 750, 225, 810, radius=50, color="#1555DC")
text_add = canvas.create_text(60, 777, text="+", fill="white", font=("Poppins", 36, "bold"))
text_label = canvas.create_text(140, 780, text="Add Task", fill="white", font=("Poppins", 26, "bold"))

def on_click(event):
    print("Add Task clicked!")

for tag in (text_add, text_label):
    canvas.tag_bind(tag, "<Button-1>", on_click)






root.mainloop()
