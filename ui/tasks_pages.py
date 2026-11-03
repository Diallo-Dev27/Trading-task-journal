"""Productivity mode pages: Home, Add Task, My Tasks, Calendar."""
from datetime import date, datetime, timedelta
from tkinter import messagebox

import customtkinter as ctk

from core.tasks_service import CATEGORIES, FILTERS, FMT, PRIORITIES, REPEATS
from ui import widgets as w
from ui.calendar_widget import MonthGrid, date_field
from ui.page import Page
from ui.theme import FONT, STATUS, THEMES

T = THEMES["productivity"]
KIND = {"Completed": "success", "Pending": "warning", "Overdue": "danger"}


def when_text(due):
    d = datetime.strptime(due, FMT)
    if d.date() == date.today():
        day = "Today"
    elif d.date() == date.today() + timedelta(days=1):
        day = "Tomorrow"
    else:
        day = d.strftime("%d %b")
    return f"{day}, {d:%H:%M}"


def _toggle(ctx, task_id):
    ctx.tasks.toggle_done(task_id)
    ctx.reload()


# =====================================================================
# HOME
# =====================================================================
def _today_row(ctx, parent, t):
    status = ctx.tasks.status(t)
    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.grid_columnconfigure(0, weight=1)
    font = ctk.CTkFont(family=FONT, size=14, overstrike=bool(t["done"]))
    box = ctk.CTkCheckBox(
        row, text=t["title"], font=font,
        text_color=T["text_muted"] if t["done"] else T["text"],
        fg_color=T["accent"], hover_color=T["accent_hover"], border_color=T["text_muted"],
        checkmark_color=T["on_accent"], command=lambda: _toggle(ctx, t["id"]))
    if t["done"]:
        box.select()
    box.grid(row=0, column=0, sticky="w")
    w.badge(row, status, KIND[status]).grid(row=0, column=1, padx=12)
    ctk.CTkLabel(row, text=t["due"][11:], width=48, anchor="e", font=(FONT, 12),
                 text_color=T["text_muted"]).grid(row=0, column=2)
    return row


def home_page(ctx, master):
    tasks = ctx.tasks
    s = tasks.stats()
    page = Page(master, "productivity", f"Welcome, {ctx.name}",
                datetime.now().strftime("%A, %d %B %Y"))
    page.add_row([
        w.stat_card(page, T, str(s["total"]), "Total Tasks", T["accent_text"]),
        w.stat_card(page, T, str(s["completed"]), "Completed", STATUS["success"][0]),
        w.stat_card(page, T, str(s["pending"]), "Pending", STATUS["warning"][0]),
        w.stat_card(page, T, str(s["overdue"]), "Overdue", STATUS["danger"][0]),
    ])

    today = w.card(page, T)
    head = ctk.CTkFrame(today, fg_color="transparent")
    head.pack(fill="x", padx=20, pady=(16, 6))
    ctk.CTkLabel(head, text="Today's Tasks", font=(FONT, 16, "bold"),
                 text_color=T["text"]).pack(side="left")
    w.button(head, T, "+ New task", lambda: ctx.navigate("add"), width=110, height=30).pack(side="right")
    w.button(head, T, "View all", lambda: ctx.navigate("tasks"), kind="secondary",
             width=80, height=30).pack(side="right", padx=8)
    rows = tasks.today_list()
    if not rows:
        w.muted(today, T, "Nothing planned for today. Insert your first reminder."
                ).pack(anchor="w", padx=20, pady=(8, 24))
    for t in rows[:6]:
        _today_row(ctx, today, t).pack(fill="x", padx=20, pady=5)
    ctk.CTkFrame(today, fg_color="transparent", height=10).pack()
    page.add_row([today])

    todays = tasks.tasks_on(date.today().isoformat())
    done_n = sum(1 for t in todays if t["done"])
    pct = done_n / len(todays) if todays else 0

    prog = w.card(page, T)
    w.card_title(prog, T, "Today's Progress")
    ctk.CTkLabel(prog, text=f"{pct * 100:.0f} %", font=(FONT, 26, "bold"),
                 text_color=T["accent_text"]).pack(anchor="w", padx=20)
    bar = ctk.CTkProgressBar(prog, height=10, corner_radius=5, fg_color=T["accent_soft"],
                             progress_color=T["accent"])
    bar.set(pct)
    bar.pack(fill="x", padx=20, pady=(8, 6))
    w.muted(prog, T, f"{done_n} of {len(todays)} tasks completed today" if todays
            else "No tasks scheduled today").pack(anchor="w", padx=20, pady=(0, 18))

    nxt_card = w.card(page, T)
    w.card_title(nxt_card, T, "Next Reminder")
    nxt = tasks.next_reminder()
    if nxt:
        ctk.CTkLabel(nxt_card, text=nxt["title"], font=(FONT, 15, "bold"),
                     text_color=T["text"], anchor="w").pack(anchor="w", padx=20)
        w.muted(nxt_card, T, when_text(nxt["due"])).pack(anchor="w", padx=20, pady=(0, 10))
        btns = ctk.CTkFrame(nxt_card, fg_color="transparent")
        btns.pack(anchor="w", padx=20, pady=(0, 18))
        w.button(btns, T, "Complete", lambda: _toggle(ctx, nxt["id"]), width=100,
                 height=30).pack(side="left")
        w.button(btns, T, "Snooze 10 min",
                 lambda: (tasks.snooze(nxt["id"], 10), ctx.reload()), kind="secondary",
                 width=120, height=30).pack(side="left", padx=8)
    else:
        w.muted(nxt_card, T, "No upcoming reminders.").pack(anchor="w", padx=20, pady=(0, 18))
    page.add_row([prog, nxt_card])
    return page


