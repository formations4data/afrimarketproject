"""
Construit le notebook Jupyter complet (analyse_afrimarket.ipynb) à partir de cellules
markdown et code, puis l'exécute pour produire un notebook avec ses sorties (tableaux, graphiques).
"""
import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []


def md(text):
    cells.append(nbf.v4.new_markdown_cell(text))


def code(text):
    cells.append(nbf.v4.new_code_cell(text))


# ============================================================ TITRE
md("""# Analyse stratégique des données AfriMarket

**Entreprise :** AfriMarket — e-commerce panafricain (Électronique, Mode, Beauté, Maison)
**Auteur :** Data Analyst
**Période analysée :** 6 mois d'activité commerciale (juillet - décembre 2025)

**Objectif :** produire une analyse stratégique complète permettant à la direction de comprendre les variations de chiffre d'affaires, le taux de retour, les dépenses marketing et les écarts de performance entre villes, afin de prendre des décisions business argumentées.

---
## Sommaire
1. [Audit & compréhension des données](#1)
2. [Data cleaning](#2)
3. [Feature engineering](#3)
4. [Analyses](#4)
    - 4.1 Performance globale
    - 4.2 Analyse par catégorie
    - 4.3 Analyse géographique
    - 4.4 Analyse marketing
    - 4.5 Analyse clients
5. [Visualisations de synthèse](#5)
6. [Recommandations stratégiques & conclusion](#6)
""")

code("""# Imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

pd.set_option("display.float_format", lambda x: f"{x:,.2f}")
sns.set_theme(style="whitegrid", palette="deep")
plt.rcParams["figure.dpi"] = 100
%matplotlib inline
""")

# ============================================================ 1. AUDIT
md("""<a id="1"></a>
## 1. Audit & compréhension des données

On charge le fichier brut `afrimarket_dataset_senior.csv` (6 mois d'activité commerciale) et on explore sa structure avant tout traitement.""")

code("""df_raw = pd.read_csv("data/afrimarket_dataset_senior.csv", encoding="utf-8")
print("Dimensions :", df_raw.shape)
df_raw.head()
""")

code("""# Types de données
df_raw.dtypes
""")

code("""# Valeurs manquantes (NaN explicites)
df_raw.isnull().sum()
""")

md("""**Constat :** aucune valeur `NaN` explicite. Les erreurs de saisie sont en réalité encodées comme des valeurs *valides mais aberrantes* (prix négatifs, quantités nulles, remises négatives, doublons, orthographes incohérentes) — typique d'un jeu de données réel.""")

code("""# Doublons
print("Lignes strictement dupliquées :", df_raw.duplicated().sum())
print("id_commande dupliqués :", df_raw.duplicated(subset=["id_commande"]).sum())
""")

code("""# Valeurs aberrantes numériques
print("Prix unitaire < 0 :", (df_raw["prix_unitaire"] < 0).sum())
print("Quantité == 0 :", (df_raw["quantite"] == 0).sum())
print("Remise < 0 :", (df_raw["remise"] < 0).sum())
df_raw[["prix_unitaire", "quantite", "remise", "cout_livraison", "cout_marketing"]].describe()
""")

md("""**Diagnostic prix négatifs :** en isolant les prix négatifs, on constate que ~97% d'entre eux valent exactement **-50.00**, une valeur constante indépendante du produit concerné (ex. un article `Électronique` qui vaut normalement ~400 apparaît aussi à -50). Il ne s'agit donc pas d'une simple inversion de signe mais d'un **code d'erreur injecté** : on les traitera comme des valeurs manquantes à imputer.

**Diagnostic remises négatives :** à l'inverse, 100% des remises négatives valent exactement **-0.10**, une valeur plausible de remise (0 à 30% observé sur le reste du dataset). C'est cohérent avec une **simple inversion de signe** : on prendra la valeur absolue.""")

code("""# Incohérences catégorielles
for c in ["ville", "categorie", "statut_commande"]:
    print(f"{c}: {sorted(df_raw[c].unique())}")
""")

