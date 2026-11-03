"""Maps (mode, page key) to the function that builds the page."""
from ui import tasks_pages, trading_pages
from ui.settings_page import settings_page

PAGES = {
    "productivity": {
        "home": tasks_pages.home_page,
        "add": tasks_pages.add_task_page,
        "tasks": tasks_pages.my_tasks_page,
        "calendar": tasks_pages.calendar_page,
    },
    "trading": {
        "dashboard": trading_pages.dashboard_page,
        "journal": trading_pages.journal_page,
        "add_trade": trading_pages.add_trade_page,
        "analysis": trading_pages.analysis_page,
    },
}


def build(ctx, mode, key, master, **kwargs):
    if key == "settings":
        return settings_page(ctx, mode, master)
    return PAGES[mode][key](ctx, master, **kwargs)
