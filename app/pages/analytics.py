# -*- coding: utf-8 -*-
"""Analytics — exploration du dataset et performance du modèle."""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from app import charts
from app.components import hero, kpi_grid, section_label
from app.data_access import (
    FAILURE_THRESHOLD,
    dataset_overview,
    get_feature_importance,
    get_model_metrics,
    load_clean,
)
from app.theme import format_fr, format_pct

MODES = ["TWF", "HDF", "PWF", "OSF", "RNF"]


def _dataset_tab() -> None:
    clean = load_clean()
    stats = dataset_overview()

    kpi_grid(
        [
            {
                "label": "Observations",
                "value": format_fr(stats["n_rows"], 0),
                "sub": "Dataset AI4I 2020 nettoyé",
                "tone": "cyan",
                "icon": "database",
            },
            {
                "label": "Pannes",
                "value": stats["n_fail"],
                "sub": format_pct(stats["fail_rate"], 2) + " du dataset",
                "tone": "red",
                "icon": "critical",
            },
            {
                "label": "Type L",
                "value": stats["type_counts"].get("L", 0),
                "sub": "60 % du parc simulé",
                "tone": "cyan",
                "icon": "server",
            },
            {
                "label": "Type M",
                "value": stats["type_counts"].get("M", 0),
                "sub": "30 % du parc simulé",
                "tone": "blue",
                "icon": "server",
            },
            {
                "label": "Type H",
                "value": stats["type_counts"].get("H", 0),
                "sub": "10 % du parc simulé",
                "tone": "violet",
                "icon": "server",
            },
        ]
    )

    section_label("Distributions capteurs")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            charts.histogram(
                clean["air_temp_c"],
                title="Température air",
                color="#22d3ee",
                x_title="°C",
                bins=40,
            ),
            width="stretch",
            config=charts.PLOT_CONFIG,
            theme=None,
        )
    with col2:
        st.plotly_chart(
            charts.histogram(
                clean["process_temp_c"],
                title="Température process",
                color="#3b82f6",
                x_title="°C",
                bins=40,
            ),
            width="stretch",
            config=charts.PLOT_CONFIG,
            theme=None,
        )
    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(
            charts.histogram(
                clean["torque"],
                title="Couple",
                color="#a78bfa",
                x_title="Nm",
                bins=40,
            ),
            width="stretch",
            config=charts.PLOT_CONFIG,
            theme=None,
        )
    with col4:
        st.plotly_chart(
            charts.histogram(
                clean["tool_wear_min"],
                title="Usure outil",
                color="#fbbf24",
                x_title="min",
                bins=40,
            ),
            width="stretch",
            config=charts.PLOT_CONFIG,
            theme=None,
        )

    section_label("Modes de défaillance & types")
    col5, col6 = st.columns([1, 1.1])
    with col5:
        mode_counts = stats["mode_counts"]
        st.plotly_chart(
            charts.donut(
                MODES,
                [mode_counts.get(mode, 0) for mode in MODES],
                title="Modes documentés",
                center_value=str(stats["n_modes"]),
                center_label="modes cumulés",
                colors=["#22d3ee", "#f87171", "#fbbf24", "#a78bfa", "#34d399"],
                height=330,
            ),
            width="stretch",
            config=charts.PLOT_CONFIG,
            theme=None,
        )
    with col6:
        failure_by_type = (
            clean.groupby("machine_type")["failure"].agg(["count", "sum"]).reindex(["L", "M", "H"])
        )
        st.plotly_chart(
            charts.grouped_bar(
                [f"Type {label}" for label in failure_by_type.index],
                {
                    "Observations (÷ 100)": (failure_by_type["count"] / 100).round(1).tolist(),
                    "Pannes": failure_by_type["sum"].tolist(),
                },
                title="Volume et pannes par type",
                height=330,
            ),
            width="stretch",
            config=charts.PLOT_CONFIG,
            theme=None,
        )

    section_label("Corrélations")
    st.plotly_chart(
        charts.correlation_heatmap(clean),
        width="stretch",
        config=charts.PLOT_CONFIG,
        theme=None,
    )


