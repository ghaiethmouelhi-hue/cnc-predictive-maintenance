# -*- coding: utf-8 -*-
"""Machine monitoring — inspection détaillée d'une machine ou d'une observation."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app import charts
from app.components import (
    bar_list,
    empty_state,
    hero,
    kpi_grid,
    level_tone,
    section_label,
    signal_cards,
    status_pill,
)
from app.data_access import (
    compute_features,
    detect_risk_signals,
    load_clean,
    predict_failure,
    reference_observation,
    risk_level,
)
from app.history_store import fleet_snapshot, load_diagnostics
from app.theme import format_fr

MODE_CHOICES = {
    "NORMAL": "Observation normale",
    "TWF": "Panne usure outil (TWF)",
    "HDF": "Panne dissipation thermique (HDF)",
    "PWF": "Panne puissance (PWF)",
    "OSF": "Panne surcharge (OSF)",
    "RNF": "Panne aléatoire (RNF)",
}

GAUGE_STEPS = {
    "air_temp_c": [(22, 32, "rgba(52,211,153,.14)")],
    "process_temp_c": [(32, 41, "rgba(52,211,153,.14)")],
    "rpm": [(1168, 2886, "rgba(56,189,248,.14)")],
    "torque": [(3.8, 76.6, "rgba(167,139,250,.14)")],
    "tool_wear_min": [
        (0, 180, "rgba(52,211,153,.14)"),
        (180, 253, "rgba(248,113,113,.18)"),
    ],
}


def _observation_from_row(row: dict) -> dict:
    features = compute_features(
        {
            "air_temp_c": float(row["air_temp_c"]),
            "process_temp_c": float(row["process_temp_c"]),
            "rpm": float(row["rpm"]),
            "torque": float(row["torque"]),
            "tool_wear_min": float(row["tool_wear_min"]),
        }
    )
    return features


def _dataset_position(clean: pd.DataFrame, features: dict) -> list[tuple]:
    rows = []
    for key, label in (
        ("air_temp_c", "Température air"),
        ("process_temp_c", "Température process"),
        ("rpm", "Vitesse broche"),
        ("torque", "Couple"),
        ("tool_wear_min", "Usure outil"),
    ):
        value = float(features[key])
        series = clean[key]
        pct = float((series <= value).mean() * 100)
        tone = "green" if 5 <= pct <= 95 else "amber"
        rows.append((label, f"{format_fr(value, 1)} · P{pct:.0f}", pct, tone))
    return rows


def render() -> None:
    diagnostics = load_diagnostics()
    fleet = fleet_snapshot(diagnostics)
    clean = load_clean()

    hero(
        "Operations control · Monitoring",
        "Chaque signal compte. Chaque dérive se voit.",
        "Inspection des mesures capteurs, des seuils de défaillance et du "
        "niveau de risque. Choisissez une machine déjà diagnostiquée ou une "
        "observation réelle du dataset AI4I 2020.",
        chips=["6 indicateurs", "Seuils documentés", "AI4I 2020"],
    )

    source_options = []
    if not fleet.empty:
        source_options.append("Flotte suivie")
    source_options.append("Observation du dataset")

    source = st.radio(
        "Source des mesures",
        source_options,
        horizontal=True,
        label_visibility="collapsed",
    )

    features = None
    machine_label = ""
    probability = None
    origin = ""

    if source == "Flotte suivie":
        machine_ids = fleet["machine_id"].tolist()
        machine_id = st.selectbox("Machine", machine_ids, key="monitor_machine")
        row = fleet[fleet["machine_id"] == machine_id].iloc[0]
        features = {
            "air_temp_c": float(row["air_temp_c"]),
            "process_temp_c": float(row["process_temp_c"]),
            "rpm": float(row["rpm"]),
            "torque": float(row["torque"]),
            "tool_wear_min": float(row["tool_wear_min"]),
            "temp_diff": float(row["temp_diff"]),
            "power_w": float(row["power_w"]),
        }
        probability = float(row["probability"])
        machine_label = f"Machine {machine_id} · type {row['machine_type']}"
        origin = f"Dernier diagnostic du {row['timestamp']:%d/%m/%Y à %H:%M}"
    else:
        preset = st.selectbox(
            "Observation de référence",
            list(MODE_CHOICES.keys()),
            format_func=lambda key: MODE_CHOICES[key],
            key="monitor_reference",
        )
        observation = reference_observation(preset)
        features = _observation_from_row(observation)
        probability = predict_failure(features, observation.get("machine_type", "L"))
        machine_label = f"Observation AI4I · {MODE_CHOICES[preset]}"
        origin = (
            f"Ligne réelle du dataset (UDI {observation.get('id', '—')}) · "
            "score calculé par le modèle XGBoost de l'application"
        )

    level = risk_level(probability)
    signals = detect_risk_signals(features)

    st.markdown(
        f'<div style="display:flex;flex-wrap:wrap;align-items:center;gap:.7rem;'
        f'margin:.3rem 0 1rem">{status_pill(level)}'
        f'<span style="color:#8da2bb;font-size:.78rem">{machine_label} · {origin}</span></div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(3)
    gauge_specs = [
        ("Température air", "air_temp_c", "°C", 22, 32, 1),
        ("Température process", "process_temp_c", "°C", 32, 41, 1),
        ("Vitesse broche", "rpm", " tr/min", 1168, 2886, 0),
        ("Couple", "torque", " Nm", 3.8, 76.6, 1),
        ("Usure outil", "tool_wear_min", " min", 0, 253, 0),
        ("Probabilité de panne", None, " %", 0, 100, 1),
    ]
    for index, (title, key, unit, vmin, vmax, digits) in enumerate(gauge_specs):
        with cols[index % 3]:
            if key is None:
                fig = charts.risk_gauge(probability, height=190)
            else:
                value = float(features[key])
                tone = "red" if key == "tool_wear_min" and value >= 180 else "cyan"
                fig = charts.gauge(
                    value,
                    min_value=vmin,
                    max_value=vmax,
                    title=title.upper(),
                    unit=unit,
                    steps=GAUGE_STEPS[key],
                    color="#f87171" if tone == "red" else "#22d3ee",
                    height=190,
                    decimals=digits,
                )
            st.plotly_chart(fig, width="stretch", config=charts.PLOT_CONFIG)

    left, right = st.columns([1.05, 1])
    with left:
        section_label("Position dans le dataset")
        st.caption(
            "Percentile de la mesure par rapport aux 10 000 observations réelles "
            "du dataset. P50 = médiane."
        )
        bar_list(_dataset_position(clean, features))
        st.markdown(
            '<div class="panel" style="margin-top:1rem">'
            '<div class="panel-title" style="font-size:.85rem">Pression hydraulique</div>'
            '<p class="panel-sub" style="margin-top:.2rem">'
            "Non instrumentée dans le dataset AI4I 2020 : aucune valeur n'est "
            "affichée pour éviter toute donnée inventée.</p></div>",
            unsafe_allow_html=True,
        )
    with right:
        section_label("Seuils de défaillance")
        signal_cards(signals)

    section_label("Synthèse du diagnostic")
    kpi_grid(
        [
            {
                "label": "Écart thermique",
                "value": f"{format_fr(features['temp_diff'], 2)} °C",
                "sub": "Seuil HDF : < 8,6 °C",
                "tone": "amber" if features["temp_diff"] < 8.6 else "green",
                "icon": "thermometer",
            },
            {
                "label": "Puissance physique",
                "value": f"{format_fr(features['power_w'], 0)} W",
                "sub": "Zone nominale 3 500–9 000 W",
                "tone": "amber"
                if not 3500 <= features["power_w"] <= 9000
                else "green",
                "icon": "zap",
            },
            {
                "label": "Produit usure × couple",
                "value": format_fr(features["tool_wear_min"] * features["torque"], 0),
                "sub": "Seuil OSF : > 11 000 min·Nm",
                "tone": "red"
                if features["tool_wear_min"] * features["torque"] > 11000
                else "green",
                "icon": "wrench",
            },
            {
                "label": "Modes déclenchés",
                "value": len(signals),
                "sub": "Heuristiques de seuils, distinctes du score XGBoost",
                "tone": level_tone(level),
                "icon": "target",
            },
        ]
    )

    section_label("Tendance enregistrée")
    if source == "Flotte suivie":
        history = (
            diagnostics[diagnostics["machine_id"] == machine_id]
            .sort_values("timestamp")
            .tail(60)
        )
    else:
        history = pd.DataFrame()
    if history.empty or len(history) < 2:
        empty_state(
            "activity",
            "Pas encore de tendance",
            "Une courbe nécessite au moins deux diagnostics enregistrés pour la "
            "même machine. Relancez un diagnostic depuis AI Prediction.",
            tone="slate",
        )
    else:
        st.plotly_chart(
            charts.line_series(
                history["timestamp"],
                [
                    {
                        "name": "Probabilité de panne",
                        "y": history["probability"],
                        "color": "#22d3ee",
                        "fill": True,
                    },
                    {
                        "name": "Usure outil (min)",
                        "y": history["tool_wear_min"] / 253,
                        "color": "#a78bfa",
                    },
                ],
                title="Derniers diagnostics de la machine",
                y_title="Probabilité / usure normalisée",
                height=320,
            ),
            width="stretch",
            config=charts.PLOT_CONFIG, theme=None,
        )

    st.caption(
        "Les jauges et les seuils proviennent de règles documentées du dataset "
        "AI4I 2020. Le score affiché reste une probabilité binaire XGBoost : "
        "les signaux de mode ne sont pas une classification multi-classes."
    )
