"""Shared objects passed to every page: database, services and navigation."""
from core.tasks_service import TaskService
from core.trades_service import TradeService


class Context:
    def __init__(self, app, db):
        self.app = app
        self.db = db
        self.tasks = TaskService(db)
        self.trades = TradeService(db)

    @property
    def name(self):
        return self.db.get_setting("name", "DIALLO")

    def navigate(self, key, **kwargs):
        self.app.navigate(key, **kwargs)

    def reload(self):
        self.app.reload()
