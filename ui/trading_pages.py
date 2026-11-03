"""Trading mode pages: Dashboard, Journal, Add Trade, Asset Analysis."""
from datetime import date, datetime
from tkinter import filedialog, messagebox

import customtkinter as ctk

from core.trades_service import (ALL_ASSETS, ASSETS, DIRECTIONS, EMOTIONS, STRATEGIES,
                                 estimate_profit)
from ui import charts
from ui import widgets as w
from ui.calendar_widget import MonthGrid, date_field
from ui.page import Page
from ui.theme import FONT, GAIN, LOSS, STATUS, THEMES

T = THEMES["trading"]


def money(value):
    return f"{value:+,.0f} $"


def pnl_color(value):
    return GAIN if value > 0 else LOSS if value < 0 else T["text"]


def _chart_card(page, title, chart_fn, *args, **kwargs):
    c = w.card(page, T)
    w.card_title(c, T, title)
    chart_fn(c, T, *args, **kwargs).pack(fill="both", expand=True, padx=12, pady=(0, 12))
    return c


# =====================================================================
# DASHBOARD
# =====================================================================
def dashboard_page(ctx, master):
    trades = ctx.trades
    st = trades.stats()
    page = Page(master, "trading", "Trading Dashboard", f"Hello {ctx.name}, here is your progress.")

    n = st["n"]
    pf = st["profit_factor"]
    pf_text = "-" if pf is None else "∞" if pf == float("inf") else f"{pf:.2f}"
    if st["streak"]:
        word = ("win" if st["streak_kind"] == "win" else "loss") + ("s" if st["streak"] > 1 else "")
        streak_text = f"{st['streak']} {word}"
    else:
        streak_text = "-"
    page.add_row([
        w.stat_card(page, T, money(st["total"]) if n else "0 $", "Total profit",
                    pnl_color(st["total"]) if n else None),
        w.stat_card(page, T, f"{st['win_rate']:.0f} %" if n else "-", f"Win rate · {n} trades"),
        w.stat_card(page, T, pf_text, "Profit factor"),
        w.stat_card(page, T, f"-{st['max_dd']:.1f} %" if st["max_dd"] else "0 %", "Max drawdown",
                    LOSS if st["max_dd"] else None),
        w.stat_card(page, T, streak_text, "Current streak", T["accent"] if st["streak"] else None),
    ])

    equity = _chart_card(page, "Equity Curve", charts.equity_chart, st["equity"])

    cal = w.card(page, T)
    w.card_title(cal, T, "P&L Calendar")

    def info(year, month):
        return {d: (f"{p:+.0f}", "success" if p > 0 else "danger" if p < 0 else None)
                for d, p in trades.month_pnl(year, month).items()}

    MonthGrid(cal, T, info_fn=info, cell_h=38).pack(fill="x", padx=14, pady=(0, 14))
    page.add_row([equity, cal], weights=[3, 2])

    daily = _chart_card(page, "Daily P&L (last 20 days)", charts.daily_bars,
                        trades.daily_pnl()[-20:])

    recent = w.card(page, T)
    w.card_title(recent, T, "Recent Trades")
    rows = trades.recent(6)
    if not rows:
        w.muted(recent, T, "No trades yet. Log your first one to fill the dashboard.",
                wraplength=300).pack(anchor="w", padx=20, pady=(0, 10))
        w.button(recent, T, "+ Add trade", lambda: ctx.navigate("add_trade"), width=110,
                 height=32).pack(anchor="w", padx=20, pady=(0, 18))
    for t in rows:
        row = ctk.CTkFrame(recent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=4)
        row.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(row, text=t["asset"], font=(FONT, 13, "bold"), text_color=T["text"],
                     width=70, anchor="w").grid(row=0, column=0)
        ctk.CTkLabel(row, text=f"{t['direction']} · {t['date'][5:]}", font=(FONT, 12),
                     text_color=T["text_muted"], anchor="w").grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(row, text=money(t["profit"]), font=(FONT, 13, "bold"),
                     text_color=pnl_color(t["profit"]), anchor="e").grid(row=0, column=2)
    if rows:
        ctk.CTkFrame(recent, fg_color="transparent", height=10).pack()
    page.add_row([daily, recent], weights=[3, 2])
    return page


# =====================================================================
# JOURNAL
# =====================================================================
COLUMNS = [("date", "Date", 90, "center"), ("asset", "Asset", 80, "center"),
           ("dir", "Side", 60, "center"), ("entry", "Entry", 90, "e"),
           ("exit", "Exit", 90, "e"), ("size", "Size", 60, "e"),
           ("profit", "Profit", 90, "e"), ("strategy", "Strategy", 130, "w"),
           ("emotion", "Emotion", 90, "w")]


