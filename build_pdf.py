"""
Génère le rapport PDF professionnel pour la Direction Générale,
selon la charte graphique Afri-Farmers Market (voir brand.py).
"""
import sys
sys.path.insert(0, ".")

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
    Image as RLImage, NextPageTemplate, PageBreak, HRFlowable, KeepTogether,
)
from reportlab.platypus.flowables import Flowable

import brand
from src_pipeline import load_clean
from src_analysis import performance_globale, analyse_categorie, analyse_ville, analyse_marketing, analyse_clients
from src_viz_brand import generate_all

C = lambda h: colors.HexColor(h)
PAGE_W, PAGE_H = A4
MARGIN = 20 * mm

# ---------------------------------------------------------------- DATA
df = load_clean()
perf = performance_globale(df)
cat_agg = analyse_categorie(df)
ville_agg = analyse_ville(df)
mkt_agg = analyse_marketing(df)
clients_info = analyse_clients(df)
charts = generate_all(df)

top_cat = cat_agg.sort_values("ca", ascending=False).iloc[0]
worst_return_cat = cat_agg.sort_values("taux_retour", ascending=False).iloc[0]
top_ville = ville_agg.sort_values("ca", ascending=False).iloc[0]
worst_annulation_ville = ville_agg.sort_values("taux_annulation", ascending=False).iloc[0]
best_roi_canal = mkt_agg.sort_values("roi", ascending=False).iloc[0]
worst_roi_canal = mkt_agg.sort_values("roi", ascending=True).iloc[0]
biggest_budget_canal = mkt_agg.sort_values("cout_marketing", ascending=False).iloc[0]
second_worst_annulation_ville = ville_agg.sort_values("taux_annulation", ascending=False).iloc[1]


def fmt(n):
    return f"{n:,.0f}".replace(",", " ")


# ---------------------------------------------------------------- STYLES
styles = getSampleStyleSheet()
styles.add(ParagraphStyle("H1Brand", fontName="Helvetica-Bold", fontSize=20, textColor=C(brand.PRIMARY),
                            spaceAfter=14, spaceBefore=6))
styles.add(ParagraphStyle("H2Brand", fontName="Helvetica-Bold", fontSize=14, textColor=C(brand.ACCENT_DARK),
                            spaceAfter=10, spaceBefore=14))
styles.add(ParagraphStyle("BodyBrand", fontName="Helvetica", fontSize=10.3, leading=15, textColor=C(brand.INK),
                            alignment=TA_JUSTIFY, spaceAfter=8))
styles.add(ParagraphStyle("BulletBrand", fontName="Helvetica", fontSize=10.3, leading=15, textColor=C(brand.INK),
                            leftIndent=12, bulletIndent=0, spaceAfter=6))
styles.add(ParagraphStyle("Caption", fontName="Helvetica-Oblique", fontSize=8.5, textColor=C(brand.GREY),
                            alignment=TA_CENTER, spaceAfter=10, spaceBefore=2))
styles.add(ParagraphStyle("CoverTitle", fontName="Helvetica-Bold", fontSize=30, textColor=colors.white,
                            alignment=TA_CENTER, leading=36))
styles.add(ParagraphStyle("CoverSub", fontName="Helvetica", fontSize=13, textColor=C(brand.ACCENT_LIGHT),
                            alignment=TA_CENTER, spaceBefore=10))
styles.add(ParagraphStyle("KPIVal", fontName="Helvetica-Bold", fontSize=17, textColor=colors.white,
                            alignment=TA_CENTER))
styles.add(ParagraphStyle("KPILabel", fontName="Helvetica", fontSize=8.3, textColor=C(brand.ACCENT_LIGHT),
                            alignment=TA_CENTER, leading=10))


def para(text, style="BodyBrand"):
    return Paragraph(text, styles[style])


def bullet(text):
    return Paragraph(f"●&nbsp;&nbsp;{text}", styles["BulletBrand"])


def section_title(text):
    return Paragraph(text, styles["H1Brand"])


def sub_title(text):
    return Paragraph(text, styles["H2Brand"])


