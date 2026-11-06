import os
from pathlib import Path

import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score
)
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parents[1]
FEATURES_PATH = str(ROOT / "data" / "processed" / "ai4i2020_features.csv")
MODEL_PATH    = str(ROOT / "models" / "xgboost_model.pkl")
FIGURES_PATH  = str(ROOT / "data" / "processed")

TARGET_COL    = "failure"

FEATURE_COLS  = [
    "air_temp_c", "process_temp_c", "rpm", "torque", "tool_wear_min",
    "temp_diff", "power", "wear_rate", "rpm_torque_ratio", "wear_temp_stress", "type_M"
]


def load_features(path: str = FEATURES_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    available = [c for c in FEATURE_COLS if c in df.columns]
    print(f"[OK] Features chargees : {df.shape[0]:,} lignes x {len(available)} features")
    return df


def split_dataset(df: pd.DataFrame) -> tuple:
    available = [c for c in FEATURE_COLS if c in df.columns]
    X = df[available]
    y = df[TARGET_COL]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    print(f"[OK] Split : Train={X_train.shape[0]:,} | Test={X_test.shape[0]:,}")
    return X_train, X_test, y_train, y_test


def train_model(X_train: pd.DataFrame, y_train: pd.Series) -> XGBClassifier:
    n_normal = (y_train == 0).sum()
    n_failure = (y_train == 1).sum()
    scale_pos_weight = n_normal / n_failure

    print(f"\n[INFO] Parametres XGBoost :")
    print(f"   n_estimators     = 100  (nombre d'arbres)")
    print(f"   max_depth        = 6    (profondeur max de chaque arbre)")
    print(f"   learning_rate    = 0.1  (vitesse d'apprentissage)")
    print(f"   scale_pos_weight = {scale_pos_weight:.1f} (correction déséquilibre)")

    model = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        eval_metric="logloss",
        verbosity=0
    )

    model.fit(X_train, y_train)
    print(f"\n[OK] Modele entraine")
    return model


def evaluate_model(model: XGBClassifier,
                   X_test: pd.DataFrame,
                   y_test: pd.Series) -> None:

    y_pred = model.predict(X_test)

    precision = precision_score(y_test, y_pred)
    recall    = recall_score(y_test, y_pred)
    f1        = f1_score(y_test, y_pred)

    print(f"\n--- Métriques principales ---")
    print(f"  Précision : {precision:.3f}  (pannes prédites qui sont vraies)")
    print(f"  Rappel    : {recall:.3f}  (vraies pannes détectées)")
    print(f"  F1-Score  : {f1:.3f}  (équilibre précision/rappel)")

    print(f"\n--- Rapport complet ---")
    print(classification_report(y_test, y_pred, target_names=["Normal", "Panne"]))

    plot_confusion_matrix(y_test, y_pred)
    plot_feature_importance(model, X_test)


def plot_confusion_matrix(y_test: pd.Series, y_pred: np.ndarray) -> None:
    cm = confusion_matrix(y_test, y_pred)

    fig, ax = plt.subplots(figsize=(7, 5))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=["Normal", "Panne"],
        yticklabels=["Normal", "Panne"],
        ax=ax
    )
    ax.set_xlabel("Prédit")
    ax.set_ylabel("Réel")
    ax.set_title("Matrice de confusion")

    tn, fp, fn, tp = cm.ravel()
    print(f"\n--- Matrice de confusion ---")
    print(f"  Vrais Negatifs  (TN) : {tn:4d}  Normal predit Normal  [OK]")
    print(f"  Faux Positifs   (FP) : {fp:4d}  Normal predit Panne   [WARN]")
    print(f"  Faux Negatifs   (FN) : {fn:4d}  Panne  predit Normal  [ERROR] critique")
    print(f"  Vrais Positifs  (TP) : {tp:4d}  Panne  predit Panne   [OK]")

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_PATH, "confusion_matrix.png"), dpi=150, bbox_inches="tight")
    plt.show()


def plot_feature_importance(model: XGBClassifier,
                             X_test: pd.DataFrame) -> None:
    importance = pd.Series(
        model.feature_importances_,
        index=X_test.columns
    ).sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(8, 6))
    importance.plot(kind="barh", ax=ax, color="steelblue")
    ax.set_title("Importance des features — XGBoost")
    ax.set_xlabel("Score d'importance")
    ax.grid(True, alpha=0.3, axis="x")

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_PATH, "feature_importance.png"), dpi=150, bbox_inches="tight")
    plt.show()
    print(f"\n--- Importance des features (top 3) ---")
    for feat, score in importance.sort_values(ascending=False).head(3).items():
        print(f"  {feat:<25} : {score:.4f}")


def save_model(model: XGBClassifier, path: str = MODEL_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(model, path)
    print(f"\n[OK] Modele sauvegarde -> {path}")


if __name__ == "__main__":
    print("=" * 50)
    print("  TRAINING — XGBoost Predictive Maintenance")
    print("=" * 50)

    df                          = load_features()
    X_train, X_test, y_train, y_test = split_dataset(df)
    model                       = train_model(X_train, y_train)
    evaluate_model(model, X_test, y_test)
    save_model(model)

    print("\n[OK] Pret pour : python -m models.evaluate")