# =====================================================================
# ADD / EDIT TASK
# =====================================================================
def add_task_page(ctx, master, task_id=None):
    editing = ctx.tasks.get(task_id) if task_id else None
    page = Page(master, "productivity", "Edit Task" if editing else "Add New Task",
                "Set a task and get a reminder at the right time.")
    form = w.card(page, T)
    body = ctk.CTkFrame(form, fg_color="transparent")
    body.pack(fill="x", padx=20, pady=(8, 6))
    for c in range(3):
        body.grid_columnconfigure(c, weight=1, uniform="f")

    if editing:
        due = datetime.strptime(editing["due"], FMT)
    else:
        due = (datetime.now() + timedelta(hours=1)).replace(minute=0, second=0)

    e_title = w.entry(body, T, editing["title"] if editing else "", "e.g. Read Software Engineering notes")
    w.field(body, T, 0, 0, "Task title", e_title, colspan=3)
    e_desc = w.textbox(body, T, 70, editing["description"] if editing else "")
    w.field(body, T, 1, 0, "Description (optional)", e_desc, colspan=3)
    date_frame, e_date = date_field(body, T, due.date().isoformat())
    w.field(body, T, 2, 0, "Date", date_frame)
    e_time = w.entry(body, T, f"{due:%H:%M}")
    w.field(body, T, 2, 1, "Time (24h, HH:MM)", e_time)
    o_prio = w.option(body, T, PRIORITIES, editing["priority"] if editing else "Medium")
    w.field(body, T, 2, 2, "Priority", o_prio)
    o_cat = w.option(body, T, CATEGORIES, editing["category"] if editing else "Study")
    w.field(body, T, 3, 0, "Category", o_cat)
    o_rep = w.option(body, T, REPEATS, editing["repeat"] if editing else "None")
    w.field(body, T, 3, 1, "Repeat", o_rep)

    msg = ctk.CTkLabel(form, text="", font=(FONT, 12), text_color=STATUS["danger"][0], anchor="w")
    msg.pack(anchor="w", padx=20, pady=(8, 0))

    def save():
        title = e_title.get().strip()
        if not title:
            msg.configure(text="Please enter a title.")
            return
        try:
            when = datetime.strptime(f"{e_date.get().strip()} {e_time.get().strip()}", "%Y-%m-%d %H:%M")
        except ValueError:
            msg.configure(text="Date must look like 2026-10-25 and time like 17:30.")
            return
        args = (title, e_desc.get("1.0", "end").strip(), when.strftime(FMT),
                o_prio.get(), o_cat.get(), o_rep.get())
        if editing:
            ctx.tasks.update(editing["id"], *args)
        else:
            ctx.tasks.add(*args)
        ctx.navigate("tasks")

    btns = ctk.CTkFrame(form, fg_color="transparent")
    btns.pack(anchor="w", padx=20, pady=(8, 18))
    w.button(btns, T, "Save", save, width=130, height=38).pack(side="left")
    w.button(btns, T, "Cancel", lambda: ctx.navigate("tasks"), kind="secondary",
             width=100, height=38).pack(side="left", padx=10)
    page.add_row([form])
    return page


# =====================================================================
# MY TASKS
# =====================================================================
COLUMNS = [("title", "Task", 250, "w"), ("date", "Date", 90, "center"),
           ("time", "Time", 60, "center"), ("priority", "Priority", 80, "center"),
           ("category", "Category", 90, "center"), ("repeat", "Repeat", 80, "center"),
           ("status", "Status", 90, "center")]


