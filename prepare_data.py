from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
raw_path = ROOT / "data" / "raw" / "ai4i2020.csv"
out_dir = ROOT / "data" / "processed"
out_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(raw_path)

# Convertir les températures de kelvins en degrés Celsius
clean = pd.DataFrame({
    "air_temp_c": df["Air temperature [K]"] - 273.15,
    "process_temp_c": df["Process temperature [K]"] - 273.15,
    "rpm": df["Rotational speed [rpm]"],
    "torque": df["Torque [Nm]"],
    "tool_wear_min": df["Tool wear [min]"],
    "failure": df["Machine failure"].astype(int),
    "machine_type": df["Type"]
})

clean.to_csv(out_dir / "ai4i2020_clean.csv", index=False)

features = clean.copy()
features["temp_diff"] = features["process_temp_c"] - features["air_temp_c"]
features["power"] = features["rpm"] * features["torque"]
features["wear_rate"] = features["tool_wear_min"] / (features["rpm"] + 1)
features["rpm_torque_ratio"] = features["rpm"] / (features["torque"] + 1)
features["wear_temp_stress"] = features["tool_wear_min"] * features["temp_diff"]
features["type_M"] = (features["machine_type"] == "M").astype(int)

expected = [
    "air_temp_c", "process_temp_c", "rpm", "torque",
    "tool_wear_min", "temp_diff", "power", "wear_rate",
    "rpm_torque_ratio", "wear_temp_stress", "type_M", "failure"
]
features[expected].to_csv(out_dir / "ai4i2020_features.csv", index=False)

print("Préparation terminée.")
print("Dimensions :", features.shape)
print("Pannes :", int(features["failure"].sum()))
print("Fichier clean :", out_dir / "ai4i2020_clean.csv")
print("Fichier features :", out_dir / "ai4i2020_features.csv")
