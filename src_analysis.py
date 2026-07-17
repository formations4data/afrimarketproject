"""
Fonctions d'analyse business pour AfriMarket, à partir de df_clean.
Chaque fonction retourne un DataFrame prêt à être visualisé (notebook et dashboard Streamlit).
"""
import pandas as pd
import numpy as np


# ---------- 4.1 Performance globale ----------

def performance_globale(df):
    df_valide = df[df["statut_commande"] != "Annulée"]
    ca_total = df_valide["chiffre_affaires"].sum()
    profit_total = df_valide["profit_net"].sum()
    panier_moyen = df_valide["chiffre_affaires"].mean()
    taux_annulation = (df["statut_commande"] == "Annulée").mean()
    taux_retour = (df["statut_commande"] == "Retournée").mean()
    return {
        "ca_total": round(ca_total, 2),
        "profit_total": round(profit_total, 2),
        "panier_moyen": round(panier_moyen, 2),
        "taux_annulation": round(taux_annulation, 4),
        "taux_retour": round(taux_retour, 4),
        "nb_commandes": len(df),
        "nb_clients": df["id_client"].nunique(),
    }


# ---------- 4.2 Analyse par catégorie ----------

def analyse_categorie(df):
    df_valide = df[df["statut_commande"] != "Annulée"]
    agg = df_valide.groupby("categorie").agg(
        ca=("chiffre_affaires", "sum"),
        marge=("marge_brute", "sum"),
        profit=("profit_net", "sum"),
        nb_commandes=("id_commande", "count"),
    ).reset_index()
    taux_retour = df.groupby("categorie")["indicateur_retour"].mean().reset_index(name="taux_retour")
    agg = agg.merge(taux_retour, on="categorie")
    agg = agg.sort_values("ca", ascending=False)
    return agg


def evolution_mensuelle_categorie(df):
    df_valide = df[df["statut_commande"] != "Annulée"]
    return (
        df_valide.groupby(["mois", "categorie"])["chiffre_affaires"]
        .sum()
        .reset_index()
        .sort_values(["categorie", "mois"])
    )


# ---------- 4.3 Analyse géographique ----------

def analyse_ville(df):
    df_valide = df[df["statut_commande"] != "Annulée"]
    agg = df_valide.groupby("ville").agg(
        ca=("chiffre_affaires", "sum"),
        profit=("profit_net", "sum"),
        nb_commandes=("id_commande", "count"),
    ).reset_index()
    taux_annulation = df.groupby("ville")["indicateur_annulation"].mean().reset_index(name="taux_annulation")
    agg = agg.merge(taux_annulation, on="ville")
    agg = agg.sort_values("ca", ascending=False)
    return agg


def croissance_mensuelle_ville(df):
    df_valide = df[df["statut_commande"] != "Annulée"]
    monthly = df_valide.groupby(["ville", "mois"])["chiffre_affaires"].sum().reset_index()
    monthly = monthly.sort_values(["ville", "mois"])
    monthly["croissance_pct"] = monthly.groupby("ville")["chiffre_affaires"].pct_change() * 100
    return monthly


# ---------- 4.4 Analyse marketing ----------

def analyse_marketing(df):
    df_valide = df[df["statut_commande"] != "Annulée"]
    ca_par_canal = df_valide.groupby("canal_marketing")["chiffre_affaires"].sum()
    cout_par_canal = df.groupby("canal_marketing")["cout_marketing"].sum()  # coût engagé même si annulé
    retention = df.groupby("canal_marketing")["indicateur_retour"].apply(lambda s: 1 - s.mean())

    agg = pd.DataFrame({
        "ca": ca_par_canal,
        "cout_marketing": cout_par_canal,
    }).reset_index()
    agg["roi"] = (agg["ca"] - agg["cout_marketing"]) / agg["cout_marketing"]
    agg["taux_retention"] = retention.reindex(agg["canal_marketing"]).values
    agg = agg.sort_values("roi", ascending=False)
    return agg


# ---------- 4.5 Analyse clients ----------

def analyse_clients(df):
    df_valide = df[df["statut_commande"] != "Annulée"]
    nb_clients = df["id_client"].nunique()
    clients_recurrents = (df.groupby("id_client")["id_commande"].count() > 1)
    pct_recurrents = clients_recurrents.mean()

    ca_par_client = df_valide.groupby("id_client")["chiffre_affaires"].sum().sort_values(ascending=False)
    top10 = ca_par_client.head(10).reset_index()
    top10.columns = ["id_client", "chiffre_affaires"]

    return {
        "nb_clients": nb_clients,
        "pct_recurrents": round(pct_recurrents, 4),
        "ca_par_client": ca_par_client,
        "top10": top10,
    }


def pareto_clients(df):
    df_valide = df[df["statut_commande"] != "Annulée"]
    ca_par_client = df_valide.groupby("id_client")["chiffre_affaires"].sum().sort_values(ascending=False)
    total_ca = ca_par_client.sum()
    cum_pct_ca = ca_par_client.cumsum() / total_ca * 100
    cum_pct_clients = (np.arange(1, len(ca_par_client) + 1) / len(ca_par_client)) * 100
    pareto = pd.DataFrame({
        "cum_pct_clients": cum_pct_clients,
        "cum_pct_ca": cum_pct_ca.values,
    })
    # part du CA générée par les 20% meilleurs clients
    idx_20 = int(len(pareto) * 0.2)
    part_top20 = pareto.iloc[idx_20 - 1]["cum_pct_ca"] if idx_20 > 0 else pareto.iloc[0]["cum_pct_ca"]
    return pareto, round(part_top20, 1)


def segmentation_clients(df):
    df_valide = df[df["statut_commande"] != "Annulée"]
    client_stats = df_valide.groupby("id_client").agg(
        ca=("chiffre_affaires", "sum"),
        nb_commandes=("id_commande", "count"),
    ).reset_index()

    def segment(row):
        if row["ca"] >= client_stats["ca"].quantile(0.8):
            return "VIP"
        elif row["nb_commandes"] >= 2:
            return "Récurrent"
        else:
            return "Occasionnel"

    client_stats["segment"] = client_stats.apply(segment, axis=1)
    return client_stats
