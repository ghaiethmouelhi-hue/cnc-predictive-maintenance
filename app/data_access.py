# -*- coding: utf-8 -*-
"""Accès aux données, au modèle XGBoost et aux métriques réelles du projet.

Aucune donnée n'est inventée ici : toutes les valeurs proviennent du dataset
AI4I 2020, du modèle sauvegardé, du scaler ou du résumé de fiabilité.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split

ROOT_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = ROOT_DIR / "models" / "xgboost_model.pkl"
SCALER_PATH = ROOT_DIR / "data" / "processed" / "scaler.pkl"
CLEAN_PATH = ROOT_DIR / "data" / "processed" / "ai4i2020_clean.csv"
FEATURES_PATH = ROOT_DIR / "data" / "processed" / "ai4i2020_features.csv"
RAW_PATH = ROOT_DIR / "data" / "raw" / "ai4i2020.csv"
SUMMARY_PATH = ROOT_DIR / "data" / "processed" / "reliability_summary.json"
REPORT_PATH = ROOT_DIR / "rapport_fiabilite_cnc.html"

FAILURE_THRESHOLD = 0.111

MODEL_FEATURE_COLS = [
    "air_temp_c",
    "process_temp_c",
    "rpm",
    "torque",
    "tool_wear_min",
    "temp_diff",
    "power",
    "wear_rate",
    "rpm_torque_ratio",
    "wear_temp_stress",
    "type_M",
]

SCALER_FEATURE_COLS = [
    "air_temp_c",
    "process_temp_c",
    "rpm",
    "torque",
    "tool_wear_min",
    "temp_diff",
    "power",
    "wear_rate",
    "rpm_torque_ratio",
    "wear_temp_stress",
]

# Plages du dataset UCI AI4I :
#   soft = plage d'entraînement, hard = garde-fou de saisie.
DATASET_RANGES = {
    "air_temp_c": (22.0, 32.0, 10.0, 50.0, "Temp. air", "°C"),
    "process_temp_c": (32.0, 41.0, 20.0, 60.0, "Temp. process", "°C"),
    "rpm": (1168, 2886, 100, 6000, "RPM", "tr/min"),
    "torque": (3.8, 76.6, 0.0, 200.0, "Couple", "Nm"),
    "tool_wear_min": (0, 253, 0, 600, "Usure outil", "min"),
}

MODE_LABELS = {
    "TWF": "Usure outil",
    "HDF": "Dissipation thermique",
    "PWF": "Défaut puissance",
    "OSF": "Surcharge mécanique",
    "RNF": "Panne aléatoire",
}

MODE_ICONS = {
    "TWF": "clock",
    "HDF": "thermometer",
    "PWF": "zap",
    "OSF": "wrench",
    "RNF": "sparkles",
}


# ─────────────────────────────────────────────────────────────
# Chargement des ressources
# ─────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_model():
    return joblib.load(MODEL_PATH)


@st.cache_resource(show_spinner=False)
def load_scaler():
    return joblib.load(SCALER_PATH)


@st.cache_resource(show_spinner="Initialisation de l'agent RAG…")
def load_agent():
    # Import différé : les embeddings ne sont chargés qu'au premier diagnostic.
    from rag.agent import MaintenanceAgent

    return MaintenanceAgent()


@st.cache_data(show_spinner=False)
def load_clean() -> pd.DataFrame:
    df = pd.read_csv(CLEAN_PATH)
    return _add_derived(df)


@st.cache_data(show_spinner=False)
def load_features() -> pd.DataFrame:
    return pd.read_csv(FEATURES_PATH)


@st.cache_data(show_spinner=False)
def load_raw() -> pd.DataFrame:
    if RAW_PATH.exists():
        raw = pd.read_csv(RAW_PATH)
        rename = {
            "UDI": "id",
            "Product ID": "product_id",
            "Type": "machine_type",
            "Air temperature [K]": "air_temp_k",
            "Process temperature [K]": "process_temp_k",
            "Rotational speed [rpm]": "rpm",
            "Torque [Nm]": "torque",
            "Tool wear [min]": "tool_wear_min",
            "Machine failure": "failure",
            "TWF": "twf",
            "HDF": "hdf",
            "PWF": "pwf",
            "OSF": "osf",
            "RNF": "rnf",
        }
        raw = raw.rename(columns=rename)
        raw["air_temp_c"] = raw["air_temp_k"] - 273.15
        raw["process_temp_c"] = raw["process_temp_k"] - 273.15
        return _add_derived(raw)
    # Repli : le dataset nettoyé ne contient pas les modes de panne.
    df = load_clean().copy()
    for mode in ("twf", "hdf", "pwf", "osf", "rnf"):
        df[mode] = 0
    df["id"] = np.arange(1, len(df) + 1)
    df["product_id"] = "—"
    return df


def _add_derived(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["temp_diff"] = out["process_temp_c"] - out["air_temp_c"]
    out["power"] = out["rpm"] * out["torque"]
    out["power_w"] = out["power"] * 2 * math.pi / 60
    out["wear_rate"] = out["tool_wear_min"] / (out["rpm"] + 1)
    out["rpm_torque_ratio"] = out["rpm"] / (out["torque"] + 1)
    out["wear_temp_stress"] = out["tool_wear_min"] * out["temp_diff"]
    out["osf_product"] = out["tool_wear_min"] * out["torque"]
    return out


@st.cache_data(show_spinner=False)
def load_summary() -> dict:
    if not SUMMARY_PATH.exists():
        return {}
    return json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))


# ─────────────────────────────────────────────────────────────
# Inférence
# ─────────────────────────────────────────────────────────────
def compute_features(raw: dict) -> dict:
    features = dict(raw)
    features["temp_diff"] = features["process_temp_c"] - features["air_temp_c"]
    features["power"] = features["rpm"] * features["torque"]
    features["power_w"] = features["power"] * 2 * math.pi / 60
    features["wear_rate"] = features["tool_wear_min"] / (features["rpm"] + 1)
    features["rpm_torque_ratio"] = features["rpm"] / (features["torque"] + 1)
    features["wear_temp_stress"] = features["tool_wear_min"] * features["temp_diff"]
    return features


def prepare_model_input(features: dict, machine_type: str, scaler) -> pd.DataFrame:
    numeric = pd.DataFrame(
        [[features[column] for column in SCALER_FEATURE_COLS]],
        columns=SCALER_FEATURE_COLS,
    )
    scaled = pd.DataFrame(scaler.transform(numeric), columns=SCALER_FEATURE_COLS)
    scaled["type_M"] = int(machine_type == "M")
    return scaled[MODEL_FEATURE_COLS]


def predict_failure(features: dict, machine_type: str) -> float:
    model = load_model()
    scaler = load_scaler()
    model_input = prepare_model_input(features, machine_type, scaler)
    return float(model.predict_proba(model_input)[0, 1])


def risk_level(probability: float) -> str:
    if probability >= 0.75:
        return "CRITIQUE"
    if probability >= 0.50:
        return "ÉLEVÉ"
    if probability >= FAILURE_THRESHOLD:
        return "MODÉRÉ"
    return "NORMAL"


def check_inputs(air_temp, process_temp, rpm, torque, tool_wear) -> tuple[list, list]:
    """Retourne (hallucinations bloquantes, avertissements de plage)."""
    hallucinations: list[str] = []
    warnings: list[str] = []
    values = {
        "air_temp_c": air_temp,
        "process_temp_c": process_temp,
        "rpm": rpm,
        "torque": torque,
        "tool_wear_min": tool_wear,
    }
    for key, value in values.items():
        soft_min, soft_max, hard_min, hard_max, label, unit = DATASET_RANGES[key]
        if value < hard_min or value > hard_max:
            hallucinations.append(
                f"**{label}** = {value} {unit} (plage dataset : "
                f"{soft_min} – {soft_max} {unit})"
            )
        elif value < soft_min or value > soft_max:
            warnings.append(
                f"**{label}** = {value} {unit} est en dehors de la plage "
                f"d'entraînement [{soft_min} – {soft_max} {unit}]"
            )
    return hallucinations, warnings


def detect_risk_signals(features: dict) -> list[dict]:
    """Heuristiques de surveillance alignées sur les règles du dataset.

    Ce n'est pas une classification de cause par XGBoost : le modèle prédit
    une probabilité binaire de panne. Ces signaux explicitent les seuils
    documentés du dataset pour aider la lecture humaine.
    """
    wear = float(features.get("tool_wear_min", 0))
    temp_diff = float(features.get("temp_diff", 0))
    torque = float(features.get("torque", 0))
    rpm = float(features.get("rpm", 0))
    power_w = rpm * torque * 2 * math.pi / 60
    osf_product = wear * torque

    signals: list[dict] = []

    if wear >= 180:
        signals.append(
            {
                "mode": "TWF",
                "severity": "critical" if wear >= 200 else "warning",
                "title": "Usure outil — TWF",
                "detail": f"Usure {wear:.0f} min ≥ 180 min "
                f"(première panne TWF du dataset : 198 min).",
                "action": "Remplacer l'outil avant le prochain cycle.",
            }
        )

    if temp_diff < 8.6:
        signals.append(
            {
                "mode": "HDF",
                "severity": "critical" if temp_diff < 7.8 else "warning",
                "title": "Dissipation thermique — HDF",
                "detail": f"Écart thermique {temp_diff:.1f} °C < 8,6 °C "
                "(seuil des pannes HDF).",
                "action": "Vérifier le refroidissement, le débit de liquide et les filtres.",
            }
        )

    if power_w < 3500 or power_w > 9000:
        signals.append(
            {
                "mode": "PWF",
                "severity": "critical" if power_w < 1200 or power_w > 10000 else "warning",
                "title": "Puissance hors plage — PWF",
                "detail": f"Puissance physique {power_w:,.0f} W hors "
                "[3 500 ; 9 000] W.",
                "action": "Réduire la profondeur de passe ou vérifier l'alimentation broche.",
            }
        )

    if osf_product > 11000:
        signals.append(
            {
                "mode": "OSF",
                "severity": "critical" if osf_product > 13000 else "warning",
                "title": "Surcharge mécanique — OSF",
                "detail": f"Produit usure × couple = {osf_product:,.0f} min·Nm "
                "> 11 000 (seuil OSF).",
                "action": "Réduire le couple et inspecter l'outil (déformation, fissures).",
            }
        )

    return signals


def reference_observation(mode: str = "NORMAL") -> dict:
    """Retourne une observation réelle du dataset AI4I 2020."""
    raw = load_raw()
    if mode == "NORMAL":
        subset = raw[raw["failure"] == 0]
    else:
        column = mode.lower()
        subset = raw[raw[column] == 1] if column in raw.columns else raw.iloc[0:0]
    if subset.empty:
        subset = raw
    row = subset.iloc[len(subset) // 2]
    return row.to_dict()


# ─────────────────────────────────────────────────────────────
# Métriques modèle (calculées sur le jeu de test réel)
# ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Évaluation du modèle sur le jeu de test…")
def get_model_metrics() -> dict:
    model = load_model()
    df = load_features()
    columns = list(model.get_booster().feature_names)
    X = df[columns]
    y = df["failure"]
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    probabilities = model.predict_proba(X_test)[:, 1]

    fpr, tpr, roc_thresholds = roc_curve(y_test, probabilities)
    precision, recall, pr_thresholds = precision_recall_curve(y_test, probabilities)
    auc_roc = roc_auc_score(y_test, probabilities)
    auc_pr = average_precision_score(y_test, probabilities)

    threshold_rows = []
    for threshold in np.arange(0.05, 0.96, 0.05):
        predicted = (probabilities >= threshold).astype(int)
        threshold_rows.append(
            {
                "Seuil": round(float(threshold), 2),
                "Précision": precision_score(y_test, predicted, zero_division=0),
                "Rappel": recall_score(y_test, predicted, zero_division=0),
                "F1": f1_score(y_test, predicted, zero_division=0),
                "Alertes": int(predicted.sum()),
            }
        )
    threshold_df = pd.DataFrame(threshold_rows)

    predicted_at_app = (probabilities >= FAILURE_THRESHOLD).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_test, predicted_at_app).ravel()

    f1_curve = 2 * precision * recall / np.clip(precision + recall, 1e-12, None)
    best_index = int(np.argmax(f1_curve))
    best_f1 = float(f1_curve[best_index])
    best_threshold = float(pr_thresholds[min(best_index, len(pr_thresholds) - 1)])

    return {
        "auc_roc": float(auc_roc),
        "auc_pr": float(auc_pr),
        "fpr": fpr,
        "tpr": tpr,
        "roc_thresholds": roc_thresholds,
        "precision": precision,
        "recall": recall,
        "pr_thresholds": pr_thresholds,
        "f1_curve": f1_curve,
        "best_f1": best_f1,
        "best_threshold": best_threshold,
        "threshold_df": threshold_df,
        "confusion": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "test_size": int(len(y_test)),
        "test_failures": int(y_test.sum()),
        "precision_at_app": float(precision_score(y_test, predicted_at_app, zero_division=0)),
        "recall_at_app": float(recall_score(y_test, predicted_at_app, zero_division=0)),
        "f1_at_app": float(f1_score(y_test, predicted_at_app, zero_division=0)),
        "probabilities": probabilities,
        "y_test": y_test.to_numpy(),
    }


@st.cache_data(show_spinner=False)
def get_feature_importance() -> pd.DataFrame:
    model = load_model()
    names = list(model.get_booster().feature_names)
    values = np.asarray(model.feature_importances_, dtype=float)
    return (
        pd.DataFrame({"Feature": names, "Importance": values})
        .sort_values("Importance", ascending=True)
        .reset_index(drop=True)
    )


@st.cache_data(show_spinner=False)
def dataset_overview() -> dict:
    clean = load_clean()
    raw = load_raw()
    type_counts = clean["machine_type"].value_counts().to_dict()
    failure_by_type = clean.groupby("machine_type")["failure"].agg(["count", "sum"])
    mode_counts = {}
    for mode, column in (("TWF", "twf"), ("HDF", "hdf"), ("PWF", "pwf"), ("OSF", "osf"), ("RNF", "rnf")):
        if column in raw.columns:
            mode_counts[mode] = int(raw[column].sum())
    return {
        "n_rows": int(len(clean)),
        "n_fail": int(clean["failure"].sum()),
        "fail_rate": float(clean["failure"].mean()),
        "type_counts": type_counts,
        "failure_by_type": failure_by_type,
        "mode_counts": mode_counts,
        "n_modes": int(sum(mode_counts.values())),
    }
