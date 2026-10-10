import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox
from zoneinfo import ZoneInfo, available_timezones
#just for reference 
DEFAULT_CITIES = [
    "America/Los_Angeles",
    "America/New_York",
    "Europe/London",
    "Europe/Madrid",
    "Asia/Dubai",
    "Asia/Tokyo",
    "Australia/Sydney",
]

BG = "#1e1e2e"
CARD = "#2a2a3d"
TEXT = "#e6e6f0"
MUTED = "#9a9ab0"
ACCENT = "#5ec8e5"


def city_name(tz_name):
    """'America/New_York' -> 'New York'."""
    return tz_name.split("/")[-1].replace("_", " ")


def offset_label(now_local, now_remote):
    """Difference from local time, e.g. '+6h' or '-3h30m'."""
    diff = now_remote.utcoffset() - now_local.utcoffset()
    minutes = int(diff.total_seconds() // 60)
    if minutes == 0:
        return "same as local"
    sign = "+" if minutes > 0 else "-"
    h, m = divmod(abs(minutes), 60)
    return f"{sign}{h}h" + (f"{m:02d}m" if m else "")


class ClockRow:
    def __init__(self, parent, tz_name, on_remove):
        self.tz = ZoneInfo(tz_name)
        self.frame = tk.Frame(parent, bg=CARD, padx=14, pady=8)
        self.frame.pack(fill="x", pady=4)

        left = tk.Frame(self.frame, bg=CARD)
        left.pack(side="left", fill="x", expand=True)
        tk.Label(left, text=city_name(tz_name), bg=CARD, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")
        self.info = tk.Label(left, bg=CARD, fg=MUTED, font=("Segoe UI", 9))
        self.info.pack(anchor="w")

        tk.Button(self.frame, text="✕", bg=CARD, fg=MUTED, bd=0,
                  activebackground=CARD, activeforeground="#ff6b6b",
                  cursor="hand2", command=lambda: on_remove(self, tz_name)
                  ).pack(side="right", padx=(10, 0))
        self.time = tk.Label(self.frame, bg=CARD, fg=ACCENT,
                             font=("Consolas", 20, "bold"))
        self.time.pack(side="right")

    def update(self, now_local):
        now = datetime.now(self.tz)
        icon = "☀" if 6 <= now.hour < 18 else "☾"
        self.time.config(text=now.strftime("%H:%M:%S"))
        self.info.config(text=f"{icon}  {now:%a %d %b} · {now:%Z} · "
                              f"{offset_label(now_local, now)}")

    def destroy(self):
        self.frame.destroy()


class WorldClockApp:
    def __init__(self, root):
        self.root = root
        root.title("World Clock")
        root.configure(bg=BG, padx=16, pady=16)
        root.minsize(440, 300)

        self.local = tk.Label(root, bg=BG, fg=TEXT, font=("Consolas", 32, "bold"))
        self.local.pack()
        self.local_info = tk.Label(root, bg=BG, fg=MUTED, font=("Segoe UI", 10))
        self.local_info.pack(pady=(0, 12))

        # Add-city bar
        bar = tk.Frame(root, bg=BG)
        bar.pack(fill="x", pady=(0, 8))
        self.zones = sorted(z for z in available_timezones() if "/" in z
                            and not z.startswith(("Etc/", "SystemV/")))
        self.choice = ttk.Combobox(bar, values=self.zones)
        self.choice.set("Type a zone, e.g. Europe/Paris")
        self.choice.pack(side="left", fill="x", expand=True)
        self.choice.bind("<KeyRelease>", self.filter_zones)
        self.choice.bind("<Return>", lambda e: self.add_city())
        tk.Button(bar, text="Add", bg=ACCENT, fg=BG, bd=0, padx=12,
                  cursor="hand2", command=self.add_city).pack(side="left", padx=(6, 0))

        self.list_frame = tk.Frame(root, bg=BG)
        self.list_frame.pack(fill="both", expand=True)

        self.rows = []
        self.shown = set()
        for tz in DEFAULT_CITIES:
            self.add_city(tz)

        self.tick()

    def filter_zones(self, event):
        if event.keysym in ("Up", "Down", "Return"):
            return
        text = self.choice.get().lower()
        self.choice["values"] = [z for z in self.zones if text in z.lower()] or self.zones

    def add_city(self, tz_name=None):
        tz_name = tz_name or self.choice.get().strip()
        if tz_name not in self.zones and tz_name not in DEFAULT_CITIES:
            messagebox.showwarning("World Clock", f"Unknown time zone: {tz_name}")
            return
        if tz_name in self.shown:
            return
        self.rows.append(ClockRow(self.list_frame, tz_name, self.remove_city))
        self.shown.add(tz_name)

    def remove_city(self, row, tz_name):
        row.destroy()
        self.rows.remove(row)
        self.shown.discard(tz_name)

    def tick(self):
        now_local = datetime.now().astimezone()
        self.local.config(text=now_local.strftime("%H:%M:%S"))
        self.local_info.config(text=f"Local time · {now_local:%A %d %B %Y · %Z}")
        for row in self.rows:
            row.update(now_local)
        # Schedule next tick just after the next whole second
        self.root.after(1000 - now_local.microsecond // 1000, self.tick)


if __name__ == "__main__":
    root = tk.Tk()
    WorldClockApp(root)
    root.mainloop()
