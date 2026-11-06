# -*- coding: utf-8 -*-
"""CNC Sentinel — point d'entrée Streamlit.

Navigation multi-pages, thème sombre global et pied de page développeur.
Toutes les vues sont définies dans ``app/pages``.
"""

from __future__ import annotations

import sys
from pathlib import Path

# La racine du dépôt doit être dans sys.path AVANT les imports
# `from app…` / `from rag…` : Streamlit Cloud exécute ce fichier
# sans garantir que le répertoire courant est au chemin Python.
# (Sans ceci : ModuleNotFoundError: No module named 'app'.)
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import streamlit as st

from app.components import footer
from app.config import is_demo_mode
from app.data_access import FAILURE_THRESHOLD, dataset_overview, load_summary
from app.pages import (
    about,
    analytics,
    developer,
    diagnostics,
    maintenance,
    monitoring,
    overview,
    prediction,
    reliability,
)
from app.theme import inject_theme, register_plotly_theme

st.set_page_config(
    page_title="CNC Sentinel · Predictive Maintenance",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "CNC Sentinel — predictive maintenance workspace built by Ghaith Mouelhi and Chadi Ammar.",
    },
)

_light_mode = bool(st.session_state.get("light_mode", False))
inject_theme(light=_light_mode)
register_plotly_theme(light=_light_mode)

pages = {
    "OPERATIONS": [
        st.Page(overview.render, title="Overview", icon=":material/space_dashboard:", url_path="overview", default=True),
        st.Page(monitoring.render, title="Machine Monitoring", icon=":material/monitoring:", url_path="monitoring"),
        st.Page(maintenance.render, title="Maintenance History", icon=":material/handyman:", url_path="maintenance"),
    ],
    "INTELLIGENCE": [
        st.Page(prediction.render, title="AI Prediction", icon=":material/neurology:", url_path="prediction"),
        st.Page(diagnostics.render, title="Diagnostics", icon=":material/fact_check:", url_path="diagnostics"),
        st.Page(analytics.render, title="Analytics", icon=":material/analytics:", url_path="analytics"),
        st.Page(reliability.render, title="Reliability", icon=":material/verified_user:", url_path="reliability"),
    ],
    "PROFILE": [
        st.Page(developer.render, title="Developer Profile", icon=":material/person:", url_path="developer"),
        st.Page(about.render, title="About", icon=":material/info:", url_path="about"),
    ],
}

page = st.navigation(pages, position="sidebar")

with st.sidebar:
    st.markdown('<div class="section-eyebrow" style="margin:.1rem .95rem .1rem">Appearance</div>', unsafe_allow_html=True)
    st.toggle(
        "☀️ Light mode",
        key="light_mode",
        help="Basculer entre le thème sombre et le thème clair.",
    )
    stats = dataset_overview()
    summary = load_summary()
    n_rows = f"{stats['n_rows']:,}".replace(",", " ")
    st.markdown(
        f'<div class="sidebar-card scan-line">'
        f'<div class="status-line"><span class="status-pill status-normal" '
        f'style="padding:.18rem .5rem;font-size:.6rem">'
        f'<span class="dot"></span>SYSTEM READY</span></div>'
        f'<div class="status-meta" style="margin-top:.45rem">'
        f"XGBoost chargé · seuil {FAILURE_THRESHOLD}<br>"
        f"{n_rows} observations · {stats['n_fail']} pannes<br>"
        f"MTBF {summary.get('MTBF_h', 0):.1f} h · "
        f"R(1 h) {summary.get('R_km_1h', 0) * 100:.1f} %"
        f"</div></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sidebar-dev">'
        '<div class="sidebar-avatar">GM</div>'
        '<div><div class="sidebar-dev-name">Ghaith Mouelhi &amp; Chadi Ammar</div>'
        '<div class="sidebar-dev-role">AI · Automation · Reliability</div></div>'
        "</div>",
        unsafe_allow_html=True,
    )
    if is_demo_mode():
        st.markdown(
            '<div class="sidebar-card" style="margin-top:.55rem">'
            '<div class="status-line">'
            '<span class="status-pill status-warning" style="padding:.18rem .5rem;font-size:.6rem">'
            '<span class="dot"></span>DEMO MODE</span></div>'
            '<div class="status-meta" style="margin-top:.45rem">'
            "Clé Gemini absente : prédiction XGBoost et RAG retrieve-only "
            "actifs, génération de texte désactivée.</div></div>",
            unsafe_allow_html=True,
        )

page.run()
footer()
