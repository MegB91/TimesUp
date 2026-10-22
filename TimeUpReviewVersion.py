import time
import tkinter as tk
from tkinter import ttk, messagebox

# Predefined Colours
#CMYK, 33,4,7,0.  16,6,42,12   20,25,40,6
#Color-hex.com

BG = "#faf0e6" #seashell2
PANEL = "#fffaf0" #seashell1
PANEL_LIGHT = "#f4c2c2"
TEXT = "#727472" #Quinacridone Magenta
MUTED = "#9f8170" #heading text
ACCENT = "#796878" #colour of the columns
GREEN = "#87a96b"
RED = "#8e3a59" #Quinacridone Magenta
GRID = "#ff91af" #gridlines
#sage bcb888a #Prussion blue 003153 #Puce cc8899 Portaland Orange ff5a36
#old lace fdf5e6 floral white fffaf0
#"#eee5de" #seashell2
#"#fff5ee" #seashell1
#text should be old burgundy 43302e
start_time = None
after_id = None
sessions = []

def format_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    whole_seconds = int(seconds)
    hundredths = int((seconds - whole_seconds) * 100)
    return f"{int(minutes):02}:{whole_seconds:02}.{hundredths:02}"

def update_display():
    global after_id

    if start_time is not None:
        timer_label.config(text=format_time(time.perf_counter() - start_time))
        after_id = root.after(30, update_display)

def start_timer():
    global start_time

    if start_time is not None:
        return

    start_time = time.perf_counter()
    status_label.config(text="RUNNING", fg=GREEN)
    start_button.config(state="disabled")
    stop_button.config(state="normal")
    update_display()

def stop_timer():
    global start_time, after_id

    if start_time is None:
        return

    elapsed = time.perf_counter() - start_time
    start_time = None

    if after_id is not None:
        root.after_cancel(after_id)
        after_id = None

    sessions.append(elapsed)
    timer_label.config(text=format_time(elapsed))
    status_label.config(text="STOPPED", fg=MUTED)
    start_button.config(state="normal")
    stop_button.config(state="disabled")

    update_stats()
    draw_chart()

    messagebox.showinfo(
        "Session complete",
        f"Session {len(sessions)}: {format_time(elapsed)}",
        parent=root
    )

def update_stats():
    total = sum(sessions)
    count_label.config(text=str(len(sessions)))
    total_label.config(text=format_time(total))

def draw_chart(event=None):
    chart.delete("all")

    width = chart.winfo_width()
    height = chart.winfo_height()
    if width < 100 or height < 100:
        return

    left, right = 48, width - 16
    top, bottom = 34, height - 32
    plot_height = bottom - top

    chart.create_text(
        4, 10, anchor="w",
        text="RECENT SESSIONS",
        fill=MUTED, font=("Arial", 9, "bold")
    )

    if not sessions:
        chart.create_text(
            width / 2, height / 2,
            text="Your completed sessions will appear here",
            fill=MUTED, font=("Arial", 10)
        )
        return

    shown = sessions[-8:]
    maximum = max(shown) or 1

    # Subtle horizontal guide lines
    for fraction in (0.25, 0.5, 0.75, 1.0):
        y = bottom - plot_height * fraction
        chart.create_line(left, y, right, y, fill=GRID)
        chart.create_text(
            left - 8, y, anchor="e",
            text=format_time(maximum * fraction),
            fill=MUTED, font=("Arial", 7)
        )

    slot = (right - left) / len(shown)
    bar_width = min(38, slot * 0.55)

    for i, duration in enumerate(shown):
        x = left + slot * (i + 0.5)
        bar_height = (duration / maximum) * (plot_height - 8)
        y = bottom - bar_height

        chart.create_rectangle(
            x - bar_width / 2, y,
            x + bar_width / 2, bottom,
            fill=ACCENT, outline=""
        )

        session_number = len(sessions) - len(shown) + i + 1
        chart.create_text(
            x, bottom + 14,
            text=str(session_number),
            fill=MUTED, font=("Arial", 8)
        )

root = tk.Tk()
root.title("Session Timer")
root.geometry("440x570")
root.minsize(360, 500)
root.configure(bg=BG)

style = ttk.Style(root)
style.theme_use("clam")
style.configure(
    "Start.TButton",
    font=("Arial", 11, "bold"),
    padding=(18, 10),
    background=GREEN,
    foreground="#06281e",
    borderwidth=0
)
style.map("Start.TButton", background=[("active", "#6ee7b7")])
style.configure(
    "Stop.TButton",
    font=("Arial", 11, "bold"),
    padding=(18, 10),
    background=RED,
    foreground="#3b0a17",
    borderwidth=0
)
style.map("Stop.TButton", background=[("active", "#fda4af")])

# Header
tk.Label(
    root, text="SESSION TIMER",
    font=("Arial", 11, "bold"), bg=BG, fg=MUTED
).pack(pady=(22, 10))

# Timer panel
timer_panel = tk.Frame(root, bg=PANEL, padx=20, pady=18)
timer_panel.pack(padx=22, fill="x")

timer_label = tk.Label(
    timer_panel, text="00:00.00",
    font=("Arial", 42, "bold"), bg=PANEL, fg=TEXT
)
timer_label.pack()

status_label = tk.Label(
    timer_panel, text="READY",
    font=("Arial", 9, "bold"), bg=PANEL, fg=MUTED
)
status_label.pack(pady=(3, 14))

button_frame = tk.Frame(timer_panel, bg=PANEL)
button_frame.pack()

start_button = ttk.Button(
    button_frame, text="Start",
    style="Start.TButton", command=start_timer
)
start_button.pack(side="left", padx=6)

stop_button = ttk.Button(
    button_frame, text="Stop",
    style="Stop.TButton", command=stop_timer, state="disabled"
)
stop_button.pack(side="left", padx=6)

summary = tk.Frame(root, bg=BG)
summary.pack(padx=22, pady=14, fill="x")
summary.columnconfigure((0, 1), weight=1)

count_card = tk.Frame(summary, bg=PANEL_LIGHT, padx=14, pady=10)
count_card.grid(row=0, column=0, sticky="ew", padx=(0, 6))

total_card = tk.Frame(summary, bg=PANEL_LIGHT, padx=14, pady=10)
total_card.grid(row=0, column=1, sticky="ew", padx=(6, 0))

tk.Label(
    count_card, text="SESSIONS",
    font=("Arial", 8, "bold"), bg=PANEL_LIGHT, fg=MUTED
).pack(anchor="w")
count_label = tk.Label(
    count_card, text="0",
    font=("Arial", 18, "bold"), bg=PANEL_LIGHT, fg=TEXT
)
count_label.pack(anchor="w", pady=(3, 0))

tk.Label(
    total_card, text="TOTAL TIME",
    font=("Arial", 8, "bold"), bg=PANEL_LIGHT, fg=MUTED
).pack(anchor="w")
total_label = tk.Label(
    total_card, text="00:00.00",
    font=("Arial", 18, "bold"), bg=PANEL_LIGHT, fg=TEXT
)
total_label.pack(anchor="w", pady=(3, 0))

# Chart panel
chart_panel = tk.Frame(root, bg=PANEL, padx=12, pady=10)
chart_panel.pack(padx=22, pady=(0, 22), fill="both", expand=True)

chart = tk.Canvas(
    chart_panel, bg=PANEL, highlightthickness=0, height=190
)
chart.pack(fill="both", expand=True)
chart.bind("<Configure>", draw_chart)

root.mainloop()
