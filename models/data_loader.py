import os
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
DATASET_URL    = "https://archive.ics.uci.edu/static/public/601/ai4i+2020+predictive+maintenance+dataset.zip"
RAW_PATH       = str(ROOT / "data" / "raw" / "ai4i2020.csv")
ZIP_PATH       = str(ROOT / "data" / "raw" / "ai4i2020.zip")
PROCESSED_PATH = str(ROOT / "data" / "processed" / "ai4i2020_clean.csv")
FIGURES_PATH   = str(ROOT / "data" / "processed")

COLUMN_RENAME = {
    "UDI":                        "id",
    "Product ID":                 "product_id",
    "Type":                       "machine_type",
    "Air temperature [K]":        "air_temp_k",
    "Process temperature [K]":    "process_temp_k",
    "Rotational speed [rpm]":     "rpm",
    "Torque [Nm]":                "torque",
    "Tool wear [min]":            "tool_wear_min",
    "Machine failure":            "failure",
    "TWF":                        "failure_twf",
    "HDF":                        "failure_hdf",
    "PWF":                        "failure_pwf",
    "OSF":                        "failure_osf",
    "RNF":                        "failure_rnf",
}

FEATURE_COLS = ["air_temp_c", "process_temp_c", "rpm", "torque", "tool_wear_min"]
TARGET_COL   = "failure"
FAILURE_COLS = ["failure_twf", "failure_hdf", "failure_pwf", "failure_osf", "failure_rnf"]


def download_dataset(url: str = DATASET_URL, save_path: str = RAW_PATH) -> None:
    if os.path.exists(save_path):
        print(f"[OK] Dataset deja present : {save_path}")
        return
    print("[INFO] Telechargement depuis UCI...")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    try:
        urllib.request.urlretrieve(url, ZIP_PATH)
        with zipfile.ZipFile(ZIP_PATH, "r") as z:
            for name in z.namelist():
                if name.endswith(".csv"):
                    z.extract(name, os.path.dirname(save_path))
                    extracted = os.path.join(os.path.dirname(save_path), name)
                    if extracted != save_path:
                        os.rename(extracted, save_path)
                    break
        os.remove(ZIP_PATH)
        print(f"[OK] Telecharge -> {save_path}")
    except Exception as e:
        print(f"[ERROR] Erreur : {e}")
        print(f"[INFO] Place manuellement le CSV dans : {save_path}")
        raise


def load_and_clean(raw_path: str = RAW_PATH) -> pd.DataFrame:
    df = pd.read_csv(raw_path)
    df = df.rename(columns=COLUMN_RENAME)
    df["air_temp_c"]     = (df["air_temp_k"] - 273.15).round(2)
    df["process_temp_c"] = (df["process_temp_k"] - 273.15).round(2)
    df = df.reset_index(drop=True)
    missing = df.isnull().sum().sum()
    print(f"[OK] Dataset charge : {df.shape[0]:,} lignes x {df.shape[1]} colonnes | NaN : {missing}")
    return df


def explore_dataset(df: pd.DataFrame) -> None:
    print("\n--- Statistiques descriptives ---")
    print(df[FEATURE_COLS].describe().round(2).to_string())

    counts = df[TARGET_COL].value_counts()
    pct    = df[TARGET_COL].value_counts(normalize=True) * 100
    print(f"\n--- Variable cible ---")
    print(f"  Normal (0) : {counts[0]:5d} ({pct[0]:.1f}%)")
    print(f"  Panne  (1) : {counts[1]:5d} ({pct[1]:.1f}%)")
    print(f"  Ratio      : {counts[0]/counts[1]:.0f}:1")

    print("\n--- Types de pannes ---")
    for col in FAILURE_COLS:
        print(f"  {col:<15} : {df[col].sum()}")

    print("\n--- Corrélations avec failure ---")
    corr = df[FEATURE_COLS + [TARGET_COL]].corr()[TARGET_COL].drop(TARGET_COL).sort_values(key=abs, ascending=False)
    for feat, val in corr.items():
        print(f"  {feat:<20} : {val:+.3f}")


def visualize_eda(df: pd.DataFrame, output_dir: str = FIGURES_PATH) -> None:
    os.makedirs(output_dir, exist_ok=True)

    # Graphique 1 : Distributions
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    fig.suptitle("Distributions des variables — UCI AI4I 2020", fontsize=14, fontweight="bold")
    axes = axes.flatten()

    for i, col in enumerate(FEATURE_COLS):
        sns.histplot(df[col], ax=axes[i], kde=True, color="steelblue", bins=40, alpha=0.7)
        axes[i].axvline(df[col].mean(), color="red", linestyle="--", linewidth=1.5, label=f"μ={df[col].mean():.1f}")
        axes[i].set_title(col)
        axes[i].legend(fontsize=8)

    counts = df[TARGET_COL].value_counts()
    axes[5].bar(["Normal (0)", "Panne (1)"], counts.values, color=["steelblue", "firebrick"])
    axes[5].set_title("Variable cible : failure")
    for j, v in enumerate(counts.values):
        axes[5].text(j, v + 30, f"{v}\n({v/len(df)*100:.1f}%)", ha="center", fontsize=9, fontweight="bold")

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "eda_1_distributions.png"), dpi=150, bbox_inches="tight")
    plt.show()

    # Graphique 2 : Heatmap de corrélation
    fig, ax = plt.subplots(figsize=(9, 7))
    corr_matrix = df[FEATURE_COLS + [TARGET_COL]].corr()
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, mask=mask, annot=True, fmt=".2f", cmap="coolwarm",
                center=0, vmin=-1, vmax=1, ax=ax, square=True, linewidths=0.5)
    ax.set_title("Matrice de corrélation (Pearson)", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "eda_2_correlation.png"), dpi=150, bbox_inches="tight")
    plt.show()

    # Graphique 3 : Boxplots Normal vs Panne
    # Fix seaborn >= 0.13 : utiliser hue= au lieu de palette= directement
    df_plot = df[FEATURE_COLS + [TARGET_COL]].copy()
    df_plot[TARGET_COL] = df_plot[TARGET_COL].astype(str)

    fig, axes = plt.subplots(1, 5, figsize=(20, 6))
    fig.suptitle("Distribution des features : Normal (0) vs Panne (1)", fontsize=13, fontweight="bold")
    for ax, col in zip(axes, FEATURE_COLS):
        sns.boxplot(
            data=df_plot, x=TARGET_COL, y=col, ax=ax,
            hue=TARGET_COL,
            palette={"0": "steelblue", "1": "firebrick"},
            width=0.5,
            legend=False
        )
        ax.set_xlabel("0=Normal | 1=Panne")
        ax.set_title(col)
        ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "eda_3_boxplots.png"), dpi=150, bbox_inches="tight")
    plt.show()
    print(f"[OK] Graphiques sauvegardes dans : {output_dir}")


def save_processed(df: pd.DataFrame, path: str = PROCESSED_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"[OK] Dataset nettoye -> {path} ({df.shape[0]:,} lignes x {df.shape[1]} colonnes)")


if __name__ == "__main__":
    print("=" * 50)
    print("  DATA LOADER — UCI AI4I 2020")
    print("=" * 50)

    download_dataset()
    df = load_and_clean()
    explore_dataset(df)
    visualize_eda(df)
    save_processed(df)

    print("\n[OK] Pret pour : python -m models.feature_engineering")