md("""**Incohérences identifiées :**
- `ville` : `"Kinshassa"` est une faute d'orthographe de `"Kinshasa"`.
- `categorie` : `"electronique"` (sans accent, minuscule) est la même catégorie que `"Électronique"`.
- `statut_commande` : `"retournée"` (minuscule) doit être harmonisé en `"Retournée"`.
""")

# ============================================================ 2. CLEANING
md("""<a id="2"></a>
## 2. Data Cleaning

On applique les corrections identifiées lors de l'audit pour produire un jeu de données propre `df_clean`. La logique est centralisée dans `src_pipeline.py` (fonction `clean_data`) pour être réutilisable par le dashboard Streamlit.""")

code("""from src_pipeline import load_raw, clean_data, add_features

df_raw = load_raw()
df_clean = clean_data(df_raw)
print("Lignes avant nettoyage :", len(df_raw))
print("Lignes après suppression des doublons :", len(df_clean))
""")

code("""# Vérification post-nettoyage
checks = {
    "prix_unitaire < 0": (df_clean["prix_unitaire"] < 0).sum(),
    "quantite == 0": (df_clean["quantite"] == 0).sum(),
    "remise < 0": (df_clean["remise"] < 0).sum(),
    "id_commande dupliqués": df_clean.duplicated(subset=["id_commande"]).sum(),
}
checks
""")

code("""print("Villes :", sorted(df_clean["ville"].unique()))
print("Catégories :", sorted(df_clean["categorie"].unique()))
print("Statuts :", sorted(df_clean["statut_commande"].unique()))
""")

md("""**Résumé des traitements appliqués :**

| Problème | Traitement | Justification |
|---|---|---|
| 100 commandes dupliquées (même `id_commande`) | Suppression des doublons (1ère occurrence conservée) | `id_commande` doit être unique |
| Prix unitaire négatif (632 lignes, ~97% = -50.00 constant) | Traité comme valeur manquante, imputé par la **médiane du même produit** | Valeur non corrélée au vrai prix du produit -> code d'erreur, pas une inversion de signe |
| Remise négative (614 lignes, 100% = -0.10 constant) | Valeur absolue | Constante plausible -> simple inversion de signe |
| Quantité nulle (608 lignes) | Traité comme valeur manquante, imputé par la **médiane de la catégorie** | Une commande à 0 article n'a pas de sens business |
| `"Kinshassa"` | Renommé en `"Kinshasa"` | Faute d'orthographe |
| `"electronique"` vs `"Électronique"` | Harmonisé en `"Électronique"` | Casse/accent incohérents |
| `"retournée"` vs `"Retournée"` | Harmonisé en `"Retournée"` | Casse incohérente |
""")

# ============================================================ 3. FEATURE ENGINEERING
md("""<a id="3"></a>
## 3. Feature Engineering

On enrichit `df_clean` avec les variables business nécessaires aux analyses.

**Hypothèses de modélisation (documentées) :**
- `chiffre_affaires` = prix unitaire x quantité x (1 - remise)
- `marge_brute` = chiffre d'affaires x 45% (hypothèse de coût de revient à 55% du prix, non fourni dans les données)
- `profit_net` = marge brute - coût de livraison - coût marketing de la commande
- Les commandes **Annulées** sont exclues du chiffre d'affaires réel (aucune vente effective), mais le coût marketing déjà engagé reste comptabilisé dans les coûts.
""")

code("""df_clean = add_features(df_clean)
df_clean.to_csv("data/df_clean.csv", index=False, encoding="utf-8")
df_clean[["chiffre_affaires", "marge_brute", "profit_net", "mois", "indicateur_retour",
          "nombre_commandes_par_client", "valeur_vie_client"]].head()
""")

# ============================================================ 4. ANALYSES
md("""<a id="4"></a>
## 4. Analyses demandées""")

md("""### 4.1 Performance globale""")