def _fmt(v):
    return "" if v is None else f"{v:g}"


def journal_page(ctx, master):
    page = Page(master, "trading", "Trading Journal", "Every trade you logged, with its result.")

    bar = w.card(page, T)
    inner = ctk.CTkFrame(bar, fg_color="transparent")
    inner.pack(fill="x", padx=20, pady=14)
    ctk.CTkLabel(inner, text="Asset", font=(FONT, 12), text_color=T["text_secondary"]).pack(side="left")
    asset_menu = w.option(inner, T, ["All"] + ALL_ASSETS, "All", command=lambda _v: refresh())
    asset_menu.configure(width=130)
    asset_menu.pack(side="left", padx=8)
    count = ctk.CTkLabel(inner, text="", font=(FONT, 12), text_color=T["text_muted"])
    count.pack(side="left", padx=8)
    page.add_row([bar])

    box = w.card(page, T)
    frame, tree = w.make_table(box, T, COLUMNS, height=12)
    frame.pack(fill="both", expand=True, padx=16, pady=(16, 8))
    actions = ctk.CTkFrame(box, fg_color="transparent")
    actions.pack(fill="x", padx=16, pady=(0, 16))

    def refresh():
        tree.delete(*tree.get_children())
        for t in ctx.trades.all(asset_menu.get()):
            tag = "success" if t["profit"] > 0 else "danger" if t["profit"] < 0 else ""
            tree.insert("", "end", iid=str(t["id"]), tags=(tag,),
                        values=(t["date"], t["asset"], t["direction"], _fmt(t["entry"]),
                                _fmt(t["exit_price"]), _fmt(t["size"]), money(t["profit"]),
                                t["strategy"] or "", t["emotion"] or ""))
        count.configure(text=f"{len(tree.get_children())} trades")

    def delete():
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Select a trade", "Click a trade in the list first.")
        elif messagebox.askyesno("Delete trade", "Delete this trade?"):
            ctx.trades.delete(int(sel[0]))
            refresh()

    def export():
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="trades.csv",
                                            filetypes=[("CSV file", "*.csv")])
        if path:
            n = ctx.trades.export_csv(path)
            messagebox.showinfo("Export done", f"{n} trades exported.")

    w.button(actions, T, "+ Add trade", lambda: ctx.navigate("add_trade"), width=110,
             height=32).pack(side="left")
    w.button(actions, T, "Export CSV", export, kind="secondary", width=100,
             height=32).pack(side="left", padx=8)
    w.button(actions, T, "Delete selected", delete, kind="danger", width=130,
             height=32).pack(side="left")
    refresh()
    page.add_row([box])
    return page


# =====================================================================
# ADD TRADE
# =====================================================================
def _num(text, name, required=False):
    text = text.strip().replace(",", ".")
    if not text:
        if required:
            raise ValueError(f"{name} is required.")
        return None
    try:
        return float(text)
    except ValueError:
        raise ValueError(f"{name} must be a number.") from None


