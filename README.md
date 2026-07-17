# Analyse Stratégique AfriMarket

Analyse de données e-commerce pour **AfriMarket**, entreprise panafricaine opérant dans 8 villes d'Afrique francophone sur 4 catégories (Électronique, Mode, Beauté, Maison). Le projet couvre l'ensemble de la chaîne : audit et nettoyage des données, feature engineering, analyses business, visualisations, et livrables prêts pour la direction (notebook, dashboard interactif, résumé exécutif, présentation PowerPoint, rapport PDF).

## Sommaire

- [Structure du projet](#structure-du-projet)
- [Installation](#installation)
- [Utilisation](#utilisation)
  - [Notebook d'analyse](#notebook-danalyse)
  - [Dashboard Streamlit](#dashboard-streamlit)
  - [Régénérer les livrables](#régénérer-les-livrables)
- [Données](#données)
- [Qualité des données et nettoyage](#qualité-des-données-et-nettoyage)
- [Résultats clés](#résultats-clés)
- [Charte graphique](#charte-graphique)
- [Déploiement](#déploiement)

## Structure du projet

```
Projet AfriMarket/
├── data/
│   ├── afrimarket_dataset_senior.csv    # Dataset brut (10 100 commandes, 6 mois)
│   └── df_clean.csv                     # Dataset nettoyé + features (10 000 commandes, 22 colonnes)
│
├── src_pipeline.py                      # Chargement, nettoyage (clean_data) et feature engineering (add_features)
├── src_analysis.py                      # Fonctions d'analyse business (performance, catégorie, ville, marketing, clients)
├── src_viz.py                           # Visualisations Matplotlib/Seaborn (palette neutre, pour le notebook)
├── src_viz_brand.py                     # Visualisations aux couleurs de la marque (pour PPT/PDF)
├── brand.py                             # Charte graphique (couleurs, logo) extraite de assets/logo.png
│
├── notebooks/
│   └── analyse_afrimarket.ipynb         # Notebook complet et exécuté : audit → cleaning → analyses → viz
│
├── dashboard/
│   └── app.py                           # Dashboard interactif Streamlit (filtres, KPIs, 4 onglets)
│
├── figures/                             # Graphiques Matplotlib/Seaborn (palette neutre) exportés en PNG
├── figures_brand/                       # Mêmes graphiques, palette de marque, pour PPT/PDF
├── assets/
│   └── logo.png                         # Logo Afri-Farmers Market
│
├── reports/
│   ├── resume_executif.md               # Résumé exécutif (5 pages) + 5 recommandations + conclusion
│   ├── AfriMarket_Presentation_Direction.pptx  # Présentation PowerPoint pour la direction (15 slides)
│   ├── AfriMarket_Rapport_Direction.pdf         # Rapport PDF professionnel (9 pages)
│   └── dashboard_screenshots/           # Captures d'écran de vérification du dashboard
│
├── build_notebook.py                    # Génère notebooks/analyse_afrimarket.ipynb
├── build_pptx.py                        # Génère reports/AfriMarket_Presentation_Direction.pptx
├── build_pdf.py                         # Génère reports/AfriMarket_Rapport_Direction.pdf
│
├── requirements.txt                     # Dépendances du dashboard (déploiement Streamlit Cloud)
└── README.md
```

## Installation

Prérequis : Python 3.10+.

```bash
# Dépendances minimales pour faire tourner le dashboard
pip install -r requirements.txt

# Dépendances additionnelles pour régénérer notebook / figures / PPT / PDF
pip install matplotlib seaborn nbformat nbclient ipykernel python-pptx reportlab Pillow
python -m ipykernel install --user --name python3 --display-name "Python 3"
```

## Utilisation

### Notebook d'analyse

Le notebook `notebooks/analyse_afrimarket.ipynb` est déjà généré et exécuté (audit, nettoyage, feature engineering, 5 blocs d'analyse, visualisations). Ouvrez-le directement avec Jupyter ou VS Code :

```bash
jupyter notebook notebooks/analyse_afrimarket.ipynb
```

### Dashboard Streamlit

```bash
streamlit run dashboard/app.py
```

Le dashboard propose des filtres (période, ville, catégorie, canal marketing, statut de commande), des KPIs globaux et 4 onglets : **Catégorie**, **Géographie**, **Marketing**, **Clients**. Il se recharge automatiquement à chaque changement de filtre et lit `data/df_clean.csv` (régénéré via `src_pipeline.load_clean()` si ce fichier est absent).

### Régénérer les livrables

Chaque script peut être relancé indépendamment après une modification des données ou du code d'analyse :

```bash
python src_pipeline.py       # régénère data/df_clean.csv
python src_viz.py            # régénère figures/ (palette neutre)
python src_viz_brand.py      # régénère figures_brand/ (palette de marque)
python build_notebook.py      # régénère le notebook (non exécuté)
python build_pptx.py         # régénère la présentation PowerPoint
python build_pdf.py          # régénère le rapport PDF
```

Pour ré-exécuter le notebook après régénération :

```bash
python -c "
import nbformat
from nbclient import NotebookClient
with open('notebooks/analyse_afrimarket.ipynb', encoding='utf-8') as f:
    nb = nbformat.read(f, as_version=4)
NotebookClient(nb, timeout=300, kernel_name='python3', resources={'metadata': {'path': '.'}}).execute()
with open('notebooks/analyse_afrimarket.ipynb', 'w', encoding='utf-8') as f:
    nbformat.write(nb, f)
"
```

## Données

Le dataset brut (`data/afrimarket_dataset_senior.csv`, 10 100 lignes) couvre 6 mois d'activité commerciale (juillet–décembre 2025) :

| Colonne | Description |
|---|---|
| `id_commande`, `id_client` | Identifiants commande / client |
| `date_commande` | Date de la commande |
| `ville` | Ville de livraison (8 villes) |
| `categorie`, `nom_produit` | Catégorie (Électronique, Mode, Beauté, Maison) et produit |
| `prix_unitaire`, `quantite`, `remise` | Prix, quantité commandée, taux de remise |
| `cout_livraison`, `cout_marketing` | Coûts logistique et marketing associés à la commande |
| `methode_paiement`, `canal_marketing` | Moyen de paiement, canal d'acquisition |
| `statut_commande` | Livrée / Retournée / Annulée |

Après nettoyage et feature engineering (`src_pipeline.py`), `data/df_clean.csv` (10 000 lignes, 22 colonnes) ajoute : `chiffre_affaires`, `marge_brute`, `profit_net`, `mois`, `indicateur_retour`, `indicateur_annulation`, `nombre_commandes_par_client`, `valeur_vie_client`.

## Qualité des données et nettoyage

| Problème détecté | Traitement appliqué |
|---|---|
| 100 commandes dupliquées | Suppression des doublons (1ère occurrence conservée) |
| 632 prix unitaires négatifs (~97% figés à -50, code d'erreur) | Imputation par la médiane du même produit |
| 608 quantités nulles | Imputation par la médiane de la catégorie |
| 614 remises négatives (constante -0.10, inversion de signe) | Valeur absolue |
| `Kinshassa` / `Kinshasa`, `electronique` / `Électronique`, `retournée` / `Retournée` | Harmonisation orthographe et casse |

**Hypothèse de marge documentée :** en l'absence de coût de revient dans les données, la marge brute est estimée à 45% du chiffre d'affaires. Les commandes annulées sont exclues du chiffre d'affaires réel.

## Résultats clés

- **CA total : 2 670 519** sur 10 000 commandes propres — profit net estimé à 1 070 207, taux d'annulation 1,9%, taux de retour 8,2%.
- **Électronique** génère 75% du CA et l'essentiel du profit, mais avec un taux de retour (13,9%) 2 à 5 fois supérieur aux autres catégories.
- **Kinshasa** est la ville la plus performante ; **Douala** affiche un taux d'annulation anormal (12,8%, contre ~0% ailleurs) à investiguer en priorité.
- **Email** offre le meilleur ROI marketing (x226) pour un coût marginal négligeable ; **Instagram Ads** concentre le plus gros budget (40 050) pour un ROI modeste (x24) ; **Influenceur** a le ROI le plus faible en proportion (x21).
- **75,5%** des 1 772 clients actifs sont récurrents ; les 20% de clients les plus rentables génèrent **64,5%** du CA total.

Le détail complet (5 recommandations stratégiques et conclusion business) est dans `reports/resume_executif.md`, la présentation `reports/AfriMarket_Presentation_Direction.pptx` et le rapport `reports/AfriMarket_Rapport_Direction.pdf`.

## Charte graphique

Les couleurs de marque (`brand.py`) sont extraites directement de `assets/logo.png` :

| Couleur | Hex | Usage |
|---|---|---|
| Vert sapin (primaire) | `#00604E` | Fonds d'en-tête, titres, barres principales |
| Vert feuille (accent) | `#00A651` | Accents, barres secondaires |
| Vert feuille clair | `#4CD964` | Highlights, valeurs positives |
| Blanc | `#FFFFFF` | Texte sur fond sombre |

Ces couleurs sont utilisées dans `src_viz_brand.py`, `build_pptx.py` et `build_pdf.py` pour garantir la cohérence visuelle des livrables destinés à la direction.

## Déploiement

Le dashboard peut être déployé sur [Streamlit Community Cloud](https://streamlit.io/cloud) :

1. Pousser le dépôt sur GitHub (`origin` déjà configuré : `formations4data/afrimarketproject`).
2. Sur Streamlit Cloud, créer une nouvelle app en pointant vers `dashboard/app.py`.
3. Streamlit Cloud installe automatiquement `requirements.txt` à la racine du dépôt.

---
*Confidentiel — usage interne AfriMarket.*
