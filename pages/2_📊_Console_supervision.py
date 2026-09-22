"""
CamerTrust — E3 — Console de supervision (page secondaire, opérateur)
========================================================================

Livrable S8 du plan (p.12) : page secondaire à destination de l'analyste
côté opérateur — CamerTrust reste avant tout un service pour l'abonné,
cette console ne sert qu'à « démontrer le service, pas à le définir »
(changement de cap documenté en page 1 du plan).

4 indicateurs + export CSV, filtrage par date et montant comme documenté
dans la référence des endpoints (`GET /admin/alerts`, p.9 du plan).
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

import api_client
from style import PHONE_CSS

st.set_page_config(page_title="CamerTrust — Supervision", page_icon="📊", layout="wide")
st.markdown(PHONE_CSS, unsafe_allow_html=True)

st.title("📊 Console de supervision")
st.caption("Vue opérateur — secondaire. L'abonné reste acteur de sa propre sécurité ; cette page ne fait que rendre le service visible côté institutionnel.")

online = api_client.is_online()
st.markdown(
    f'<span class="{"status-pill-online" if online else "status-pill-offline"}">'
    f'{"API en ligne" if online else "Mode démo hors ligne"}</span>',
    unsafe_allow_html=True,
)

if st.button("🔄 Actualiser"):
    st.rerun()

stats = api_client.get_admin_stats()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Transactions du jour", f"{stats.get('transactions_jour', 0):,}".replace(",", " "))
c2.metric("Alertes émises", stats.get("alertes_jour", 0))
c3.metric("Taux de réponse abonnés", f"{stats.get('taux_reponse_pct', 0)} %")
c4.metric("Comptes protégés (bloqués)", stats.get("alertes_bloquees", 0))

st.divider()
st.subheader("Alertes récentes")

alertes = api_client.get_admin_alerts()
if not alertes:
    st.info("Aucune alerte enregistrée.")
else:
    df = pd.DataFrame(alertes)
    df["horodatage"] = pd.to_datetime(df["horodatage"], errors="coerce")

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        dates_disponibles = sorted(df["horodatage"].dt.date.dropna().unique())
        date_choisie = st.selectbox(
            "Filtrer par date", ["Toutes"] + [d.isoformat() for d in dates_disponibles],
        )
    with col_f2:
        montant_min = st.number_input("Montant minimum (FCFA)", min_value=0, value=0, step=10_000)
    with col_f3:
        statuts = ["Tous"] + sorted(df["statut"].unique().tolist())
        statut_choisi = st.selectbox("Filtrer par statut", statuts)

    df_filtre = df.copy()
    if date_choisie != "Toutes":
        df_filtre = df_filtre[df_filtre["horodatage"].dt.date.astype(str) == date_choisie]
    if montant_min:
        df_filtre = df_filtre[df_filtre["montant"] >= montant_min]
    if statut_choisi != "Tous":
        df_filtre = df_filtre[df_filtre["statut"] == statut_choisi]

    libelle_statut = {"en_attente": "En attente", "confirmee": "Confirmée", "bloquee": "Bloquée"}
    df_affiche = df_filtre.rename(columns={
        "horodatage": "Horodatage", "user_id": "Compte", "montant": "Montant (FCFA)",
        "type_op": "Type", "heure": "Heure",
    })
    df_affiche["statut"] = df_filtre["statut"].map(libelle_statut).fillna(df_filtre["statut"])
    df_affiche = df_affiche.rename(columns={"statut": "Statut"})

    st.dataframe(
        df_affiche[["Horodatage", "Compte", "Type", "Montant (FCFA)", "Heure", "Statut"]],
        width='stretch', hide_index=True,
    )

    csv = df_affiche.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Export CSV", data=csv,
        file_name=f"alertes_camertrust_{datetime.now():%Y%m%d_%H%M}.csv",
        mime="text/csv",
    )
