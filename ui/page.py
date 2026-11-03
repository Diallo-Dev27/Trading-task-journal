"""Base page: a Canvas with the background image, a title and rows of cards.

customtkinter widgets have opaque backgrounds, so the cards are drawn into the
background image (see background.py) and their content is placed on top with
create_window. The page scrolls (scrollbar, mouse wheel, PageUp/PageDown) when it
is taller than the window.
"""
import tkinter as tk

import customtkinter as ctk
from PIL import ImageTk

from ui.background import make_page_image
from ui.theme import FONT, THEMES


class Page(tk.Canvas):
    MARGIN = 28
    GAP = 14
    HEADER_H = 118
    INSET = 6            # space between the drawn card edge and its content
    BOTTOM_PAD = 48      # extra space under the last card
    SCROLL_STEP = 70     # pixels per mouse wheel notch

    def __init__(self, master, mode, title, subtitle=""):
        theme = THEMES[mode]
        super().__init__(master, bg=theme["bg"], highlightthickness=0, bd=0)
        self.mode = mode
        self.theme = theme
        self.rows = []
        self.scroll_y = 0
        self._content_h = 0
        self._photo = None
        self._after = None
        self._last_key = None

        self._bg_item = self.create_image(0, 0, anchor="nw")
        self._title = self.create_text(self.MARGIN, 28, anchor="nw", text=title,
                                       fill=theme["text"], font=(FONT, 24, "bold"))
        self._subtitle = self.create_text(self.MARGIN, 72, anchor="nw", text=subtitle,
                                          fill=theme["text_secondary"], font=(FONT, 12))
        self._bar = ctk.CTkScrollbar(self, width=12, corner_radius=6, fg_color=theme["bg"],
                                     button_color=theme["text_muted"],
                                     button_hover_color=theme["accent"], command=self._on_bar)
        self.bind("<Configure>", self._schedule_layout)
        

    # ---------- content ----------
    def add_row(self, widgets, weights=None):
        """Adds a row of widgets (children of this page) split into columns."""
        wins = [self.create_window(0, 0, anchor="nw", window=w) for w in widgets]
        self.rows.append((widgets, wins, weights or [1] * len(widgets)))

    def relayout(self):
        """Call after the content of a card changed size."""
        self.update_idletasks()
        self._relayout()
    def layout_now(self):
        """Place tout immédiatement, pour que rien ne bouge après le premier affichage."""
        self.update_idletasks()
        self._relayout()

    # ---------- scrolling ----------
    def _limit(self):
        return max(0, self._content_h - self.winfo_height())

    def scroll_to(self, y):
        new = int(min(max(y, 0), self._limit()))
        if new != self.scroll_y:
            self.scroll_y = new
            self._relayout()

    def scroll_by(self, dy):
        self.scroll_to(self.scroll_y + dy)

    def _on_bar(self, *args):
        if args[0] == "moveto":
            self.scroll_to(float(args[1]) * self._content_h)
        elif args[0] == "scroll":
            step = self.SCROLL_STEP if args[2] == "units" else self.winfo_height() * 0.9
            self.scroll_by(int(args[1]) * step)

    def _update_bar(self, h):
        if self._content_h - h > 4:
            self._bar.configure(height=max(40, h - 16))
            self._bar.place(relx=1.0, x=-18, y=8)
            self._bar.set(self.scroll_y / self._content_h,
                          min(1.0, (self.scroll_y + h) / self._content_h))
        else:
            self._bar.place_forget()

    # ---------- layout ----------
    def _schedule_layout(self, _event=None):
        if self._after:
            try:
                self.after_cancel(self._after)
            except tk.TclError:
                pass
        self._after = self.after(60, self._relayout)

    def _relayout(self):
        self._after = None
        try:
            w, h = self.winfo_width(), self.winfo_height()
        except tk.TclError:  # the page was destroyed in the meantime
            return
        if w < 50 or h < 50:
            return
        self.scroll_y = min(self.scroll_y, self._limit())

        self.coords(self._title, self.MARGIN, 28 - self.scroll_y)
        self.coords(self._subtitle, self.MARGIN, 72 - self.scroll_y)

        rects = []
        inset = self.INSET
        y = self.HEADER_H - self.scroll_y
        for widgets, wins, weights in self.rows:
            available = w - 2 * self.MARGIN - self.GAP * (len(widgets) - 1)
            total = sum(weights)
            x = self.MARGIN
            col_ws = []
            for widget, win, weight in zip(widgets, wins, weights):
                col_w = int(available * weight / total)
                col_ws.append(col_w)
                self.coords(win, x + inset, y + inset)
                self.itemconfigure(win, width=col_w - 2 * inset)
                widget.update_idletasks()
                x += col_w + self.GAP
            content_h = max(widget.winfo_reqheight() for widget in widgets)
            x = self.MARGIN
            for win, col_w in zip(wins, col_ws):
                self.itemconfigure(win, height=content_h)
                rects.append((x, y, col_w, content_h + 2 * inset))
                x += col_w + self.GAP
            y += content_h + 2 * inset + self.GAP

        self._content_h = y + self.scroll_y - self.GAP + self.BOTTOM_PAD
        self._update_bar(h)

        key = (w, h, tuple(rects))
        if key != self._last_key:  # on ne redessine le fond que si quelque chose a changé
            self._last_key = key
            self._photo = ImageTk.PhotoImage(make_page_image(w, h, self.mode, key[2]))
            self.itemconfigure(self._bg_item, image=self._photo)
            self.tag_lower(self._bg_item)