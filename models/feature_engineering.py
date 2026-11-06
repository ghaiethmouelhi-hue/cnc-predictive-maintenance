import os
from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib

ROOT = Path(__file__).resolve().parents[1]
PROCESSED_PATH  = str(ROOT / "data" / "processed" / "ai4i2020_clean.csv")
FEATURES_PATH   = str(ROOT / "data" / "processed" / "ai4i2020_features.csv")
SCALER_PATH     = str(ROOT / "data" / "processed" / "scaler.pkl")

FEATURE_COLS = ["air_temp_c", "process_temp_c", "rpm", "torque", "tool_wear_min"]
TARGET_COL   = "failure"


def load_processed(path: str = PROCESSED_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"[OK] Dataset charge : {df.shape[0]:,} lignes x {df.shape[1]} colonnes")
    return df


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Écart thermique entre la machine et l'ambiant
    # Plus cet écart est grand, plus la machine chauffe anormalement
    df["temp_diff"] = df["process_temp_c"] - df["air_temp_c"]

    # Puissance mécanique approximative
    # Loi physique : P = couple × vitesse angulaire
    # rpm × torque est proportionnel à la puissance réelle
    df["power"] = df["rpm"] * df["torque"]

    # Usure normalisée par la vitesse
    # Une usure de 200 min à 2000 RPM est plus critique
    # qu'une usure de 200 min à 1000 RPM
    df["wear_rate"] = df["tool_wear_min"] / (df["rpm"] + 1)

    # Ratio régime/couple : capture l'équilibre de fonctionnement
    # Valeur élevée = haute vitesse, faible couple (régime léger)
    # Valeur faible  = basse vitesse, fort couple (régime chargé)
    df["rpm_torque_ratio"] = df["rpm"] / (df["torque"] + 1)

    # ── NOUVELLE FEATURE ──────────────────────────────────────────
    # Stress combiné usure × écart thermique
    #
    # POURQUOI cette feature ?
    # L'analyse des faux négatifs a révélé 10 pannes manquées
    # avec un profil spécifique :
    #   → tool_wear_min très élevé (+1.416σ au-dessus de la moyenne)
    #   → couple modéré ou faible (pattern "silencieux")
    #   → Les autres features ne détectent pas ces pannes TWF
    #
    # Ces pannes de type TWF (Tool Wear Failure) ont un pattern :
    # l'outil est en fin de vie ET soumis à un stress thermique.
    # Séparément, chaque signal semble normal.
    # Ensemble, ils signalent une casse imminente.
    #
    # wear_temp_stress = tool_wear_min × temp_diff
    # Élevé uniquement quand les DEUX conditions sont réunies.
    # C'est l'interaction entre usure et thermique que le modèle
    # ne capturait pas avec les features séparées.
    df["wear_temp_stress"] = df["tool_wear_min"] * df["temp_diff"]
    # ─────────────────────────────────────────────────────────────

    new_features = ['temp_diff', 'power', 'wear_rate', 'rpm_torque_ratio', 'wear_temp_stress']
    print(f"[OK] Features creees : {new_features}")
    return df


