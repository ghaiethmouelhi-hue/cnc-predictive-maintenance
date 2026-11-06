# -*- coding: utf-8 -*-
"""About — architecture, données et limites du projet."""

from __future__ import annotations

import streamlit as st

from app.components import (
    CHADI_LINKEDIN_URL,
    chip_row,
    co_developer_card,
    hero,
    icon,
    pipeline,
    section_label,
    social_buttons,
)
from app.data_access import FAILURE_THRESHOLD

PAGES = [
    ("grid", "Overview", "Santé de la flotte suivie et statistiques du dataset."),
    ("monitoring", "Machine Monitoring", "Jauges capteurs, seuils et signaux de défaillance."),
    ("brain", "AI Prediction", "Score XGBoost, causes heuristiques et recommandation RAG."),
    ("clipboard", "Diagnostics", "Journal filtrable, graphiques et export CSV."),
    ("wrench", "Maintenance History", "Interventions réelles et indicateurs d'activité."),
    ("analytics", "Analytics", "Dataset, métriques du modèle et relations capteurs-pannes."),
    ("shield", "Reliability", "Kaplan-Meier, MTBF, modes et politique de maintenance."),
    ("user", "Developer Profile", "Parcours, centres d'intérêt et contact."),
    ("info", "About", "Architecture, provenance des données et limites."),
]


def render() -> None:
    hero(
        "About · CNC Sentinel",
        "Une plateforme de maintenance prédictive, transparente par construction.",
        "Chaque score est traçable, chaque donnée a une source, chaque limite "
        "est documentée. CNC Sentinel relie un modèle XGBoost, une analyse de "
        "fiabilité et un assistant RAG dans une interface industrielle sombre.",
        chips=["Streamlit", "XGBoost", "RAG Gemini", "AI4I 2020"],
    )

    left, right = st.columns([1.3, 1], gap="large")

    with left:
        section_label("Pipeline de diagnostic")
        pipeline(
            [
                ("Mesures capteurs", "5 variables saisies ou issues du dataset.", "gauge"),
                ("Feature engineering", "ΔT, puissance, usure normalisée, stress thermique.", "layers"),
                ("Score XGBoost", "Probabilité binaire de panne au seuil 0,111.", "brain"),
                ("Seuils documentés", "TWF, HDF, PWF, OSF — lecture des causes possibles.", "target"),
                ("RAG Gemini", "Connaissance maintenance + contexte pour l'action.", "sparkles"),
            ]
        )

        section_label("Pages de la plateforme")
        cards = "".join(
            f'<div class="alert-item">'
            f'<span class="alert-dot" style="--tone: var(--cyan)"></span>'
            f'<div class="alert-main"><div class="alert-title">'
            f'{icon(icon_name, 13)} {title}</div>'
            f'<div class="alert-meta">{description}</div></div></div>'
            for icon_name, title, description in PAGES
        )
        st.markdown(cards, unsafe_allow_html=True)

        section_label("Données & provenance")
        st.markdown(
            '<div class="panel">'
            '<p class="panel-sub" style="margin:0">'
            "Dataset <strong>AI4I 2020 Predictive Maintenance</strong> "
            "(UCI Machine Learning Repository, S. Matzka) : 10 000 observations "
            "synthétiques de fraiseuses CNC, 339 pannes, modes TWF, HDF, PWF, "
            "OSF et RNF. Le rapport de fiabilité est produit par "
            "<code>reliability_analysis.py</code> à partir de ces données. "
            "Les diagnostics et interventions de l'application sont stockés "
            "localement dans <code>data/processed/</code>."
            "</p></div>",
            unsafe_allow_html=True,
        )

    with right:
        section_label("Ce que le système fait")
        st.markdown(
            f'<div class="glass-card" style="margin-bottom:.6rem">'
            f'<div class="card-eyebrow">Modèle</div>'
            f"<h4>XGBoost binaire</h4>"
            f"<p>Probabilité de panne apprise sur les variables capteurs et "
            f"quatre variables dérivées. Seuil de décision {FAILURE_THRESHOLD} "
            f"choisi pour privilégier le rappel.</p></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="glass-card" style="margin-bottom:.6rem">'
            '<div class="card-eyebrow">Assistant</div>'
            "<h4>RAG ancré</h4>"
            "<p>Recherche vectorielle dans la base de connaissances maintenance, "
            "puis génération Gemini. Si le service est indisponible, aucun "
            "contenu n'est inventé.</p></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="glass-card">'
            '<div class="card-eyebrow">Fiabilité</div>'
            "<h4>Analyse de survie</h4>"
            "<p>Kaplan-Meier, loi exponentielle contrainte, MTBF, disponibilité "
            "et coût de maintenance intégrés au rapport.</p></div>",
            unsafe_allow_html=True,
        )

        section_label("Limites assumées")
        limitations = [
            "Aucune télémétrie temps réel : les vues affichent des diagnostics enregistrés ou des observations réelles du dataset.",
            "Le modèle prédit une panne binaire ; les modes TWF/HDF/PWF/OSF sont des heuristiques de seuils, pas une classification multi-classes.",
            "Le scaler a été ajusté avant le split : une fuite légère est documentée dans le notebook d'entraînement.",
            "Le dataset AI4I 2020 est synthétique : les conclusions doivent être validées sur des données d'atelier.",
            "La recommandation RAG dépend d'un service externe (Gemini) et peut être momentanément indisponible.",
        ]
        st.markdown(
            "".join(f'<div class="alert-item" style="margin-bottom:.4rem">'
                    f'<span class="alert-dot" style="--tone: var(--amber)"></span>'
                    f'<div class="alert-main"><div class="alert-meta">{item}</div></div>'
                    f"</div>" for item in limitations),
            unsafe_allow_html=True,
        )

        section_label("Technologies")
        chip_row(
            [
                "Python 3.12",
                "Streamlit",
                "Plotly",
                "XGBoost",
                "scikit-learn",
                "LangChain",
                "Gemini",
                "ChromaDB",
                "sentence-transformers",
                "lifelines",
            ]
        )

        section_label("Auteurs")
        st.markdown(
            '<div class="alert-item" style="margin-bottom:.6rem">'
            '<span class="alert-dot" style="--tone: var(--cyan)"></span>'
            '<div class="alert-main"><div class="alert-title">Ghaith Mouelhi</div>'
            '<div class="alert-meta">Electrical Engineering and Automation · '
            "AI, automatisation industrielle et maintenance prédictive.</div>"
            "</div></div>",
            unsafe_allow_html=True,
        )
        social_buttons()
        st.markdown('<div style="height:.7rem"></div>', unsafe_allow_html=True)
        co_developer_card(
            name="Chadi Ammar",
            role="Electrical and Automation Engineering Student",
            linkedin_url=CHADI_LINKEDIN_URL,
            initials="CA",
        )