def _model_tab() -> None:
    metrics = get_model_metrics()

    kpi_grid(
        [
            {
                "label": "AUC-ROC",
                "value": f"{metrics['auc_roc']:.4f}".replace(".", ","),
                "sub": f"Jeu de test · {metrics['test_size']} observations",
                "tone": "cyan",
                "icon": "target",
            },
            {
                "label": "AUC-PR",
                "value": f"{metrics['auc_pr']:.4f}".replace(".", ","),
                "sub": "Classe minoritaire (pannes)",
                "tone": "violet",
                "icon": "activity",
            },
            {
                "label": "Rappel @ 0,111",
                "value": format_pct(metrics["recall_at_app"], 1),
                "sub": f"{metrics['confusion']['tp']} pannes détectées / "
                f"{metrics['test_failures']}",
                "tone": "green",
                "icon": "check",
            },
            {
                "label": "Précision @ 0,111",
                "value": format_pct(metrics["precision_at_app"], 1),
                "sub": f"{metrics['confusion']['fp']} faux positifs",
                "tone": "amber",
                "icon": "alert",
            },
            {
                "label": "F1 @ 0,111",
                "value": f"{metrics['f1_at_app']:.4f}".replace(".", ","),
                "sub": "Compromis précision / rappel",
                "tone": "blue",
                "icon": "gauge",
            },
            {
                "label": "Meilleur F1",
                "value": f"{metrics['best_f1']:.4f}".replace(".", ","),
                "sub": f"Seuil {metrics['best_threshold']:.2f}",
                "tone": "cyan",
                "icon": "sparkles",
            },
        ]
    )

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            charts.roc_curve_chart(metrics),
            width="stretch",
            config=charts.PLOT_CONFIG,
            theme=None,
        )
    with col2:
        st.plotly_chart(
            charts.pr_curve_chart(metrics),
            width="stretch",
            config=charts.PLOT_CONFIG,
            theme=None,
        )

    col3, col4 = st.columns([1.2, 1])
    with col3:
        st.plotly_chart(
            charts.threshold_chart(metrics),
            width="stretch",
            config=charts.PLOT_CONFIG,
            theme=None,
        )
    with col4:
        st.plotly_chart(
            charts.confusion_chart(metrics),
            width="stretch",
            config=charts.PLOT_CONFIG,
            theme=None,
        )

    section_label("Arbitrage du seuil")
    table = metrics["threshold_df"].copy()
    table["Précision"] = table["Précision"].map(lambda value: format_pct(value, 1))
    table["Rappel"] = table["Rappel"].map(lambda value: format_pct(value, 1))
    table["F1"] = table["F1"].map(lambda value: f"{value:.3f}".replace(".", ","))
    st.dataframe(table, width="stretch", hide_index=True)

    section_label("Importance des variables")
    importance = get_feature_importance()
    st.plotly_chart(
        charts.bar(
            importance["Feature"].tolist(),
            importance["Importance"].tolist(),
            title="Contribution globale du modèle XGBoost",
            horizontal=True,
            color="#22d3ee",
            height=380,
        ),
        width="stretch",
        config=charts.PLOT_CONFIG,
        theme=None,
    )
    st.caption(
        f"Seuil applicatif : {FAILURE_THRESHOLD}. Les métriques sont recalculées "
        "sur le même split stratifié que l'entraînement (random_state=42)."
    )


def _sensors_tab() -> None:
    clean = load_clean()

    section_label("Relations capteurs / panne")
    sample = clean.sample(min(len(clean), 4000), random_state=7)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            charts.scatter(
                sample["process_temp_c"],
                sample["air_temp_c"],
                title="Températures air × process",
                color_values=sample["failure"],
                x_title="Température process (°C)",
                y_title="Température air (°C)",
                colorbar_title="Panne",
                height=340,
            ),
            width="stretch",
            config=charts.PLOT_CONFIG,
            theme=None,
        )
    with col2:
        st.plotly_chart(
            charts.scatter(
                sample["rpm"],
                sample["torque"],
                title="RPM × couple",
                color_values=sample["failure"],
                x_title="tr/min",
                y_title="Nm",
                colorbar_title="Panne",
                height=340,
            ),
            width="stretch",
            config=charts.PLOT_CONFIG,
            theme=None,
        )

    section_label("Taux de panne par tranche d'usure")
    bins = [0, 50, 100, 150, 200, 253]
    labels = ["0–50", "50–100", "100–150", "150–200", "200–253"]
    clean = clean.copy()
    clean["wear_bin"] = pd.cut(
        clean["tool_wear_min"], bins=bins, labels=labels, include_lowest=True
    )
    rates = clean.groupby("wear_bin", observed=False)["failure"].mean() * 100
    counts = clean.groupby("wear_bin", observed=False)["failure"].size()
    st.plotly_chart(
        charts.bar(
            labels,
            rates.tolist(),
            title="Taux de panne (%) par tranche d'usure (min)",
            color="#fbbf24",
            text_suffix=" %",
            height=320,
        ),
        width="stretch",
        config=charts.PLOT_CONFIG,
        theme=None,
    )
    st.dataframe(
        pd.DataFrame(
            {
                "Tranche (min)": labels,
                "Observations": counts.tolist(),
                "Pannes": [
                    int(round(rate / 100 * count))
                    for rate, count in zip(rates.tolist(), counts.tolist())
                ],
                "Taux de panne": [format_pct(rate, 1, already_pct=True) for rate in rates],
            }
        ),
        width="stretch",
        hide_index=True,
    )

    section_label("Écart thermique et puissance")
    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(
            charts.histogram(
                clean.loc[clean["failure"] == 1, "temp_diff"],
                title=f"Écart thermique des {int(clean['failure'].sum())} pannes",
                color="#f87171",
                x_title="°C",
                bins=30,
            ),
            width="stretch",
            config=charts.PLOT_CONFIG,
            theme=None,
        )
    with col4:
        power_kw = clean["power"] * 2 * np.pi / 60 / 1000
        st.plotly_chart(
            charts.histogram(
                power_kw,
                title="Puissance physique (kW)",
                color="#3b82f6",
                x_title="kW",
                bins=40,
            ),
            width="stretch",
            config=charts.PLOT_CONFIG,
            theme=None,
        )


def render() -> None:
    hero(
        "Intelligence · Analytics",
        "Les données racontent la machine avant la panne.",
        "Exploration du dataset AI4I 2020, performance réelle du modèle sur le "
        "jeu de test et relations capteurs-pannes. Toutes les valeurs sont "
        "recalculées depuis les fichiers du projet.",
        accent="green",
        chips=["10 000 observations", "Jeu de test réel", "ROC · PR · seuils"],
    )

    tab_dataset, tab_model, tab_sensors = st.tabs(
        ["Dataset", "Modèle XGBoost", "Capteurs & pannes"]
    )
    with tab_dataset:
        _dataset_tab()
    with tab_model:
        _model_tab()
    with tab_sensors:
        _sensors_tab()
