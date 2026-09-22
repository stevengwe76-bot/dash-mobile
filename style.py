"""
CamerTrust — E3 — Style du cadre téléphone.

Conseil du plan (p.11) : « n'essaie pas de reproduire un iPhone. Un cadre
noir arrondi en CSS, une police à chasse fixe, un fond clair : cela suffit
et c'est même plus crédible pour un terminal basique. » C'est exactement
ce que fait ce module — un seul bloc CSS injecté une fois par page.
"""

PHONE_CSS = """
<style>
.phone-frame {
    background: #1c1c1e;
    border-radius: 34px;
    padding: 18px 14px 22px 14px;
    width: 320px;
    margin: 0 auto 1rem auto;
    box-shadow: 0 8px 24px rgba(0,0,0,0.35);
}
.phone-notch {
    width: 60px;
    height: 6px;
    background: #3a3a3c;
    border-radius: 3px;
    margin: 0 auto 10px auto;
}
.phone-screen {
    background: #d7e6d0;
    color: #16281a;
    font-family: "Courier New", Courier, monospace;
    font-size: 15px;
    line-height: 1.5;
    min-height: 190px;
    padding: 14px;
    border-radius: 6px;
    white-space: pre-wrap;
    word-wrap: break-word;
    border: 2px solid #0f1a11;
}
.phone-screen .cursor {
    display: inline-block;
    width: 8px;
    background: #16281a;
    animation: blink 1s steps(2) infinite;
}
@keyframes blink { 50% { opacity: 0; } }
.phone-label {
    text-align: center;
    color: #8e8e93;
    font-size: 11px;
    letter-spacing: 1px;
    margin-top: 10px;
    text-transform: uppercase;
}
.sms-bubble-in {
    background: #2f3136;
    color: #f2f2f2;
    padding: 10px 14px;
    border-radius: 14px 14px 14px 2px;
    max-width: 80%;
    margin: 4px 0;
    font-size: 14px;
}
.sms-bubble-out {
    background: #2e7d32;
    color: #ffffff;
    padding: 10px 14px;
    border-radius: 14px 14px 2px 14px;
    max-width: 80%;
    margin: 4px 0 4px auto;
    font-size: 14px;
    text-align: right;
}
.sms-meta {
    font-size: 10px;
    color: #9a9a9a;
    margin: 0 6px 8px 6px;
}
.status-pill-online {
    background: #1b5e20; color: white; padding: 2px 10px;
    border-radius: 12px; font-size: 12px; display: inline-block;
}
.status-pill-offline {
    background: #b71c1c; color: white; padding: 2px 10px;
    border-radius: 12px; font-size: 12px; display: inline-block;
}
</style>
"""
