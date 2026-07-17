"""Charte graphique Afri-Farmers Market (extraite de assets/logo.png)."""

PRIMARY = "#00604E"        # vert sapin (fond du logo)
PRIMARY_DARK = "#00473A"   # variante plus sombre (fonds de titres, footers)
ACCENT = "#00A651"         # vert feuille (moyen)
ACCENT_LIGHT = "#4CD964"   # vert feuille clair (highlights)
ACCENT_DARK = "#007A3D"    # vert feuille foncé
WHITE = "#FFFFFF"
INK = "#1A1A1A"            # texte sombre sur fond clair
GREY = "#6B7280"           # texte secondaire
LIGHT_BG = "#F4F8F6"       # fond clair légèrement teinté vert

# Palette catégorielle pour graphiques (dégradé vert cohérent avec la marque)
CATEGORICAL = [PRIMARY, ACCENT, ACCENT_LIGHT, "#8FD19E", "#B7E4C7"]

# Palette séquentielle (pour heatmaps, intensité)
SEQUENTIAL = "Greens"

LOGO_PATH = "assets/logo.png"

FONT_HEADING = "Arial"
FONT_BODY = "Arial"


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
