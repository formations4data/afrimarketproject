# AfriMarket — Résumé exécutif
**Analyse de 6 mois d'activité commerciale (juillet – décembre 2025)**
**Préparé par : Data Analyst | Destinataire : Direction Générale**

---

## 1. Contexte et méthode

AfriMarket a constaté des variations de chiffre d'affaires, un taux de retour préoccupant, des dépenses marketing élevées et des écarts de performance entre villes. Cette analyse s'appuie sur 10 100 commandes brutes couvrant 4 catégories (Électronique, Mode, Beauté, Maison), 8 villes et 4 canaux marketing.

**Qualité des données.** L'audit a révélé 100 commandes dupliquées, 632 prix unitaires négatifs (dont 97% figés à une valeur constante de -50, signature d'un code d'erreur plutôt que d'une inversion de signe), 608 quantités nulles, 614 remises négatives (constante à -0.10, cohérente avec une inversion de signe), ainsi que des incohérences orthographiques (*Kinshassa*/*Kinshasa*) et de casse (*electronique*/*Électronique*, *retournée*/*Retournée*). Après nettoyage : **10 000 commandes propres et fiables** (`df_clean`), soit 99% des données conservées.

**Hypothèse de marge.** En l'absence de coût de revient fourni, la marge brute est estimée à 45% du chiffre d'affaires (coût de revient supposé à 55%) ; le profit net déduit en plus les coûts de livraison et marketing engagés par commande. Les commandes annulées sont exclues du chiffre d'affaires réel.

---

## 2. Performance globale

| Indicateur | Valeur |
|---|---|
| Chiffre d'affaires total | **2 670 519** (unité dataset) |
| Profit net estimé | **1 070 207** |
| Panier moyen | **272** / commande |
| Taux d'annulation | **1.9%** |
| Taux de retour | **8.2%** |
| Clients actifs | **1 772** |

L'activité est globalement saine (annulation faible), mais le taux de retour de 8.2% mérite attention — il est très concentré sur une seule catégorie (voir §3).

---

## 3. Analyse par catégorie

| Catégorie | CA | Profit net | Taux de retour |
|---|---|---|---|
| **Électronique** | 1 991 810 (75% du CA) | 854 215 | **13.9%** |
| Maison | 401 544 | 155 483 | 4.8% |
| Mode | 195 076 | 48 812 | 7.5% |
| Beauté | 82 089 | 11 698 | 2.9% |

**Constat clé :** Électronique génère les trois quarts du CA et la quasi-totalité du profit — c'est le moteur économique de l'entreprise. Mais son taux de retour (13.9%) est 2 à 5 fois supérieur aux autres catégories, ce qui grève sa rentabilité réelle (coûts de logistique inverse, remboursements, image client) bien au-delà de ce que montre le profit comptable.

---

## 4. Analyse géographique

| Ville | CA | Profit | Taux d'annulation |
|---|---|---|---|
| **Kinshasa** | 810 104 (1ère) | 325 656 | 0.3% |
| Abidjan | 534 445 | 215 280 | 0.0% |
| Dakar | 372 084 | 148 519 | 0.0% |
| **Douala** | 343 701 | 137 813 | **12.8%** |
| Lomé / Cotonou / Libreville / Brazzaville | 114 811 – 196 232 | 45 518 – 78 434 | 0.0% |

**Constat clé :** Kinshasa est de loin la ville la plus performante (CA, profit, quasi zéro annulation) et un candidat naturel à un investissement renforcé. Douala se distingue par un **taux d'annulation anormal de 12.8%**, contre 0.3% pour Kinshasa (2ème ville la plus touchée, soit ~42x moins) et 0% pour les six autres villes — un signal opérationnel localisé (paiement, logistique locale, expérience client) qu'il faut diagnostiquer avant d'y investir davantage, sous peine de démultiplier un problème non résolu.

---

## 5. Analyse marketing

| Canal | CA généré | Coût marketing | ROI | Rétention |
|---|---|---|---|---|
| **Email** | 569 904 | 2 511 | **x226** | 92.5% |
| Google Ads | 698 739 | 13 891 | x49 | 92.3% |
| Instagram Ads | 1 011 475 | 40 050 | x24 | 91.3% |
| Influenceur | 390 401 | 17 435 | x21 | 91.7% |

*ROI = (CA − coût marketing) / coût marketing.*

**Constat clé :** Instagram Ads capte le plus gros budget (40 050) et génère le plus de CA en absolu, mais avec un ROI modeste (x24) : c'est le plus gros gisement d'optimisation en valeur absolue. Influenceur affiche le ROI le plus faible en proportion (x21), sur un budget plus restreint (17 435). Email, à l'inverse, ne représente qu'une fraction du budget marketing total mais affiche un ROI ~4.6 fois supérieur à Google Ads et ~10.6 fois supérieur au canal le moins efficace (Influenceur). Il existe une marge de manœuvre claire pour rééquilibrer l'allocation budgétaire.

---

## 6. Analyse clients

- **1 772 clients actifs**, dont **75.5% récurrents** (plus d'une commande) — une base de fidélisation globalement solide.
- **Concentration Pareto :** les 20% de clients les plus rentables génèrent **64.5%** du chiffre d'affaires total.
- **Segmentation :** 352 clients **VIP**, 965 **Récurrents**, 442 **Occasionnels** (une seule commande, à risque de churn).

**Constat clé :** la dépendance à un noyau de clients VIP est un facteur de risque autant qu'un actif — leur rétention doit être activement protégée, tandis que le segment "Occasionnel" représente le plus grand gisement de croissance immédiat par la relance.

---

## 7. Cinq recommandations stratégiques

1. **Sécuriser et développer la catégorie Électronique tout en réduisant ses retours.** Elle porte 75% du CA : maintenir un stock prioritaire et une visibilité forte, mais lancer un plan qualité ciblé (contrôle fournisseur, fiches produit plus précises, politique de retour repensée) pour faire baisser un taux de retour presque 5x supérieur à la moyenne des autres catégories.

2. **Concentrer l'investissement additionnel sur Kinshasa, et auditer Douala avant tout investissement supplémentaire.** Kinshasa combine le meilleur CA et une fiabilité opérationnelle quasi parfaite. Douala affiche un taux d'annulation ~42 fois supérieur à celui de Kinshasa (la 2ème ville la plus touchée, à 0.3%), les six autres villes étant à 0% : il faut en identifier la cause racine (méthode de paiement locale, fiabilité de livraison, service client) avant d'y injecter du budget marketing, qui amplifierait sinon un problème non résolu.

3. **Réallouer une partie du budget Instagram Ads vers le canal Email, et revoir le canal Influenceur.** Instagram Ads concentre le plus gros budget (40 050) pour un ROI modeste (x24) : c'est le plus gros gisement d'optimisation. Email offre un ROI ~9x supérieur (x226 vs x24) pour un coût marginal quasi négligeable (2 511). Influenceur, dont le ROI (x21) est le plus faible en proportion, doit aussi être revu malgré son budget plus restreint. Un test A/B de réallocation progressive (ex. +30% budget Email, -15% Instagram) permettrait de vérifier le gain net avant généralisation.

4. **Lancer un programme de fidélisation dédié aux clients VIP.** Les 352 clients VIP portent une part disproportionnée du CA (top 20% = 64.5%) : avantages exclusifs, service prioritaire, gestion de compte dédiée pour sécuriser cette rente contre la concurrence.

5. **Mettre en place une séquence de relance automatisée pour les clients occasionnels.** 442 clients n'ont commandé qu'une fois : un parcours de réactivation (email/SMS à J+30, offre de bienvenue seconde commande) peut convertir une partie significative de ce segment en clients récurrents, avec un ROI potentiellement élevé compte tenu du coût d'acquisition déjà amorti.

---

## 8. Conclusion business orientée action

AfriMarket dispose d'un modèle rentable et d'une base client majoritairement fidèle, mais sa performance est **concentrée et donc fragile** : une catégorie (Électronique) porte l'essentiel du CA, une ville (Douala) capte une anomalie opérationnelle non expliquée, et un canal marketing (Instagram Ads) absorbe un budget disproportionné à son efficacité réelle. Les prochaines 90 jours devraient prioriser, dans l'ordre : (1) l'audit opérationnel de Douala — coût faible, risque de ne rien faire élevé ; (2) le test de réallocation budgétaire Instagram → Email — gain rapide à faible risque ; (3) le lancement du programme VIP — protection du cœur de revenu. Le plan qualité Électronique et la relance des clients occasionnels, plus structurants, s'inscrivent sur un horizon 2-3 trimestres.