def add_trade_page(ctx, master):
    page = Page(master, "trading", "Add Trade", "Log a trade right after you close it.")
    form = w.card(page, T)
    body = ctk.CTkFrame(form, fg_color="transparent")
    body.pack(fill="x", padx=20, pady=(8, 6))
    for c in range(3):
        body.grid_columnconfigure(c, weight=1, uniform="f")

    date_frame, e_date = date_field(body, T, date.today().isoformat())
    w.field(body, T, 0, 0, "Date", date_frame)
    o_asset = w.option(body, T, ALL_ASSETS, ALL_ASSETS[0])
    w.field(body, T, 0, 1, "Asset", o_asset)
    o_dir = w.option(body, T, DIRECTIONS, "Buy")
    w.field(body, T, 0, 2, "Direction", o_dir)
    e_entry = w.entry(body, T)
    w.field(body, T, 1, 0, "Entry price", e_entry)
    e_sl = w.entry(body, T)
    w.field(body, T, 1, 1, "Stop loss", e_sl)
    e_tp = w.entry(body, T)
    w.field(body, T, 1, 2, "Take profit", e_tp)
    e_exit = w.entry(body, T)
    w.field(body, T, 2, 0, "Exit price", e_exit)
    e_size = w.entry(body, T)
    w.field(body, T, 2, 1, "Size (lots / quantity)", e_size)
    e_profit = w.entry(body, T, placeholder="e.g. 85 or -40")
    w.field(body, T, 2, 2, "Profit ($)", e_profit)
    o_strat = w.option(body, T, STRATEGIES, STRATEGIES[0])
    w.field(body, T, 3, 0, "Strategy", o_strat)
    o_emo = w.option(body, T, EMOTIONS, "Calm")
    w.field(body, T, 3, 1, "Emotion", o_emo)
    e_notes = w.textbox(body, T, 70)
    w.field(body, T, 4, 0, "Notes", e_notes, colspan=3)

    w.muted(form, T, "Profit: copy the real result from your platform. If you leave it empty, "
                     "it is estimated as (exit - entry) x size, which can be inaccurate for some "
                     "contracts.", wraplength=700).pack(anchor="w", padx=20, pady=(10, 0))
    msg = ctk.CTkLabel(form, text="", font=(FONT, 12), text_color=STATUS["danger"][0], anchor="w")
    msg.pack(anchor="w", padx=20, pady=(6, 0))

    def save():
        try:
            day = datetime.strptime(e_date.get().strip(), "%Y-%m-%d").date().isoformat()
            entry = _num(e_entry.get(), "Entry price")
            sl, tp = _num(e_sl.get(), "Stop loss"), _num(e_tp.get(), "Take profit")
            exit_p = _num(e_exit.get(), "Exit price")
            size = _num(e_size.get(), "Size")
            profit = _num(e_profit.get(), "Profit")
            if profit is None:
                if None in (entry, exit_p, size):
                    raise ValueError("Enter the profit, or entry + exit + size to estimate it.")
                profit = estimate_profit(o_dir.get(), entry, exit_p, size)
        except ValueError as err:
            text = str(err)
            msg.configure(text="Date must look like 2026-10-25." if "does not match" in text else text)
            return

        today_count = ctx.trades.count_on(day)
        limit = ctx.trades.max_per_day
        if today_count >= limit and not messagebox.askyesno(
                "Discipline alert",
                f"You already logged {today_count} trades on {day} (your limit is {limit}).\n\n"
                "Save this one anyway?"):
            return
        ctx.trades.add(day, o_asset.get(), o_dir.get(), entry, sl, tp, exit_p, size, profit,
                       o_strat.get(), o_emo.get(), e_notes.get("1.0", "end").strip())
        ctx.navigate("journal")

    btns = ctk.CTkFrame(form, fg_color="transparent")
    btns.pack(anchor="w", padx=20, pady=(8, 18))
    w.button(btns, T, "Save Trade", save, width=130, height=38).pack(side="left")
    w.button(btns, T, "Cancel", lambda: ctx.navigate("dashboard"), kind="secondary",
             width=100, height=38).pack(side="left", padx=10)
    page.add_row([form])
    return page


# =====================================================================
# ASSET ANALYSIS
# =====================================================================
def analysis_page(ctx, master):
    t = ctx.trades
    st = t.stats()
    page = Page(master, "trading", "Asset Analysis", "Where do you actually make (or lose) money?")
    page.add_row([
        _chart_card(page, "Profit by asset", charts.bars_by, t.by_asset()),
        _chart_card(page, "Profit by asset class", charts.bars_by, t.by_class(), horizontal=False),
    ])
    page.add_row([
        _chart_card(page, "Wins vs losses", charts.win_loss_pie, st["wins"], st["losses"],
                    st["breakeven"]),
        _chart_card(page, "Profit by emotion", charts.bars_by, t.by_emotion()),
    ])
    summary = w.card(page, T)
    w.card_title(summary, T, "Best and worst trade")
    line = ctk.CTkFrame(summary, fg_color="transparent")
    line.pack(anchor="w", padx=20, pady=(0, 16))
    if st["n"]:
        ctk.CTkLabel(line, text=f"Best  {money(st['best'])}", font=(FONT, 14, "bold"),
                     text_color=GAIN).pack(side="left")
        ctk.CTkLabel(line, text=f"Worst  {money(st['worst'])}", font=(FONT, 14, "bold"),
                     text_color=LOSS).pack(side="left", padx=24)
        classes = " · ".join(f"{k}: {', '.join(v)}" for k, v in ASSETS.items())
        w.muted(summary, T, classes, wraplength=800).pack(anchor="w", padx=20, pady=(0, 14))
    else:
        w.muted(line, T, "No trades yet.").pack(side="left")
    page.add_row([summary])
    return page
