import os
from pathlib import Path

import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_curve,
    roc_auc_score,
    precision_recall_curve,
    average_precision_score,
    confusion_matrix,
    classification_report,
    f1_score,
    precision_score,
    recall_score
)

ROOT = Path(__file__).resolve().parents[1]
FEATURES_PATH = str(ROOT / "data" / "processed" / "ai4i2020_features.csv")
MODEL_PATH    = str(ROOT / "models" / "xgboost_model.pkl")
FIGURES_PATH  = str(ROOT / "data" / "processed")

TARGET_COL   = "failure"
FEATURE_COLS = [
    "air_temp_c", "process_temp_c", "rpm", "torque", "tool_wear_min",
    "temp_diff", "power", "wear_rate", "rpm_torque_ratio",
    "wear_temp_stress",  
    "type_M"
]


def load_model_and_data() -> tuple:
    model = joblib.load(MODEL_PATH)
    df    = pd.read_csv(FEATURES_PATH)

    available = [c for c in FEATURE_COLS if c in df.columns]
    X = df[available]
    y = df[TARGET_COL]

    _, X_test, _, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    print(f"[OK] Modele charge   : {MODEL_PATH}")
    print(f"[OK] Test set charge : {X_test.shape[0]:,} lignes x {X_test.shape[1]} features")
    return model, X_test, y_test


def compute_predictions(model, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    y_proba = model.predict_proba(X_test)[:, 1]
    y_pred  = model.predict(X_test)

    auc_roc = roc_auc_score(y_test, y_proba)
    auc_pr  = average_precision_score(y_test, y_proba)

    print(f"\n--- Métriques globales ---")
    print(f"  AUC-ROC          : {auc_roc:.4f}  (1.0 = parfait, 0.5 = aléatoire)")
    print(f"  AUC-PR           : {auc_pr:.4f}  (résumé courbe précision/rappel)")
    print(f"  F1-Score (0.5)   : {f1_score(y_test, y_pred):.4f}")
    print(f"  Précision (0.5)  : {precision_score(y_test, y_pred):.4f}")
    print(f"  Rappel    (0.5)  : {recall_score(y_test, y_pred):.4f}")

    return {"y_proba": y_proba, "y_pred": y_pred, "auc_roc": auc_roc, "auc_pr": auc_pr}


def plot_roc_curve(y_test: pd.Series, results: dict) -> None:
    fpr, tpr, thresholds = roc_curve(y_test, results["y_proba"])

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(fpr, tpr, color="steelblue", linewidth=2,
            label=f"XGBoost (AUC = {results['auc_roc']:.3f})")
    ax.plot([0, 1], [0, 1], color="gray", linestyle="--",
            linewidth=1, label="Modèle aléatoire (AUC = 0.5)")

    optimal_idx       = np.argmax(tpr - fpr)
    optimal_threshold = thresholds[optimal_idx]
    ax.scatter(fpr[optimal_idx], tpr[optimal_idx],
               color="firebrick", s=100, zorder=5,
               label=f"Seuil optimal = {optimal_threshold:.2f}")

    ax.set_xlabel("Taux de Faux Positifs (fausses alarmes)")
    ax.set_ylabel("Taux de Vrais Positifs (rappel)")
    ax.set_title("Courbe ROC")
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_PATH, "roc_curve.png"), dpi=150, bbox_inches="tight")
    plt.show()

    print(f"\n--- Courbe ROC ---")
    print(f"  Seuil optimal    : {optimal_threshold:.3f}")
    print(f"  Rappel associé   : {tpr[optimal_idx]:.3f}")
    print(f"  Fausses alarmes  : {fpr[optimal_idx]:.3f}")


def plot_precision_recall_curve(y_test: pd.Series, results: dict) -> None:
    precision, recall, thresholds = precision_recall_curve(y_test, results["y_proba"])

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(recall, precision, color="darkorange", linewidth=2,
            label=f"XGBoost (AUC-PR = {results['auc_pr']:.3f})")

    baseline = y_test.mean()
    ax.axhline(y=baseline, color="gray", linestyle="--",
               linewidth=1, label=f"Modèle aléatoire ({baseline:.3f})")

    f1_scores      = 2 * (precision * recall) / (precision + recall + 1e-9)
    best_idx       = np.argmax(f1_scores)
    best_threshold = thresholds[best_idx] if best_idx < len(thresholds) else thresholds[-1]

    ax.scatter(recall[best_idx], precision[best_idx],
               color="firebrick", s=100, zorder=5,
               label=f"F1 max → seuil = {best_threshold:.2f}")

    ax.set_xlabel("Rappel (% de vraies pannes détectées)")
    ax.set_ylabel("Précision (% d'alarmes qui sont vraies)")
    ax.set_title("Courbe Précision / Rappel")
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_PATH, "precision_recall_curve.png"), dpi=150, bbox_inches="tight")
    plt.show()

    print(f"\n--- Courbe Précision/Rappel ---")
    print(f"  Seuil F1 max     : {best_threshold:.3f}")
    print(f"  Précision assoc. : {precision[best_idx]:.3f}")
    print(f"  Rappel associé   : {recall[best_idx]:.3f}")
    print(f"  F1-Score max     : {f1_scores[best_idx]:.3f}")


