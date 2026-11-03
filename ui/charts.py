"""matplotlib charts embedded in Tkinter, styled to match the cards."""
import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402

from ui.theme import GAIN, LOSS  # noqa: E402


def _new(theme, height=2.4, margins=(0.12, 0.97, 0.95, 0.18)):
    """margins = (gauche, droite, haut, bas). Des marges fixes sont bien plus rapides que
    constrained_layout, qui remesure tous les textes plusieurs fois."""
    fig = Figure(figsize=(5, height), dpi=100, facecolor=theme["card"])
    fig.subplots_adjust(left=margins[0], right=margins[1], top=margins[2], bottom=margins[3])
    ax = fig.add_subplot(111)
    ax.set_facecolor(theme["card"])
    ax.tick_params(colors=theme["text_muted"], labelsize=8)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(theme["card_border"])
    ax.grid(True, color=theme["card_border"], linewidth=0.6, alpha=0.6)
    ax.set_axisbelow(True)
    return fig, ax


def _embed(parent, fig, theme):
    widget = FigureCanvasTkAgg(fig, master=parent).get_tk_widget()
    widget.configure(bg=theme["card"], highlightthickness=0)
    return widget


def _empty(fig, ax, theme, text="No trades yet"):
    ax.clear()
    ax.set_facecolor(theme["card"])
    ax.axis("off")
    ax.text(0.5, 0.5, text, ha="center", va="center", color=theme["text_muted"],
            fontsize=10, transform=ax.transAxes)


def _money(value, _pos=None):
    return f"{value:,.0f}"


def equity_chart(parent, theme, equity):
    fig, ax = _new(theme)
    if len(equity) < 2:
        _empty(fig, ax, theme)
    else:
        xs = list(range(len(equity)))
        ax.plot(xs, equity, color=theme["accent"], linewidth=2)
        ax.fill_between(xs, equity, min(equity), color=theme["accent"], alpha=0.12)
        ax.axhline(equity[0], color=theme["text_muted"], linewidth=0.8, linestyle="--")
        ax.set_xlabel("Trade #", color=theme["text_muted"], fontsize=8)
        ax.yaxis.set_major_formatter(_money)
    return _embed(parent, fig, theme)


def daily_bars(parent, theme, daily):
    fig, ax = _new(theme, margins=(0.1, 0.98, 0.95, 0.14))
    if not daily:
        _empty(fig, ax, theme)
    else:
        labels = [d[5:] for d, _ in daily]
        values = [v for _, v in daily]
        ax.bar(range(len(values)), values, color=[GAIN if v >= 0 else LOSS for v in values])
        step = max(1, len(labels) // 8)
        ax.set_xticks(range(0, len(labels), step))
        ax.set_xticklabels(labels[::step], rotation=0)
        ax.axhline(0, color=theme["text_muted"], linewidth=0.8)
        ax.yaxis.set_major_formatter(_money)
    return _embed(parent, fig, theme)


def bars_by(parent, theme, items, horizontal=True):
    """items = [(label, pnl)]."""
    fig, ax = _new(theme, margins=(0.2, 0.96, 0.95, 0.12) if horizontal else (0.12, 0.98, 0.95, 0.14))
    if not items:
        _empty(fig, ax, theme)
    else:
        labels = [k for k, _ in items]
        values = [v for _, v in items]
        colors = [GAIN if v >= 0 else LOSS for v in values]
        if horizontal:
            ax.barh(labels, values, color=colors)
            ax.xaxis.set_major_formatter(_money)
            ax.axvline(0, color=theme["text_muted"], linewidth=0.8)
        else:
            ax.bar(labels, values, color=colors)
            ax.yaxis.set_major_formatter(_money)
            ax.axhline(0, color=theme["text_muted"], linewidth=0.8)
    return _embed(parent, fig, theme)


def win_loss_pie(parent, theme, wins, losses, breakeven):
    fig, ax = _new(theme, margins=(0.1, 0.9, 0.92, 0.08))
    ax.grid(False)
    values = [wins, losses, breakeven]
    if sum(values) == 0:
        _empty(fig, ax, theme)
    else:
        labels, sizes, colors = [], [], []
        for name, n, color in (("Wins", wins, GAIN), ("Losses", losses, LOSS),
                               ("Break-even", breakeven, "#94A3B8")):
            if n:
                labels.append(f"{name} ({n})")
                sizes.append(n)
                colors.append(color)
        for side in ("left", "bottom"):
            ax.spines[side].set_visible(False)
        ax.pie(sizes, labels=labels, colors=colors, autopct="%1.0f%%", startangle=90,
               textprops={"color": theme["text"], "fontsize": 9},
               wedgeprops={"edgecolor": theme["card"], "linewidth": 2})
    return _embed(parent, fig, theme)
