"""Task logic: add / edit / delete, recurrence, snooze, reminders and statistics."""
from datetime import date, datetime, timedelta

FMT = "%Y-%m-%d %H:%M"
PRIORITIES = ["High", "Medium", "Low"]
CATEGORIES = ["Study", "Project", "Sport", "Personal", "Trading"]
REPEATS = ["None", "Daily", "Weekly"]
FILTERS = ["All", "Pending", "Completed", "Overdue"]

TRADING_REMINDERS = [
    ("Open your trading journal and log today's trades", "21:00", "Daily"),
    ("London session opens", "09:00", "Daily"),
    ("New York session opens", "14:30", "Daily"),
    ("Weekly trade review", "18:00", "Weekly"),
]


def _now():
    return datetime.now().strftime(FMT)


class TaskService:
    def __init__(self, db):
        self.db = db

    @staticmethod
    def status(task):
        if task["done"]:
            return "Completed"
        return "Overdue" if task["due"] < _now() else "Pending"

    # ---------- CRUD ----------
    def add(self, title, description, due, priority, category, repeat):
        return self.db.execute(
            "INSERT INTO tasks (title, description, due, priority, category, repeat, done, notified) "
            "VALUES (?, ?, ?, ?, ?, ?, 0, 0)",
            (title, description, due, priority, category, repeat))

    def update(self, task_id, title, description, due, priority, category, repeat):
        self.db.execute(
            "UPDATE tasks SET title=?, description=?, due=?, priority=?, category=?, repeat=?, "
            "notified=0 WHERE id=?",
            (title, description, due, priority, category, repeat, task_id))

    def delete(self, task_id):
        self.db.execute("DELETE FROM tasks WHERE id=?", (task_id,))

    def get(self, task_id):
        return self.db.one("SELECT * FROM tasks WHERE id=?", (task_id,))

    def all(self, search="", status="All"):
        search = search.strip().lower()
        out = []
        for t in self.db.query("SELECT * FROM tasks ORDER BY done, due"):
            if status != "All" and self.status(t) != status:
                continue
            text = f"{t['title']} {t['description'] or ''} {t['category']}".lower()
            if search and search not in text:
                continue
            out.append(t)
        return out

    # ---------- actions ----------
    def toggle_done(self, task_id):
        t = self.get(task_id)
        if t is None:
            return
        new = 0 if t["done"] else 1
        self.db.execute("UPDATE tasks SET done=? WHERE id=?", (new, task_id))
        if new and t["repeat"] != "None":
            self._spawn_next(t)

    def _spawn_next(self, t):
        step = timedelta(days=1 if t["repeat"] == "Daily" else 7)
        due = datetime.strptime(t["due"], FMT) + step
        while due <= datetime.now():
            due += step
        due_s = due.strftime(FMT)
        if self.db.one("SELECT id FROM tasks WHERE title=? AND due=?", (t["title"], due_s)):
            return
        self.add(t["title"], t["description"], due_s, t["priority"], t["category"], t["repeat"])

    def snooze(self, task_id, minutes=10):
        due = (datetime.now() + timedelta(minutes=minutes)).strftime(FMT)
        self.db.execute("UPDATE tasks SET due=?, notified=0, done=0 WHERE id=?", (due, task_id))

    # ---------- reminders ----------
    def due_reminders(self):
        return self.db.query(
            "SELECT * FROM tasks WHERE done=0 AND notified=0 AND due<=? ORDER BY due", (_now(),))

    def mark_notified(self, task_id):
        self.db.execute("UPDATE tasks SET notified=1 WHERE id=?", (task_id,))

    def next_reminder(self):
        return self.db.one(
            "SELECT * FROM tasks WHERE done=0 AND due>? ORDER BY due LIMIT 1", (_now(),))

    def add_trading_reminders(self):
        """Adds the standard trading reminders (skips the ones that already exist)."""
        created = 0
        for title, hhmm, repeat in TRADING_REMINDERS:
            if self.db.one("SELECT id FROM tasks WHERE title=? AND category='Trading'", (title,)):
                continue
            h, m = map(int, hhmm.split(":"))
            due = datetime.now().replace(hour=h, minute=m, second=0, microsecond=0)
            if repeat == "Weekly":
                due += timedelta(days=(6 - due.weekday()) % 7)  # next Sunday
            if due <= datetime.now():
                due += timedelta(days=7 if repeat == "Weekly" else 1)
            self.add(title, "Trading routine", due.strftime(FMT), "Medium", "Trading", repeat)
            created += 1
        return created

    # ---------- views and statistics ----------
    def stats(self):
        rows = self.db.query("SELECT done, due FROM tasks")
        now = _now()
        total = len(rows)
        completed = sum(1 for r in rows if r["done"])
        overdue = sum(1 for r in rows if not r["done"] and r["due"] < now)
        return {"total": total, "completed": completed, "overdue": overdue,
                "pending": total - completed - overdue}

    def today_list(self):
        today = date.today().isoformat()
        return self.db.query(
            "SELECT * FROM tasks WHERE substr(due,1,10)=? OR (done=0 AND due<?) "
            "ORDER BY done, due", (today, _now()))

    def tasks_on(self, day_iso):
        return self.db.query(
            "SELECT * FROM tasks WHERE substr(due,1,10)=? ORDER BY due", (day_iso,))

    def counts_by_day(self, year, month):
        """{date: (total, open, overdue)} for the calendar."""
        prefix = f"{year:04d}-{month:02d}"
        now = _now()
        out = {}
        for t in self.db.query("SELECT due, done FROM tasks WHERE due LIKE ?", (prefix + "%",)):
            d = date.fromisoformat(t["due"][:10])
            total, open_, late = out.get(d, (0, 0, 0))
            total += 1
            if not t["done"]:
                open_ += 1
                if t["due"] < now:
                    late += 1
            out[d] = (total, open_, late)
        return out
