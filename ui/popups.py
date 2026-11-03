"""Reminder pop-up shown when a task is due."""
from datetime import datetime

import customtkinter as ctk

from core.tasks_service import FMT
from ui import widgets as w
from ui.theme import FONT, THEMES

T = THEMES["productivity"]


class ReminderPopup(ctk.CTkToplevel):
    def __init__(self, app, ctx, task):
        super().__init__(app)
        self.ctx = ctx
        self.task_id = task["id"]
        self.title("Task Reminder")
        self.geometry("400x330")
        self.resizable(False, False)
        self.configure(fg_color=T["card"])
        self.attributes("-topmost", True)

        due = datetime.strptime(task["due"], FMT)
        ctk.CTkLabel(self, text="Task Reminder!", font=(FONT, 24, "bold"),
                     text_color=T["text"]).pack(pady=(26, 2))
        ctk.CTkLabel(self, text="It's time to do your task. Don't Snooze pls!", font=(FONT, 13),
                     text_color=T["text_secondary"]).pack()

        info = ctk.CTkFrame(self, fg_color=T["input"], corner_radius=12)
        info.pack(fill="x", padx=28, pady=18)
        for r, (label, value) in enumerate((("Task", task["title"]),
                                            ("Time", f"{due:%H:%M}"),
                                            ("Date", f"{due:%d %B %Y}"))):
            ctk.CTkLabel(info, text=label, width=60, anchor="w", font=(FONT, 12),
                         text_color=T["text_muted"]).grid(row=r, column=0, padx=(16, 4), pady=5)
            ctk.CTkLabel(info, text=value, anchor="w", font=(FONT, 14, "bold"), wraplength=240,
                         justify="left", text_color=T["text"]).grid(row=r, column=1, sticky="w")

        w.button(self, T, "Mark as Completed", self.complete, width=344, height=38).pack(pady=(0, 8))
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack()
        w.button(row, T, "Snooze (10 min)", self.snooze, kind="secondary", width=168,
                 height=34).pack(side="left", padx=(0, 8))
        w.button(row, T, "Close", self.destroy, kind="secondary", width=168,
                 height=34).pack(side="left")

        self.after(200, self.lift)

    def complete(self):
        self.ctx.tasks.toggle_done(self.task_id)
        self.destroy()
        self.ctx.reload()

    def snooze(self):
        self.ctx.tasks.snooze(self.task_id, 10)
        self.destroy()
        self.ctx.reload()
