"""
CamerTrust — E3 — Espace client (mini-application smartphone)
================================================================

Livrable S7 du plan (p.12) : trois écrans réellement branchés sur l'API —
Mon score de confiance, Mes alertes, Mes réglages. C'est la version
« smartphone » du service, complémentaire du terminal USSD/SMS de la page
principale (téléphone à touches).

Le plan suggère `st.sidebar.radio('Écran', [...])` pour la navigation
entre les trois écrans : conservé tel quel ci-dessous.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

import api_client
from style import PHONE_CSS

st.set_page_config(page_title="CamerTrust — Espace client", page_icon="📲", layout="centered")
st.markdown(PHONE_CSS, unsafe_allow_html=True)

USER_ID_DEMO = "C123"  # voir README : généralisation multi-comptes hors périmètre de la démo

st.sidebar.header("📲 Espace client")
online = api_client.is_online()
st.sidebar.markdown(
    f'<span class="{"status-pill-online" if online else "status-pill-offline"}">'
    f'{"API en ligne" if online else "Mode démo hors ligne"}</span>',
    unsafe_allow_html=True,
)
ecran = st.sidebar.radio("Écran", ["Mon score de confiance", "Mes alertes", "Mes réglages"])

st.title("CamerTrust — Mon compte")
st.caption(f"Compte {USER_ID_DEMO} · connecté depuis la mini-application")

if ecran == "Mon score de confiance":
    data = api_client.get_trustscore(USER_ID_DEMO)
    score = data.get("score")
    if score is None:
        st.warning("Score indisponible pour ce compte.")
    else:
        if score >= 70:
            couleur, appreciation = "normal", "Bon niveau de confiance"
        elif score >= 40:
            couleur, appreciation = "off", "Niveau de confiance moyen"
        else:
            couleur, appreciation = "inverse", "Niveau de confiance faible"
        st.metric("Score de confiance", f"{score}/100", delta=appreciation, delta_color=couleur)
        st.progress(min(max(score, 0), 100) / 100)
        st.caption(
            "Ce score reflète la régularité de vos habitudes de transaction. "
            "Il augmente quand vous confirmez vos opérations, et n'est jamais "
            "communiqué à des tiers."
        )

elif ecran == "Mes alertes":
    alertes = api_client.get_alerts(USER_ID_DEMO)
    if not alertes:
        st.info("Aucune alerte pour l'instant — c'est bon signe.")
    else:
        df = pd.DataFrame(alertes)
        libelle_statut = {"en_attente": "⏳ En attente", "confirmee": "✅ Confirmée", "bloquee": "🔒 Bloquée"}
        df["statut"] = df["statut"].map(libelle_statut).fillna(df["statut"])
        df = df.rename(columns={
            "montant": "Montant (FCFA)", "type_op": "Type", "heure": "Heure",
            "motif": "Motif", "statut": "Statut", "horodatage": "Horodatage",
        })
        colonnes = [c for c in ["Horodatage", "Type", "Montant (FCFA)", "Heure", "Motif", "Statut"] if c in df.columns]
        st.dataframe(df[colonnes], width='stretch', hide_index=True)

        en_attente = [a for a in alertes if a["statut"] == "en_attente"]
        if en_attente:
            st.warning(f"{len(en_attente)} alerte(s) en attente de votre réponse.")
            for a in en_attente:
                with st.container(border=True):
                    st.write(f"**{a['type_op'].capitalize()}** de {a['montant']:,} FCFA à {a['heure']}".replace(",", " "))
                    c1, c2 = st.columns(2)
                    if c1.button("1️⃣ C'est moi", key=f"esp_ok_{a['alert_id']}"):
                        api_client.respond_alert(a["alert_id"], 1)
                        st.rerun()
                    if c2.button("2️⃣ Ce n'est pas moi", key=f"esp_ko_{a['alert_id']}", type="primary"):
                        api_client.respond_alert(a["alert_id"], 2)
                        st.rerun()

elif ecran == "Mes réglages":
    reglages = api_client.get_settings(USER_ID_DEMO)
    if not reglages:
        st.warning("Réglages indisponibles pour ce compte.")
    else:
        with st.form("form_reglages"):
            plafond = st.number_input(
                "Plafond de transaction (FCFA)", min_value=0, step=10_000,
                value=int(reglages.get("plafond", 500_000)),
            )
            plafond_nocturne = st.slider(
                "Plafond nocturne (FCFA)", 0, 1_000_000,
                value=int(reglages.get("plafond_nocturne", 100_000)), step=10_000,
            )
            liste_blanche_texte = st.text_area(
                "Numéros habituels (liste blanche) — un par ligne",
                value="\n".join(reglages.get("liste_blanche", [])),
                height=100,
            )
            canal = st.radio(
                "Canal préféré pour les alertes", ["ussd", "sms", "app"],
                index=["ussd", "sms", "app"].index(reglages.get("canal_prefere", "ussd")),
                horizontal=True,
            )
            langue = st.selectbox(
                "Langue", ["fr", "en"],
                index=["fr", "en"].index(reglages.get("langue", "fr")),
            )
            valide = st.form_submit_button("Enregistrer", type="primary")

        if valide:
            liste_blanche = [n.strip() for n in liste_blanche_texte.splitlines() if n.strip()]
            api_client.put_settings(
                USER_ID_DEMO,
                plafond=int(plafond),
                plafond_nocturne=int(plafond_nocturne),
                liste_blanche=liste_blanche,
                canal_prefere=canal,
                langue=langue,
            )
            st.success("Réglages enregistrés.")

        st.divider()
        st.caption("Vous pouvez vous désinscrire à tout moment depuis le menu USSD (*888*6#) ou ci-dessous.")
        if st.button("🚫 Désactiver CamerTrust"):
            api_client.delete_user(USER_ID_DEMO)
            st.success("Compte désinscrit. Vos données d'analyse ont été effacées.")
