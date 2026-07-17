"""
Dashboard interactif Streamlit - AfriMarket
Lancer avec : streamlit run dashboard/app.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.express as px

from src_pipeline import load_clean
from src_analysis import (
    performance_globale, analyse_categorie, evolution_mensuelle_categorie,
    analyse_ville, croissance_mensuelle_ville, analyse_marketing,
    analyse_clients, pareto_clients, segmentation_clients,
)

st.set_page_config(page_title="AfriMarket - Dashboard", layout="wide", page_icon="📊")

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "df_clean.csv")


@st.cache_data
def get_data():
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH, encoding="utf-8", parse_dates=["date_commande"])
    else:
        df = load_clean()
    return df


df = get_data()

# ---------------------------------------------------------------- SIDEBAR
st.sidebar.title("AfriMarket 📊")
st.sidebar.caption("Filtres d'analyse")

min_date, max_date = df["date_commande"].min(), df["date_commande"].max()
date_range = st.sidebar.date_input(
    "Période", value=(min_date, max_date), min_value=min_date, max_value=max_date
)

villes = st.sidebar.multiselect("Ville", sorted(df["ville"].unique()), default=list(sorted(df["ville"].unique())))
categories = st.sidebar.multiselect("Catégorie", sorted(df["categorie"].unique()), default=list(sorted(df["categorie"].unique())))
canaux = st.sidebar.multiselect("Canal marketing", sorted(df["canal_marketing"].unique()), default=list(sorted(df["canal_marketing"].unique())))
statuts = st.sidebar.multiselect("Statut commande", sorted(df["statut_commande"].unique()), default=list(sorted(df["statut_commande"].unique())))

if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start, end = min_date, max_date

mask = (
    (df["date_commande"] >= start) & (df["date_commande"] <= end)
    & df["ville"].isin(villes) & df["categorie"].isin(categories)
    & df["canal_marketing"].isin(canaux) & df["statut_commande"].isin(statuts)
)
dff = df[mask]

st.sidebar.markdown("---")
st.sidebar.caption(f"{len(dff):,} commandes sélectionnées sur {len(df):,}")

# ---------------------------------------------------------------- HEADER + KPIs
st.title("Analyse stratégique AfriMarket")
st.caption("Dashboard interactif — 6 mois d'activité commerciale (données nettoyées : `df_clean`)")

if dff.empty:
    st.warning("Aucune commande ne correspond aux filtres sélectionnés.")
    st.stop()

perf = performance_globale(dff)

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("CA total", f"{perf['ca_total']:,.0f}")
k2.metric("Profit net", f"{perf['profit_total']:,.0f}")
k3.metric("Panier moyen", f"{perf['panier_moyen']:,.0f}")
k4.metric("Taux annulation", f"{perf['taux_annulation']:.1%}")
k5.metric("Taux retour", f"{perf['taux_retour']:.1%}")
k6.metric("Clients actifs", f"{perf['nb_clients']:,}")

st.markdown("---")

tab_cat, tab_geo, tab_mkt, tab_clients = st.tabs(
    ["📦 Catégorie", "🌍 Géographie", "📣 Marketing", "👥 Clients"]
)

# ---------------------------------------------------------------- TAB CATEGORIE
with tab_cat:
    cat_agg = analyse_categorie(dff)
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(cat_agg, x="categorie", y="ca", color="categorie", title="Chiffre d'affaires par catégorie",
                     text_auto=",.0f")
        st.plotly_chart(fig, width='stretch')
    with c2:
        fig = px.bar(cat_agg, x="categorie", y="taux_retour", color="categorie",
                     title="Taux de retour par catégorie")
        fig.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig, width='stretch')

    monthly_cat = evolution_mensuelle_categorie(dff)
    fig = px.line(monthly_cat, x="mois", y="chiffre_affaires", color="categorie", markers=True,
                  title="Évolution mensuelle du CA par catégorie")
    st.plotly_chart(fig, width='stretch')

    st.dataframe(cat_agg.style.format({"ca": "{:,.0f}", "marge": "{:,.0f}", "profit": "{:,.0f}", "taux_retour": "{:.1%}"}),
                 width='stretch')

# ---------------------------------------------------------------- TAB GEO
with tab_geo:
    ville_agg = analyse_ville(dff)
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(ville_agg.sort_values("ca"), y="ville", x="ca", orientation="h", color="ca",
                     title="Chiffre d'affaires par ville", color_continuous_scale="Blues")
        st.plotly_chart(fig, width='stretch')
    with c2:
        fig = px.bar(ville_agg.sort_values("taux_annulation"), y="ville", x="taux_annulation", orientation="h",
                     color="taux_annulation", title="Taux d'annulation par ville", color_continuous_scale="Reds")
        fig.update_xaxes(tickformat=".0%")
        st.plotly_chart(fig, width='stretch')

    pivot = dff[dff["statut_commande"] != "Annulée"].pivot_table(
        index="ville", columns="categorie", values="chiffre_affaires", aggfunc="sum", fill_value=0)
    fig = px.imshow(pivot, text_auto=",.0f", color_continuous_scale="YlGnBu", title="CA par ville x catégorie",
                     aspect="auto")
    st.plotly_chart(fig, width='stretch')

    monthly_ville = croissance_mensuelle_ville(dff)
    top_villes = ville_agg.sort_values("ca", ascending=False)["ville"].head(4).tolist()
    fig = px.line(monthly_ville[monthly_ville["ville"].isin(top_villes)], x="mois", y="chiffre_affaires",
                  color="ville", markers=True, title="Évolution mensuelle du CA - Top 4 villes")
    st.plotly_chart(fig, width='stretch')

    st.dataframe(ville_agg.style.format({"ca": "{:,.0f}", "profit": "{:,.0f}", "taux_annulation": "{:.1%}"}),
                 width='stretch')

# ---------------------------------------------------------------- TAB MARKETING
with tab_mkt:
    mkt_agg = analyse_marketing(dff)
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(mkt_agg, x="canal_marketing", y="roi", color="canal_marketing", title="ROI par canal marketing")
        st.plotly_chart(fig, width='stretch')
    with c2:
        melted = mkt_agg.melt(id_vars="canal_marketing", value_vars=["ca", "cout_marketing"],
                               var_name="indicateur", value_name="valeur")
        fig = px.bar(melted, x="canal_marketing", y="valeur", color="indicateur", barmode="group", log_y=True,
                     title="CA généré vs coût marketing par canal (log)")
        st.plotly_chart(fig, width='stretch')

    st.caption("ROI = (CA − coût marketing) / coût marketing")
    st.dataframe(mkt_agg.style.format({"ca": "{:,.0f}", "cout_marketing": "{:,.0f}", "roi": "{:.1f}",
                                       "taux_retention": "{:.1%}"}), width='stretch')

# ---------------------------------------------------------------- TAB CLIENTS
with tab_clients:
    clients_info = analyse_clients(dff)
    c1, c2, c3 = st.columns(3)
    c1.metric("Clients actifs", f"{clients_info['nb_clients']:,}")
    c2.metric("% clients récurrents", f"{clients_info['pct_recurrents']:.1%}")

    pareto, part20 = pareto_clients(dff)
    c3.metric("CA généré par le top 20% clients", f"{part20}%")

    c1, c2 = st.columns(2)
    with c1:
        fig = px.line(pareto, x="cum_pct_clients", y="cum_pct_ca", title="Courbe de Pareto (concentration du CA)")
        fig.add_hline(y=part20, line_dash="dash", line_color="grey")
        fig.add_vline(x=20, line_dash="dash", line_color="grey")
        st.plotly_chart(fig, width='stretch')
    with c2:
        seg = segmentation_clients(dff)
        counts = seg["segment"].value_counts().reset_index()
        counts.columns = ["segment", "nb_clients"]
        fig = px.pie(counts, names="segment", values="nb_clients", title="Segmentation des clients")
        st.plotly_chart(fig, width='stretch')

    st.subheader("Top 10 clients par chiffre d'affaires")
    st.dataframe(clients_info["top10"].style.format({"chiffre_affaires": "{:,.0f}"}), width='stretch')

st.markdown("---")
st.caption("Source : afrimarket_dataset_senior.csv (nettoyé) — Dashboard généré avec Streamlit + Plotly")
