"""Génère le fond « Aurore » (lueurs violette et menthe) et dessine les cartes dessus.

Tkinter n'a ni dégradé, ni transparence, ni coins arrondis lissés : on dessine
donc le fond ET les cartes dans une image Pillow, redimensionnée avec la fenêtre.
"""
from functools import lru_cache

from PIL import Image, ImageDraw

from ui.theme import THEMES

SQRT2 = 2 ** 0.5
CARD_RADIUS = 16


@lru_cache(maxsize=8)
def make_background(width: int, height: int, mode: str) -> Image.Image:
    theme = THEMES[mode]
    if not theme["glows"]:
        return Image.new("RGB", (width, height), theme["bg"])

    # les lueurs sont très douces : on les dessine en petit (÷3), puis on agrandit (beaucoup plus rapide)
    sw, sh = max(1, width // 3), max(1, height // 3)
    img = Image.new("RGB", (sw, sh), theme["bg"])
    biggest = max(sw, sh)

    for corner, rgb, strength, factor in theme["glows"]:
        radius = int(biggest * factor)
        cx = 0 if "l" in corner else sw
        cy = 0 if "t" in corner else sh

        # masque radial : 255 au centre, 0 à la distance « radius » (pas de bord visible)
        mask = Image.radial_gradient("L").resize(
            (radius * 2, radius * 2), Image.Resampling.BILINEAR
        )
        mask = mask.point(
            lambda v, s=strength: int(max(0.0, 1 - v * SQRT2 / 255) ** 2 * 255 * s)
        )
        glow = Image.new("RGB", (radius * 2, radius * 2), rgb)
        img.paste(glow, (cx - radius, cy - radius), mask)

    return img.resize((width, height), Image.Resampling.BICUBIC)

@lru_cache(maxsize=128)
def _card_image(w: int, h: int, fill: str, border: str) -> Image.Image:
    """Rectangle arrondi lissé (dessiné 3x plus grand puis réduit)."""
    s = 3
    big = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    d.rounded_rectangle((0, 0, w * s - 1, h * s - 1), CARD_RADIUS * s, fill=border)
    d.rounded_rectangle((s, s, w * s - 1 - s, h * s - 1 - s),
                        (CARD_RADIUS - 1) * s, fill=fill)
    return big.resize((w, h), Image.Resampling.LANCZOS)


def make_page_image(width: int, height: int, mode: str, rects) -> Image.Image:
    """Fond + cartes. rects = liste de (x, y, largeur, hauteur)."""
    theme = THEMES[mode]
    img = make_background(width, height, mode).copy()
    for x, y, w, h in rects:
        if w > 2 * CARD_RADIUS and h > 2 * CARD_RADIUS:
            card = _card_image(w, h, theme["card"], theme["card_border"])
            img.paste(card, (x, y), card)
    return img
