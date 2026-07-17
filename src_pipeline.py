"""
Pipeline d'analyse AfriMarket : audit -> nettoyage -> feature engineering -> analyses -> visualisations.
Ce script est la source de vérité; le notebook Jupyter et le dashboard Streamlit le réutilisent.
"""
import re
import unicodedata
import pandas as pd
import numpy as np

RAW_PATH = "data/afrimarket_dataset_senior.csv"
CLEAN_PATH = "data/df_clean.csv"


def strip_accents(s):
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    )


def load_raw(path=RAW_PATH):
    return pd.read_csv(path, encoding="utf-8")


def clean_data(df_raw):
    df = df_raw.copy()

    # 1. Doublons exacts (id_commande dupliqué avec la même ligne) -> on garde la 1ere occurrence
    df = df.drop_duplicates(subset=["id_commande"], keep="first").reset_index(drop=True)

    # 2. Dates
    df["date_commande"] = pd.to_datetime(df["date_commande"], errors="coerce")

    # 3. Villes : corriger la faute d'orthographe "Kinshassa" -> "Kinshasa"
    df["ville"] = df["ville"].replace({"Kinshassa": "Kinshasa"})

    # 4. Catégories : unifier casse/accents ("electronique" vs "Électronique")
    canon_categories = {"mode": "Mode", "beaute": "Beauté", "maison": "Maison", "electronique": "Électronique"}
    df["categorie"] = df["categorie"].apply(lambda s: canon_categories.get(strip_accents(s).lower(), s))

    # 5. Statuts de commande : unifier la casse
    canon_statuts = {"livree": "Livrée", "annulee": "Annulée", "retournee": "Retournée"}
    df["statut_commande"] = df["statut_commande"].apply(lambda s: canon_statuts.get(strip_accents(s).lower(), s))

    # 6. Remise : les valeurs négatives sont une inversion de signe (constante à -0.10 -> 0.10 plausible)
    df["remise"] = df["remise"].abs()

    # 7. Prix unitaire aberrant : les valeurs négatives sont des codes d'erreur (majoritairement -50,
    #    indépendants du vrai prix du produit) -> traitées comme manquantes puis imputées par la
    #    médiane du même produit (nom_produit), qui est un bien meilleur estimateur que la moyenne
    #    globale car chaque produit a une fourchette de prix propre.
    df.loc[df["prix_unitaire"] < 0, "prix_unitaire"] = np.nan
    df["prix_unitaire"] = df.groupby("nom_produit")["prix_unitaire"].transform(
        lambda s: s.fillna(s.median())
    )

    # 8. Quantité nulle : une commande avec 0 article n'a pas de sens business -> traitée comme
    #    manquante puis imputée par la médiane de la catégorie.
    df.loc[df["quantite"] == 0, "quantite"] = np.nan
    df["quantite"] = df.groupby("categorie")["quantite"].transform(
        lambda s: s.fillna(s.median())
    ).astype(int)

    # 9. Types finaux
    df["cout_livraison"] = df["cout_livraison"].round(2)
    df["cout_marketing"] = df["cout_marketing"].round(2)
    df["prix_unitaire"] = df["prix_unitaire"].round(2)

    return df.reset_index(drop=True)


def add_features(df):
    df = df.copy()

    # Chiffre d'affaires de la ligne (après remise)
    df["chiffre_affaires"] = (df["prix_unitaire"] * df["quantite"] * (1 - df["remise"])).round(2)

    # Marge brute estimée : hypothèse coût de revient = 55% du prix (marge commerciale brute de 45%)
    # avant frais logistiques -- hypothèse documentée dans le résumé exécutif.
    COGS_RATE = 0.55
    df["marge_brute"] = (df["chiffre_affaires"] * (1 - COGS_RATE)).round(2)

    # Profit net estimé = marge brute - coûts logistique et marketing de la commande
    df["profit_net"] = (df["marge_brute"] - df["cout_livraison"] - df["cout_marketing"]).round(2)

    # Mois (période)
    df["mois"] = df["date_commande"].dt.to_period("M").astype(str)

    # Indicateur de retour
    df["indicateur_retour"] = (df["statut_commande"] == "Retournée").astype(int)
    df["indicateur_annulation"] = (df["statut_commande"] == "Annulée").astype(int)

    # Nombre de commandes par client (répété sur chaque ligne du client)
    df["nombre_commandes_par_client"] = df.groupby("id_client")["id_commande"].transform("count")

    # Valeur vie client (CLV simplifiée) = somme du CA généré par client sur la période
    # (uniquement les commandes livrées/retournées comptent comme du revenu réel, les annulées non)
    ca_reel = df["chiffre_affaires"].where(df["statut_commande"] != "Annulée", 0)
    df["_ca_reel_ligne"] = ca_reel
    clv = df.groupby("id_client")["_ca_reel_ligne"].transform("sum")
    df["valeur_vie_client"] = clv.round(2)
    df = df.drop(columns=["_ca_reel_ligne"])

    return df


def load_clean():
    df_raw = load_raw()
    df = clean_data(df_raw)
    df = add_features(df)
    return df


if __name__ == "__main__":
    df = load_clean()
    df.to_csv(CLEAN_PATH, index=False, encoding="utf-8")
    print(f"df_clean shape: {df.shape}")
    print(df.dtypes)
