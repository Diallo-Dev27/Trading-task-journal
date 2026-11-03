"""Barre latérale : logo, sélecteur de mode (Productivité / Trading) et menu."""
import customtkinter as ctk

from ui.theme import FONT, MENUS, THEMES


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_mode, on_nav):
        super().__init__(master, width=230, corner_radius=0)
        self.pack_propagate(False)
        self.on_mode = on_mode
        self.on_nav = on_nav
        self.theme = None
        self.menu_buttons = {}
        self.active_key = None

        self.logo = ctk.CTkLabel(self, text="DAILY TASK", font=(FONT, 18, "bold"))
        self.logo.pack(anchor="w", padx=22, pady=(26, 16))

        # sélecteur de mode : deux boutons dans un cadre arrondi
        self.switch = ctk.CTkFrame(self, corner_radius=12)
        self.switch.pack(fill="x", padx=16, pady=(0, 20))
        self.switch_buttons = {}
        for col, (key, theme) in enumerate(THEMES.items()):
            self.switch.grid_columnconfigure(col, weight=1, uniform="mode")
            btn = ctk.CTkButton(
                self.switch, text=theme["label"], width=10, height=32, corner_radius=9,
                font=(FONT, 11, "bold"), command=lambda k=key: self.on_mode(k),
            )
            btn.grid(row=0, column=col, sticky="ew", padx=3, pady=3)
            self.switch_buttons[key] = btn

                # les deux menus sont construits une fois ; changer de mode en affiche un et cache l'autre
        self.menu_frames = {}
        self.all_buttons = {}
        for mode in THEMES:
            frame = ctk.CTkFrame(self, fg_color="transparent")
            buttons = {}
            for key, label in MENUS[mode]:
                btn = ctk.CTkButton(
                    frame, text=label, anchor="w", height=42, corner_radius=10,
                    font=(FONT, 14), command=lambda k=key: self.on_nav(k),
                )
                btn.pack(fill="x", pady=2)
                buttons[key] = btn
            self.menu_frames[mode] = frame
            self.all_buttons[mode] = buttons

    def apply_mode(self, mode):
        """Change les couleurs, le bouton actif du sélecteur et le menu."""
        t = THEMES[mode]
        self.theme = t
        self.configure(fg_color=t["sidebar"])
        self.logo.configure(text_color=t["text"])
        self.switch.configure(fg_color=t["card"])
        for key, btn in self.switch_buttons.items():
            if key == mode:
                btn.configure(fg_color=t["accent"], hover_color=t["accent_hover"],
                              text_color=t["on_accent"])
            else:
                btn.configure(fg_color="transparent", hover_color=t["card_border"],
                              text_color=t["text_secondary"])

        # Show the appropriate menu frame based on the selected mode
        for frame in self.menu_frames.values():
            frame.configure(bg_color=t["sidebar"])
            frame.pack_forget()
        self.menu_frames[mode].pack(fill="x", padx=12)

        self.menu_buttons = self.all_buttons[mode]
       

    def highlight(self, key):
        #Met en avant l'entrée de menu de la page affichée."""
        t = self.theme
        for k, btn in self.menu_buttons.items():
            if k == key:
                btn.configure(bg_color=t["sidebar"], fg_color=t["accent_soft"],
                              hover_color=t["accent_soft"], text_color=t["accent_text"])
            else:
                btn.configure(bg_color=t["sidebar"], fg_color="transparent",
                              hover_color=t["card"], text_color=t["text_secondary"])
        self.active_key = key
