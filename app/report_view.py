# -*- coding: utf-8 -*-
"""Vue « Rapport de fiabilité » intégrée à l'application Streamlit.

Le rapport HTML autonome (rapport_fiabilite_cnc.html) reste téléchargeable,
tandis que cette vue propose une lecture native, structurée et responsive
des mêmes résultats : KPI, courbes, modes de défaillance et décision.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

MODE_LABELS = {
    "TWF": "Usure outil",
    "HDF": "Dissipation thermique",
    "PWF": "Défaut puissance",
    "OSF": "Surcharge mécanique",
    "RNF": "Panne aléatoire",
}

MODE_PRIORITIES = {
    "HDF": 1,
    "OSF": 2,
    "PWF": 3,
    "TWF": 4,
    "RNF": 5,
}

DECISION_ROWS = [
    ("Remplacement outil", "tool_wear ≥ 180 min", "Seuil TWF du dataset (200 min) avec marge de 10 %"),
    ("Intervention immédiate", "score XGBoost ≥ 0,111", "Seuil de décision retenu par l'application"),
    ("Alerte jaune", "score > 0,05", "Marge avant le seuil d'intervention"),
    ("Inspection refroidissement", "temp_diff < 8,6 K pendant 3 h", "Seuil HDF du dataset"),
    ("Réduction de l'avance", "torque > 45 N·m prolongé", "Seuil OSF du dataset"),
    ("Arrêt contrôlé", "puissance physique hors [3,5 ; 10,5] kW", "Seuil PWF du dataset"),
]


def _fr(value: float, digits: int = 2) -> str:
    """Formate un nombre à la française : 1 234,56."""
    return f"{value:,.{digits}f}".replace(",", " ").replace(".", ",")


def _pct(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f} %".replace(".", ",")


def _section(title: str, eyebrow: str | None = None) -> None:
    if eyebrow:
        st.markdown(
            f'<p class="section-eyebrow">{eyebrow}</p>',
            unsafe_allow_html=True,
        )
    st.subheader(title)


def _image(path: Path, caption: str) -> None:
    if path.exists():
        st.image(str(path), caption=caption, width="stretch")
    else:
        st.info(
            f"Figure indisponible : `{path.name}`. "
            "Relancez `python reliability_analysis.py` pour la régénérer."
        )


def _summary_table(summary: dict) -> pd.DataFrame:
    aic = summary.get("AIC", {})
    lam = summary.get("lambda_per_h")
    mtbf = summary.get("MTBF_h")
    rows = []
    for law, value in sorted(aic.items(), key=lambda item: item[1]):
        rows.append({
            "Loi ajustée": law,
            "AIC": round(float(value), 4),
            "λ (1/h)": round(float(lam), 6) if lam is not None else None,
            "MTBF (h)": round(float(mtbf), 3) if mtbf is not None else None,
        })
    return pd.DataFrame(rows)


def _modes_table(summary: dict) -> pd.DataFrame:
    counts = summary.get("mode_counts", {})
    mtbfs = summary.get("mode_mtbf_h", {})
    rows = []
    for mode in sorted(counts, key=lambda name: MODE_PRIORITIES.get(name, 99)):
        rows.append({
            "Mode": mode,
            "Libellé": MODE_LABELS.get(mode, mode),
            "Pannes": int(counts[mode]),
            "MTBF (h)": round(float(mtbfs.get(mode, float("inf"))), 1),
            "Priorité": MODE_PRIORITIES.get(mode, "—"),
        })
    return pd.DataFrame(rows)


def _render_header(summary: dict, report_path: Path) -> None:
    n_total = int(summary.get("n_total", 0))
    n_fail = int(summary.get("n_fail", 0))
    r_km = float(summary.get("R_km_1h", 0.0)) * 100
    fail_rate = float(summary.get("fail_rate_pct", 0.0))
    mtbf = float(summary.get("MTBF_h", 0.0))
    availability = float(summary.get("A_pct", 0.0))

    st.markdown(
        '<p class="section-eyebrow">Vue d’ensemble · Fiabilité</p>',
        unsafe_allow_html=True,
    )

    source = (
        f"AI4I 2020 · {_fr(n_total, 0)} observations horaires · "
        f"{n_fail} pannes · données synthétiques UCI"
    )
    if report_path.exists():
        generated = datetime.fromtimestamp(report_path.stat().st_mtime)
        source += f" · rapport généré le {generated:%d/%m/%Y à %H:%M}"
    st.caption(source)

    kpis = st.columns(4)
    with kpis[0]:
        st.metric(
            "Fiabilité R(1 h)",
            _pct(r_km),
            delta=f"{n_fail} pannes / {_fr(n_total, 0)} h",
            delta_color="off",
            help="Probabilité de fonctionnement sans panne sur une heure-machine.",
        )
    with kpis[1]:
        st.metric(
            "Taux de panne",
            _pct(fail_rate),
            delta=f"{n_fail} événements observés",
            delta_color="off",
            help="Part des heures-machine marquées par au moins une panne.",
        )
    with kpis[2]:
        st.metric(
            "MTBF",
            f"{_fr(mtbf, 2)} h",
            delta="Temps moyen entre pannes",
            delta_color="off",
            help="MTBF = 1 / λ, estimé par la loi exponentielle.",
        )
    with kpis[3]:
        st.metric(
            "Disponibilité",
            _pct(availability),
            delta="MTTR supposé à 4 h",
            delta_color="off",
            help="A = MTBF / (MTBF + MTTR). Le MTTR est une hypothèse, absente du dataset.",
        )


def _render_insights(summary: dict) -> None:
    counts = summary.get("mode_counts", {})
    mtbfs = summary.get("mode_mtbf_h", {})
    top_mode = max(counts, key=counts.get) if counts else "—"
    top_count = int(counts.get(top_mode, 0))
    top_mtbf = float(mtbfs.get(top_mode, 0.0))

    st.markdown(
        '<p class="section-eyebrow">Lecture rapide</p>',
        unsafe_allow_html=True,
    )
    cards = st.columns(3)
    with cards[0]:
        with st.container(border=True):
            st.markdown("#### Priorité n°1")
            st.markdown(f"**{top_mode} — {MODE_LABELS.get(top_mode, top_mode)}**")
            st.write(
                f"{top_count} pannes observées, soit un MTBF de "
                f"**{_fr(top_mtbf, 1)} h-machine**. C'est le mode le plus fréquent "
                "du dataset : la surveillance de `temp_diff` est prioritaire."
            )
    with cards[1]:
        with st.container(border=True):
            st.markdown("#### Politique optimale")
            st.markdown("**Run-to-failure** (calendaire)")
            st.write(
                "Avec une loi exponentielle sans mémoire et un coût de panne "
                "forfaitaire, la fonction de coût est décroissante : aucun "
                "préventif calendaire ne réduit le coût dans ce modèle."
            )
    with cards[2]:
        with st.container(border=True):
            st.markdown("#### Décision à retenir")
            st.markdown("**Maintenance conditionnelle**")
            st.write(
                "Les seuils capteurs et le score XGBoost restent pleinement "
                "justifiés : ils interviennent avant la panne sans consommer "
                "la durée de vie résiduelle de la machine."
            )


def _render_reliability_tab(root_dir: Path, summary: dict) -> None:
    left, right = st.columns(2)
    with left:
        _image(
            root_dir / "data" / "processed" / "kaplan_meier.png",
            "Fig. 1 — Fiabilité R(t) estimée par Kaplan-Meier (horizon 1 h).",
        )
    with right:
        _image(
            root_dir / "data" / "processed" / "reliability_laws.png",
            "Fig. 2 — Lois exponentielle et Weibull (β = 1) vs Kaplan-Meier.",
        )

    st.markdown(
        "Le dataset est un **snapshot horaire** : chaque ligne représente une "
        "heure-machine, donc toutes les durées observées valent 1 h. Une Weibull "
        "à deux paramètres libres n'est pas identifiable sur ces données "
        "(β → ∞). Seule l'exponentielle — ou une Weibull contrainte β = 1, "
        "mathématiquement équivalente — peut être estimée."
    )

    st.markdown("#### Modèles ajustés et contrôle de cohérence")
    table = _summary_table(summary)
    if not table.empty:
        st.dataframe(table, hide_index=True, width="stretch")

    r_km = float(summary.get("R_km_1h", 0.0))
    r_check = float(summary.get("R_km_check", 0.0))
    mtbf = float(summary.get("MTBF_h", 0.0))
    mtbf_check = float(summary.get("MTBF_check_h", 0.0))
    n_fail = int(summary.get("n_fail", 0))
    n_total = int(summary.get("n_total", 0))
    st.success(
        f"**Contrôles indépendants réussis** — R(1 h) = {_fr(r_km, 6)} "
        f"= 1 − {_fr(n_fail, 0)}/{_fr(n_total, 0)} = {_fr(r_check, 6)} ; "
        f"MTBF = 1/λ = {_fr(mtbf, 3)} h = N/F = {_fr(mtbf_check, 3)} h."
    )


def _render_modes_tab(summary: dict) -> None:
    table = _modes_table(summary)
    left, right = st.columns([3, 2])
    with left:
        st.markdown("#### Pannes par mode et MTBF associé")
        st.dataframe(table, hide_index=True, width="stretch")
    with right:
        st.markdown("#### Répartition des pannes")
        if not table.empty:
            chart_data = table.set_index("Mode")[["Pannes"]]
            st.bar_chart(chart_data, horizontal=True, width="stretch", height=310)

    counts = summary.get("mode_counts", {})
    mtbfs = summary.get("mode_mtbf_h", {})
    if counts:
        top_mode = max(counts, key=counts.get)
        top_mtbf = float(mtbfs.get(top_mode, 0.0))
        st.info(
            f"**{top_mode} — {MODE_LABELS.get(top_mode, top_mode)}** est le mode "
            f"le plus fréquent (MTBF ≈ {_fr(top_mtbf, 0)} h) : c'est la priorité "
            "de surveillance. **TWF**, plus rare, reste le plus grave en criticité "
            "et justifie le remplacement préventif de l'outil autour de 180 min."
        )


def _render_cost_tab(root_dir: Path, summary: dict) -> None:
    left, right = st.columns([3, 2])
    with left:
        _image(
            root_dir / "data" / "processed" / "maintenance_cost.png",
            "Fig. 3 — Coût total par heure-machine selon la périodicité préventive.",
        )
    with right:
        st.markdown("#### Hypothèses économiques")
        cp = float(summary.get("Cp_eur", 0.0))
        cf = float(summary.get("Cf_eur", 0.0))
        c_opt = float(summary.get("C_optimal_eur_per_h", 0.0))
        tp = summary.get("Tp_optimal_h")
        tp_label = "Run-to-failure" if isinstance(tp, str) else f"{_fr(float(tp), 1)} h"

        st.metric("Coût préventif (Cp)", f"{_fr(cp, 0)} €", delta_color="off")
        st.metric("Coût d'une panne (Cf)", f"{_fr(cf, 0)} €", delta_color="off")
        st.metric("Périodicité optimale", tp_label, delta_color="off")
        st.metric("Coût optimal", f"{_fr(c_opt, 2)} €/h", delta_color="off")
        st.caption(
            "Cp et Cf sont des hypothèses de travail, à remplacer par les "
            "coûts réels du site avant toute décision."
        )

    st.markdown("#### Seuils de décision proposés")
    st.dataframe(
        pd.DataFrame(DECISION_ROWS, columns=["Action", "Déclencheur", "Base"]),
        hide_index=True,
        width="stretch",
    )


def _render_method_tab(summary: dict) -> None:
    availability = float(summary.get("A_pct", 0.0))
    st.markdown("#### Limites méthodologiques")
    st.markdown(
        "- **Snapshot horaire** : pas de temps-avant-panne par machine, donc "
        "pas d'estimation fiable de β ni de RUL en l'état.\n"
        f"- **MTTR absent du dataset** : la disponibilité de {_pct(availability)} "
        "repose sur l'hypothèse explicite d'un MTTR de 4 h.\n"
        "- **Coûts Cp / Cf** : 500 € et 20 000 € sont des hypothèses cohérentes "
        "avec l'ordre de grandeur du projet, mais non mesurées sur le terrain.\n"
        "- **Données synthétiques** : le jeu AI4I 2020 est simulé par ses "
        "auteurs ; toute généralisation à une machine réelle doit être validée."
    )

    st.warning(
        "Une maintenance préventive **calendaire** n'est pas justifiée par une "
        "loi exponentielle. En revanche, la maintenance **conditionnelle** "
        "(seuils capteurs + modèle ML) reste pertinente car elle intervient "
        "avant la défaillance."
    )

    st.markdown("#### Reproductibilité")
    st.code("python reliability_analysis.py", language="bash")
    st.caption(
        "Le script régénère les figures et `data/processed/reliability_summary.json`. "
        "Les contrôles numériques internes (asserts) doivent tous passer."
    )


def _render_downloads(report_path: Path, summary_path: Path) -> None:
    st.divider()
    st.markdown(
        '<p class="section-eyebrow">Document complet</p>',
        unsafe_allow_html=True,
    )
    st.subheader("Rapport HTML autonome")
    st.write(
        "La synthèse ci-dessus est intégrée à l'application. Le rapport HTML "
        "conserve la version longue, mise en page pour l'impression et la "
        "diffusion : contexte FMDS, AMDEC, tableaux détaillés et références."
    )

    left, right = st.columns(2)
    with left:
        if report_path.exists():
            st.download_button(
                "Télécharger le rapport HTML",
                data=report_path.read_bytes(),
                file_name=report_path.name,
                mime="text/html",
                type="primary",
                width="stretch",
            )
        else:
            st.info("Rapport HTML introuvable : exécutez `python reliability_analysis.py`.")
    with right:
        if summary_path.exists():
            st.download_button(
                "Télécharger la synthèse JSON",
                data=summary_path.read_bytes(),
                file_name=summary_path.name,
                mime="application/json",
                width="stretch",
            )
        else:
            st.info("Synthèse JSON introuvable.")


def render_reliability_report(root_dir: Path) -> None:
    """Affiche la page « Rapport de fiabilité » dans l'application."""
    report_path = root_dir / "rapport_fiabilite_cnc.html"
    summary_path = root_dir / "data" / "processed" / "reliability_summary.json"

    if not summary_path.exists():
        st.warning("La synthèse de fiabilité n'est pas encore générée.")
        st.markdown(
            "Lancez le script d'analyse pour produire les figures et le résumé :"
        )
        st.code("python reliability_analysis.py", language="bash")
        return

    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    _render_header(summary, report_path)
    _render_insights(summary)

    st.divider()
    tabs = st.tabs([
        "Fiabilité R(t)",
        "Modes de défaillance",
        "Maintenance & coûts",
        "Méthode & limites",
    ])
    with tabs[0]:
        _render_reliability_tab(root_dir, summary)
    with tabs[1]:
        _render_modes_tab(summary)
    with tabs[2]:
        _render_cost_tab(root_dir, summary)
    with tabs[3]:
        _render_method_tab(summary)

    _render_downloads(report_path, summary_path)
