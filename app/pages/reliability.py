# -*- coding: utf-8 -*-
"""Reliability — rapport de fiabilité existant, conservé et intégré."""

from __future__ import annotations

import streamlit as st

from app.components import hero
from app.data_access import ROOT_DIR
from app.report_view import render_reliability_report


def render() -> None:
    hero(
        "Intelligence · Reliability",
        "La fiabilité se mesure, elle ne s'estime pas.",
        "Kaplan-Meier, loi exponentielle, MTBF, modes de défaillance et "
        "politique de maintenance : la synthèse complète du rapport de "
        "fiabilité, intégrée au tableau de bord.",
        accent="blue",
        chips=["Kaplan-Meier", "MTBF 29,5 h", "Rapport HTML"],
    )
    st.markdown('<p class="section-eyebrow">Rapport de fiabilité · AI4I 2020</p>', unsafe_allow_html=True)
    render_reliability_report(ROOT_DIR)
