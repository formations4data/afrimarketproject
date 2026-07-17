"""
Génération des visualisations (Matplotlib/Seaborn) pour le notebook et le résumé exécutif.
Toutes les figures sont sauvegardées en PNG dans figures/.
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

FIG_DIR = "figures"
sns.set_theme(style="whitegrid", palette="deep")
plt.rcParams["figure.dpi"] = 110
plt.rcParams["font.size"] = 10


def _save(fig, name):
    os.makedirs(FIG_DIR, exist_ok=True)
    path = os.path.join(FIG_DIR, name)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def fig_ca_par_categorie(df):
    agg = analyse_categorie(df)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    sns.barplot(data=agg, x="categorie", y="ca", ax=ax, hue="categorie", legend=False)
    ax.set_title("Chiffre d'affaires par catégorie")
    ax.set_xlabel("")
    ax.set_ylabel("CA (FCFA/€ - unité dataset)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    for i, v in enumerate(agg["ca"]):
        ax.text(i, v, f"{v:,.0f}", ha="center", va="bottom", fontsize=9)
    return _save(fig, "01_ca_par_categorie.png")


def fig_marge_profit_categorie(df):
    agg = analyse_categorie(df).melt(id_vars="categorie", value_vars=["marge", "profit"],
                                      var_name="indicateur", value_name="valeur")
    fig, ax = plt.subplots(figsize=(7, 4.5))
    sns.barplot(data=agg, x="categorie", y="valeur", hue="indicateur", ax=ax)
    ax.set_title("Marge brute et profit net estimés par catégorie")
    ax.set_xlabel("")
    ax.set_ylabel("Montant")
    return _save(fig, "02_marge_profit_categorie.png")


def fig_evolution_mensuelle_categorie(df):
    monthly = evolution_mensuelle_categorie(df)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.lineplot(data=monthly, x="mois", y="chiffre_affaires", hue="categorie", marker="o", ax=ax)
    ax.set_title("Évolution mensuelle du CA par catégorie")
    ax.set_xlabel("Mois")
    ax.set_ylabel("CA")
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    return _save(fig, "03_evolution_mensuelle_categorie.png")


def fig_taux_retour_categorie(df):
    agg = analyse_categorie(df)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    sns.barplot(data=agg.sort_values("taux_retour", ascending=False), x="categorie", y="taux_retour",
                ax=ax, hue="categorie", legend=False)
    ax.set_title("Taux de retour par catégorie")
    ax.set_xlabel("")
    ax.set_ylabel("Taux de retour")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    return _save(fig, "04_taux_retour_categorie.png")


def fig_ca_par_ville(df):
    agg = analyse_ville(df)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.barplot(data=agg, y="ville", x="ca", ax=ax, hue="ville", legend=False)
    ax.set_title("Chiffre d'affaires par ville")
    ax.set_xlabel("CA")
    ax.set_ylabel("")
    return _save(fig, "05_ca_par_ville.png")


def fig_taux_annulation_ville(df):
    agg = analyse_ville(df)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.barplot(data=agg.sort_values("taux_annulation", ascending=False), y="ville", x="taux_annulation",
                ax=ax, hue="ville", legend=False)
    ax.set_title("Taux d'annulation par ville")
    ax.set_xlabel("Taux d'annulation")
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    return _save(fig, "06_taux_annulation_ville.png")


def fig_heatmap_ville_categorie(df):
    df_valide = df[df["statut_commande"] != "Annulée"]
    pivot = df_valide.pivot_table(index="ville", columns="categorie", values="chiffre_affaires", aggfunc="sum", fill_value=0)
    fig, ax = plt.subplots(figsize=(7, 5.5))
    sns.heatmap(pivot, annot=True, fmt=",.0f", cmap="YlGnBu", ax=ax, cbar_kws={"label": "CA"})
    ax.set_title("CA par ville x catégorie")
    return _save(fig, "07_heatmap_ville_categorie.png")


def fig_roi_canal(df):
    agg = analyse_marketing(df)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    sns.barplot(data=agg, x="canal_marketing", y="roi", ax=ax, hue="canal_marketing", legend=False)
    ax.set_title("ROI marketing par canal  (ROI = (CA - coût) / coût)")
    ax.set_xlabel("")
    ax.set_ylabel("ROI (x)")
    plt.setp(ax.get_xticklabels(), rotation=15, ha="right")
    return _save(fig, "08_roi_canal.png")


def fig_ca_cout_canal(df):
    agg = analyse_marketing(df).melt(id_vars="canal_marketing", value_vars=["ca", "cout_marketing"],
                                      var_name="indicateur", value_name="valeur")
    fig, ax = plt.subplots(figsize=(7, 4.5))
    sns.barplot(data=agg, x="canal_marketing", y="valeur", hue="indicateur", ax=ax)
    ax.set_yscale("log")
    ax.set_title("CA généré vs coût marketing par canal (échelle log)")
    ax.set_xlabel("")
    plt.setp(ax.get_xticklabels(), rotation=15, ha="right")
    return _save(fig, "09_ca_cout_canal.png")


def fig_distribution_panier(df):
    df_valide = df[df["statut_commande"] != "Annulée"]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    sns.histplot(df_valide["chiffre_affaires"], bins=50, kde=True, ax=ax)
    ax.set_title("Distribution du panier (chiffre d'affaires par commande)")
    ax.set_xlabel("Chiffre d'affaires de la commande")
    return _save(fig, "10_distribution_panier.png")


def fig_pareto_clients(df):
    pareto, part20 = pareto_clients(df)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(pareto["cum_pct_clients"], pareto["cum_pct_ca"], color="#2b6cb0")
    ax.axvline(20, color="grey", linestyle="--", linewidth=1)
    ax.axhline(part20, color="grey", linestyle="--", linewidth=1)
    ax.scatter([20], [part20], color="red", zorder=5)
    ax.annotate(f"20% des clients = {part20}% du CA", xy=(20, part20), xytext=(30, part20 - 15),
                arrowprops=dict(arrowstyle="->"))
    ax.set_title("Courbe de Pareto : concentration du CA par client")
    ax.set_xlabel("% cumulé des clients")
    ax.set_ylabel("% cumulé du CA")
    return _save(fig, "11_pareto_clients.png")


def fig_segmentation_clients(df):
    seg = segmentation_clients(df)
    counts = seg["segment"].value_counts()
    fig, ax = plt.subplots(figsize=(6, 4.5))
    ax.pie(counts.values, labels=counts.index, autopct="%1.0f%%", startangle=90,
           colors=sns.color_palette("deep"))
    ax.set_title("Segmentation des clients")
    return _save(fig, "12_segmentation_clients.png")


def fig_evolution_ville(df):
    monthly = croissance_mensuelle_ville(df)
    top_villes = df.groupby("ville")["chiffre_affaires"].sum().sort_values(ascending=False).head(4).index
    monthly_top = monthly[monthly["ville"].isin(top_villes)]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.lineplot(data=monthly_top, x="mois", y="chiffre_affaires", hue="ville", marker="o", ax=ax)
    ax.set_title("Évolution mensuelle du CA - Top 4 villes")
    ax.set_xlabel("Mois")
    ax.set_ylabel("CA")
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    return _save(fig, "13_evolution_ville.png")


def generate_all(df):
    paths = [
        fig_ca_par_categorie(df),
        fig_marge_profit_categorie(df),
        fig_evolution_mensuelle_categorie(df),
        fig_taux_retour_categorie(df),
        fig_ca_par_ville(df),
        fig_taux_annulation_ville(df),
        fig_heatmap_ville_categorie(df),
        fig_roi_canal(df),
        fig_ca_cout_canal(df),
        fig_distribution_panier(df),
        fig_pareto_clients(df),
        fig_segmentation_clients(df),
        fig_evolution_ville(df),
    ]
    return paths


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from src_pipeline import load_clean
    df = load_clean()
    paths = generate_all(df)
    print("\n".join(paths))
