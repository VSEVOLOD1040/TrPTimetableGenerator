import random
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
import json
import webbrowser
import os
import sys
import platform
import subprocess
# pyinstaller --clean --onefile --icon=TrPTimetableGenerator/logo.ico --noconsole TrPTimetableGenerator/TrPTG.py

version = "1.0"
release = "01.07.2025"
DiscordLink = "https://discord.gg/F8DgYkwEMD"

font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/arialbd.ttf", 40)
font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/arialbd.ttf", 30)
font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/arialbd.ttf", 30)
font_text_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/arialbd.ttf", 24)

font_uptext = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/arialbd.ttf", 35)

show_cut_line = False

img_width, img_height = 930, 760
padding_left = 50
padding_top = 30
row_height = 34
stop_width = 420
time_col_width = 100
column_count = 4
gap_between_tables = 25

table1_top = 150
table2_top = table1_top
table2_left = padding_left + stop_width + gap_between_tables

# Name : font size
long_names = {
            "Antidisestablishmentarianism street":24,
            "New Green village, building 28":28,
            "New Green village, building 12":28,
            "Prodisestablishmentarianism street":24
}


def GenerateTimetable(data):
    ReturnTime = None

    for row in reversed(data["Times"]):
        for time in reversed(row):
            if time:
                ReturnTime = time
                break
        if ReturnTime:
            break


    img = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(img)

    draw.text((img_width / 2, padding_top + 5), f"Route {data["Route"]}", font=font_title, fill="black", anchor="mm")

    draw.text((padding_left, padding_top + 38), f"Schedule - {data["Schedule"]}.", font=font_uptext, fill="black")
    draw.text((padding_left, padding_top + 78), f"Departure: {data["Departure"]} ({data["Stops"][0]})", font=font_uptext, fill="black")

    draw.rectangle(
        [padding_left, table1_top, padding_left + stop_width, table1_top + row_height * len(data["Stops"])],
        outline="black", width=2
    )
    for i, stop in enumerate(data["Stops"]):
        y = table1_top + i * row_height
        draw.line([(padding_left, y), (padding_left + stop_width, y)], fill="black", width=1)


        if stop not in long_names:
            draw.text(
                (padding_left + stop_width / 2, y + row_height / 2),
                stop,
                font=font_text,
                fill="black",
                anchor="mm"
            )
        else:
            draw.text(
                (padding_left + stop_width / 2, y + row_height / 2),
                stop,
                font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/arialbd.ttf", long_names[stop]),
                fill="black",
                anchor="mm"
            )
    draw.line(
        [(padding_left, table1_top + row_height * len(data["Stops"])),
         (padding_left + stop_width, table1_top + row_height * len(data["Stops"]))],
        fill="black", width=1
    )

    table2_width = time_col_width * column_count
    draw.rectangle(
        [table2_left, table2_top, table2_left + table2_width, table2_top + row_height * len(data["Stops"])],
        outline="black", width=2
    )
    for i in range(len(data["Stops"])):
        y = table2_top + i * row_height
        for j in range(column_count):
            x = table2_left + j * time_col_width
            draw.line([(x, table2_top), (x, table2_top + row_height * len(data["Stops"]))], fill="black", width=1)
            draw.line([(table2_left, y), (table2_left + table2_width, y)], fill="black", width=1)
            draw.text(
                (x + time_col_width / 2, y + row_height / 2),
                data["Times"][i][j],
                font=font_text,
                fill="black",
                anchor="mm"
            )
    draw.line(
        [(table2_left, table2_top + row_height * len(data["Stops"])),
         (table2_left + table2_width, table2_top + row_height * len(data["Stops"]))],
        fill="black", width=1
    )

    return_text_y = table1_top + row_height * len(data["Stops"]) + 40
    draw.text((padding_left, return_text_y), f"Return: {ReturnTime}", font=font_bold, fill="black")

    def draw_dashed_rectangle(draw, box, dash_length=5, gap=5, color="grey"):
        x1, y1, x2, y2 = box

        for x in range(x1, x2, dash_length + gap):
            draw.line([(x, y1), (min(x + dash_length, x2), y1)], fill=color)

        for x in range(x1, x2, dash_length + gap):
            draw.line([(x, y2 - 1), (min(x + dash_length, x2), y2 - 1)], fill=color)

        for y in range(y1, y2, dash_length + gap):
            draw.line([(x1, y), (x1, min(y + dash_length, y2))], fill=color)

        for y in range(y1, y2, dash_length + gap):
            draw.line([(x2 - 1, y), (x2 - 1, min(y + dash_length, y2))], fill=color)

    margin = 1
    if show_cut_line:

        draw_dashed_rectangle(draw, [margin, margin, img_width - margin, img_height - margin])

    output_path = f"lasttimetable.png"
    img.save(output_path)
    def open_image(path):
        system = platform.system()
        if system == "Windows":
            os.startfile(path)
        elif system == "Darwin":  # macOS
            subprocess.run(["open", path])
        else:  # Linux
            subprocess.run(["xdg-open", path])

    open_image("lasttimetable.png")