def rule():
    return HRFlowable(width="100%", thickness=1, color=C("#D8E0DC"), spaceAfter=12)


def kpi_row(items):
    """items: list of (value, label)"""
    n = len(items)
    col_w = (PAGE_W - 2 * MARGIN) / n
    cells = []
    for val, label in items:
        cell = Table([[Paragraph(val, styles["KPIVal"])], [Paragraph(label, styles["KPILabel"])]],
                      colWidths=[col_w - 4], rowHeights=[26, 22])
        cell.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), C(brand.PRIMARY)),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, 0), 6),
            ("BOTTOMPADDING", (0, 1), (-1, 1), 6),
        ]))
        cells.append(cell)
    t = Table([cells], colWidths=[col_w] * n)
    t.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 2), ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def chart_image(path, width=None, max_h=95 * mm):
    img = RLImage(path)
    ratio = img.imageHeight / float(img.imageWidth)
    w = width or (PAGE_W - 2 * MARGIN)
    h = w * ratio
    if h > max_h:
        h = max_h
        w = h / ratio
    img.drawWidth = w
    img.drawHeight = h
    img.hAlign = "CENTER"
    return img


def data_table(data, col_widths=None, highlight_row=None):
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), C(brand.PRIMARY)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, C(brand.LIGHT_BG)]),
        ("GRID", (0, 0), (-1, -1), 0.5, C("#D8E0DC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ]
    if highlight_row is not None:
        style.append(("BACKGROUND", (0, highlight_row), (-1, highlight_row), C("#D7F0DE")))
    t.setStyle(TableStyle(style))
    return t


# ---------------------------------------------------------------- PAGE TEMPLATES
def cover_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(C(brand.PRIMARY))
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canvas.setFillColor(C(brand.ACCENT))
    canvas.rect(0, 0, PAGE_W, 4 * mm, fill=1, stroke=0)
    logo_w = 45 * mm
    canvas.drawImage(brand.LOGO_PATH, (PAGE_W - logo_w) / 2, PAGE_H - 90 * mm, width=logo_w, height=logo_w,
                       mask="auto")
    canvas.restoreState()


def content_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(C(brand.WHITE))
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    # header bar
    canvas.setFillColor(C(brand.PRIMARY))
    canvas.rect(0, PAGE_H - 14 * mm, PAGE_W, 14 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(MARGIN, PAGE_H - 9.5 * mm, "AFRIMARKET — ANALYSE STRATÉGIQUE")
    canvas.drawImage(brand.LOGO_PATH, PAGE_W - MARGIN - 8 * mm, PAGE_H - 12.5 * mm, width=8 * mm, height=8 * mm,
                       mask="auto")
    # footer
    canvas.setStrokeColor(C("#D8E0DC"))
    canvas.line(MARGIN, 14 * mm, PAGE_W - MARGIN, 14 * mm)
    canvas.setFillColor(C(brand.GREY))
    canvas.setFont("Helvetica", 8)
    canvas.drawString(MARGIN, 9 * mm, "Confidentiel — Usage interne Direction Générale")
    canvas.drawRightString(PAGE_W - MARGIN, 9 * mm, f"Page {doc.page - 1}")
    canvas.restoreState()


doc = BaseDocTemplate("reports/AfriMarket_Rapport_Direction.pdf", pagesize=A4,
                        leftMargin=MARGIN, rightMargin=MARGIN, topMargin=22 * mm, bottomMargin=18 * mm)
cover_frame = Frame(0, 0, PAGE_W, PAGE_H, id="cover")
content_frame = Frame(MARGIN, 18 * mm, PAGE_W - 2 * MARGIN, PAGE_H - 22 * mm - 14 * mm, id="content")
doc.addPageTemplates([
    PageTemplate(id="Cover", frames=[cover_frame], onPage=cover_page),
    PageTemplate(id="Content", frames=[content_frame], onPage=content_page),
])

story = []

# ============================================================ COVER
story.append(NextPageTemplate("Content"))
story.append(Spacer(1, 130 * mm))
story.append(para("Analyse Stratégique AfriMarket", "CoverTitle"))
story.append(para("6 mois d'activité commerciale — Rapport à la Direction Générale", "CoverSub"))
story.append(Spacer(1, 6 * mm))
story.append(para("Direction Data & Analyse — Juillet 2026", "CoverSub"))
story.append(PageBreak())

# ============================================================ 1. CONTEXTE & METHODE
story.append(section_title("1. Contexte et méthode"))
story.append(para(
    "AfriMarket est une entreprise e-commerce panafricaine opérant dans 8 grandes villes d'Afrique francophone, "
    "sur 4 catégories : Électronique, Mode, Beauté, Maison. La direction a constaté des variations de chiffre "
    "d'affaires, un taux de retour préoccupant, des dépenses marketing élevées et des écarts de performance entre "
    "villes. Cette analyse s'appuie sur 10 100 commandes brutes couvrant 6 mois d'activité."))

story.append(sub_title("Qualité des données"))
story.append(para(
    "L'audit a révélé 100 commandes dupliquées, 632 prix unitaires négatifs (dont 97% figés à une valeur "
    "constante de -50, signature d'un code d'erreur plutôt que d'une inversion de signe), 608 quantités nulles, "
    "614 remises négatives (constante à -0.10, cohérente avec une inversion de signe), ainsi que des "
    "incohérences orthographiques (<i>Kinshassa</i>/<i>Kinshasa</i>) et de casse (<i>electronique</i>/"
    "<i>Électronique</i>, <i>retournée</i>/<i>Retournée</i>). Après nettoyage : <b>10 000 commandes propres et "
    "fiables</b> (df_clean), soit 99% des données conservées."))

story.append(data_table([
    ["Problème détecté", "Traitement appliqué"],
    ["100 commandes dupliquées", "Suppression des doublons (1ère occurrence conservée)"],
    ["632 prix unitaires négatifs (~97% = -50 constant)", "Imputation par la médiane du même produit"],
    ["608 quantités nulles", "Imputation par la médiane de la catégorie"],
    ["614 remises négatives (100% = -0.10 constant)", "Valeur absolue (inversion de signe)"],
    ["Villes / catégories / statuts incohérents", "Harmonisation orthographe et casse"],
], col_widths=[80 * mm, 90 * mm]))

story.append(Spacer(1, 6))
story.append(para(
    "<b>Hypothèse de marge :</b> en l'absence de coût de revient fourni, la marge brute est estimée à 45% du "
    "chiffre d'affaires (coût de revient supposé à 55%) ; le profit net déduit en plus les coûts de livraison et "
    "marketing engagés par commande. Les commandes annulées sont exclues du chiffre d'affaires réel."))

story.append(PageBreak())

# ============================================================ 2. PERFORMANCE GLOBALE
story.append(section_title("2. Performance globale"))
story.append(kpi_row([
    (fmt(perf["ca_total"]), "Chiffre d'affaires total"),
    (fmt(perf["profit_total"]), "Profit net estimé"),
    (fmt(perf["panier_moyen"]), "Panier moyen"),
]))
story.append(Spacer(1, 6))
story.append(kpi_row([
    (f"{perf['taux_annulation']:.1%}", "Taux d'annulation"),
    (f"{perf['taux_retour']:.1%}", "Taux de retour"),
    (f"{perf['nb_clients']:,}".replace(",", " "), "Clients actifs"),
]))
story.append(Spacer(1, 10))
story.append(para(
    "L'activité est globalement saine (taux d'annulation faible), mais le taux de retour de 8,2% mérite "
    "attention — il est très concentré sur une seule catégorie (voir section 3)."))

story.append(PageBreak())

# ============================================================ 3. CATEGORIE
story.append(section_title("3. Analyse par catégorie"))
story.append(chart_image(charts["ca_categorie"], width=80 * mm))
cat_table = [["Catégorie", "CA", "Profit net", "Taux de retour"]]
for _, r in cat_agg.sort_values("ca", ascending=False).iterrows():
    cat_table.append([r["categorie"], fmt(r["ca"]), fmt(r["profit"]), f"{r['taux_retour']:.1%}"])
story.append(data_table(cat_table, col_widths=[45 * mm, 40 * mm, 40 * mm, 40 * mm], highlight_row=1))
story.append(Spacer(1, 8))
story.append(chart_image(charts["retour_categorie"], width=80 * mm))
story.append(para(
    f"<b>Constat clé :</b> {top_cat['categorie']} génère à elle seule {top_cat['ca']/perf['ca_total']:.0%} du CA "
    f"total et la quasi-totalité du profit — c'est le moteur économique de l'entreprise. Mais son taux de retour "
    f"({worst_return_cat['taux_retour']:.1%}) est 2 à 5 fois supérieur aux autres catégories, ce qui grève sa "
    "rentabilité réelle bien au-delà de ce que montre le profit comptable."))

story.append(PageBreak())

# ============================================================ 4. GEOGRAPHIE
story.append(section_title("4. Analyse géographique"))
story.append(chart_image(charts["ca_ville"], width=90 * mm))
story.append(Spacer(1, 8))
story.append(chart_image(charts["annulation_ville"], width=90 * mm))
story.append(para(
    f"<b>Constat clé :</b> {top_ville['ville']} est de loin la ville la plus performante (CA, profit, quasi zéro "
    f"annulation) et un candidat naturel à un investissement renforcé. {worst_annulation_ville['ville']} se "
    f"distingue par un taux d'annulation anormal de {worst_annulation_ville['taux_annulation']:.1%}, alors que "
    "toutes les autres villes sont proches de 0% — un signal opérationnel localisé qu'il faut diagnostiquer avant "
    "d'y investir davantage."))

story.append(PageBreak())

# ============================================================ 5. MARKETING
story.append(section_title("5. Analyse marketing"))
story.append(chart_image(charts["roi_canal"], width=90 * mm))
mkt_table = [["Canal", "CA généré", "Coût marketing", "ROI", "Rétention"]]
for _, r in mkt_agg.sort_values("roi", ascending=False).iterrows():
    mkt_table.append([r["canal_marketing"], fmt(r["ca"]), fmt(r["cout_marketing"]), f"x{r['roi']:.0f}",
                        f"{r['taux_retention']:.1%}"])
story.append(data_table(mkt_table, col_widths=[38 * mm, 38 * mm, 38 * mm, 22 * mm, 28 * mm], highlight_row=1))
story.append(Spacer(1, 8))
story.append(para("<i>ROI = (CA − coût marketing) / coût marketing</i>", "Caption"))
story.append(para(
    f"<b>Constat clé :</b> {biggest_budget_canal['canal_marketing']} capte le plus gros budget marketing "
    f"({fmt(biggest_budget_canal['cout_marketing'])}) et génère le plus de CA en absolu, mais avec un ROI modeste "
    f"(x{biggest_budget_canal['roi']:.0f}) : c'est le plus gros gisement d'optimisation en valeur absolue. "
    f"{worst_roi_canal['canal_marketing']} affiche le ROI le plus faible en proportion (x{worst_roi_canal['roi']:.0f}), "
    f"sur un budget plus restreint. {best_roi_canal['canal_marketing']}, à l'inverse, ne représente qu'une fraction "
    f"du budget marketing total mais affiche un ROI {best_roi_canal['roi']/worst_roi_canal['roi']:.0f} fois "
    "supérieur au canal le moins efficace."))

story.append(PageBreak())

# ============================================================ 6. CLIENTS
story.append(section_title("6. Analyse clients"))
story.append(chart_image(charts["pareto"], width=80 * mm))
story.append(Spacer(1, 8))
story.append(chart_image(charts["segmentation"], width=70 * mm))
story.append(para(
    f"<b>Constat clé :</b> {clients_info['nb_clients']:,}".replace(",", " ") +
    f" clients actifs, dont {clients_info['pct_recurrents']:.1%} récurrents (plus d'une commande) — une base de "
    f"fidélisation globalement solide. Les 20% de clients les plus rentables génèrent {charts['part20']}% du "
    "chiffre d'affaires total : la dépendance à ce noyau de clients VIP est un facteur de risque autant qu'un "
    "actif."))

story.append(PageBreak())

# ============================================================ 7. RECOMMANDATIONS
story.append(section_title("7. Cinq recommandations stratégiques"))
recos = [
    ("Sécuriser et développer Électronique tout en réduisant ses retours",
     "Elle porte 75% du CA : maintenir un stock prioritaire et une visibilité forte, tout en lançant un plan "
     "qualité ciblé (contrôle fournisseur, fiches produit, politique de retour repensée)."),
    (f"Concentrer l'investissement sur {top_ville['ville']}, auditer {worst_annulation_ville['ville']}",
     f"{top_ville['ville']} combine le meilleur CA et une fiabilité opérationnelle quasi parfaite. "
     f"{worst_annulation_ville['ville']} affiche un taux d'annulation anormal à investiguer avant tout "
     "investissement supplémentaire."),
    (f"Réallouer le budget {biggest_budget_canal['canal_marketing']} vers {best_roi_canal['canal_marketing']}",
     f"{biggest_budget_canal['canal_marketing']} concentre le plus gros budget pour un ROI modeste (x{biggest_budget_canal['roi']:.0f}) ; "
     f"{best_roi_canal['canal_marketing']} génère un ROI très supérieur (x{best_roi_canal['roi']:.0f}) pour un coût marginal quasi négligeable. "
     f"{worst_roi_canal['canal_marketing']}, dont le ROI (x{worst_roi_canal['roi']:.0f}) est le plus faible en proportion, doit aussi être revu. "
     "Un test A/B de réallocation progressive permettrait de vérifier le gain net avant généralisation."),
    ("Lancer un programme de fidélisation dédié aux clients VIP",
     "Les clients VIP portent une part disproportionnée du CA : avantages exclusifs, service prioritaire, "
     "gestion de compte dédiée pour sécuriser cette rente."),
    ("Mettre en place une relance automatisée des clients occasionnels",
     "Un parcours de réactivation (email/SMS, offre de bienvenue seconde commande) peut convertir ce segment en "
     "clients récurrents, avec un ROI potentiellement élevé."),
]
for i, (title, detail) in enumerate(recos, start=1):
    story.append(KeepTogether([
        Table([[
            Table([[Paragraph(str(i), ParagraphStyle("num", parent=styles["KPIVal"], fontSize=13))]],
                   colWidths=[9 * mm], rowHeights=[9 * mm],
                   style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), C(brand.PRIMARY)),
                                       ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                       ("ALIGN", (0, 0), (-1, -1), "CENTER")])),
            Paragraph(f"<b>{title}</b><br/>{detail}", styles["BodyBrand"]),
        ]], colWidths=[12 * mm, PAGE_W - 2 * MARGIN - 12 * mm],
            style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (1, 0), (1, 0), 8)])),
        Spacer(1, 8),
    ]))