def my_tasks_page(ctx, master):
    page = Page(master, "productivity", "My Tasks", "Search, filter and manage all your tasks.")

    bar = w.card(page, T)
    inner = ctk.CTkFrame(bar, fg_color="transparent")
    inner.pack(fill="x", padx=20, pady=14)
    search = w.entry(inner, T, placeholder="Search tasks…")
    search.pack(side="left", fill="x", expand=True)
    flt = ctk.CTkSegmentedButton(
        inner, values=FILTERS, fg_color=T["input"], selected_color=T["accent"],
        selected_hover_color=T["accent_hover"], unselected_color=T["input"],
        unselected_hover_color=T["card_border"], text_color=T["text"], font=(FONT, 12),
        height=34, command=lambda _v: refresh())
    flt.set("All")
    flt.pack(side="right", padx=(12, 0))
    page.add_row([bar])

    box = w.card(page, T)
    frame, tree = w.make_table(box, T, COLUMNS, height=11)
    frame.pack(fill="both", expand=True, padx=16, pady=(16, 8))
    actions = ctk.CTkFrame(box, fg_color="transparent")
    actions.pack(fill="x", padx=16, pady=(0, 16))
    count = ctk.CTkLabel(actions, text="", font=(FONT, 12), text_color=T["text_muted"])

    def refresh():
        keep = tree.selection()
        tree.delete(*tree.get_children())
        for t in ctx.tasks.all(search.get(), flt.get()):
            st = ctx.tasks.status(t)
            tree.insert("", "end", iid=str(t["id"]), tags=(KIND[st],),
                        values=(t["title"], t["due"][:10], t["due"][11:], t["priority"],
                                t["category"], t["repeat"], st))
        still = [i for i in keep if tree.exists(i)]
        if still:
            tree.selection_set(still)
        count.configure(text=f"{len(tree.get_children())} tasks")

    def selected():
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Select a task", "Click a task in the list first.")
            return None
        return int(sel[0])

    def complete():
        if (tid := selected()) is not None:
            ctx.tasks.toggle_done(tid)
            refresh()

    def edit():
        if (tid := selected()) is not None:
            ctx.navigate("add", task_id=tid)

    def snooze():
        if (tid := selected()) is not None:
            ctx.tasks.snooze(tid, 10)
            refresh()

    def delete():
        if (tid := selected()) is not None and messagebox.askyesno("Delete task", "Delete this task?"):
            ctx.tasks.delete(tid)
            refresh()

    w.button(actions, T, "Complete / Undo", complete, width=130, height=32).pack(side="left")
    w.button(actions, T, "Edit", edit, kind="secondary", width=70, height=32).pack(side="left", padx=8)
    w.button(actions, T, "Snooze 10 min", snooze, kind="secondary", width=120, height=32).pack(side="left")
    w.button(actions, T, "Delete", delete, kind="danger", width=80, height=32).pack(side="left", padx=8)
    count.pack(side="right")
    search.bind("<KeyRelease>", lambda _e: refresh())
    tree.bind("<Double-1>", lambda _e: edit())
    refresh()
    page.add_row([box])
    return page


# =====================================================================
# CALENDAR
# =====================================================================
def calendar_page(ctx, master):
    page = Page(master, "productivity", "Calendar", "Pick a day to see its tasks.")

    left = w.card(page, T)

    def info(year, month):
        out = {}
        for d, (total, open_, late) in ctx.tasks.counts_by_day(year, month).items():
            out[d] = (str(total), "danger" if late else "warning" if open_ else "success")
        return out

    right = w.card(page, T)
    title = w.card_title(right, T, "")
    body = ctk.CTkFrame(right, fg_color="transparent")
    body.pack(fill="x", padx=20, pady=(0, 16))

    def show_day(d):
        title.configure(text=d.strftime("%A, %d %B"))
        for child in body.winfo_children():
            child.destroy()
        rows = ctx.tasks.tasks_on(d.isoformat())
        if not rows:
            w.muted(body, T, "No tasks on this day.").pack(anchor="w", pady=(4, 10))
        for t in rows:
            st = ctx.tasks.status(t)
            row = ctk.CTkFrame(body, fg_color="transparent")
            row.pack(fill="x", pady=4)
            row.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(row, text=t["due"][11:], width=44, anchor="w", font=(FONT, 12),
                         text_color=T["text_muted"]).grid(row=0, column=0)
            ctk.CTkLabel(row, text=t["title"], anchor="w", font=(FONT, 13),
                         text_color=T["text"]).grid(row=0, column=1, sticky="w")
            w.badge(row, st, KIND[st], width=80).grid(row=0, column=2, padx=6)
            w.button(row, T, "Undo" if t["done"] else "Done",
                     lambda tid=t["id"]: (ctx.tasks.toggle_done(tid), show_day(d), grid.render()),
                     kind="secondary", width=56, height=26).grid(row=0, column=3)
        w.button(body, T, "+ Add task", lambda: ctx.navigate("add"), width=100,
                 height=30).pack(anchor="w", pady=(10, 0))
        page.relayout()

    grid = MonthGrid(left, T, info_fn=info, on_select=show_day, selected=date.today(), cell_h=44)
    grid.pack(fill="x", padx=16, pady=16)
    show_day(date.today())
    page.add_row([left, right], weights=[3, 2])
    return page