with open("routes.json", "r", encoding="utf-8") as f:
    routes = json.load(f)



def launch_gui():
    root = tk.Tk()
    root.title("TrP Timetable Generator by SDAN1040")
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
        root.tk.call('tk', 'scaling', 1.5)

    except:
        pass

    def has_ico_file():
        if getattr(sys, 'frozen', False):
            # Запущено как .exe
            current_folder = os.path.dirname(sys.executable)
        else:
            # Запущено как .py
            current_folder = os.path.dirname(os.path.abspath(__file__))

        return os.path.isfile(os.path.join(current_folder, "sdansserver.ico"))
    def SetIcon(rt):
        if has_ico_file():
            rt.iconbitmap("sdansserver.ico")
        else:
            root.withdraw()
            show_error("Error\nError code: 1 - invalid hierarchy",
                       "Check the integrity of the program files. Reinstall the program."
                       "If this does not help, contact support in the Discord server using the link below.")
            sys.exit()



    def toggle_cut_line():
        global show_cut_line
        show_cut_line = not show_cut_line
        if show_cut_line:
            cut_btn.config(bg="SpringGreen3", activebackground="SpringGreen3")
        else:
            cut_btn.config(bg="tomato", activebackground="tomato")

    def show_error(error, message):
        root = tk.Tk()
        root.withdraw()

        help_window = tk.Toplevel(root)
        help_window.title("ERROR")
        help_window.geometry("400x350")

        help_label = tk.Label(help_window, text=error, font=("Arial", 12), wraplength=280, justify="left", anchor="w",
                              foreground="red")
        help_label.pack(pady=1, fill="both", expand=True)

        help_label = tk.Label(help_window, text=message, font=("Arial", 10), wraplength=280, justify="left", anchor="w")
        help_label.pack(pady=10, fill="both", expand=True)

        link = tk.Label(help_window, text=DiscordLink, fg="blue", cursor="hand2", font=("Arial", 10, "underline"))
        link.pack()
        link.bind("<Button-1>", lambda e: webbrowser.open(DiscordLink))

        help_label = tk.Label(help_window, text=f"TrPTimetableGenerator. Version: {version}", font=("Arial", 10),
                              wraplength=280, justify="left", anchor="w")
        help_label.pack(pady=10, fill="both", expand=True)

        help_window.protocol("WM_DELETE_WINDOW", root.quit)
        root.mainloop()
    SetIcon(root)
    def show_help():
        help_window = tk.Toplevel(root)
        help_window.title("Information")
        help_window.geometry("500x300")
        SetIcon(help_window)
        help_label = tk.Label(help_window, text=(
            f"Author: SDAN1040\nVersion: {version}\nRelease date: {release}\n\n"
            f"The program uses SDAN1040's Group server routes\nAll information is on the Discord server\nSDAN's Server"
        ), font=("Arial", 10))
        help_label.pack(pady=1)
        link = tk.Label(help_window, text=DiscordLink, fg="blue", cursor="hand2", font=("Arial", 10, "underline"))
        link.pack()
        link.bind("<Button-1>", lambda e: webbrowser.open(DiscordLink))

    help_btn = ttk.Button(root, text="?", command=show_help, width=2)
    help_btn.grid(row=0, column=0, padx=5, pady=5, sticky="nw")

    real_time_mode = tk.BooleanVar(value=False)
    schedule_number = tk.IntVar(value=random.randint(1, 99))
    rounds_var = tk.IntVar(value=3)

    def update_time_loop():
        if real_time_mode.get():
            now = datetime.now().strftime("%H:%M")
            time_entry.delete(0, tk.END)
            time_entry.insert(0, now)
        root.after(1000, update_time_loop)

    def toggle_real_time():
        real_time_mode.set(not real_time_mode.get())
        btn_color = "SpringGreen3" if real_time_mode.get() else "tomato"
        real_time_btn.config(bg=btn_color)
        if real_time_mode.get():
            now = datetime.now().strftime("%H:%M")
            time_entry.delete(0, tk.END)
            time_entry.insert(0, now)

    def generate():
        route = route_entry.get()
        if route not in routes:
            route_warning.config(text="Route not found")
            return
        else:
            route_warning.config(text="")

        route_data = routes[route]
        stops = route_data["Stops"]
        delays = route_data["Delays"]
        restart_delay = delays[-1]
        one_loop_duration = sum(delays[:-1]) + restart_delay

        if real_time_mode.get():
            departure_time = datetime.now()
            departure_str = departure_time.strftime("%H:%M")
        else:
            try:
                departure_str = time_entry.get()
                departure_time = datetime.strptime(departure_str, "%H:%M")
            except ValueError:
                messagebox.showerror("Error", "Invalid time format")
                return

        sched = schedule_spin.get()
        if not sched.isdigit() or not (1 <= int(sched) <= 99):
            messagebox.showerror("Error", "Schedule number must be between 1 and 99.")
            return
        sched = int(sched)

        rounds = rounds_var.get()
        if not (1 <= rounds <= 4):
            messagebox.showerror("Error", "The number of flights must be between 1 and 4.")
            return

        times = [['' for _ in range(4)] for _ in range(len(stops))]
        offset_start = timedelta(minutes=2)

        for r in range(rounds):
            current_time = departure_time + offset_start + timedelta(minutes=one_loop_duration * r)
            for i in range(len(stops)):
                if i > 0:
                    current_time += timedelta(minutes=delays[i - 1])
                times[i][r] = current_time.strftime("%H:%M")
        rows_count = 14

        if len(stops) < rows_count:
            stops = stops + [""] * (rows_count - len(stops))

        if len(times) < rows_count:
            for _ in range(rows_count - len(times)):
                times.append(['' for _ in range(4)])

        data = {
            "Route": route,
            "Schedule": sched,
            "Departure": departure_str,
            "Stops": stops,
            "Times": times
        }

        GenerateTimetable(data)

    tk.Label(root, text="Route number:").grid(row=1, column=0, sticky="w")
    route_entry = ttk.Entry(root)
    route_entry.grid(row=1, column=1)
    route_warning = tk.Label(root, text="", fg="red")
    route_warning.grid(row=1, column=2, padx=5)

    tk.Label(root, text="Departure time:").grid(row=2, column=0, sticky="w")
    time_entry = ttk.Entry(root)
    time_entry.grid(row=2, column=1)
    real_time_btn = tk.Button(root, text="Real time", bg="tomato", fg="white", command=toggle_real_time)
    real_time_btn.grid(row=2, column=2, padx=5)

    tk.Label(root, text="Schedule number (1-99):").grid(row=3, column=0, sticky="w")
    schedule_spin = ttk.Entry(root, textvariable=schedule_number)
    schedule_spin.grid(row=3, column=1)
    def randomize_schedule():
        schedule_number.set(random.randint(1, 99))
    ttk.Button(root, text="Random", command=randomize_schedule).grid(row=3, column=2)

    tk.Label(root, text="Flights amount (1-4):").grid(row=4, column=0, sticky="w")
    rounds_spin = ttk.Spinbox(root, from_=1, to=4, textvariable=rounds_var, width=5)
    rounds_spin.grid(row=4, column=1)

    cut_btn = tk.Button(root, text="✂ Cut line (for printing)", bg="tomato", fg="white", command=toggle_cut_line)
    cut_btn.grid(row=4, column=2, padx=5, pady=5, sticky="nw")

    generate_btn = tk.Button(root, text="Generate", command=generate, bg="SteelBlue1", fg="white", font=("Arial", 14))
    generate_btn.grid(row=6, column=0, columnspan=3, pady=10)

    update_time_loop()
    root.mainloop()

launch_gui()