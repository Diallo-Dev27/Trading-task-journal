"""Reusable components: cards, form fields, buttons, tables, badges."""
from tkinter import ttk

import customtkinter as ctk

from ui.theme import FONT, STATUS


# ---------- cards and text ----------
def card(master, theme):
    # flat frame: the rounded shape is drawn by Page (see background.py)
    return ctk.CTkFrame(master, fg_color=theme["card"], bg_color=theme["card"],
                        corner_radius=0, border_width=0)


def card_title(parent, theme, text, pady=(16, 8)):
    lbl = ctk.CTkLabel(parent, text=text, font=(FONT, 16, "bold"), text_color=theme["text"])
    lbl.pack(anchor="w", padx=20, pady=pady)
    return lbl


def muted(master, theme, text, wraplength=420, size=12):
    return ctk.CTkLabel(master, text=text, font=(FONT, size), text_color=theme["text_secondary"],
                        justify="left", anchor="w", wraplength=wraplength)


def stat_card(master, theme, value, label, color=None):
    c = card(master, theme)
    ctk.CTkLabel(c, text=value, font=(FONT, 23, "bold"),
                 text_color=color or theme["text"]).pack(anchor="w", padx=16, pady=(14, 0))
    ctk.CTkLabel(c, text=label, font=(FONT, 12),
                 text_color=theme["text_secondary"]).pack(anchor="w", padx=16, pady=(0, 14))
    return c


def badge(master, text, kind, width=88):
    fg, bg = STATUS[kind]
    return ctk.CTkLabel(master, text=text, width=width, height=24, corner_radius=12,
                        fg_color=bg, text_color=fg, font=(FONT, 11, "bold"))


# ---------- inputs ----------
def entry(master, theme, value="", placeholder=None):
    e = ctk.CTkEntry(master, height=34, corner_radius=8, fg_color=theme["input"],
                     border_color=theme["card_border"], text_color=theme["text"],
                     placeholder_text=placeholder)
    if value:
        e.insert(0, value)
    return e


def option(master, theme, values, value=None, command=None):
    m = ctk.CTkOptionMenu(
        master, values=list(values), height=34, corner_radius=8, anchor="w",
        fg_color=theme["input"], button_color=theme["card_border"],
        button_hover_color=theme["accent_soft"], text_color=theme["text"],
        dropdown_fg_color=theme["card"], dropdown_text_color=theme["text"],
        dropdown_hover_color=theme["accent_soft"], font=(FONT, 13), dropdown_font=(FONT, 13),
        command=command)
    m.set(value if value is not None else list(values)[0])
    return m


def textbox(master, theme, height=70, value=""):
    tb = ctk.CTkTextbox(master, height=height, corner_radius=8, fg_color=theme["input"],
                        border_width=1, border_color=theme["card_border"],
                        text_color=theme["text"], font=(FONT, 13))
    if value:
        tb.insert("1.0", value)
    return tb


def field(parent, theme, row, col, text, widget, colspan=1):
    """Label above a widget, on a 2-rows-per-field grid."""
    ctk.CTkLabel(parent, text=text, font=(FONT, 12), text_color=theme["text_secondary"],
                 anchor="w").grid(row=row * 2, column=col, columnspan=colspan,
                                  sticky="w", pady=(10, 3))
    widget.grid(row=row * 2 + 1, column=col, columnspan=colspan, sticky="ew",
                padx=(0, 12) if col + colspan < 3 else 0)


def button(master, theme, text, command, kind="primary", width=120, height=34):
    colors = {
        "primary": (theme["accent"], theme["accent_hover"], theme["on_accent"]),
        "secondary": (theme["card_border"], theme["accent_soft"], theme["text"]),
        "danger": (STATUS["danger"][1], "#4B2028", STATUS["danger"][0]),
    }
    fg, hover, txt = colors[kind]
    return ctk.CTkButton(master, text=text, command=command, width=width, height=height,
                         corner_radius=9, fg_color=fg, hover_color=hover, text_color=txt,
                         font=(FONT, 13, "bold"))


# ---------- table ----------
def apply_ttk_style(theme):
    s = ttk.Style()
    s.theme_use("clam")
    s.configure("Treeview", background=theme["card"], fieldbackground=theme["card"],
                foreground=theme["text"], rowheight=30, borderwidth=0, font=(FONT, 11),
                bordercolor=theme["card"], lightcolor=theme["card"], darkcolor=theme["card"])
    s.map("Treeview", background=[("selected", theme["accent_soft"])],
          foreground=[("selected", theme["accent_text"])])
    s.configure("Treeview.Heading", background=theme["input"], foreground=theme["text_secondary"],
                relief="flat", borderwidth=0, font=(FONT, 11, "bold"))
    s.map("Treeview.Heading", background=[("active", theme["card_border"])])


def make_table(master, theme, columns, height=10):
    """columns = [(id, heading, width, anchor)]. Returns (frame, tree)."""
    frame = ctk.CTkFrame(master, fg_color="transparent")
    tree = ttk.Treeview(frame, columns=[c[0] for c in columns], show="headings",
                        height=height, selectmode="browse")
    for cid, heading, width, anchor in columns:
        tree.heading(cid, text=heading)
        tree.column(cid, width=width, anchor=anchor, stretch=True)
    scroll = ctk.CTkScrollbar(frame, command=tree.yview, fg_color="transparent",
                              button_color=theme["card_border"],
                              button_hover_color=theme["accent_soft"])
    tree.configure(yscrollcommand=scroll.set)
    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y", padx=(4, 0))
    tree.tag_configure("success", foreground=STATUS["success"][0])
    tree.tag_configure("warning", foreground=STATUS["warning"][0])
    tree.tag_configure("danger", foreground=STATUS["danger"][0])
    return frame, tree
