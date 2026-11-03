"""Colors, fonts and menus for the two modes."""

FONT = "Segoe UI"

# glows: (corner, RGB color, strength 0-1, radius relative to the window)
THEMES = {
    "productivity": {
        "label": "Productivity",
        "bg": "#0D0E1F",
        "sidebar": "#1E1B2E",
        "card": "#1A1B33",
        "card_border": "#2E2F4D",
        "input": "#121328",
        "accent": "#8B5CF6",
        "accent_hover": "#7C3AED",
        "accent_soft": "#2A2250",
        "accent_text": "#DDD6FE",
        "on_accent": "#FFFFFF",
        "text": "#F1F0FA",
        "text_secondary": "#C3C0DD",
        "text_muted": "#8F8CB0",
        "glows": [
            ("tl", (139, 92, 246), 0.55, 0.9),
            ("br", (52, 211, 153), 0.32, 0.8),
        ],
    },
    "trading": {
        "label": "Trading",
        "bg": "#0B1220",
        "sidebar": "#080D18",
        "card": "#131C2E",
        "card_border": "#1F2A3D",
        "input": "#0D1524",
        "accent": "#E0B13A",
        "accent_hover": "#C99B2B",
        "accent_soft": "#2A2412",
        "accent_text": "#E0B13A",
        "on_accent": "#0B1220",
        "text": "#E5E7EB",
        "text_secondary": "#94A3B8",
        "text_muted": "#64748B",
        "glows": [],
    },
}

# (text color, background color): green = success / gain, red = danger / loss
STATUS = {
    "success": ("#32A55C", "#14301F"),
    "warning": ("#E7A864", "#3A2410"),
    "danger": ("#E26363", "#3A1A1F"),
}
GAIN = "#3BD774"
LOSS = "#E43E3E"

MENUS = {
    "productivity": [
        ("home", "Home"),
        ("add", "Add Task"),
        ("tasks", "My Tasks"),
        ("calendar", "Calendar"),
        ("settings", "Settings"),
    ],
    "trading": [
        ("dashboard", "Dashboard"),
        ("journal", "Journal"),
        ("add_trade", "Add Trade"),
        ("analysis", "Asset Analysis"),
        ("settings", "Settings"),
    ],
}
