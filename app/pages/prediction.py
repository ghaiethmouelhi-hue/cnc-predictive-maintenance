# -*- coding: utf-8 -*-
"""AI Prediction — diagnostic XGBoost et recommandation RAG."""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from app import charts
from app.components import (
    empty_state,
    hero,
    kpi_grid,
    level_tone,
    recommendation_cards,
    section_label,
    signal_cards,
    status_pill,
)
from app.config import is_demo_mode
from app.data_access import (
    check_inputs,
    compute_features,
    detect_risk_signals,
    get_feature_importance,
    load_agent,
    predict_failure,
    reference_observation,
    risk_level,
)
from app.history_store import append_diagnostic
from app.theme import format_fr

DEFAULTS = {
    "air_temp_c": 26.95,
    "process_temp_c": 36.95,
    "rpm": 1503.0,
    "torque": 40.1,
    "tool_wear_min": 108.0,
}

PRESETS = {
    "Médianes du dataset": "medians",
    "Observation normale du dataset": "NORMAL",
    "Panne usure outil (TWF)": "TWF",
    "Panne dissipation thermique (HDF)": "HDF",
    "Panne puissance (PWF)": "PWF",
    "Panne surcharge (OSF)": "OSF",
    "Panne aléatoire (RNF)": "RNF",
}


def _apply_preset() -> None:
    key = PRESETS[st.session_state["pred_preset"]]
    if key == "medians":
        values = DEFAULTS
        machine_type = "L"
    else:
        row = reference_observation(key)
        values = {
            "air_temp_c": round(float(row["air_temp_c"]), 2),
            "process_temp_c": round(float(row["process_temp_c"]), 2),
            "rpm": float(row["rpm"]),
            "torque": round(float(row["torque"]), 2),
            "tool_wear_min": float(row["tool_wear_min"]),
        }
        machine_type = str(row.get("machine_type", "L"))
    st.session_state["pred_air"] = values["air_temp_c"]
    st.session_state["pred_process"] = values["process_temp_c"]
    st.session_state["pred_rpm"] = values["rpm"]
    st.session_state["pred_torque"] = values["torque"]
    st.session_state["pred_wear"] = values["tool_wear_min"]
    st.session_state["pred_type"] = machine_type


