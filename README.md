# Trading Planner

A desktop app (Python, customtkinter, SQLite, matplotlib) with two modes you switch
with a button in the sidebar:

- **Productivity** - Daily Task Reminder System: add / edit / delete tasks, priorities,
  categories, repeat (daily / weekly), calendar, search and filters, reminder pop-up with
  "Mark as Completed" and "Snooze (10 min)".
- **Trading** - Trading Journal: log trades (forex pairs, US30, NAS100, SP500, gold, silver,
  Bitcoin), dashboard with equity curve, P&L calendar, daily P&L, win rate, profit factor,
  max drawdown, streak, analysis by asset / class / emotion, CSV export, discipline alert.

## Run

    pip install -r requirements.txt
    python main.py

Python 3.9+ is required (tkinter is included with the standard Windows installer).
Your data is stored locally in `data/app.db`. It starts empty. In **Settings** you can
load demo data to see the dashboard filled, or clear everything.

## Project structure

    main.py                 window, mode switch, navigation, reminder loop
    core/                   logic without any UI
      database.py           SQLite connection and tables
      tasks_service.py      tasks, recurrence, snooze, reminders, stats
      trades_service.py     trades, statistics, groupings, CSV export
      demo.py               optional demo data
    ui/
      theme.py              colors and menus for both modes
      background.py         "Aurora" glow background and rounded cards (Pillow)
      page.py               base page (cards layout + scrolling)
      sidebar.py            sidebar and mode switch
      widgets.py            cards, form fields, buttons, tables
      calendar_widget.py    month grid and date picker
      charts.py             matplotlib charts
      tasks_pages.py        Home, Add Task, My Tasks, Calendar
      trading_pages.py      Dashboard, Journal, Add Trade, Asset Analysis
      settings_page.py      Settings
      popups.py             reminder pop-up
