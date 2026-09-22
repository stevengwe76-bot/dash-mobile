"""
CamerTrust — E3 — Émulateur de terminal (page principale)
===========================================================

C'est la pièce maîtresse de la démo (plan p.11) : « le jury ne regarde pas
des courbes, il voit un téléphone qui reçoit une alerte et un doigt qui
répond « 2 »." Cette page réunit :

  1. Le terminal USSD (*888#) — S2 puis S5 du plan.
  2. La boîte de réception SMS simulée, avec réponse « 1 »/« 2 » en un
     clic — S6 du plan.

Les deux autres livrables d'E3 (espace client smartphone, console de
supervision) sont dans `pages/`, comme le veut le multipage natif de
Streamlit.

Lancement : `streamlit run app.py` depuis le dossier `dashboard/`.
"""

from __future__ import annotations

import uuid

import streamlit as st

import api_client
from style import PHONE_CSS

st.set_page_config(
    page_title="CamerTrust — Émulateur",
    page_icon="📱",
    layout="wide",
)
st.markdown(PHONE_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Numéros de démonstration — pré-remplis pour ne jamais laisser le jury
# face à un champ vide. C123 correspond au scénario amorcé par le
# simulateur de repli (demo_backend.py) : une alerte est déjà en attente.
# ---------------------------------------------------------------------------
NUMEROS_DEMO = {
    "Abonné de démo (alerte déjà en attente)": "+237690000123",
    "Nouvel abonné (à inscrire)": "+237691234567",
}


def _init_state() -> None:
    defaults = {
        "phone_number": NUMEROS_DEMO["Abonné de démo (alerte déjà en attente)"],
        "session_id": None,
        "accumulated": [],       # étapes USSD déjà envoyées, ex. ["3", "1", "500000"]
        "current_screen": "Composez *888# pour démarrer une session.",
        "session_active": False,
        "keypad_buffer": "",
        "api_url": api_client.get_api_url(),
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


_init_state()


# ---------------------------------------------------------------------------
# Barre latérale — réglages de démo, jamais montrés au jury comme
# « interface finale », juste des commandes de mise en scène.
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Réglages de démo")

    choix_numero = st.selectbox("Abonné simulé", list(NUMEROS_DEMO.keys()))
    nouveau_numero = NUMEROS_DEMO[choix_numero]
    if nouveau_numero != st.session_state["phone_number"]:
        st.session_state["phone_number"] = nouveau_numero
        st.session_state["session_id"] = None
        st.session_state["accumulated"] = []
        st.session_state["session_active"] = False
        st.session_state["current_screen"] = "Composez *888# pour démarrer une session."

    st.text_input("Numéro affiché", value=st.session_state["phone_number"], disabled=True)

    st.divider()
    api_url_input = st.text_input("URL de l'API (E2)", value=st.session_state["api_url"])
    if api_url_input != st.session_state["api_url"]:
        st.session_state["api_url"] = api_url_input

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔄 Vérifier la connexion"):
            api_client.check_health()
    with col_b:
        if st.button("⏰ Réveiller le service"):
            with st.spinner("Ping /health (jusqu'à 10 min si l'instance dormait)…"):
                api_client.check_health()

    online = api_client.is_online()
    pill_class = "status-pill-online" if online else "status-pill-offline"
    pill_text = "API en ligne" if online else "Mode démo hors ligne (Plan B)"
    st.markdown(f'<span class="{pill_class}">{pill_text}</span>', unsafe_allow_html=True)
    if not online:
        st.caption(
            "Aucune réponse de l'API — l'émulateur rejoue un scénario local "
            "réaliste (`demo_backend.py`) pour que la démo reste jouable."
        )

    st.divider()
    with st.expander("💡 Simuler une transaction suspecte"):
        st.caption("Injecte une transaction pour déclencher une alerte, comme le ferait un vrai flux transactionnel côté opérateur.")
        montant = st.number_input("Montant (FCFA)", min_value=1000, value=450_000, step=10_000)
        heure = st.slider("Heure de la transaction", 0, 23, 2)
        type_op = st.selectbox("Type d'opération", ["retrait", "transfert"])
        if st.button("Envoyer la transaction"):
            res = api_client.score_transaction(
                user_id="C123", amount=int(montant), type_op=type_op, hour=int(heure),
            )
            if res.get("is_fraud"):
                st.success("Transaction risquée détectée — une alerte vient d'être envoyée à l'abonné (voir la boîte SMS).")
            else:
                st.info("Transaction jugée conforme aux habitudes — aucune alerte envoyée.")


# ---------------------------------------------------------------------------
# Mise en page : terminal USSD à gauche, boîte SMS à droite.
# ---------------------------------------------------------------------------
st.title("📱 CamerTrust — Terminal abonné")
st.caption("Vue exacte de ce que verrait un abonné sur un téléphone à touches : USSD *888# et SMS.")

col_ussd, col_sms = st.columns([1, 1.2], gap="large")

# --- Colonne terminal USSD -------------------------------------------------
with col_ussd:
    st.subheader("Menu USSD — *888#")

    screen_html = (
        f'<div class="phone-frame"><div class="phone-notch"></div>'
        f'<div class="phone-screen">{st.session_state["current_screen"]}<span class="cursor">&nbsp;</span></div>'
        f'<div class="phone-label">CamerTrust · terminal simulé</div></div>'
    )
    st.markdown(screen_html, unsafe_allow_html=True)

    if not st.session_state["session_active"]:
        if st.button("☎️ Composer *888#", width='stretch', type="primary"):
            st.session_state["session_id"] = str(uuid.uuid4())
            st.session_state["accumulated"] = []
            reponse = api_client.ussd_request(
                st.session_state["session_id"], st.session_state["phone_number"], "",
            )
            st.session_state["current_screen"] = reponse[4:].strip() if reponse[:3] in ("CON", "END") else reponse
            st.session_state["session_active"] = reponse.startswith("CON")
            st.rerun()
    else:
        st.markdown("**Clavier**")
        buffer = st.session_state["keypad_buffer"]
        st.text_input("Saisie en cours", value=buffer, disabled=True, label_visibility="collapsed")

        pad_rows = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"], ["*", "0", "#"]]
        for row in pad_rows:
            cols = st.columns(3)
            for c, digit in zip(cols, row):
                if c.button(digit, key=f"pad_{digit}", width='stretch'):
                    st.session_state["keypad_buffer"] += digit
                    st.rerun()

        col_send, col_clear, col_end = st.columns(3)
        with col_send:
            if st.button("✅ Envoyer", type="primary", width='stretch', disabled=not buffer):
                st.session_state["accumulated"].append(buffer)
                st.session_state["keypad_buffer"] = ""
                texte = "*".join(st.session_state["accumulated"])
                reponse = api_client.ussd_request(
                    st.session_state["session_id"], st.session_state["phone_number"], texte,
                )
                st.session_state["current_screen"] = reponse[4:].strip() if reponse[:3] in ("CON", "END") else reponse
                st.session_state["session_active"] = reponse.startswith("CON")
                st.rerun()
        with col_clear:
            if st.button("⌫ Effacer", width='stretch', disabled=not buffer):
                st.session_state["keypad_buffer"] = buffer[:-1]
                st.rerun()
        with col_end:
            if st.button("🔴 Terminer", width='stretch'):
                st.session_state["session_active"] = False
                st.session_state["current_screen"] = "Session terminee."
                st.session_state["keypad_buffer"] = ""
                st.rerun()

    with st.expander("Historique brut de la session (débogage)"):
        st.code(
            f"sessionId = {st.session_state['session_id']}\n"
            f"phoneNumber = {st.session_state['phone_number']}\n"
            f"text = {'*'.join(st.session_state['accumulated'])!r}",
            language="text",
        )

# --- Colonne SMS ------------------------------------------------------------
with col_sms:
    st.subheader("Messages reçus")
    if st.button("🔄 Actualiser la boîte de réception"):
        st.rerun()

    messages = api_client.get_outbox(st.session_state["phone_number"])
    if not messages:
        st.info("Aucun SMS pour cet abonné pour l'instant.")

    for m in messages:
        st.markdown(
            f'<div class="sms-bubble-in">CamerTrust : {m["body"]}</div>'
            f'<div class="sms-meta">{m.get("horodatage", "")}</div>',
            unsafe_allow_html=True,
        )
        alert_id = m.get("alert_id")
        if alert_id:
            alerts = api_client.get_alerts("C123")  # démo mono-compte ; voir README pour la généralisation multi-comptes
            alerte = next((a for a in alerts if a["alert_id"] == alert_id), None)
            if alerte and alerte.get("statut") == "en_attente":
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("1️⃣ C'est moi", key=f"ok_{m['id']}", width='stretch'):
                        api_client.respond_alert(alert_id, 1)
                        st.rerun()
                with c2:
                    if st.button("2️⃣ Ce n'est pas moi", key=f"ko_{m['id']}", width='stretch', type="primary"):
                        api_client.respond_alert(alert_id, 2)
                        st.rerun()
            elif alerte:
                statut_lisible = {"confirmee": "✅ Confirmée par l'abonné", "bloquee": "🔒 Compte protégé — transferts suspendus"}
                st.caption(statut_lisible.get(alerte["statut"], alerte["statut"]))

st.divider()
st.caption(
    "CamerTrust protège votre argent, pas vos habitudes. — "
    "Émulateur de terminal, projet de fin d'études SUP'PTIC 2023-2026."
)
