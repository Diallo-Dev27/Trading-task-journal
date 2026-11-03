"""Optional demo data (Settings > Load demo data) to see the dashboard filled."""
import random
from datetime import date, datetime, timedelta

from core.tasks_service import FMT
from core.trades_service import ALL_ASSETS, EMOTIONS, STRATEGIES

BASE_PRICE = {
    "USDJPY": 150.0, "EURUSD": 1.08, "AUDUSD": 0.65, "GBPUSD": 1.27, "EURAUD": 1.65,
    "US30": 39000, "NAS100": 18000, "SP500": 5200, "XAUUSD": 2350, "XAGUSD": 28,
    "BTCUSD": 65000,
}


def load_demo(tasks, trades):
    rnd = random.Random(11)
    weights = [3 if a in ("EURUSD", "XAUUSD", "NAS100", "GBPUSD") else 1 for a in ALL_ASSETS]
    today = date.today()

    for back in range(60, -1, -1):
        day = today - timedelta(days=back)
        if day.weekday() >= 5:
            continue
        for _ in range(rnd.choice([0, 1, 1, 2, 2, 3])):
            asset = rnd.choices(ALL_ASSETS, weights=weights)[0]
            win = rnd.random() < 0.58
            profit = round(rnd.uniform(40, 180), 2) if win else -round(rnd.uniform(30, 110), 2)
            direction = rnd.choice(["Buy", "Sell"])
            digits = 5 if BASE_PRICE[asset] < 10 else 2
            entry = round(BASE_PRICE[asset] * (1 + rnd.uniform(-0.004, 0.004)), digits)
            move = BASE_PRICE[asset] * 0.0015 * rnd.uniform(0.6, 1.4)
            sign = 1 if (profit > 0) == (direction == "Buy") else -1
            emotion = "FOMO" if (not win and rnd.random() < 0.5) else rnd.choice(EMOTIONS)
            trades.add(day.isoformat(), asset, direction, entry, None, None,
                       round(entry + sign * move, digits), round(rnd.uniform(0.1, 1.0), 2),
                       profit, rnd.choice(STRATEGIES), emotion, "Demo trade")

    now = datetime.now()
    demo_tasks = [
        ("Study Data Mining", now.replace(hour=9, minute=0), "High", "Study", "None"),
        ("Prepare lab report", now.replace(hour=11, minute=0), "Medium", "Study", "None"),
        ("Gym training", now.replace(hour=14, minute=0), "Low", "Sport", "Daily"),
        ("Work on Python project", now.replace(hour=17, minute=0), "High", "Project", "None"),
        ("Submit assignment", now - timedelta(days=1), "High", "Study", "None"),
    ]
    for title, due, priority, category, repeat in demo_tasks:
        tasks.add(title, "Demo task", due.strftime(FMT), priority, category, repeat)