story.append(PageBreak())

# ============================================================ 8. CONCLUSION
story.append(section_title("8. Conclusion business orientée action"))
story.append(para(
    "AfriMarket dispose d'un modèle rentable et d'une base client majoritairement fidèle, mais sa performance est "
    "concentrée et donc fragile : une catégorie (Électronique) porte l'essentiel du CA, une ville "
    f"({worst_annulation_ville['ville']}) capte une anomalie opérationnelle non expliquée, et un canal marketing "
    f"({biggest_budget_canal['canal_marketing']}) absorbe un budget disproportionné à son efficacité réelle."))
story.append(para(
    "Les prochains 90 jours devraient prioriser, dans l'ordre : (1) l'audit opérationnel de "
    f"{worst_annulation_ville['ville']} — coût faible, risque de ne rien faire élevé ; (2) le test de "
    f"réallocation budgétaire {biggest_budget_canal['canal_marketing']} → {best_roi_canal['canal_marketing']} — gain "
    "rapide à faible risque ; (3) le lancement du programme VIP — protection du cœur de revenu. Le plan qualité "
    "Électronique et la relance des clients occasionnels, plus structurants, s'inscrivent sur un horizon 2-3 "
    "trimestres."))

doc.build(story)
print("PDF généré : reports/AfriMarket_Rapport_Direction.pdf")
