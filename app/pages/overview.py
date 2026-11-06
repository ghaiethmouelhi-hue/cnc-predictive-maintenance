# -*- coding: utf-8 -*-
"""Vue d'ensemble — état de la flotte suivie et santé du parc."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app import charts
from app.components import (
    alert_list,
    empty_state,
    hero,
    kpi_grid,
    section_label,
)
from app.data_access import dataset_overview, load_clean, load_summary
from app.history_store import fleet_snapshot, load_diagnostics
from app.theme import format_fr, format_pct

RISK_TONE = {
    "NORMAL": "green",
    "MODÉRÉ": "amber",
    "ÉLEVÉ": "orange",
    "CRITIQUE": "red",
}


def _fleet_metrics(fleet: pd.DataFrame) -> dict:
    total = int(len(fleet))
    counts = fleet["risk_level"].value_counts().to_dict() if total else {}
    normal = int(counts.get("NORMAL", 0))
    warning = int(counts.get("MODÉRÉ", 0))
    elevated = int(counts.get("ÉLEVÉ", 0))
    critical = int(counts.get("CRITIQUE", 0))
    availability = (normal / total) if total else None
    mean_risk = float(fleet["probability"].mean()) if total else None
    max_risk = float(fleet["probability"].max()) if total else None
    return {
        "total": total,
        "normal": normal,
        "warning": warning,
        "elevated": elevated,
        "critical": critical,
        "availability": availability,
        "mean_risk": mean_risk,
        "max_risk": max_risk,
    }


def render() -> None:
    summary = load_summary()
    stats = dataset_overview()
    diagnostics = load_diagnostics()
    fleet = fleet_snapshot(diagnostics)
    metrics = _fleet_metrics(fleet)

    hero(
        "Operations control · Overview",
        "Une lecture claire de la santé de votre parc.",
        "Supervision de la flotte réellement diagnostiquée dans l'application, "
        "complétée par les statistiques du dataset AI4I 2020. Aucune télémétrie "
        "n'est simulée : les machines apparaissent dès leur premier diagnostic.",
        chips=[
            f"{stats['n_rows']:,} observations dataset".replace(",", " "),
            "XGBoost · seuil 0,111",
            "AI4I 2020 · UCI",
        ],
    )

    availability_value = (
        format_pct(metrics["availability"], 1)
        if metrics["availability"] is not None
        else "—"
    )
    availability_sub = (
        f"<strong>{metrics['normal']}</strong> machine(s) sans alerte sur "
        f"<strong>{metrics['total']}</strong> suivie(s)"
        if metrics["total"]
        else "Aucune machine diagnostiquée pour l'instant"
    )
    risk_value = (
        format_pct(metrics["max_risk"], 1)
        if metrics["max_risk"] is not None
        else "—"
    )
    risk_sub = (
        f"Risque moyen de la flotte : <strong>{format_pct(metrics['mean_risk'], 1)}</strong>"
        if metrics["mean_risk"] is not None
        else "Lancez un diagnostic pour alimenter cet indicateur"
    )

    kpi_grid(
        [
            {
                "label": "Total machines",
                "value": metrics["total"],
                "sub": "Machines avec au moins un diagnostic enregistré",
                "tone": "cyan",
                "icon": "server",
            },
            {
                "label": "Operational",
                "value": metrics["normal"],
                "sub": "Risque sous le seuil de décision",
                "tone": "green",
                "icon": "check",
            },
            {
                "label": "Warning",
                "value": metrics["warning"] + metrics["elevated"],
                "sub": f"{metrics['warning']} modérée(s) · {metrics['elevated']} élevée(s)",
                "tone": "amber",
                "icon": "alert",
            },
            {
                "label": "Critical",
                "value": metrics["critical"],
                "sub": "Probabilité de panne ≥ 75 %",
                "tone": "red",
                "icon": "critical",
            },
            {
                "label": "Availability rate",
                "value": availability_value,
                "sub": availability_sub,
                "tone": "blue",
                "icon": "activity",
            },
            {
                "label": "Overall failure risk",
                "value": risk_value,
                "sub": risk_sub,
                "tone": "violet",
                "icon": "target",
            },
        ]
    )

    if metrics["total"] == 0:
        empty_state(
            "monitoring",
            "Aucune machine enregistrée",
            "Ouvrez la page AI Prediction et lancez un diagnostic : la machine "
            "apparaîtra ici avec son dernier niveau de risque. Les graphiques "
            "ci-dessous décrivent le dataset réel, pas une flotte connectée.",
            tone="cyan",
        )

    left, right = st.columns([1.25, 1])
    with left:
        section_label("Répartition des défaillances · dataset")
        mode_counts = stats["mode_counts"]
        labels = ["TWF", "HDF", "PWF", "OSF", "RNF"]
        values = [mode_counts.get(mode, 0) for mode in labels]
        fig = charts.donut(
            labels,
            values,
            title="Modes documentés (une panne peut cumuler plusieurs modes)",
            center_value=str(stats["n_fail"]),
            center_label="pannes",
            colors=[
                "#22d3ee",
                "#f87171",
                "#fbbf24",
                "#a78bfa",
                "#34d399",
            ],
            height=330,
        )
        st.plotly_chart(fig, width="stretch", config=charts.PLOT_CONFIG)
    with right:
        section_label("Dernières alertes")
        if diagnostics.empty:
            empty_state(
                "check",
                "Aucune alerte enregistrée",
                "Les alertes proviennent uniquement des diagnostics que vous "
                "lancez. Aucun événement n'est fabriqué.",
                tone="green",
            )
        else:
            recent = diagnostics.head(6)
            alert_list(
                [
                    {
                        "title": f"{row.machine_id} · type {row.machine_type}",
                        "meta": f"{row.timestamp:%d/%m/%Y %H:%M} · "
                        f"usure {format_fr(row.tool_wear_min, 0)} min",
                        "value": format_pct(row.probability, 1),
                        "tone": RISK_TONE.get(row.risk_level, "cyan"),
                    }
                    for row in recent.itertuples()
                ]
            )

    section_label("Signaux capteurs · dataset AI4I 2020")
    clean = load_clean()
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            charts.histogram(
                clean["air_temp_c"],
                title="Température air — 10 000 observations",
                color="#38bdf8",
                x_title="°C",
                bins=40,
                height=290,
            ),
            width="stretch",
            config=charts.PLOT_CONFIG, theme=None,
        )
    with col2:
        st.plotly_chart(
            charts.histogram(
                clean["process_temp_c"],
                title="Température process",
                color="#22d3ee",
                x_title="°C",
                bins=40,
                height=290,
            ),
            width="stretch",
            config=charts.PLOT_CONFIG, theme=None,
        )

    col_rpm, col_torque = st.columns(2)
    with col_rpm:
        st.plotly_chart(
            charts.histogram(
                clean["rpm"],
                title="Vitesse de broche",
                color="#3b82f6",
                x_title="tr/min",
                bins=40,
                height=290,
            ),
            width="stretch",
            config=charts.PLOT_CONFIG, theme=None,
        )
    with col_torque:
        st.plotly_chart(
            charts.histogram(
                clean["torque"],
                title="Couple",
                color="#a78bfa",
                x_title="Nm",
                bins=40,
                height=290,
            ),
            width="stretch",
            config=charts.PLOT_CONFIG, theme=None,
        )

    col3, col4 = st.columns([1.35, 1])
    with col3:
        sample = clean.sample(min(len(clean), 2500), random_state=42)
        st.plotly_chart(
            charts.scatter(
                sample["rpm"],
                sample["torque"],
                title="RPM × couple — nuage réel (échantillon 2 500 points)",
                color_values=sample["failure"],
                x_title="tr/min",
                y_title="Nm",
                colorbar_title="Panne",
                height=350,
            ),
            width="stretch",
            config=charts.PLOT_CONFIG, theme=None,
        )
    with col4:
        by_type = clean.groupby("machine_type")["failure"].mean().reindex(["L", "M", "H"])
        st.plotly_chart(
            charts.bar(
                [f"Type {label}" for label in by_type.index],
                [value * 100 for value in by_type.values],
                title="Taux de panne par type de machine",
                color=["#22d3ee", "#3b82f6", "#a78bfa"],
                text_suffix=" %",
                height=350,
            ),
            width="stretch",
            config=charts.PLOT_CONFIG, theme=None,
        )

    section_label("Anomalies & usure")
    col5, col6 = st.columns([1, 1])
    with col5:
        failures = clean[clean["failure"] == 1]
        st.plotly_chart(
            charts.histogram(
                failures["tool_wear_min"],
                title=f"Usure outil au moment des {len(failures)} pannes",
                color="#f87171",
                x_title="min",
                bins=30,
            ),
            width="stretch",
            config=charts.PLOT_CONFIG, theme=None,
        )
    with col6:
        if diagnostics.empty:
            empty_state(
                "history",
                "Historique vide",
                "L'historique des anomalies se construit à partir des "
                "diagnostics enregistrés dans l'application.",
                tone="slate",
            )
        else:
            series = diagnostics.sort_values("timestamp")
            st.plotly_chart(
                charts.line_series(
                    series["timestamp"],
                    [
                        {
                            "name": "Probabilité de panne",
                            "y": series["probability"],
                            "color": "#22d3ee",
                            "fill": True,
                        }
                    ],
                    title="Historique des scores de diagnostic",
                    y_title="Probabilité",
                    height=300,
                ),
                width="stretch",
                config=charts.PLOT_CONFIG, theme=None,
            )

    section_label("Fiabilité & disponibilité · modèle de survie")
    reliability_cols = st.columns(4)
    reliability_items = [
        ("R(1 h)", format_pct(float(summary.get("R_km_1h", 0.0)), 2, already_pct=True), "Probabilité de survie à 1 heure", "cyan"),
        ("MTBF", f"{format_fr(float(summary.get('MTBF_h', 0.0)), 2)} h", "Temps moyen entre défaillances", "blue"),
        ("Disponibilité", format_pct(float(summary.get("A_pct", 0.0)), 2, already_pct=True), "Hypothèse MTTR 4 h", "green"),
        ("Taux de panne", format_pct(float(summary.get("fail_rate_pct", 0.0)), 2, already_pct=True), "Sur les 10 000 observations", "amber"),
    ]
    for column, (label, value, sub, tone) in zip(reliability_cols, reliability_items):
        with column:
            kpi_grid(
                [
                    {
                        "label": label,
                        "value": value,
                        "sub": sub,
                        "tone": tone,
                        "icon": "shield",
                    }
                ]
            )

    if not fleet.empty:
        section_label("Flotte suivie")
        table = fleet[
            ["machine_id", "machine_type", "probability", "risk_level", "timestamp"]
        ].copy()
        table["probability"] = table["probability"].map(lambda value: format_pct(value, 1))
        table["timestamp"] = pd.to_datetime(table["timestamp"]).dt.strftime("%d/%m/%Y %H:%M")
        table.columns = ["Machine", "Type", "Risque", "Niveau", "Dernier diagnostic"]
        st.dataframe(table, width="stretch", hide_index=True)

    st.caption(
        "Les KPI de flotte sont calculés à partir des diagnostics enregistrés. "
        "Les graphiques de cette page décrivent le dataset AI4I 2020 (données "
        "synthétiques UCI), pas une machine en production."
    )
