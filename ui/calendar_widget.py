"""Month grid (task calendar and P&L calendar) and a small date picker."""
import calendar
import tkinter as tk
from datetime import date

import customtkinter as ctk

from ui.theme import FONT, STATUS


class MonthGrid(ctk.CTkFrame):
    """A month view. info_fn(year, month) -> {date: (text, kind)} colors the days.
    kind is 'success', 'warning', 'danger' or None."""

    def __init__(self, master, theme, info_fn=None, on_select=None, selected=None, cell_h=38):
        super().__init__(master, fg_color="transparent")
        self.theme = theme
        self.info_fn = info_fn
        self.on_select = on_select
        self.selected = selected
        self.cell_h = cell_h
        base = selected or date.today()
        self.year, self.month = base.year, base.month
        self._cells = []

        for c in range(7):
            self.grid_columnconfigure(c, weight=1, uniform="day")
        self._prev = self._nav_button("<", -1, 0)
        self._next = self._nav_button(">", 1, 6)
        self._title = ctk.CTkLabel(self, text="", font=(FONT, 14, "bold"),
                                   text_color=theme["text"])
        self._title.grid(row=0, column=1, columnspan=5, pady=(0, 6))
        for c, name in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            ctk.CTkLabel(self, text=name, font=(FONT, 11),
                         text_color=theme["text_muted"]).grid(row=1, column=c, pady=(0, 2))
        self.render()

    def _nav_button(self, text, delta, col):
        b = ctk.CTkButton(self, text=text, width=32, height=28, corner_radius=8,
                          fg_color=self.theme["card_border"], hover_color=self.theme["accent_soft"],
                          text_color=self.theme["text"], font=(FONT, 13, "bold"),
                          command=lambda: self._shift(delta))
        b.grid(row=0, column=col, pady=(0, 6))
        return b

    def _shift(self, delta):
        month = self.month + delta
        self.year += (month - 1) // 12
        self.month = (month - 1) % 12 + 1
        self.render()

    def set_selected(self, d):
        self.selected = d
        self.render()

    def render(self):
        t = self.theme
        for cell in self._cells:
            cell.destroy()
        self._cells = []
        self._title.configure(text=f"{calendar.month_name[self.month]} {self.year}")
        info = self.info_fn(self.year, self.month) if self.info_fn else {}
        today = date.today()

        weeks = calendar.Calendar(0).monthdayscalendar(self.year, self.month)
        for r, week in enumerate(weeks):
            for c, day in enumerate(week):
                if day == 0:
                    continue
                d = date(self.year, self.month, day)
                text, kind = info.get(d, (None, None))
                fg, txt = t["input"], t["text"]
                if kind:
                    txt, fg = STATUS[kind]
                border = 0
                if d == self.selected:
                    border = 2
                elif d == today:
                    border = 1
                # simple tk.Label : environ 10 fois plus rapide à créer qu'un CTkButton (35 cases par mois)
                cell = tk.Label(
                    self, text=f"{day}\n{text or ' '}", bg=fg, fg=txt, font=(FONT, 10), bd=0,
                    cursor="hand2", highlightthickness=border,
                    highlightbackground=t["accent"] if d == self.selected else t["text_muted"])
                cell.bind("<Button-1>", lambda _e, dd=d: self._click(dd))
                cell.bind("<Enter>", lambda _e, c=cell: c.configure(bg=t["card_border"]))
                cell.bind("<Leave>", lambda _e, c=cell, b=fg: c.configure(bg=b))
                cell.grid(row=r + 2, column=c, sticky="nsew", padx=2, pady=2,
                          ipady=max(0, (self.cell_h - 30) // 2))
                self._cells.append(cell)

    def _click(self, d):
        self.selected = d
        self.render()
        if self.on_select:
            self.on_select(d)


def pick_date(parent, theme, current, on_pick):
    """Small pop-up with a month grid. Calls on_pick(date) and closes."""
    win = ctk.CTkToplevel(parent)
    win.title("Pick a date")
    win.configure(fg_color=theme["card"])
    win.resizable(False, False)
    win.attributes("-topmost", True)
    win.geometry(f"+{parent.winfo_pointerx()}+{parent.winfo_pointery()}")

    def choose(d):
        on_pick(d)
        win.destroy()

    MonthGrid(win, theme, on_select=choose, selected=current, cell_h=34).pack(padx=14, pady=14)


def date_field(parent, theme, value):
    """Entry + 'Pick' button. Returns (frame, entry)."""
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.grid_columnconfigure(0, weight=1)
    entry = ctk.CTkEntry(frame, height=34, corner_radius=8, fg_color=theme["input"],
                         border_color=theme["card_border"], text_color=theme["text"])
    entry.insert(0, value)
    entry.grid(row=0, column=0, sticky="ew")

    def on_pick(d):
        entry.delete(0, "end")
        entry.insert(0, d.isoformat())

    def open_picker():
        try:
            current = date.fromisoformat(entry.get().strip())
        except ValueError:
            current = date.today()
        pick_date(frame, theme, current, on_pick)

    ctk.CTkButton(frame, text="Pick", width=52, height=34, corner_radius=8,
                  fg_color=theme["card_border"], hover_color=theme["accent_soft"],
                  text_color=theme["text"], font=(FONT, 12),
                  command=open_picker).grid(row=0, column=1, padx=(6, 0))
    return frame, entry
