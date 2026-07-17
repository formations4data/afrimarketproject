"""
Génère des graphiques aux couleurs de la charte Afri-Farmers Market (vert sapin / vert feuille),
sans titre intégré (les titres sont posés par la diapositive / la page PDF), pour le PPTX et le PDF.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import pandas as pd
import numpy as np
import os

from src_analysis import (
    analyse_categorie, evolution_mensuelle_categorie, analyse_ville,
    croissance_mensuelle_ville, analyse_marketing, pareto_clients, segmentation_clients,
)
import brand

FIG_DIR = "figures_brand"
sns.set_theme(style="white")
plt.rcParams.update({
    "figure.dpi": 150,
    "font.family": "sans-serif",
    "font.size": 13,
    "axes.edgecolor": "#D8E0DC",
    "axes.labelcolor": brand.INK,
    "text.color": brand.INK,
    "xtick.color": brand.GREY,
    "ytick.color": brand.GREY,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

PAL = brand.CATEGORICAL


def _save(fig, name, transparent=True):
    os.makedirs(FIG_DIR, exist_ok=True)
    path = os.path.join(FIG_DIR, name)
    fig.savefig(path, bbox_inches="tight", transparent=transparent, dpi=200)
    plt.close(fig)
    return path


def fig_ca_par_categorie(df):
    agg = analyse_categorie(df)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    bars = ax.bar(agg["categorie"], agg["ca"], color=PAL[:len(agg)])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1000:,.0f}k"))
    for b, v in zip(bars, agg["ca"]):
        ax.text(b.get_x() + b.get_width() / 2, v, f"{v:,.0f}", ha="center", va="bottom", fontsize=11, color=brand.INK)
    ax.set_ylabel("Chiffre d'affaires")
    ax.set_xlabel("")
    return _save(fig, "ca_par_categorie.png")


def fig_taux_retour_categorie(df):
    agg = analyse_categorie(df).sort_values("taux_retour", ascending=False)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    colors = [brand.PRIMARY if v == agg["taux_retour"].max() else brand.ACCENT_LIGHT for v in agg["taux_retour"]]
    bars = ax.bar(agg["categorie"], agg["taux_retour"], color=colors)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    for b, v in zip(bars, agg["taux_retour"]):
        ax.text(b.get_x() + b.get_width() / 2, v, f"{v:.1%}", ha="center", va="bottom", fontsize=11, color=brand.INK)
    ax.set_ylabel("Taux de retour")
    ax.set_xlabel("")
    return _save(fig, "taux_retour_categorie.png")


def fig_evolution_categorie(df):
    monthly = evolution_mensuelle_categorie(df)
    fig, ax = plt.subplots(figsize=(9, 4))
    cats = monthly["categorie"].unique()
    for i, c in enumerate(cats):
        sub = monthly[monthly["categorie"] == c]
        ax.plot(sub["mois"], sub["chiffre_affaires"], marker="o", label=c, color=PAL[i % len(PAL)], linewidth=2.5)
    ax.legend(frameon=False, ncol=len(cats))
    ax.set_ylabel("Chiffre d'affaires")
    ax.set_xlabel("")
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    return _save(fig, "evolution_categorie.png")


def fig_ca_par_ville(df):
    agg = analyse_ville(df).sort_values("ca")
    fig, ax = plt.subplots(figsize=(7, 4.5))
    colors = [brand.PRIMARY if v == agg["ca"].max() else brand.ACCENT for v in agg["ca"]]
    ax.barh(agg["ville"], agg["ca"], color=colors)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1000:,.0f}k"))
    ax.set_xlabel("Chiffre d'affaires")
    return _save(fig, "ca_par_ville.png")


def fig_taux_annulation_ville(df):
    agg = analyse_ville(df).sort_values("taux_annulation")
    fig, ax = plt.subplots(figsize=(7, 4.5))
    colors = ["#C0392B" if v == agg["taux_annulation"].max() else brand.ACCENT_LIGHT for v in agg["taux_annulation"]]
    ax.barh(agg["ville"], agg["taux_annulation"], color=colors)
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax.set_xlabel("Taux d'annulation")
    return _save(fig, "taux_annulation_ville.png")


def fig_roi_canal(df):
    agg = analyse_marketing(df).sort_values("roi", ascending=False)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    colors = [brand.PRIMARY if v == agg["roi"].max() else brand.ACCENT_LIGHT for v in agg["roi"]]
    bars = ax.bar(agg["canal_marketing"], agg["roi"], color=colors)
    for b, v in zip(bars, agg["roi"]):
        ax.text(b.get_x() + b.get_width() / 2, v, f"x{v:.0f}", ha="center", va="bottom", fontsize=11, color=brand.INK)
    ax.set_ylabel("ROI (x)")
    ax.set_xlabel("")
    return _save(fig, "roi_canal.png")


def fig_pareto_clients(df):
    pareto, part20 = pareto_clients(df)
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    ax.plot(pareto["cum_pct_clients"], pareto["cum_pct_ca"], color=brand.PRIMARY, linewidth=3)
    ax.fill_between(pareto["cum_pct_clients"], pareto["cum_pct_ca"], color=brand.ACCENT_LIGHT, alpha=0.25)
    ax.axvline(20, color=brand.GREY, linestyle="--", linewidth=1)
    ax.axhline(part20, color=brand.GREY, linestyle="--", linewidth=1)
    ax.scatter([20], [part20], color=brand.ACCENT_DARK, zorder=5, s=60)
    ax.set_xlabel("% cumulé des clients")
    ax.set_ylabel("% cumulé du CA")
    return _save(fig, "pareto_clients.png"), part20


def fig_segmentation_clients(df):
    seg = segmentation_clients(df)
    counts = seg["segment"].value_counts()
    fig, ax = plt.subplots(figsize=(5.5, 5))
    colors = {"VIP": brand.PRIMARY, "Récurrent": brand.ACCENT, "Occasionnel": brand.ACCENT_LIGHT}
    wedge_colors = [colors.get(k, brand.GREY) for k in counts.index]
    ax.pie(counts.values, labels=counts.index, autopct="%1.0f%%", startangle=90,
           colors=wedge_colors, textprops={"color": brand.INK, "fontsize": 12},
           wedgeprops={"edgecolor": "white", "linewidth": 2})
    return _save(fig, "segmentation_clients.png")


def fig_heatmap_ville_categorie(df):
    df_valide = df[df["statut_commande"] != "Annulée"]
    pivot = df_valide.pivot_table(index="ville", columns="categorie", values="chiffre_affaires", aggfunc="sum", fill_value=0)
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    sns.heatmap(pivot, annot=True, fmt=",.0f", cmap="Greens", ax=ax, cbar=False, linewidths=1, linecolor="white",
                annot_kws={"fontsize": 9})
    ax.set_xlabel("")
    ax.set_ylabel("")
    return _save(fig, "heatmap_ville_categorie.png")


def generate_all(df):
    paths = {}
    paths["ca_categorie"] = fig_ca_par_categorie(df)
    paths["retour_categorie"] = fig_taux_retour_categorie(df)
    paths["evolution_categorie"] = fig_evolution_categorie(df)
    paths["ca_ville"] = fig_ca_par_ville(df)
    paths["annulation_ville"] = fig_taux_annulation_ville(df)
    paths["roi_canal"] = fig_roi_canal(df)
    paths["pareto"], paths["part20"] = fig_pareto_clients(df)
    paths["segmentation"] = fig_segmentation_clients(df)
    paths["heatmap"] = fig_heatmap_ville_categorie(df)
    return paths


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from src_pipeline import load_clean
    df = load_clean()
    paths = generate_all(df)
    for k, v in paths.items():
        print(k, v)
