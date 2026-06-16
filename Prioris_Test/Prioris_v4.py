import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import mysql.connector
from datetime import date, datetime, timedelta
import socket, threading, webbrowser, time, requests
from flask import Flask, request, jsonify, render_template_string

API_KEY = "AIzaSyAajd58n7_B6YY94QWEBGsjB4RbASIFdE8"

# -------------------- MySQL Connection --------------------
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="new_password",
    database="prioris"
)
cursor = connection.cursor(buffered=True)
print("✅ Connected to MySQL!")

# -------------------- Tkinter Window --------------------
root = tk.Tk()
root.title("Prioris - Task Manager")
root.geometry("1300x900")
root.config(bg="#DEDEDE")

canvas = tk.Canvas(root, bg="#F3F4F6", highlightthickness=0)
canvas.pack(fill="both", expand=True)

# -------------------- Logo --------------------
img = Image.open("/Users/tanishk/Downloads/prioris_logo.png")
img = img.resize((250, 110))
photo = ImageTk.PhotoImage(img)
canvas.create_image(25, 5, image=photo, anchor="nw")
canvas.image = photo

# -------------------- Rounded Rectangle Function --------------------
def draw_rounded_rect(canvas, x1, y1, x2, y2, radius=25, color="#1555DC", outline=None, width=2):
    points = [
        x1+radius, y1, x2-radius, y1,
        x2, y1, x2, y1+radius,
        x2, y2-radius, x2, y2,
        x2-radius, y2, x1+radius, y2,
        x1, y2, x1, y2-radius,
        x1, y1+radius, x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, fill=color,
                                 outline=outline if outline else color, width=width)