def plot_threshold_analysis(y_test: pd.Series, results: dict) -> None:
    thresholds  = np.arange(0.01, 1.0, 0.01)
    precisions  = []
    recalls     = []
    f1_scores   = []

    for t in thresholds:
        y_pred_t = (results["y_proba"] >= t).astype(int)
        precisions.append(precision_score(y_test, y_pred_t, zero_division=0))
        recalls.append(recall_score(y_test, y_pred_t, zero_division=0))
        f1_scores.append(f1_score(y_test, y_pred_t, zero_division=0))

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(thresholds, precisions, color="steelblue",   linewidth=2, label="Précision")
    ax.plot(thresholds, recalls,    color="firebrick",   linewidth=2, label="Rappel")
    ax.plot(thresholds, f1_scores,  color="forestgreen", linewidth=2, label="F1-Score")
    ax.axvline(x=0.5, color="gray", linestyle="--", linewidth=1,
               label="Seuil par défaut (0.5)")
    ax.axvline(x=0.111, color="firebrick", linestyle=":", linewidth=1.5,
               label="Seuil application (0.111)")

    ax.set_xlabel("Seuil de décision")
    ax.set_ylabel("Score")
    ax.set_title("Impact du seuil de décision sur les métriques")
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_PATH, "threshold_analysis.png"), dpi=150, bbox_inches="tight")
    plt.show()

    best_f1_idx = int(np.argmax(f1_scores))
    best_f1 = f1_scores[best_f1_idx]
    plateau = thresholds[np.isclose(f1_scores, best_f1, atol=1e-12)]
    print(f"\n--- Analyse des seuils ---")
    print(f"  Seuil optimal F1 : {plateau.min():.2f} – {plateau.max():.2f} (plateau)")
    print(f"  Précision        : {precisions[best_f1_idx]:.3f}")
    print(f"  Rappel           : {recalls[best_f1_idx]:.3f}")
    print(f"  F1-Score         : {best_f1:.3f}")


def analyze_errors(model, X_test: pd.DataFrame,
                   y_test: pd.Series, results: dict) -> None:
    X_test_copy            = X_test.copy()
    X_test_copy["y_real"]  = y_test.values
    X_test_copy["y_pred"]  = results["y_pred"]
    X_test_copy["y_proba"] = results["y_proba"]

    false_negatives = X_test_copy[
        (X_test_copy["y_real"] == 1) & (X_test_copy["y_pred"] == 0)
    ]

    print(f"\n--- Analyse des erreurs critiques (Faux Négatifs) ---")
    print(f"  Nombre de pannes manquées : {len(false_negatives)}")
    print(f"  Probabilité moyenne assignée par le modèle : {false_negatives['y_proba'].mean():.3f}")
    print(f"  (Le modele etait tres peu sur -> pannes ambiguës)")

    if len(false_negatives) > 0:
        print(f"\n  Caractéristiques moyennes des pannes manquées :")
        base_cols = ["torque", "rpm", "tool_wear_min", "power", "wear_temp_stress", "y_proba"]
        available = [c for c in base_cols if c in false_negatives.columns]
        print(false_negatives[available].describe().round(3).to_string())


def plot_feature_importance(model, X_test: pd.DataFrame) -> None:
    importance = pd.Series(
        model.feature_importances_,
        index=X_test.columns
    ).sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(8, 6))
    colors = ["firebrick" if v > importance.quantile(0.75) else "steelblue"
              for v in importance]
    importance.plot(kind="barh", ax=ax, color=colors)
    ax.set_title("Importance des features — XGBoost")
    ax.set_xlabel("Score d'importance (gain moyen)")
    ax.grid(True, alpha=0.3, axis="x")

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_PATH, "feature_importance.png"), dpi=150, bbox_inches="tight")
    plt.show()

    print(f"\n--- Importance des features ---")
    for feat, score in importance.sort_values(ascending=False).items():
        bar = "#" * max(1, min(20, int(score * 100)))
        print(f"  {feat:<25} : {score:.4f} {bar}")


if __name__ == "__main__":
    print("=" * 50)
    print("  EVALUATE — XGBoost Predictive Maintenance")
    print("=" * 50)

    model, X_test, y_test = load_model_and_data()
    results               = compute_predictions(model, X_test, y_test)

    plot_roc_curve(y_test, results)
    plot_precision_recall_curve(y_test, results)
    plot_threshold_analysis(y_test, results)
    plot_feature_importance(model, X_test)
    analyze_errors(model, X_test, y_test, results)

    print("\n" + "=" * 50)
    print("  ÉVALUATION COMPLÈTE TERMINÉE")
    print("=" * 50)
    print("\n[OK] Pilier 2 complet -> pret pour le Pilier 3 RAG")