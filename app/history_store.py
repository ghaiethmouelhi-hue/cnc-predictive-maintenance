# -*- coding: utf-8 -*-
"""Persistance locale des diagnostics et des interventions.

Les fichiers CSV sont créés à la première écriture. Ils ne contiennent que
des événements réellement produits par l'utilisateur ou saisis dans le journal
de maintenance — aucune donnée n'est générée automatiquement.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from app.data_access import ROOT_DIR

DIAGNOSTICS_PATH = ROOT_DIR / "data" / "processed" / "diagnostics_log.csv"
MAINTENANCE_PATH = ROOT_DIR / "data" / "processed" / "maintenance_log.csv"

DIAGNOSTIC_COLUMNS = [
    "timestamp",
    "machine_id",
    "machine_type",
    "air_temp_c",
    "process_temp_c",
    "rpm",
    "torque",
    "tool_wear_min",
    "temp_diff",
    "power_w",
    "probability",
    "risk_level",
    "signals",
    "warnings",
]

MAINTENANCE_COLUMNS = [
    "date",
    "machine_id",
    "intervention_type",
    "component",
    "description",
    "technician",
    "status",
    "created_at",
]


def _empty(columns: list[str]) -> pd.DataFrame:
    return pd.DataFrame(columns=columns)


def export_csv(df: pd.DataFrame) -> bytes:
    """CSV compatible Excel (BOM UTF-8)."""
    return df.to_csv(index=False).encode("utf-8-sig")


def append_diagnostic(record: dict) -> None:
    row = {column: record.get(column, "") for column in DIAGNOSTIC_COLUMNS}
    df = pd.DataFrame([row], columns=DIAGNOSTIC_COLUMNS)
    header = not DIAGNOSTICS_PATH.exists()
    DIAGNOSTICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(DIAGNOSTICS_PATH, mode="a", header=header, index=False, encoding="utf-8-sig")


def load_diagnostics() -> pd.DataFrame:
    if not DIAGNOSTICS_PATH.exists():
        return _empty(DIAGNOSTIC_COLUMNS)
    try:
        df = pd.read_csv(DIAGNOSTICS_PATH, encoding="utf-8-sig")
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        return _empty(DIAGNOSTIC_COLUMNS)
    if df.empty:
        return _empty(DIAGNOSTIC_COLUMNS)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    for column in ("air_temp_c", "process_temp_c", "rpm", "torque", "tool_wear_min", "temp_diff", "power_w", "probability"):
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    df = df.sort_values("timestamp", ascending=False, na_position="last")
    return df.reset_index(drop=True)


def clear_diagnostics() -> None:
    if DIAGNOSTICS_PATH.exists():
        DIAGNOSTICS_PATH.unlink()


def fleet_snapshot(df: pd.DataFrame) -> pd.DataFrame:
    """Dernier diagnostic connu pour chaque machine."""
    if df.empty or "machine_id" not in df.columns:
        return df.copy()
    ordered = df.sort_values("timestamp", ascending=True, na_position="first")
    latest = ordered.groupby("machine_id", as_index=False).tail(1)
    return latest.sort_values("probability", ascending=False).reset_index(drop=True)


def append_maintenance(record: dict) -> None:
    row = {column: record.get(column, "") for column in MAINTENANCE_COLUMNS}
    if not row.get("created_at"):
        row["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = pd.DataFrame([row], columns=MAINTENANCE_COLUMNS)
    header = not MAINTENANCE_PATH.exists()
    MAINTENANCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(MAINTENANCE_PATH, mode="a", header=header, index=False, encoding="utf-8-sig")


def load_maintenance() -> pd.DataFrame:
    if not MAINTENANCE_PATH.exists():
        return _empty(MAINTENANCE_COLUMNS)
    try:
        df = pd.read_csv(MAINTENANCE_PATH, encoding="utf-8-sig")
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        return _empty(MAINTENANCE_COLUMNS)
    if df.empty:
        return _empty(MAINTENANCE_COLUMNS)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df.sort_values("date", ascending=False, na_position="last").reset_index(drop=True)


def clear_maintenance() -> None:
    if MAINTENANCE_PATH.exists():
        MAINTENANCE_PATH.unlink()