# -------------------- Helper: WiFi + City Picker --------------------
def get_local_ip():
    """Return current connected local IP, or None if not connected."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None


def pick_city(API_KEY, port=5051):
    app = Flask(__name__)
    result = {"city": None}

    HTML = """
    <!doctype html>
    <html><head>
      <meta charset="utf-8">
      <title>Pick Location</title>
      <style>html,body,#map{height:100%;margin:0;padding:0}</style>
    </head>
    <body><div id="map"></div>
    <script>
      let map, marker;
      function initMap() {
        map = new google.maps.Map(document.getElementById('map'), {
          center:{lat:28.6,lng:77.2},zoom:6
        });
        map.addListener('click', e=>{
          if(marker)marker.setMap(null);
          marker=new google.maps.Marker({position:e.latLng,map});
          const lat=e.latLng.lat(),lng=e.latLng.lng();
          fetch(`https://maps.googleapis.com/maps/api/geocode/json?latlng=${lat},${lng}&key={{k}}`)
          .then(r=>r.json()).then(j=>{
            let c=null;
            for(const r1 of (j.results||[]))
              for(const a of (r1.address_components||[]))
                if(a.types.includes("locality")){c=a.long_name;break;}
            fetch('/set',{method:'POST',headers:{'Content-Type':'application/json'},
              body:JSON.stringify({city:c})});
          });
        });
      }
    </script>
    <script src="https://maps.googleapis.com/maps/api/js?key={{k}}&callback=initMap" async defer></script>
    </body></html>
    """

    @app.route("/")
    def index(): return render_template_string(HTML, k=API_KEY)

    @app.route("/set", methods=["POST"])
    def set_city():
        data = request.get_json()
        result["city"] = data.get("city")
        try: requests.get(f"http://127.0.0.1:{port}/shutdown", timeout=1)
        except: pass
        return jsonify(ok=True)

    @app.route("/shutdown")
    def shutdown():
        func = request.environ.get("werkzeug.server.shutdown")
        if func: func()
        return "ok"

    def run(): app.run(port=port, debug=False, use_reloader=False)
    threading.Thread(target=run, daemon=True).start()
    webbrowser.open(f"http://127.0.0.1:{port}/")

    while result["city"] is None:
        time.sleep(0.2)
    return result["city"]



# -------------------- Blue Sidebar --------------------
draw_rounded_rect(canvas, 25, 125, 400, 550, radius=40, color="#1555DC")
canvas.create_text(160, 160, text="Suggested Tasks",
                   font=("Poppins", 28, "bold"), fill="white")

# -------------------- Filter Buttons --------------------
filter_buttons = [
    {"text": "All", "x1": 425, "y1": 40, "x2": 520, "y2": 80},
    {"text": "Today", "x1": 530, "y1": 40, "x2": 630, "y2": 80},
    {"text": "Completed", "x1": 1140, "y1": 40, "x2": 1280, "y2": 80}
]
active_button = 0

for i, btn in enumerate(filter_buttons):
    color = "#1555DC" if i == active_button else "#FFFFFF"
    text_color = "white" if i == active_button else "black"
    btn["shape_id"] = draw_rounded_rect(canvas, btn["x1"], btn["y1"], btn["x2"], btn["y2"],
                                        radius=35, color=color, outline="#DEDEDE")
    btn["text_id"] = canvas.create_text(
        (btn["x1"] + btn["x2"]) / 2,
        (btn["y1"] + btn["y2"]) / 2,
        text=btn["text"],
        font=("Poppins", 20, "bold"),
        fill=text_color
    )

# -------------------- Eisenhower Boxes --------------------
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
    canvas.create_text(x + 15, y + 30, text=text,
                       font=("Poppins", 25, "bold"),
                       fill=color, anchor="w")

# -------------------- Coordinates --------------------
positions = {
    1: (padding_x + 20, padding_y + 80),
    2: (padding_x + box_width + gap + 20, padding_y + 80),
    3: (padding_x + 20, padding_y + box_height + gap + 80),
    4: (padding_x + box_width + gap + 20, padding_y + box_height + gap + 80)
}
task_text_ids = {1: [], 2: [], 3: [], 4: []}
deadline_text_ids = {1: [], 2: [], 3: [], 4: []}
checkbox_ids = {}
tick_ids = {}
delete_icon_ids = {1: [], 2: [], 3: [], 4: []}

# --- Fixed right-edge x for deadlines ---
DEADLINE_RIGHT_PAD = 16
deadline_x = {
    1: padding_x + box_width - DEADLINE_RIGHT_PAD,
    2: (padding_x + box_width + gap) + box_width - DEADLINE_RIGHT_PAD,
    3: padding_x + box_width - DEADLINE_RIGHT_PAD,
    4: (padding_x + box_width + gap) + box_width - DEADLINE_RIGHT_PAD,
}

def clear_matrix():
    for cat in task_text_ids:
        for tid in task_text_ids[cat]:
            canvas.delete(tid)
        task_text_ids[cat].clear()
    for cat in deadline_text_ids:
        for did in deadline_text_ids[cat]:
            canvas.delete(did)
        deadline_text_ids[cat].clear()
    for cat in checkbox_ids:
        for cid in checkbox_ids[cat]:
            canvas.delete(cid)
    checkbox_ids.clear()
    for cat in tick_ids:
        for kid in tick_ids[cat]:
            canvas.delete(kid)
    tick_ids.clear()
    for cat in delete_icon_ids:
        for did in delete_icon_ids[cat]:
            canvas.delete(did)
    delete_icon_ids.clear()

# -------------------- Animations --------------------
def animate_checkbox(rect_id, start_color, end_color, steps=10, delay=30):
    def hex_lerp(a, b, t): return int(a + (b - a) * t)
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
        root.after(i * delay, lambda c=color: canvas.itemconfig(rect_id, outline=c))

def animate_tick(tick_id, show=True, steps=10, delay=30):
    bg_rgb = (243, 244, 246)
    green_rgb = (0, 170, 0)
    start = bg_rgb if show else green_rgb
    end = green_rgb if show else bg_rgb
    def lerp(a, b, t): return int(a + (b - a) * t)
    for i in range(steps + 1):
        t = i / steps
        r, g, b = lerp(start[0], end[0], t), lerp(start[1], end[1], t), lerp(start[2], end[2], t)
        color = f"#{r:02x}{g:02x}{b:02x}"
        root.after(i * delay, lambda c=color: canvas.itemconfig(tick_id, fill=c))

# -------------------- DB Helpers --------------------
def toggle_status(task_name, current_status):
    new_status = 0 if current_status == 1 else 1
    with connection.cursor(buffered=True) as cur:
        cur.execute("UPDATE taskinfo SET taskStatus=%s WHERE taskName=%s", (new_status, task_name))
    connection.commit()
    print(f"✅ {task_name} → {new_status}")
    current_filter = filter_buttons[active_button]["text"]
    displayTask(current_filter, smooth=True)

def delete_task(task_name):
    with connection.cursor(buffered=True) as cur:
        cur.execute("DELETE FROM taskinfo WHERE taskName=%s", (task_name,))
    connection.commit()
    print(f"🗑️ Deleted task → {task_name}")
    current_filter = filter_buttons[active_button]["text"]
    displayTask(current_filter, smooth=True)

ANIM_STEPS = 30
ANIM_DELAY = 20

MONTH_FIX = {"Sep": "Sept"}
def format_deadline(d):
    if not d:
        return ""
    if isinstance(d, datetime):
        d = d.date()
    try:
        mon = d.strftime("%b")
    except Exception:
        mon = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][d.month-1]
    mon = MONTH_FIX.get(mon, mon)
    return f"{d.day} {mon}"



# -------------------- Edit Tag Popup --------------------


# -------------------- Tag Manager Window --------------------
def open_tag_manager_popup():
    popup = tk.Toplevel(root)
    popup.title("Manage Tags")
    popup.geometry("500x350")
    popup.configure(bg="#FFFFFF")
    popup.grab_set()

    # ---- Title ----
    tk.Label(
        popup,
        text="Your Tags",
        font=("Poppins", 28, "bold"),
        bg="#FFFFFF",
        fg="#1555DC"
    ).pack(pady=(22, 12))

    # ---- Header ----
    header = tk.Frame(popup, bg="#F3F4F6", highlightbackground="#E0E0E0", highlightthickness=1)
    header.pack(fill="x", padx=35, pady=(0, 8))
    header.grid_columnconfigure(0, weight=3, uniform="col")
    header.grid_columnconfigure(1, weight=2, uniform="col")
    header.grid_columnconfigure(2, weight=1, uniform="col")

    tk.Label(header, text="Tag Name", font=("Poppins", 16, "bold"),
             bg="#F3F4F6", fg="#000000", anchor="w", padx=12).grid(row=0, column=0, sticky="we")
    tk.Label(header, text="Type", font=("Poppins", 16, "bold"),
             bg="#F3F4F6", fg="#000000", anchor="center").grid(row=0, column=1, sticky="we")
    tk.Label(header, text="Delete", font=("Poppins", 16, "bold"),
             bg="#F3F4F6", fg="#000000", anchor="center").grid(row=0, column=2, sticky="we")

    # ---- Table container ----
    table_frame = tk.Frame(popup, bg="#FFFFFF")
    table_frame.pack(fill="both", expand=True, padx=35, pady=(0, 70))
    table_frame.grid_columnconfigure(0, weight=3, uniform="col")
    table_frame.grid_columnconfigure(1, weight=2, uniform="col")
    table_frame.grid_columnconfigure(2, weight=1, uniform="col")

    # ---- Load tags ----
    def load_tags():
        for w in table_frame.winfo_children():
            w.destroy()

        cursor.execute("SELECT tagID, tagName, wifi, location FROM TAGS")
        tags = cursor.fetchall()

        if not tags:
            tk.Label(table_frame, text="No tags defined yet.",
                     font=("Poppins", 14), bg="#FFFFFF", fg="#888888").pack(pady=20)
            return

        for i, (tid, name, wifi, loc) in enumerate(tags):
            tag_type = "WiFi" if wifi else "Weather"
            bg_color = "#FAFAFA" if i % 2 == 0 else "#FFFFFF"

            name_lbl = tk.Label(table_frame, text=name, font=("Poppins", 15,"bold"),
                                bg=bg_color, fg="#000000", anchor="w", padx=12)
            type_lbl = tk.Label(table_frame, text=tag_type, font=("Poppins", 14),
                                bg=bg_color, fg="#000000", anchor="center")
            del_btn = tk.Label(table_frame, text="✖", fg="#E11D48",
                               font=("Poppins", 18, "bold"), bg=bg_color,
                               anchor="center", cursor="hand2")

            name_lbl.grid(row=i, column=0, sticky="we", pady=2, ipady=6)
            type_lbl.grid(row=i, column=1, sticky="we", pady=2, ipady=6)
            del_btn.grid(row=i, column=2, sticky="we", pady=2, ipady=6)

            def delete_tag(tid=tid, name=name):
                if messagebox.askyesno("Confirm Delete", f"Delete tag '{name}'?"):
                    cursor.execute("DELETE FROM TAGS WHERE tagID=%s", (tid,))
                    connection.commit()
                    load_tags()

            del_btn.bind("<Button-1>", lambda e, tid=tid, name=name: delete_tag(tid, name))

    load_tags()

    # ---- Floating Add Tag button ----
    add_btn_canvas = tk.Canvas(popup, width=100, height=35, bg="#FFFFFF", highlightthickness=0)
    add_btn_canvas.place(relx=0.88, rely=0.9, anchor="center")

    pill_id = draw_rounded_rect(add_btn_canvas, 0, 0, 100, 35,
                                radius=35, color="#1555DC", outline="#1555DC")
    text_id = add_btn_canvas.create_text(50, 17, text="+ Add Tag",
                                         fill="white", font=("Poppins", 18, "bold"))

    def open_add_tag(_=None):
        popup.destroy()
        open_edit_tag_popup()

    for tag in (pill_id, text_id):
        add_btn_canvas.tag_bind(tag, "<Button-1>", open_add_tag)




def open_edit_tag_popup():
    popup = tk.Toplevel(root)
    popup.title("Add / Edit Tag")
    popup.geometry("500x400")
    popup.configure(bg="#DEDEDE")
    popup.grab_set()

    tk.Label(popup, text="Enter Tag Name:", font=("Poppins", 22, "bold"),
             bg="#DEDEDE",fg="#1555DC").pack(pady=(30, 8))
    tag_entry = tk.Entry(popup, font=("Poppins", 18), width=25,bg="#5A565F")
    tag_entry.pack(pady=(0, 20), ipady=6)

    tk.Label(popup, text="Tag Type:", font=("Poppins", 22, "bold"),
             bg="#DEDEDE",fg="#1555DC").pack(pady=(10, 8))
    tag_type = ttk.Combobox(popup, values=["WiFi", "Weather"],
                            state="readonly", font=("Poppins", 16))
    tag_type.pack(pady=(0, 25))
    tag_type.set("Select Type")

    def save_tag():
        tag = tag_entry.get().strip()
        tp = tag_type.get()

        if not tag or tp == "Select Type":
            messagebox.showerror("Error", "Please enter name and type.")
            return

        if tp == "WiFi":
            wifi = get_local_ip()
            if not wifi:
                messagebox.showerror("Error", "WiFi not detected!")
                return
            val = (tag, wifi)
            sql = "INSERT INTO TAGS (tagname, wifi) VALUES (%s, %s)"
            cursor.execute(sql, val)
            connection.commit()
            messagebox.showinfo("Success", f"Tag '{tag}' added (WiFi linked).")
            popup.destroy()

        elif tp == "Weather":
            messagebox.showinfo("Info", "Select your city on the map.")
            city = pick_city(API_KEY, port=5051)
            val = (tag, city)
            sql = "INSERT INTO TAGS (tagname, location) VALUES (%s, %s)"
            cursor.execute(sql, val)
            connection.commit()
            messagebox.showinfo("Success", f"Tag '{tag}' added for city: {city}")
            popup.destroy()

    # ---- Rounded blue Save button (matches your Add Task pill) ----
    btn_holder = tk.Frame(popup, bg="#DEDEDE")
    btn_holder.pack(pady=16)
    pill_w, pill_h = 150, 50
    btn_canvas = tk.Canvas(btn_holder, width=pill_w, height=pill_h,
                           bg="#DEDEDE", highlightthickness=0)
    btn_canvas.pack()
    pill_id = draw_rounded_rect(btn_canvas, 0, 0, pill_w, pill_h,
                                radius=40, color="#1555DC", outline="#1555DC")
    text_id = btn_canvas.create_text(pill_w/2, pill_h/2,
                                     text="Save", fill="white",
                                     font=("Poppins", 20, "bold"))
    for tag in (pill_id, text_id):
        btn_canvas.tag_bind(tag, "<Button-1>", lambda e: save_tag())
    popup.bind("<Return>", lambda e: save_tag())




# -------------------- Add Task Popup --------------------

def open_add_task_popup():
    popup = tk.Toplevel(root)
    popup.title("Add Task")
    popup.geometry("600x400")
    popup.configure(bg="#FFFFFF")
    popup.grab_set()  # modal

    # --- Task Name ---
    name_entry = tk.Entry(
        popup,
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
    name_entry.insert(0, "Enter Task")
    name_entry.pack(padx=24, pady=(30, 12), ipady=6, ipadx=6)

    def on_entry_click(event):
        if name_entry.get() == "Enter Task":
            name_entry.delete(0, "end")
            name_entry.config(fg="black")

    def on_focusout(event):
        if name_entry.get().strip() == "":
            name_entry.insert(0, "Enter Task")
            name_entry.config(fg="gray")

    name_entry.bind("<FocusIn>", on_entry_click)
    name_entry.bind("<FocusOut>", on_focusout)

    # ---------- Form grid ----------
    form = tk.Frame(popup, bg="#FFFFFF")
    form.pack(fill="x", padx=24, pady=(4, 6))
    form.grid_columnconfigure(0, weight=0)
    form.grid_columnconfigure(1, weight=1, uniform="in")
    form.grid_columnconfigure(2, weight=1, uniform="in")

    # ---- White combobox style ----
    style = ttk.Style(popup)
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
    popup.option_add("*TCombobox*Listbox.background", "#FFFFFF")
    popup.option_add("*TCombobox*Listbox.foreground", "#000000")
    popup.option_add("*TCombobox*Listbox.selectBackground", "#E5E7EB")
    popup.option_add("*TCombobox*Listbox.selectForeground", "#000000")

    CB_FONT = ("Poppins", 12)

    # ---- Deadline ----
    tk.Label(form, text="Deadline:", font=("Poppins", 25, "bold"),
             bg="#FFFFFF", fg="#000000").grid(row=0, column=0, sticky="w", pady=(0, 8))

    today_date = datetime.today().date()
    date_options = ["Date"] + [(today_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(365)]
    time_options = ["Time"] + [f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 30)]

    date_var = tk.StringVar()
    time_var = tk.StringVar()

    date_box = ttk.Combobox(form, textvariable=date_var, state="readonly",
                            font=CB_FONT, style="Popup.TCombobox", values=date_options)
    date_box.set("Date")  # ✅ explicitly set default
    date_box.grid(row=0, column=1, sticky="we", padx=(8, 4), pady=(0, 12))

    time_box = ttk.Combobox(form, textvariable=time_var, state="readonly",
                            font=CB_FONT, style="Popup.TCombobox", values=time_options)
    time_box.set("Time")  # ✅ explicitly set default
    time_box.grid(row=0, column=2, sticky="we", padx=(4, 2), pady=(0, 12))

    # ---- Category ----
    tk.Label(form, text="Category:", font=("Poppins", 25, "bold"),
             bg="#FFFFFF", fg="#000000").grid(row=1, column=0, sticky="w", pady=(8, 10))

    cat_var = tk.StringVar()
    category_values = [
        "1 - Urgent & Important",
        "2 - Not Urgent but Important",
        "3 - Urgent but Not Important",
        "4 - Not Urgent & Not Important",
    ]
    cat_box = ttk.Combobox(form, textvariable=cat_var, state="readonly",
                           font=CB_FONT, style="Popup.TCombobox", values=category_values)
    cat_box.set("Select Category")  # ✅ placeholder
    cat_box.grid(row=1, column=1, columnspan=2, sticky="we", padx=(8, 4), pady=(8, 12))

    # ---- Tag ----
    tk.Label(form, text="Tag:", font=("Poppins", 25, "bold"),
             bg="#FFFFFF", fg="#000000").grid(row=2, column=0, sticky="w", pady=(8, 10))

    cursor.execute("SELECT tagName, tagID FROM Tags")
    tags = cursor.fetchall()
    tag_map = {f"{tname} (#{tid})": tname for tname, tid in tags}
    tag_values = list(tag_map.keys())
    tag_var = tk.StringVar()

    tag_box = ttk.Combobox(form, textvariable=tag_var, state="readonly",
                           font=CB_FONT, style="Popup.TCombobox", values=tag_values)
    tag_box.set("Select Tag")  # ✅ placeholder
    tag_box.grid(row=2, column=1, columnspan=2, sticky="we", padx=(8, 4), pady=(8, 12))

    # ---- Save ----
    def save_task():
        task_name = name_entry.get().strip()
        if not task_name or task_name == "Enter Task":
            messagebox.showerror("Error", "Please enter a task name.")
            return

        if cat_var.get() == "Select Category":
            messagebox.showerror("Error", "Please choose a category.")
            return

        try:
            category = int(cat_var.get().split(" - ")[0])
        except Exception:
            category = 1

        if tag_var.get() == "Select Tag":
            tag_name = ""
        else:
            tag_name = tag_map.get(tag_var.get(), "")

        sel_date, sel_time = date_var.get(), time_var.get()
        if sel_date == "Date" or sel_time == "Time":
            messagebox.showerror("Error", "Please select both date and time.")
            return

        try:
            dl = datetime.strptime(f"{sel_date} {sel_time}:00", "%Y-%m-%d %H:%M:%S")
        except ValueError:
            messagebox.showerror("Error", "Invalid date/time selected.")
            return

        sql = "INSERT INTO TaskInfo (taskName, Category, Tag, taskStatus, deadline) VALUES (%s,%s,%s,%s,%s)"
        cursor.execute(sql, (task_name, category, tag_name, 0, dl))
        connection.commit()
        messagebox.showinfo("Success", f"Task '{task_name}' added.")
        popup.destroy()
        displayTask(filter_buttons[active_button]["text"])

        # ----- Add Task pill button (same look as main "Add Task") -----
    # remove the old tk.Button(...) and use a canvas pill:
    btn_holder = tk.Frame(popup, bg="#FFFFFF")
    btn_holder.pack(pady=16)

    pill_w, pill_h = 100, 30
    btn_canvas = tk.Canvas(btn_holder, width=pill_w, height=pill_h,
                           bg="#FFFFFF", highlightthickness=0)
    btn_canvas.pack()

    # draw rounded blue pill
    pill_id = draw_rounded_rect(btn_canvas, 0, 0, pill_w, pill_h,
                                radius=30, color="#1555DC", outline="#1555DC")

    # plus icon and text, matching main button
    text_id = btn_canvas.create_text(50, pill_h//2, text="Save",
                                     fill="white", font=("Poppins", 20, "bold"))

    def on_click(_event=None):
        save_task()

    # click bindings on pill + text
    for tag in (pill_id,  text_id):
        btn_canvas.tag_bind(tag, "<Button-1>", on_click)

    # allow pressing Enter to submit
    popup.bind("<Return>", on_click)

# -------------------- Display Tasks --------------------
def displayTask(filter_type="All", smooth=False):
    clear_matrix()
    cursor.execute("SELECT tagName FROM tags")
    tag_list = [r[0] for r in cursor.fetchall()]
    today = date.today()

    def draw(cat, sql, params=(), show_deadline=False):
        cursor.execute(sql, params)
        result = cursor.fetchall()
        x, y = positions[cat]
        checkbox_ids[cat] = []
        tick_ids[cat] = []
        deadline_text_ids[cat] = []
        delete_icon_ids[cat] = []
        for i, row in enumerate(result):
            if len(row) == 3:
                task_name, status, dl = row
            else:
                task_name, status = row
                dl = None

            box_x, box_y = x, y + i * 28
            size = 14

            rect_id = canvas.create_rectangle(
                box_x, box_y - 6, box_x + size, box_y + size - 6,
                fill="#FFFFFF", outline="#1555DC", width=2
            )
            tick_fill = "#00AA00" if status == 1 else "#F3F4F6"
            tick_id = canvas.create_text(
                box_x + size / 2, box_y - 6 + size / 2,
                text="✓", font=("Poppins", 16, "bold"), fill=tick_fill
            )
            tid = canvas.create_text(
                x + 25, y + i * 28,
                text=task_name,
                font=("Poppins", 20, "bold"),
                fill="gray" if status == 1 else "black",
                anchor="w"
            )

            if show_deadline and dl:
                dtext = format_deadline(dl)
                did = canvas.create_text(
                    deadline_x[cat], y + i * 28,
                    text=dtext, font=("Poppins", 16),
                    fill="#808080", anchor="e"
                )
                deadline_text_ids[cat].append(did)

            def make_cb(name=task_name, st=status, rid=rect_id, tkid=tick_id):
                def handler(event=None):
                    animate_checkbox(rid, "#1555DC", "#1555DC", steps=ANIM_STEPS, delay=ANIM_DELAY)
                    animate_tick(tkid, show=(st == 0), steps=ANIM_STEPS // 2, delay=ANIM_DELAY)
                    root.after(ANIM_STEPS * ANIM_DELAY, lambda: toggle_status(name, st))
                return handler

            cb = make_cb()
            canvas.tag_bind(rect_id, "<Button-1>", cb)
            canvas.tag_bind(tid, "<Button-1>", cb)
            canvas.tag_bind(tick_id, "<Button-1>", cb)

            # Add delete icon if in completed view
            if filter_type.lower() == "completed":
                if cat in (1, 3):
                    col_left = padding_x
                else:
                    col_left = padding_x + box_width + gap
                x_right = col_left + box_width - 25
                del_id = canvas.create_text(
                    x_right, y + i * 28,
                    text="✖", font=("Poppins", 20, "bold"),
                    fill="#E11D48", anchor="e"
                )
                canvas.tag_bind(del_id, "<Button-1>", lambda e, name=task_name: delete_task(name))
                delete_icon_ids[cat].append(del_id)

            task_text_ids[cat].append(tid)
            checkbox_ids[cat].append(rect_id)
            tick_ids[cat].append(tick_id)

    if filter_type.lower() == "all":
        for c in range(1, 5):
            draw(c, f"SELECT taskName, taskStatus, deadline FROM taskinfo WHERE category={c} AND taskStatus=0 ORDER BY deadline ASC", (), True)
    elif filter_type.lower() == "today":
        for c in range(1, 5):
            draw(c, f"SELECT taskName, taskStatus, deadline FROM taskinfo WHERE category={c} AND taskStatus=0 AND DATE(deadline)=%s ORDER BY deadline ASC", (date.today(),), True)
    elif filter_type.lower() == "completed":
        for c in range(1, 5):
            draw(c, f"SELECT taskName, taskStatus, deadline FROM taskinfo WHERE category={c} AND taskStatus=1 ORDER BY deadline ASC", (), False)
    else:
        cursor.execute("SELECT tagName FROM tags")
        tag_list = [r[0] for r in cursor.fetchall()]
        if filter_type in tag_list:
            for c in range(1, 5):
                draw(c, f"SELECT taskName, taskStatus FROM taskinfo WHERE category={c} AND taskStatus=0 AND tag=%s", (filter_type,), False)

# -------------------- Filter Button Logic --------------------
def set_active(index):
    global active_button
    for i, btn in enumerate(filter_buttons):
        if i == index:
            canvas.itemconfig(btn["shape_id"], fill="#1555DC", outline="#1555DC")
            canvas.itemconfig(btn["text_id"], fill="white")
        else:
            canvas.itemconfig(btn["shape_id"], fill="#FFFFFF", outline="#DEDEDE")
            canvas.itemconfig(btn["text_id"], fill="black")
    active_button = index
    filter_type = filter_buttons[index]["text"]
    displayTask(filter_type)
    print(f"Filter → {filter_type}")

for i, btn in enumerate(filter_buttons):
    for tag in (btn["shape_id"], btn["text_id"]):
        canvas.tag_bind(tag, "<Button-1>", lambda e, idx=i: set_active(idx))

# -------------------- Edit + Add Buttons --------------------
draw_rounded_rect(canvas, 25, 670, 195, 730, radius=50, color="#FFFFFF", outline="#DEDEDE")
canvas.create_text(60, 697, text="✎", fill="black", font=("Poppins", 27, "bold"))
canvas.create_text(130, 700, text="Edit Tags", fill="black", font=("Poppins", 22, "bold"))
draw_rounded_rect(canvas, 25, 750, 225, 810, radius=50, color="#1555DC")
canvas.create_text(60, 777, text="+", fill="white", font=("Poppins", 36, "bold"))
canvas.create_text(140, 780, text="Add Task", fill="white", font=("Poppins", 26, "bold"))

# >>> Click hotspot over the existing "Add Task" button (no UI change)
add_task_hotspot = canvas.create_rectangle(25, 750, 225, 810, outline="", fill="")
canvas.tag_bind(add_task_hotspot, "<Button-1>", lambda e: open_add_task_popup())
# Click hotspot over the existing "Edit Tags" card
edit_tag_hotspot = canvas.create_rectangle(25, 670, 195, 730, outline="", fill="")
canvas.tag_bind(edit_tag_hotspot, "<Button-1>", lambda e: open_tag_manager_popup())


# -------------------- Initial Load --------------------
displayTask("All")
root.mainloop()
