"""Trade logic: add / delete, statistics, groupings for the charts, CSV export."""
import csv
from datetime import date

ASSETS = {
    "Forex": ["USDJPY", "EURUSD", "AUDUSD", "GBPUSD", "EURAUD"],
    "Indices": ["US30", "NAS100", "SP500"],
    "Metals": ["XAUUSD", "XAGUSD"],
    "Crypto": ["BTCUSD"],
}
ALL_ASSETS = [a for group in ASSETS.values() for a in group]
STRATEGIES = ["Breakout", "Trend following", "Reversal", "Support / Resistance", "News", "Other"]
EMOTIONS = ["Calm", "Confident", "Hesitant", "FOMO", "Fear", "Revenge", "Bored"]
DIRECTIONS = ["Buy", "Sell"]


def asset_class(asset):
    for name, items in ASSETS.items():
        if asset in items:
            return name
    return "Other"


def estimate_profit(direction, entry, exit_price, size):
    """Rough estimate (exit - entry) x size. Real profit depends on the contract size."""
    sign = 1 if direction == "Buy" else -1
    return round((exit_price - entry) * size * sign, 2)


class TradeService:
    def __init__(self, db):
        self.db = db

    # ---------- settings ----------
    @property
    def capital(self):
        try:
            return float(self.db.get_setting("capital", "1000"))
        except ValueError:
            return 1000.0

    @property
    def max_per_day(self):
        try:
            return int(self.db.get_setting("max_trades_day", "3"))
        except ValueError:
            return 3

    # ---------- CRUD ----------
    def add(self, date, asset, direction, entry, sl, tp, exit_price, size, profit,
            strategy, emotion, notes):
        return self.db.execute(
            "INSERT INTO trades (date, asset, asset_class, direction, entry, sl, tp, exit_price, "
            "size, profit, strategy, emotion, notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (date, asset, asset_class(asset), direction, entry, sl, tp, exit_price, size,
             profit, strategy, emotion, notes))

    def delete(self, trade_id):
        self.db.execute("DELETE FROM trades WHERE id=?", (trade_id,))

    def all(self, asset=None):
        if asset and asset != "All":
            return self.db.query(
                "SELECT * FROM trades WHERE asset=? ORDER BY date DESC, id DESC", (asset,))
        return self.db.query("SELECT * FROM trades ORDER BY date DESC, id DESC")

    def chronological(self):
        return self.db.query("SELECT * FROM trades ORDER BY date, id")

    def recent(self, n=6):
        return self.db.query("SELECT * FROM trades ORDER BY date DESC, id DESC LIMIT ?", (n,))

    def count_on(self, day_iso):
        return self.db.one("SELECT COUNT(*) AS n FROM trades WHERE date=?", (day_iso,))["n"]

    # ---------- statistics ----------
    def stats(self):
        profits = [t["profit"] or 0.0 for t in self.chronological()]
        capital = self.capital
        n = len(profits)
        wins = [p for p in profits if p > 0]
        losses = [p for p in profits if p < 0]
        gross_win, gross_loss = sum(wins), -sum(losses)
        if gross_loss > 0:
            profit_factor = gross_win / gross_loss
        elif gross_win > 0:
            profit_factor = float("inf")
        else:
            profit_factor = None

        equity = [capital]
        for p in profits:
            equity.append(equity[-1] + p)
        peak, max_dd = equity[0], 0.0
        for e in equity:
            peak = max(peak, e)
            if peak > 0:
                max_dd = max(max_dd, (peak - e) / peak * 100)

        streak, kind = 0, None
        for p in reversed(profits):
            k = "win" if p > 0 else "loss" if p < 0 else None
            if k is None or (kind is not None and k != kind):
                break
            kind = k
            streak += 1

        return {
            "n": n, "wins": len(wins), "losses": len(losses),
            "breakeven": n - len(wins) - len(losses),
            "win_rate": len(wins) / n * 100 if n else 0.0,
            "profit_factor": profit_factor, "total": sum(profits),
            "best": max(profits, default=0.0), "worst": min(profits, default=0.0),
            "max_dd": max_dd, "streak": streak, "streak_kind": kind, "equity": equity,
        }

    def daily_pnl(self):
        rows = self.db.query("SELECT date, SUM(profit) AS p FROM trades GROUP BY date ORDER BY date")
        return [(r["date"], r["p"]) for r in rows]

    def _group(self, column):
        rows = self.db.query(
            f"SELECT {column} AS k, SUM(profit) AS p FROM trades "
            f"WHERE {column} IS NOT NULL AND {column} != '' GROUP BY {column} ORDER BY p")
        return [(r["k"], r["p"]) for r in rows]

    def by_asset(self):
        return self._group("asset")

    def by_class(self):
        return self._group("asset_class")

    def by_emotion(self):
        return self._group("emotion")

    def month_pnl(self, year, month):
        prefix = f"{year:04d}-{month:02d}"
        rows = self.db.query(
            "SELECT date, SUM(profit) AS p FROM trades WHERE date LIKE ? GROUP BY date",
            (prefix + "%",))
        return {date.fromisoformat(r["date"]): r["p"] for r in rows}

    # ---------- export ----------
    def export_csv(self, path):
        rows = self.chronological()
        cols = ["date", "asset", "asset_class", "direction", "entry", "sl", "tp",
                "exit_price", "size", "profit", "strategy", "emotion", "notes"]
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(cols)
            for r in rows:
                writer.writerow([r[c] for c in cols])
        return len(rows)