code("""from src_analysis import performance_globale

perf = performance_globale(df_clean)
for k, v in perf.items():
    print(f"{k:20s}: {v}")
""")

md("""### 4.2 Analyse par catégorie""")

code("""from src_analysis import analyse_categorie, evolution_mensuelle_categorie

cat_agg = analyse_categorie(df_clean)
cat_agg
""")

code("""fig, ax = plt.subplots(figsize=(7, 4.5))
sns.barplot(data=cat_agg, x="categorie", y="ca", hue="categorie", legend=False, ax=ax)
ax.set_title("Chiffre d'affaires par catégorie")
ax.set_xlabel("")
plt.show()
""")

code("""monthly_cat = evolution_mensuelle_categorie(df_clean)
fig, ax = plt.subplots(figsize=(8, 4.5))
sns.lineplot(data=monthly_cat, x="mois", y="chiffre_affaires", hue="categorie", marker="o", ax=ax)
ax.set_title("Évolution mensuelle du CA par catégorie")
plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
plt.show()
""")

md("""**Question stratégique — Quelle catégorie doit être priorisée ou optimisée ?**

`Électronique` génère à elle seule ~75% du CA total et domine largement le profit net. C'est la catégorie à **prioriser en stock et en visibilité**. Mais elle affiche aussi le taux de retour le plus élevé (≈14%, contre 2 à 7% pour les autres catégories) : c'est la catégorie à **optimiser en priorité sur la qualité/fiabilité produit**, car chaque point de retour y coûte proportionnellement bien plus cher qu'ailleurs.""")

md("""### 4.3 Analyse géographique""")

code("""from src_analysis import analyse_ville, croissance_mensuelle_ville

ville_agg = analyse_ville(df_clean)
ville_agg
""")

code("""fig, ax = plt.subplots(figsize=(8, 4.5))
sns.barplot(data=ville_agg, y="ville", x="ca", hue="ville", legend=False, ax=ax)
ax.set_title("Chiffre d'affaires par ville")
plt.show()
""")

code("""fig, ax = plt.subplots(figsize=(8, 4.5))
sns.barplot(data=ville_agg.sort_values("taux_annulation", ascending=False), y="ville", x="taux_annulation",
            hue="ville", legend=False, ax=ax)
ax.set_title("Taux d'annulation par ville")
ax.xaxis.set_major_formatter(mticker.PercentFormatter(1.0))
plt.show()
""")

md("""**Question stratégique — Où devons-nous investir davantage ?**

`Kinshasa` est la ville la plus performante (CA et profit les plus élevés, taux d'annulation quasi nul) : elle mérite un **renforcement de l'investissement** (stock, marketing local). À l'inverse, `Douala` combine un CA/profit correct mais un **taux d'annulation anormalement élevé (~12.8%)**, contre quasiment 0% ailleurs — un signal opérationnel local (logistique, paiement, expérience client) à investiguer avant d'investir davantage dans cette ville.""")

md("""### 4.4 Analyse marketing""")

code("""from src_analysis import analyse_marketing

mkt_agg = analyse_marketing(df_clean)
mkt_agg
""")

code("""fig, ax = plt.subplots(figsize=(7, 4.5))
sns.barplot(data=mkt_agg, x="canal_marketing", y="roi", hue="canal_marketing", legend=False, ax=ax)
ax.set_title("ROI marketing par canal")
ax.set_ylabel("ROI (x)")
plt.setp(ax.get_xticklabels(), rotation=15, ha="right")
plt.show()
""")

md("""**Formule ROI :** `ROI = (Revenus - Coût marketing) / Coût marketing`

**Question stratégique — Quel canal mérite plus de budget ? Lequel doit être optimisé ou réduit ?**

`Email` a de très loin le meilleur ROI (~226x) pour un coût marketing très faible : c'est un canal **sous-exploité à renforcer en priorité** (quick win, coût marginal faible). `Instagram Ads` génère le plus de CA en absolu et capte le budget le plus élevé, mais avec un ROI modeste (~24x) : c'est le plus gros gisement d'optimisation en valeur absolue, ce canal doit être **optimisé (ciblage, créa) plutôt que simplement augmenté en budget**. `Influenceur` affiche le ROI le plus faible en proportion (~21x), sur un budget plus restreint.""")