def _initialise_state() -> None:
    defaults = {
        "pred_machine_id": "CNC-01",
        "pred_type": "L",
        "pred_air": DEFAULTS["air_temp_c"],
        "pred_process": DEFAULTS["process_temp_c"],
        "pred_rpm": DEFAULTS["rpm"],
        "pred_torque": DEFAULTS["torque"],
        "pred_wear": DEFAULTS["tool_wear_min"],
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _render_advice(advice: dict) -> None:
    if advice.get("demo_mode"):
        st.warning(
            "Mode démonstration — génération Gemini désactivée. "
            "La prédiction XGBoost, les seuils métier et la recherche "
            "vectorielle restent opérationnels ; aucun conseil n'est inventé."
        )
        st.markdown(
            f"**Risque ML : {advice.get('niveau_risque', '—')}** · "
            f"**Panne probable : {advice.get('type_panne_probable', '—')}**"
        )
        st.markdown(f"**Action immédiate** — {advice.get('action_immediate', '—')}")
        st.markdown(f"**Pour activer l'IA** — {advice.get('action_preventive', '—')}")

        context = (advice.get("rag_context") or "").strip()
        if context:
            st.markdown("**Extraits réellement retrouvés dans la base RAG**")
            for block in [part.strip() for part in context.split("\n\n") if part.strip()][:3]:
                st.markdown("\n".join(f"> {line}" for line in block.splitlines()))
            st.caption(
                "Extraits de data/knowledge/cnc_knowledge.md — aucune synthèse "
                "par LLM en mode démonstration."
            )
        return

    if advice.get("service_error"):
        st.warning(advice.get("explication", "Service IA indisponible."))
        st.info(
            "La prédiction XGBoost reste valide. Aucun conseil IA n'a été généré : "
            "aucun texte n'est simulé."
        )
        return
    st.markdown(
        f"**Risque : {advice.get('niveau_risque', '—')}** · "
        f"**Panne probable : {advice.get('type_panne_probable', '—')}**"
    )
    recommendation_cards(
        advice.get("explication", "—"),
        advice.get("action_immediate", "—"),
        advice.get("action_preventive", "—"),
    )


def render() -> None:
    _initialise_state()
    hero(
        "Intelligence · AI Prediction",
        "Un score clair, des causes explicites, une action.",
        "Le modèle XGBoost estime la probabilité binaire de panne. Le RAG "
        "recherche ensuite la connaissance maintenance et Gemini formule une "
        "recommandation structurée.",
        accent="violet",
        chips=["XGBoost", "RAG Gemini", "Seuil 0,111"],
    )

    if is_demo_mode():
        st.info(
            "**Mode démonstration** — aucune clé API Gemini n'est configurée. "
            "Le diagnostic XGBoost, les causes heuristiques et la recherche RAG "
            "restent utilisables. La génération de texte par Gemini est désactivée "
            "et remplacée par l'affichage des extraits de la base de connaissances."
        )

    left, right = st.columns([1.02, 1.18], gap="large")

    with left:
        section_label("Mesures capteurs")
        st.selectbox(
            "Charger une observation réelle",
            list(PRESETS.keys()),
            key="pred_preset",
            on_change=_apply_preset,
            help="Pré-remplit le formulaire avec une observation du dataset AI4I 2020.",
        )

        with st.form("prediction_form", border=True):
            machine_id = st.text_input("Identifiant machine", key="pred_machine_id")
            machine_type = st.selectbox(
                "Type de machine",
                ["L", "M", "H"],
                key="pred_type",
                help="Type L, M ou H du dataset AI4I 2020.",
            )
            col_a, col_b = st.columns(2)
            with col_a:
                air_temp = st.number_input(
                    "Température air (°C)",
                    min_value=10.0,
                    max_value=50.0,
                    step=0.1,
                    key="pred_air",
                )
                rpm = st.number_input(
                    "Vitesse broche (tr/min)",
                    min_value=100.0,
                    max_value=6000.0,
                    step=1.0,
                    key="pred_rpm",
                )
                tool_wear = st.number_input(
                    "Usure outil (min)",
                    min_value=0.0,
                    max_value=600.0,
                    step=1.0,
                    key="pred_wear",
                )
            with col_b:
                process_temp = st.number_input(
                    "Température process (°C)",
                    min_value=20.0,
                    max_value=60.0,
                    step=0.1,
                    key="pred_process",
                )
                torque = st.number_input(
                    "Couple (Nm)",
                    min_value=0.0,
                    max_value=200.0,
                    step=0.1,
                    key="pred_torque",
                )
            submitted = st.form_submit_button(
                "RUN AI DIAGNOSTIC",
                type="primary",
                width="stretch",
            )

        if submitted:
            hallucinations, warnings = check_inputs(
                air_temp, process_temp, rpm, torque, tool_wear
            )
            if hallucinations:
                st.error(
                    "Saisie hors plage physique : la prédiction est bloquée pour "
                    "éviter un résultat trompeur."
                )
                for item in hallucinations:
                    st.markdown(f"- {item}")
            elif not machine_id.strip():
                st.error("Renseignez un identifiant machine.")
            else:
                features = compute_features(
                    {
                        "air_temp_c": float(air_temp),
                        "process_temp_c": float(process_temp),
                        "rpm": float(rpm),
                        "torque": float(torque),
                        "tool_wear_min": float(tool_wear),
                    }
                )
                probability = predict_failure(features, machine_type)
                level = risk_level(probability)
                signals = detect_risk_signals(features)
                st.session_state["last_prediction"] = {
                    "machine_id": machine_id.strip(),
                    "machine_type": machine_type,
                    "features": features,
                    "probability": probability,
                    "risk_level": level,
                    "signals": signals,
                    "warnings": warnings,
                    "timestamp": datetime.now(),
                }
                st.session_state["cnc_advice"] = None
                append_diagnostic(
                    {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "machine_id": machine_id.strip(),
                        "machine_type": machine_type,
                        "air_temp_c": round(float(air_temp), 3),
                        "process_temp_c": round(float(process_temp), 3),
                        "rpm": round(float(rpm), 3),
                        "torque": round(float(torque), 3),
                        "tool_wear_min": round(float(tool_wear), 3),
                        "temp_diff": round(features["temp_diff"], 3),
                        "power_w": round(features["power_w"], 2),
                        "probability": round(probability, 6),
                        "risk_level": level,
                        "signals": " | ".join(signal["mode"] for signal in signals),
                        "warnings": " | ".join(warnings),
                    }
                )
                st.success("Diagnostic enregistré dans l'historique local.")

        section_label("Importance des variables")
        importance = get_feature_importance().tail(8)
        st.plotly_chart(
            charts.bar(
                importance["Feature"].tolist(),
                importance["Importance"].tolist(),
                title="Contribution des variables — modèle XGBoost",
                horizontal=True,
                color="#a78bfa",
                height=300,
            ),
            width="stretch",
            config=charts.PLOT_CONFIG, theme=None,
        )

    with right:
        prediction = st.session_state.get("last_prediction")
        if not prediction:
            section_label("Résultat du diagnostic")
            empty_state(
                "brain",
                "Prêt pour un diagnostic",
                "Renseignez les mesures puis lancez RUN AI DIAGNOSTIC. Le score, "
                "les causes possibles et les recommandations s'afficheront ici.",
                tone="violet",
            )
        else:
            features = prediction["features"]
            probability = prediction["probability"]
            level = prediction["risk_level"]
            signals = prediction["signals"]

            st.markdown(
                f'<div style="display:flex;flex-wrap:wrap;align-items:center;gap:.6rem;'
                f'margin:.3rem 0 .8rem">{status_pill(level)}'
                f'<span style="color:#8da2bb;font-size:.78rem">'
                f'{prediction["machine_id"]} · type {prediction["machine_type"]} · '
                f'{prediction["timestamp"]:%d/%m/%Y %H:%M}</span></div>',
                unsafe_allow_html=True,
            )

            gauge_col, metric_col = st.columns([1, 1.05])
            with gauge_col:
                st.plotly_chart(
                    charts.risk_gauge(probability, height=215),
                    width="stretch",
                    config=charts.PLOT_CONFIG, theme=None,
                )
            with metric_col:
                kpi_grid(
                    [
                        {
                            "label": "Décision",
                            "value": "PANNE PROBABLE"
                            if probability >= 0.111
                            else "NORMAL",
                            "sub": "Seuil de décision 0,111",
                            "tone": level_tone(level),
                            "icon": "target",
                        },
                        {
                            "label": "Écart thermique",
                            "value": f"{format_fr(features['temp_diff'], 1)} °C",
                            "sub": "Seuil HDF < 8,6 °C",
                            "tone": "amber"
                            if features["temp_diff"] < 8.6
                            else "green",
                            "icon": "thermometer",
                        },
                        {
                            "label": "Puissance",
                            "value": f"{format_fr(features['power_w'], 0)} W",
                            "sub": "Zone nominale 3 500–9 000 W",
                            "tone": "green"
                            if 3500 <= features["power_w"] <= 9000
                            else "amber",
                            "icon": "zap",
                        },
                    ]
                )

            if prediction["warnings"]:
                st.warning(
                    "Certaines mesures sortent de la plage d'entraînement : "
                    "interprétez le score avec prudence."
                )
                with st.expander("Voir les avertissements"):
                    for warning in prediction["warnings"]:
                        st.markdown(f"- {warning}")

            section_label("Causes possibles")
            if signals:
                signal_cards(signals)
            else:
                empty_state(
                    "check",
                    "Aucun seuil documenté franchi",
                    "Le score ne s'accompagne d'aucun dépassement des seuils TWF, "
                    "HDF, PWF ou OSF. Une panne aléatoire (RNF) reste possible : "
                    "le modèle ne fournit pas de cause certaine.",
                    tone="green",
                )
            if signals:
                st.caption(
                    "Causes heuristiques issues des seuils documentés du dataset — "
                    "distinctes de la classification binaire XGBoost."
                )

            st.divider()
            if is_demo_mode():
                st.caption(
                    "Mode démonstration : la recherche RAG s'exécute, la "
                    "génération Gemini est désactivée faute de clé API."
                )
            if st.button("Générer la recommandation IA (RAG)", type="primary", width="stretch"):
                with st.spinner(
                    "Recherche dans la base de connaissances et génération du conseil…"
                ):
                    try:
                        agent = load_agent()
                        st.session_state["cnc_advice"] = agent.get_advice(
                            features, probability
                        )
                    except Exception as error:  # pragma: no cover - service externe
                        st.session_state["cnc_advice"] = {
                            "service_error": True,
                            "explication": f"Agent RAG indisponible ({type(error).__name__}).",
                        }

            advice = st.session_state.get("cnc_advice")
            if advice:
                _render_advice(advice)

            st.caption(
                "Le score XGBoost et les seuils sont calculés localement. La "
                "recommandation RAG dépend d'un appel Gemini : en cas d'erreur "
                "de service, aucun conseil n'est inventé."
            )
