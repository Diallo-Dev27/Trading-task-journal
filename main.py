"""Trading Planner: Daily Task Reminder + Trading Journal.

Run with:  python main.py
"""
import sys
import time
import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

from core.database import Database
from ui import screens
from ui import widgets
from ui.context import Context
from ui.popups import ReminderPopup
from ui.sidebar import Sidebar
from ui.theme import MENUS, THEMES

REMINDER_CHECK_MS = 15_000
CACHEABLE = {"home", "tasks", "calendar", "dashboard", "journal", "analysis"}  # pages sans formulaire
CACHE_SECONDS = 60  # une page gardée plus longtemps est reconstruite (les statuts des tâches dépendent de l'heure)


class App(ctk.CTk):
    def __init__(self, db_path=None):
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.title("Daily Task Reminder & Trading Journal")
        self.geometry("1240x740")
        self.minsize(1060, 680)

        self.db = Database(db_path) if db_path else Database()
        self.ctx = Context(self, self.db)
        self.mode = None
        self.current = None
        self.current_key = None
        self.current_kwargs = {}
        self.cache = {}

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.sidebar = Sidebar(self, on_mode=self.set_mode, on_nav=self.navigate)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.content = tk.Frame(self, bd=0, highlightthickness=0)
        self.content.grid(row=0, column=1, sticky="nsew")

        # mouse wheel scrolls the current page
        self.bind_all("<Enter>", self._focus_page)

        self.bind_all("<Prior>", lambda e: self._page_key(-0.9))   # PageUp
        self.bind_all("<Next>", lambda e: self._page_key(0.9))     # PageDown

        self.set_mode("productivity")
        self.after(200, self._maximize)
        self.after(1500, self.check_reminders)

    def _maximize(self):
        try:
            if sys.platform == "win32":
                self.state("zoomed")
            else:
                self.attributes("-zoomed", True)
        except tk.TclError:
            pass

    def _page_key(self, fraction):
        if self.current is not None:
            self.current.scroll_by(self.current.winfo_height() * fraction)

    # ---------- modes and navigation ----------
    def set_mode(self, mode):
        if mode == self.mode:
            return
        self.mode = mode
        theme = THEMES[mode]
        self.configure(fg_color=theme["bg"])
        self.content.configure(bg=theme["bg"])
        widgets.apply_ttk_style(theme)
        self.sidebar.apply_mode(mode)
        self._show(MENUS[mode][0][0], {})
    def navigate(self, key, **kwargs):
        self._show(key, kwargs)

    def reload(self):
        self._show(self.current_key, self.current_kwargs)

    def _show(self, key, kwargs):
        old = self.current
        self.current_key, self.current_kwargs = key, kwargs
        cacheable = key in CACHEABLE and not kwargs
        slot = (self.mode, key)

        page = None
        if cacheable:
            hit = self.cache.get(slot)
            if hit and hit[0] == self.db.version and time.time() - hit[1] < CACHE_SECONDS:
                page = hit[2]                       # rien n'a changé : on réutilise la page
        if page is None:
            page = screens.build(self.ctx, self.mode, key, self.content, **kwargs)
            page.cached = cacheable
            if cacheable:
                stale = self.cache.get(slot)
                if stale and stale[2] is not old:
                    stale[2].destroy()              # cachée et périmée : on la libère
                self.cache[slot] = (self.db.version, time.time(), page)

        page.place(x=0, y=0, relwidth=1, relheight=1)
        page.layout_now()                           # positions finales avant tout affichage
        self.current = page
        self.sidebar.highlight(key)
        page.focus_set()

        if old is not None and old is not page:
            if self._is_cached(old):
                old.place_forget()                  # on la garde cachée pour la prochaine visite
            else:
                self.after(250, old.destroy)        # on la supprime quand la nouvelle est affichée

    def _is_cached(self, page):
        return any(entry[2] is page for entry in self.cache.values())

    def _focus_page(self, _event=None):
        #Windows envoie la molette au widget qui a le focus. Si personne ne l'a, on le donne à la page pour que la molette marche toujours."""
        if self.current is not None and self.focus_get() is None:
            self.current.focus_set()

    def _on_wheel(self, event):
        print("wheel:", event.widget, event.num, event.delta)
        if self.current is None:
            return
        widget = event.widget
        # un tableau qui a plus de lignes que visibles défile lui-même ; sinon on fait défiler la page
        if isinstance(widget, ttk.Treeview) and len(widget.get_children()) > int(widget.cget("height")):
            return
        if event.num == 4:         
            notches = -1
        elif event.num == 5:        
            notches = 1
        else:                       
            delta = getattr(event, "delta", 0)
            if delta == 0:
                return
            notches = -max(abs(delta) / 120, 0.25) * (1 if delta > 0 else -1)
        self.current.scroll_by(notches * self.current.SCROLL_STEP)

    # ---------- reminders ----------
    def check_reminders(self):
        try:
            for task in self.ctx.tasks.due_reminders():
                self.ctx.tasks.mark_notified(task["id"])
                self.bell()
                if sys.platform == "win32":
                    import winsound
                    winsound.MessageBeep()
                ReminderPopup(self, self.ctx, task)
        finally:
            self.after(REMINDER_CHECK_MS, self.check_reminders)


if __name__ == "__main__":
    App().mainloop()