md("""### 4.5 Analyse clients""")

code("""from src_analysis import analyse_clients, pareto_clients, segmentation_clients

clients_info = analyse_clients(df_clean)
print("Nombre total de clients :", clients_info["nb_clients"])
print("% clients récurrents (>1 commande) :", f'{clients_info["pct_recurrents"]:.1%}')
clients_info["top10"]
""")

code("""pareto, part_top20 = pareto_clients(df_clean)
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(pareto["cum_pct_clients"], pareto["cum_pct_ca"])
ax.axvline(20, color="grey", linestyle="--")
ax.axhline(part_top20, color="grey", linestyle="--")
ax.set_title("Courbe de Pareto : concentration du CA par client")
ax.set_xlabel("% cumulé des clients")
ax.set_ylabel("% cumulé du CA")
plt.show()
print(f"Les 20% meilleurs clients génèrent {part_top20}% du CA")
""")

code("""seg = segmentation_clients(df_clean)
seg["segment"].value_counts()
""")

md("""**Question stratégique — Comment améliorer la rétention ?**

75% des clients sont déjà récurrents (>1 commande) et les 20% meilleurs clients concentrent **64.5%** du CA : la base de fidélisation est solide mais **concentrée sur un noyau de clients VIP**. La priorité est un programme de fidélité ciblé sur le segment VIP (352 clients) pour sécuriser cette rente, et une séquence de relance dédiée au segment "Occasionnel" (442 clients, une seule commande) pour les convertir en récurrents.""")

# ============================================================ 5. VISUALISATIONS DE SYNTHESE
md("""<a id="5"></a>
## 5. Visualisations complémentaires""")

code("""fig, ax = plt.subplots(figsize=(7, 5.5))
pivot = df_clean[df_clean["statut_commande"] != "Annulée"].pivot_table(
    index="ville", columns="categorie", values="chiffre_affaires", aggfunc="sum", fill_value=0)
sns.heatmap(pivot, annot=True, fmt=",.0f", cmap="YlGnBu", ax=ax, cbar_kws={"label": "CA"})
ax.set_title("CA par ville x catégorie")
plt.show()
""")

code("""fig, ax = plt.subplots(figsize=(7, 4.5))
sns.histplot(df_clean.loc[df_clean["statut_commande"] != "Annulée", "chiffre_affaires"], bins=50, kde=True, ax=ax)
ax.set_title("Distribution du panier (chiffre d'affaires par commande)")
plt.show()
""")

# ============================================================ 6. RECOS
md("""<a id="6"></a>
## 6. Recommandations stratégiques & conclusion

Voir le résumé exécutif (`reports/resume_executif.md`) pour les 5 recommandations stratégiques détaillées et la conclusion business orientée action. En synthèse :

1. **Prioriser Électronique en stock/visibilité, tout en engageant un plan qualité** pour faire baisser son taux de retour (14%).
2. **Renforcer l'investissement à Kinshasa** (meilleure ville) et **auditer les causes d'annulation à Douala** (12.8% vs ~0% ailleurs) avant tout investissement supplémentaire.
3. **Réallouer une partie du budget Instagram Ads vers Email**, qui offre un ROI ~9x supérieur pour un coût marginal.
4. **Lancer un programme de fidélisation VIP** pour sécuriser les 20% de clients qui génèrent 64.5% du CA.
5. **Mettre en place une séquence de relance pour les clients occasionnels** (442 clients à une seule commande) afin d'augmenter le taux de clients récurrents.
""")

nb["cells"] = cells
with open("notebooks/analyse_afrimarket.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print("Notebook créé :", len(cells), "cellules")
