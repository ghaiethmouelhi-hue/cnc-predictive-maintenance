# -*- coding: utf-8 -*-
"""
Fiabilité CNC (AI4I 2020) - Projet Predictive Maintenance
=========================================================
Kaplan-Meier · Lois paramétriques (AIC) · MTBF/MTTR/Disponibilité
· Coût de maintenance préventive optimal

IMPORTANT (limite méthodologique assumée) :
Le dataset AI4I 2020 est un snapshot horaire : toutes les durées observées
valent 1 h. Sur une seule valeur de durée, une loi à 2 paramètres
(Weibull complète, log-normale) est NON identifiable (beta -> infini).
On ajuste donc :
  - l'exponentielle (1 paramètre, identifiable),
  - une Weibull CONTRAINTE beta = 1 (équivalente à l'exponentielle),
et on documente que l'estimation de beta < / > 1 nécessiterait un
historique GMAO avec temps-avant-panne variés.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from lifelines import KaplanMeierFitter, ExponentialFitter
from scipy.optimize import minimize_scalar

ROOT = Path(__file__).resolve().parent
OUT = str(ROOT / "data" / "processed")

# ------------------------------------------------------------------
# 1. CHARGEMENT & PRÉPARATION
# ------------------------------------------------------------------
df = pd.read_csv(ROOT / "data" / "raw" / "ai4i2020.csv")
n_tot = len(df)
n_fail = int(df["Machine failure"].sum())
print(f"Dataset : {n_tot} lignes, {n_fail} pannes "
      f"({100 * n_fail / n_tot:.2f} %)")

# Contrôle qualité : valeurs aberrantes
bad = int(((df["Torque [Nm]"] < 0) |
           (df["Rotational speed [rpm]"] < 0)).sum())
print(f"Lignes aberrantes (torque/rpm négatifs) : {bad}")

# Durées : chaque ligne = 1 h-machine observée
#   panne -> événement à t = 1 h ; sinon censure à droite à 1 h
T = np.ones(n_tot)
E = df["Machine failure"].astype(int).to_numpy()

# ------------------------------------------------------------------
# 2. KAPLAN-MEIER
# ------------------------------------------------------------------
kmf = KaplanMeierFitter()
kmf.fit(T, E, label="KM - machine CNC (AI4I 2020)")
R_km = float(kmf.predict(1.0))

fig, ax = plt.subplots(figsize=(7, 4.5))
kmf.plot_survival_function(ax=ax)
ax.set_title("Fiabilité R(t) - Kaplan-Meier (AI4I 2020, horizon 1 h)")
ax.set_xlabel("Temps (h-machine)")
ax.set_ylabel("R(t)")
ax.set_ylim(0.90, 1.001)
fig.tight_layout()
fig.savefig(f"{OUT}/kaplan_meier.png", dpi=150)
plt.close(fig)

# Contrôle indépendant n°1 : R(1h) = 1 - taux de panne empirique
R_km_check = 1.0 - n_fail / n_tot
print(f"\nKM   R(1h)       = {R_km:.6f}")
print(f"Emp.  1 - F(1)   = {R_km_check:.6f}")
assert abs(R_km - R_km_check) < 1e-9, "INCOHÉRENCE KM vs empirique !"
print("Cohérence KM / taux empirique : OK")

# ------------------------------------------------------------------
# 3. LOIS PARAMÉTRIQUES & COMPARAISON AIC
# ------------------------------------------------------------------
# Exponentielle : ajustée via lifelines (MLE). NB : lifelines paramétrise
# S(t) = exp(-t/lambda_) -> lambda_ = échelle = MTBF ; le TAUX est 1/lambda_.
exp_f = ExponentialFitter().fit(T, E)
MTBF_h = float(exp_f.lambda_)
lam = 1.0 / MTBF_h

# Weibull CONTRAINTE beta = 1 : identique à l'exponentielle.
# MLE analytique (censure à droite) : lambda_hat = n_ev / sum(T_i)
n_ev = int(E.sum())
lam_weib = n_ev / T.sum()
LL = n_ev * np.log(lam_weib) - lam_weib * T.sum()
AIC_weib = 2 * 1 - 2 * LL             # 1 paramètre (beta fixé = 1)

aic = {
    "Exponentielle": float(exp_f.AIC_),
    "Weibull (beta=1 fixé)": float(AIC_weib),
}
print("\nAIC par loi :")
for name, val in sorted(aic.items(), key=lambda kv: kv[1]):
    print(f"  {name:<24} {val:.4f}")

# Contrôle indépendant n°2 : lambda exp == lambda Weibull(beta=1)
# (MLE analytique avec censure à droite : lambda_hat = n_ev / sum(T_i)
#  = n_fail / n_tot ici, car toutes les durées valent 1 h)
print(f"\nlambda exp    = {lam:.6f} /h")
print(f"lambda Weibull(b=1) = {lam_weib:.6f} /h")
assert abs(lam - lam_weib) < 1e-6, "INCOHÉRENCE lambda exp/Weibull !"
print("Cohérence lambda : OK")

# Contrôle indépendant n°3 : MTBF = n_total / n_pannes
MTBF_check = n_tot / n_fail
print(f"\nMTBF (1/lambda)      = {MTBF_h:.3f} h-machine")
print(f"MTBF (empirique N/F) = {MTBF_check:.3f} h-machine")
assert abs(MTBF_h - MTBF_check) < 1e-3, "INCOHÉRENCE MTBF !"
print("Cohérence MTBF : OK")

# Pannes par mode (diagnostic)
modes = ["TWF", "HDF", "PWF", "OSF", "RNF"]
mode_counts = {m: int(df[m].sum()) for m in modes}
mode_mtbf = {m: (n_tot / c if c else float("inf"))
             for m, c in mode_counts.items()}
print("\nPannes par mode et MTBF associé :")
for m in modes:
    print(f"  {m}: {mode_counts[m]:4d} pannes  ->  "
          f"MTBF ~ {mode_mtbf[m]:8.1f} h-machine")

# ------------------------------------------------------------------
# 4. MTTR, DISPONIBILITÉ (hypothèses EXPLICITES, jamais inventées)
# ------------------------------------------------------------------
MTTR_HYP = 4.0                        # heures - HYPOTHÈSE (pas de GMAO ici)
A = MTBF_h / (MTBF_h + MTTR_HYP)
print(f"\nMTTR (hypothèse)   = {MTTR_HYP:.1f} h")
print(f"Disponibilité A    = {100 * A:.3f} %")

# ------------------------------------------------------------------
# 5. PÉRIODICITÉ PRÉVENTIVE OPTIMALE (loi exponentielle)
# ------------------------------------------------------------------
# Coûts HYPOTHÈSES (cohérents README : panne 2 000-50 000 EUR)
Cp, Cf = 500.0, 20_000.0

def cost_rate(Tp, lam=lam):
    """Coût total par h-machine pour un préventif tous les Tp."""
    F = 1.0 - np.exp(-lam * Tp)                      # proba panne avant Tp
    uptime = (1.0 - np.exp(-lam * Tp)) / lam         # E[min(T, Tp)]
    return (Cp * (1 - F) + Cf * F) / uptime

C_lf = Cf * lam                       # limite Tp -> infini : Cf/MTBF
res = minimize_scalar(cost_rate, bounds=(0.01, 200.0), method="bounded")
Tp_opt, C_opt = float(res.x), float(res.fun)
RTF = res.x >= 199.9                  # optimum à la borne supérieure
if RTF:                               # c(Tp) décroissante => run-to-failure
    Tp_opt, C_opt = float("inf"), float(C_lf)
print(f"\nCoûts (hypothèses) : Cp = {Cp:.0f} EUR, Cf = {Cf:.0f} EUR")
Tp_str = ("inf (run-to-failure)" if RTF else f"{Tp_opt:.3f}")
print(f"Périodicité optimale Tp* = {Tp_str} h-machine "
      f"(coût {C_opt:.2f} EUR/h-machine)")
if RTF:
    print("NB : loi exponentielle (sans mémoire) + Cf forfaitaire => "
          "c(Tp) décroissante : aucun préventif ne réduit le coût ;")
    print("    un préventif ne devient optimal qu'avec une loi d'usure "
          "(Weibull beta > 1) — historique GMAO requis.")

fig, ax = plt.subplots(figsize=(7, 4.5))
tps = np.linspace(0.05, 40, 400)
ax.plot(tps, [cost_rate(t) for t in tps], label="c(Tp)")
ax.axhline(C_lf, color="g", ls=":", label=f"Run-to-failure : {C_lf:.0f} EUR/h")
if not RTF:
    ax.axvline(Tp_opt, color="r", ls="--", label=f"Tp* = {Tp_opt:.2f} h")
ax.set_title("Coût total de maintenance par h-machine (loi exponentielle)")
ax.set_xlabel("Périodicité préventive Tp (h)")
ax.set_ylabel("Coût (EUR/h-machine)")
ax.legend()
fig.tight_layout()
fig.savefig(f"{OUT}/maintenance_cost.png", dpi=150)
plt.close(fig)

# Figure : survie des lois ajustées
fig, ax = plt.subplots(figsize=(7, 4.5))
t_grid = np.linspace(0.05, 1.0, 200)
ax.plot(t_grid, exp_f.survival_function_at_times(t_grid).to_numpy().ravel(),
        lw=2, label=f"Exponentielle (AIC={aic['Exponentielle']:.1f})")
ax.plot(t_grid, np.exp(-lam_weib * t_grid),
        lw=2, ls="--",
        label=f"Weibull beta=1 (AIC={aic['Weibull (beta=1 fixé)']:.1f})")
ax.step([0, 1], [1, R_km], where="post", color="k", label="Kaplan-Meier")
ax.set_title("Fiabilité R(t) - lois ajustées vs Kaplan-Meier")
ax.set_xlabel("Temps (h-machine)")
ax.set_ylabel("R(t)")
ax.legend()
ax.set_ylim(0.90, 1.001)
fig.tight_layout()
fig.savefig(f"{OUT}/reliability_laws.png", dpi=150)
plt.close(fig)
print("Figures -> kaplan_meier.png, reliability_laws.png, maintenance_cost.png")

# ------------------------------------------------------------------
# 6. SYNTHÈSE JSON (pour le rapport HTML)
# ------------------------------------------------------------------
summary = {
    "n_total": n_tot,
    "n_fail": n_fail,
    "fail_rate_pct": 100 * n_fail / n_tot,
    "bad_lines": bad,
    "R_km_1h": R_km,
    "R_km_check": R_km_check,
    "AIC": aic,
    "lambda_per_h": lam,
    "MTBF_h": MTBF_h,
    "MTBF_check_h": MTBF_check,
    "MTTR_hypothese_h": MTTR_HYP,
    "A_pct": 100 * A,
    "mode_counts": mode_counts,
    "mode_mtbf_h": mode_mtbf,
    "Cp_eur": Cp,
    "Cf_eur": Cf,
    "Tp_optimal_h": ("inf (run-to-failure)" if np.isinf(Tp_opt) else float(Tp_opt)),
    "C_optimal_eur_per_h": float(C_opt),
}
with open(f"{OUT}/reliability_summary.json", "w", encoding="utf-8") as fh:
    json.dump(summary, fh, indent=2, ensure_ascii=False)
print("\nRésumé JSON ->", f"{OUT}/reliability_summary.json")