def encode_machine_type(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # One-Hot Encoding : transforme la colonne textuelle "machine_type"
    # (valeurs L, M, H) en 3 colonnes binaires 0/1
    # Pourquoi ? Les algorithmes ML ne savent pas lire du texte.
    # Ils ont besoin de nombres.
    #
    # Exemple :
    # machine_type = "L"  →  type_L=1, type_M=0, type_H=0
    # machine_type = "M"  →  type_L=0, type_M=1, type_H=0
    #
    # drop_first=True : supprime une colonne pour éviter la redondance
    # Si type_L=0 et type_M=0, on sait déjà que c'est type_H=1
    dummies = pd.get_dummies(df["machine_type"], prefix="type", drop_first=True)
    df = pd.concat([df, dummies], axis=1)

    print(f"[OK] Encodage machine_type -> colonnes : {list(dummies.columns)}")
    return df


def normalize_features(df: pd.DataFrame,
                        fit: bool = True,
                        scaler_path: str = SCALER_PATH) -> tuple[pd.DataFrame, StandardScaler]:
    df = df.copy()

    feature_cols_to_scale = [
        "air_temp_c", "process_temp_c", "rpm", "torque", "tool_wear_min",
        "temp_diff", "power", "wear_rate", "rpm_torque_ratio",
        "wear_temp_stress"   # ← AJOUT
    ]

    # StandardScaler : normalise chaque feature pour avoir
    # moyenne = 0 et écart-type = 1
    #
    # Formule : z = (x - μ) / σ
    # x  = valeur originale
    # μ  = moyenne de la colonne
    # σ  = écart-type de la colonne
    # z  = valeur normalisée
    #
    # fit=True  : on CALCULE μ et σ sur les données (training uniquement)
    # fit=False : on RÉUTILISE μ et σ déjà calculés (test et production)
    # Règle absolue : ne jamais fitter le scaler sur les données de test.

    if fit:
        scaler = StandardScaler()
        df[feature_cols_to_scale] = scaler.fit_transform(df[feature_cols_to_scale])
        os.makedirs(os.path.dirname(scaler_path), exist_ok=True)
        joblib.dump(scaler, scaler_path)
        print(f"[OK] Scaler ajuste et sauvegarde -> {scaler_path}")
    else:
        scaler = joblib.load(scaler_path)
        df[feature_cols_to_scale] = scaler.transform(df[feature_cols_to_scale])
        print(f"[OK] Scaler charge et applique depuis -> {scaler_path}")

    return df, scaler


def split_dataset(df: pd.DataFrame) -> tuple:
    all_feature_cols = [
        "air_temp_c", "process_temp_c", "rpm", "torque", "tool_wear_min",
        "temp_diff", "power", "wear_rate", "rpm_torque_ratio",
        "wear_temp_stress",  # ← AJOUT
        "type_M", "type_H"
    ]

    # On ne garde que les colonnes qui existent réellement dans le df
    available_cols = [c for c in all_feature_cols if c in df.columns]

    X = df[available_cols]
    y = df[TARGET_COL]

    # train_test_split : divise le dataset en deux parties
    #
    # POURQUOI diviser ?
    # Le modèle apprend sur les données d'entraînement (train).
    # On évalue sa performance sur des données qu'il n'a JAMAIS vues (test).
    # Si on évalue sur les mêmes données qu'il a vues, il "triche" :
    # il a mémorisé les réponses. C'est l'overfitting.
    #
    # test_size=0.2   : 20% des données pour le test, 80% pour le train
    # random_state=42 : graine aléatoire pour la reproductibilité
    # stratify=y      : garantit que le ratio 96.6%/3.4% est respecté
    #                   dans les deux parties. Sans ça, par malchance,
    #                   le test pourrait n'avoir aucune panne.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    print(f"\n[OK] Split train/test :")
    print(f"   Train : {X_train.shape[0]:,} lignes ({X_train.shape[0]/len(X)*100:.0f}%)")
    print(f"   Test  : {X_test.shape[0]:,} lignes  ({X_test.shape[0]/len(X)*100:.0f}%)")
    print(f"   Features utilisées : {list(available_cols)}")
    print(f"\n   Distribution failure dans train :")
    print(f"     Normal : {(y_train==0).sum():,} ({(y_train==0).mean()*100:.1f}%)")
    print(f"     Panne  : {(y_train==1).sum():,} ({(y_train==1).mean()*100:.1f}%)")

    return X_train, X_test, y_train, y_test


def save_features(df: pd.DataFrame, path: str = FEATURES_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"\n[OK] Dataset final -> {path} ({df.shape[0]:,} lignes x {df.shape[1]} colonnes)")


if __name__ == "__main__":
    print("=" * 50)
    print("  FEATURE ENGINEERING")
    print("=" * 50)

    df = load_processed()
    df = create_features(df)
    df = encode_machine_type(df)
    df, scaler = normalize_features(df, fit=True)
    save_features(df)
    X_train, X_test, y_train, y_test = split_dataset(df)

    print("\n[OK] Pret pour : python -m models.train")