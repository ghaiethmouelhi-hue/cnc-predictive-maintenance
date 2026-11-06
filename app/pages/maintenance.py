# -*- coding: utf-8 -*-
"""Maintenance History — journal des interventions et planification."""

from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from app import charts
from app.components import empty_state, hero, kpi_grid, section_label
from app.history_store import (
    append_maintenance,
    clear_maintenance,
    export_csv,
    load_maintenance,
)
from app.theme import format_fr

TYPES = ["Préventive", "Corrective", "Conditionnelle", "Inspection"]
STATUSES = ["Planifiée", "En cours", "Terminée"]


def render() -> None:
    history = load_maintenance()

    flash = st.session_state.pop("maintenance_flash", None)
    if flash:
        st.success(flash)

    hero(
        "Operations control · Maintenance",
        "Capitaliser chaque intervention, pas seulement chaque panne.",
        "Journal local des actions de maintenance : préventif, correctif, "
        "conditionnel et inspections. Les indicateurs sont calculés uniquement "
        "à partir des interventions réellement saisies.",
        accent="green",
        chips=["Journal local", "MTTR suivi", "Export CSV"],
    )

    with st.expander("Ajouter une intervention", expanded=history.empty):
        with st.form("maintenance_form", border=False):
            row1 = st.columns(3)
            with row1[0]:
                intervention_date = st.date_input("Date", value=date.today())
            with row1[1]:
                machine_id = st.text_input("Machine", placeholder="CNC-01")
            with row1[2]:
                intervention_type = st.selectbox("Type", TYPES)
            row2 = st.columns(3)
            with row2[0]:
                component = st.text_input("Composant", placeholder="Broche, outil, pompe…")
            with row2[1]:
                technician = st.text_input("Technicien", placeholder="Nom")
            with row2[2]:
                status = st.selectbox("Statut", STATUSES)
            description = st.text_area(
                "Description",
                placeholder="Constat, action réalisée, pièces remplacées…",
                height=90,
            )
            submitted = st.form_submit_button(
                "Enregistrer l'intervention", type="primary", width="stretch"
            )
        if submitted:
            if not machine_id.strip() or not component.strip():
                st.error("Renseignez au minimum la machine et le composant.")
            else:
                append_maintenance(
                    {
                        "date": intervention_date.strftime("%Y-%m-%d"),
                        "machine_id": machine_id.strip(),
                        "intervention_type": intervention_type,
                        "component": component.strip(),
                        "description": description.strip(),
                        "technician": technician.strip(),
                        "status": status,
                    }
                )
                st.session_state["maintenance_flash"] = "Intervention enregistrée."
                st.rerun()

    if history.empty:
        empty_state(
            "wrench",
            "Aucune intervention enregistrée",
            "Ajoutez une première intervention ci-dessus. Le journal alimente "
            "les indicateurs de maintenance et l'export CSV.",
            tone="green",
        )
        return

    section_label("Indicateurs du journal")
    total = len(history)
    done = int((history["status"] == "Terminée").sum())
    corrective = int((history["intervention_type"] == "Corrective").sum())
    machines = int(history["machine_id"].nunique())
    kpi_grid(
        [
            {
                "label": "Interventions",
                "value": total,
                "sub": f"{machines} machine(s) concernée(s)",
                "tone": "cyan",
                "icon": "clipboard",
            },
            {
                "label": "Terminées",
                "value": done,
                "sub": f"{format_fr(100 * done / total, 1)} % du journal",
                "tone": "green",
                "icon": "check",
            },
            {
                "label": "Correctives",
                "value": corrective,
                "sub": "Part curative de l'activité",
                "tone": "amber",
                "icon": "wrench",
            },
            {
                "label": "En cours / planifiées",
                "value": total - done,
                "sub": "Actions encore ouvertes",
                "tone": "violet",
                "icon": "clock",
            },
        ]
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        type_counts = history["intervention_type"].value_counts().reindex(TYPES).fillna(0)
        st.plotly_chart(
            charts.bar(
                TYPES,
                type_counts.tolist(),
                title="Interventions par type",
                color=["#34d399", "#f87171", "#fbbf24", "#22d3ee"],
                height=300,
            ),
            width="stretch",
            config=charts.PLOT_CONFIG,
            theme=None,
        )
    with col2:
        status_counts = history["status"].value_counts().reindex(STATUSES).fillna(0)
        st.plotly_chart(
            charts.donut(
                STATUSES,
                status_counts.tolist(),
                title="Statut des interventions",
                center_value=str(total),
                center_label="interventions",
                colors=["#22d3ee", "#fbbf24", "#34d399"],
                height=300,
            ),
            width="stretch",
            config=charts.PLOT_CONFIG,
            theme=None,
        )

    section_label("Historique")
    filters = st.columns([1, 1, 1])
    with filters[0]:
        selected_type = st.multiselect("Type", TYPES, placeholder="Tous")
    with filters[1]:
        selected_status = st.multiselect("Statut", STATUSES, placeholder="Tous")
    with filters[2]:
        selected_machine = st.multiselect(
            "Machine",
            sorted(history["machine_id"].dropna().unique().tolist()),
            placeholder="Toutes",
        )

    view = history.copy()
    if selected_type:
        view = view[view["intervention_type"].isin(selected_type)]
    if selected_status:
        view = view[view["status"].isin(selected_status)]
    if selected_machine:
        view = view[view["machine_id"].isin(selected_machine)]

    table = view.copy()
    table["date"] = pd.to_datetime(table["date"], errors="coerce").dt.strftime("%d/%m/%Y")
    table = table.rename(
        columns={
            "date": "Date",
            "machine_id": "Machine",
            "intervention_type": "Type",
            "component": "Composant",
            "description": "Description",
            "technician": "Technicien",
            "status": "Statut",
        }
    )
    st.dataframe(
        table[["Date", "Machine", "Type", "Composant", "Description", "Technicien", "Statut"]],
        width="stretch",
        hide_index=True,
        height=360,
    )

    download_col, reset_col = st.columns([1, 1])
    with download_col:
        st.download_button(
            "Exporter le journal (CSV)",
            data=export_csv(view),
            file_name="cnc_maintenance_export.csv",
            mime="text/csv",
            width="stretch",
        )
    with reset_col:
        with st.expander("Effacer le journal"):
            confirm = st.checkbox(
                "Je confirme la suppression définitive du journal de maintenance."
            )
            if st.button("Supprimer les interventions", disabled=not confirm):
                clear_maintenance()
                st.session_state["maintenance_flash"] = "Journal de maintenance supprimé."
                st.rerun()

    st.caption(
        "Aucune intervention n'est générée automatiquement : le journal reflète "
        "exclusivement les saisies effectuées dans cette page."
    )
