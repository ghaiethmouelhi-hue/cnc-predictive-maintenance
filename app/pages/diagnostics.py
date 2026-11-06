# -*- coding: utf-8 -*-
"""Diagnostics — historique filtrable, statistiques et export."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app import charts
from app.components import empty_state, hero, kpi_grid, section_label
from app.history_store import clear_diagnostics, export_csv, load_diagnostics
from app.theme import format_fr, format_pct

LEVELS = ["NORMAL", "MODÉRÉ", "ÉLEVÉ", "CRITIQUE"]


def _filtered(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    st.markdown('<p class="section-eyebrow">Filtres</p>', unsafe_allow_html=True)
    row1 = st.columns([1.2, 1.6, 1])
    with row1[0]:
        machines = st.multiselect(
            "Machines",
            sorted(df["machine_id"].dropna().unique().tolist()),
            placeholder="Toutes",
        )
    with row1[1]:
        levels = st.multiselect(
            "Niveaux de risque",
            [level for level in LEVELS if level in df["risk_level"].unique()],
            placeholder="Tous",
        )
    with row1[2]:
        if df["timestamp"].notna().any():
            minimum = df["timestamp"].min().date()
            maximum = df["timestamp"].max().date()
            date_range = st.date_input(
                "Période",
                value=(minimum, maximum),
                min_value=minimum,
                max_value=maximum,
            )
        else:
            date_range = None

    search = st.text_input("Rechercher une machine ou un mode", placeholder="CNC-01, OSF…")

    out = df.copy()
    if machines:
        out = out[out["machine_id"].isin(machines)]
    if levels:
        out = out[out["risk_level"].isin(levels)]
    if date_range and len(date_range) == 2:
        start = pd.Timestamp(date_range[0])
        end = pd.Timestamp(date_range[1]) + pd.Timedelta(days=1)
        out = out[(out["timestamp"] >= start) & (out["timestamp"] < end)]
    if search:
        needle = search.strip().lower()
        mask = (
            out["machine_id"].astype(str).str.lower().str.contains(needle, na=False)
            | out["signals"].astype(str).str.lower().str.contains(needle, na=False)
        )
        out = out[mask]
    return out


def render() -> None:
    diagnostics = load_diagnostics()

    flash = st.session_state.pop("diagnostics_flash", None)
    if flash:
        st.success(flash)

    hero(
        "Intelligence · Diagnostics",
        "L'historique qui transforme une alerte en décision.",
        "Tous les diagnostics lancés dans l'application sont conservés "
        "localement. Filtrez par machine, période et gravité, puis exportez "
        "les données pour votre GMAO.",
        accent="amber",
        chips=["Journal local", "Export CSV", "Filtres"],
    )

    if diagnostics.empty:
        empty_state(
            "clipboard",
            "Aucun diagnostic enregistré",
            "Lancez RUN AI DIAGNOSTIC depuis la page AI Prediction. Chaque "
            "diagnostic sera journalisé ici avec ses mesures et son niveau de risque.",
            tone="amber",
        )
        return

    filtered = _filtered(diagnostics)

    section_label("Synthèse de la sélection")
    if filtered.empty:
        st.info("Aucun diagnostic ne correspond aux filtres sélectionnés.")
        return

    probability = pd.to_numeric(filtered["probability"], errors="coerce")
    kpi_grid(
        [
            {
                "label": "Diagnostics",
                "value": len(filtered),
                "sub": f"sur {len(diagnostics)} au total",
                "tone": "cyan",
                "icon": "clipboard",
            },
            {
                "label": "Machines",
                "value": filtered["machine_id"].nunique(),
                "sub": "Identifiants distincts",
                "tone": "blue",
                "icon": "server",
            },
            {
                "label": "Risque moyen",
                "value": format_pct(float(probability.mean()), 1),
                "sub": "Probabilité XGBoost moyenne",
                "tone": "violet",
                "icon": "gauge",
            },
            {
                "label": "Risque maximal",
                "value": format_pct(float(probability.max()), 1),
                "sub": "Diagnostic le plus critique",
                "tone": "red",
                "icon": "critical",
            },
            {
                "label": "Pannes probables",
                "value": int((probability >= 0.111).sum()),
                "sub": "Score ≥ seuil 0,111",
                "tone": "orange",
                "icon": "alert",
            },
        ]
    )

    section_label("Analyse graphique")
    col1, col2 = st.columns([1, 1])
    with col1:
        counts = filtered["risk_level"].value_counts().reindex(LEVELS).fillna(0)
        st.plotly_chart(
            charts.bar(
                LEVELS,
                counts.tolist(),
                title="Répartition des niveaux de risque",
                color=["#34d399", "#fbbf24", "#fb923c", "#f87171"],
                height=310,
            ),
            width="stretch",
            config=charts.PLOT_CONFIG,
            theme=None,
        )
    with col2:
        st.plotly_chart(
            charts.histogram(
                probability,
                title="Distribution des scores de diagnostic",
                color="#22d3ee",
                bins=24,
                x_title="Probabilité de panne",
                height=310,
            ),
            width="stretch",
            config=charts.PLOT_CONFIG,
            theme=None,
        )

    col3, col4 = st.columns([1.25, 1])
    with col3:
        series = filtered.sort_values("timestamp")
        st.plotly_chart(
            charts.line_series(
                series["timestamp"],
                [
                    {
                        "name": "Probabilité",
                        "y": series["probability"],
                        "color": "#22d3ee",
                        "fill": True,
                    }
                ],
                title="Chronologie de la sélection",
                y_title="Probabilité",
                height=320,
            ),
            width="stretch",
            config=charts.PLOT_CONFIG,
            theme=None,
        )
    with col4:
        st.plotly_chart(
            charts.scatter(
                filtered["tool_wear_min"],
                probability,
                title="Usure outil × risque",
                color_values=probability,
                x_title="Usure (min)",
                y_title="Probabilité",
                colorbar_title="Risque",
                height=320,
            ),
            width="stretch",
            config=charts.PLOT_CONFIG,
            theme=None,
        )

    section_label("Journal détaillé")
    table = filtered.copy()
    table["timestamp"] = pd.to_datetime(table["timestamp"]).dt.strftime("%d/%m/%Y %H:%M")
    table["probability"] = table["probability"].map(lambda value: format_pct(value, 1))
    table["temp_diff"] = table["temp_diff"].map(lambda value: format_fr(value, 2))
    table["power_w"] = table["power_w"].map(lambda value: format_fr(value, 0))
    table = table.rename(
        columns={
            "timestamp": "Horodatage",
            "machine_id": "Machine",
            "machine_type": "Type",
            "probability": "Risque",
            "risk_level": "Niveau",
            "tool_wear_min": "Usure (min)",
            "torque": "Couple (Nm)",
            "rpm": "RPM",
            "temp_diff": "ΔT (°C)",
            "power_w": "Puissance (W)",
            "signals": "Modes détectés",
        }
    )
    table = table[
        [
            "Horodatage",
            "Machine",
            "Type",
            "Risque",
            "Niveau",
            "RPM",
            "Couple (Nm)",
            "Usure (min)",
            "ΔT (°C)",
            "Puissance (W)",
            "Modes détectés",
        ]
    ]
    st.dataframe(table, width="stretch", hide_index=True, height=420)

    download_col, reset_col = st.columns([1, 1])
    with download_col:
        st.download_button(
            "Exporter la sélection (CSV)",
            data=export_csv(filtered),
            file_name="cnc_diagnostics_export.csv",
            mime="text/csv",
            width="stretch",
        )
    with reset_col:
        with st.expander("Effacer l'historique"):
            confirm = st.checkbox(
                "Je confirme la suppression définitive du journal local."
            )
            if st.button("Supprimer les diagnostics", disabled=not confirm):
                clear_diagnostics()
                st.session_state["diagnostics_flash"] = "Journal supprimé."
                st.rerun()

    st.caption(
        "Le journal ne contient que les diagnostics réellement exécutés dans "
        "l'application. Les fichiers sont stockés dans data/processed/."
    )
