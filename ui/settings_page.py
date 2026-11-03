"""Settings page (same content in both modes, colored by the current mode)."""
from tkinter import messagebox

import customtkinter as ctk

from core.demo import load_demo
from ui import widgets as w
from ui.page import Page
from ui.theme import FONT, GAIN, LOSS, THEMES


def settings_page(ctx, mode, master):
    t = THEMES[mode]
    page = Page(master, mode, "Settings", "Personalise and manage your data.")

    # ---- profile and trading rules ----
    prof = w.card(page, t)
    w.card_title(prof, t, "Profile and trading rules")
    body = ctk.CTkFrame(prof, fg_color="transparent")
    body.pack(fill="x", padx=20, pady=(0, 4))
    body.grid_columnconfigure(0, weight=1)
    e_name = w.entry(body, t, ctx.name)
    w.field(body, t, 0, 0, "Display name", e_name, colspan=3)
    e_cap = w.entry(body, t, f"{ctx.trades.capital:g}")
    w.field(body, t, 1, 0, "Starting capital ($)", e_cap, colspan=3)
    e_max = w.entry(body, t, str(ctx.trades.max_per_day))
    w.field(body, t, 2, 0, "Max trades per day (discipline alert)", e_max, colspan=3)
    msg1 = ctk.CTkLabel(prof, text="", font=(FONT, 12), anchor="w")
    msg1.pack(anchor="w", padx=20, pady=(8, 0))

    def save():
        try:
            capital = float(e_cap.get().replace(",", "."))
            limit = int(e_max.get())
            if capital <= 0 or limit < 1:
                raise ValueError
        except ValueError:
            msg1.configure(text="Capital must be a positive number and the limit a whole number.",
                           text_color=LOSS)
            return
        ctx.db.set_setting("name", e_name.get().strip() or "Prince")
        ctx.db.set_setting("capital", capital)
        ctx.db.set_setting("max_trades_day", limit)
        msg1.configure(text="Settings saved.", text_color=GAIN)

    w.button(prof, t, "Save settings", save, width=130, height=36).pack(anchor="w", padx=20, pady=(8, 18))

    # ---- data ----
    data = w.card(page, t)
    w.card_title(data, t, "Data and reminders")
    msg2 = ctk.CTkLabel(data, text="", font=(FONT, 12), anchor="w", wraplength=360, justify="left")

    def reminders():
        n = ctx.tasks.add_trading_reminders()
        msg2.configure(text=f"{n} trading reminder(s) added to My Tasks (local time)." if n
                       else "Trading reminders are already in My Tasks.", text_color=LOSS)

    def demo():
        load_demo(ctx.tasks, ctx.trades)
        msg2.configure(text="Demo data loaded.", text_color=GAIN)

    def clear():
        if messagebox.askyesno("Clear all data", "Delete ALL tasks and trades? This cannot be undone."):
            ctx.db.execute("DELETE FROM tasks")
            ctx.db.execute("DELETE FROM trades")
            msg2.configure(text="All tasks and trades deleted.", text_color=GAIN)

    for text, command, kind in (("Add trading reminders to My Tasks", reminders, "primary"),
                                ("Load demo data", demo, "secondary"),
                                ("Clear all data", clear, "danger")):
        w.button(data, t, text, command, kind=kind, width=250, height=36).pack(anchor="w", padx=20, pady=5)
    msg2.pack(anchor="w", padx=20, pady=(6, 18))
    page.add_row([prof, data])
    return page
