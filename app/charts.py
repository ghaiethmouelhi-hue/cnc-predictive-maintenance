# -*- coding: utf-8 -*-
"""Figures Plotly du design system CNC Sentinel."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from app.data_access import FAILURE_THRESHOLD
from app.theme import COLORS, COLORWAY, is_light_mode

PLOT_CONFIG = {
    "displayModeBar": False,
    "responsive": True,
    "scrollZoom": False,
}


def _ink(light: str, dark: str) -> str:
    """Couleur de texte lisible selon le thème actif."""
    return light if is_light_mode() else dark


def _hex_to_rgba(color: str, alpha: float) -> str:
    color = color.lstrip("#")
    r, g, b = (int(color[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def _finish(fig: go.Figure, height: int = 320, title: str | None = None) -> go.Figure:
    fig.update_layout(
        template="cnc_sentinel",
        height=height,
        margin=dict(l=12, r=12, t=54, b=12),
    )
    if title:
        fig.update_layout(title=dict(text=title))
    return fig


def gauge(
    value: float,
    *,
    min_value: float = 0,
    max_value: float = 100,
    title: str,
    unit: str = "",
    steps: list[tuple[float, float, str]] | None = None,
    color: str | None = None,
    height: int = 176,
    decimals: int = 0,
) -> go.Figure:
    """Jauge circulaire compacte."""
    if steps is None:
        steps = [(min_value, max_value, "rgba(34,211,238,.12)")]
    gauge_steps = [
        {"range": [start, end], "color": step_color}
        for start, end, step_color in steps
    ]
    if color is None:
        color = COLORS["cyan"]
        for start, end, step_color in steps:
            if start <= value <= end:
                color = step_color
                break
    number = {"font": {"size": 25, "color": _ink("#0b1f33", "#f4faff")}, "suffix": unit}
    if decimals:
        number["valueformat"] = f".{decimals}f"
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=float(value),
            number=number,
            title={"text": title, "font": {"size": 10.5, "color": _ink("#556b82", "#8da2bb")}},
            gauge={
                "axis": {
                    "range": [min_value, max_value],
                    "tickwidth": 0,
                    "tickcolor": "rgba(0,0,0,0)",
                    "tickfont": {"size": 8.5, "color": _ink("#4b6076", "#6f849c")},
                },
                "bar": {"color": color, "thickness": 0.30},
                "bgcolor": _ink("rgba(15,42,74,.06)", "rgba(148,163,184,.06)"),
                "borderwidth": 0,
                "steps": gauge_steps,
                "threshold": {
                    "line": {"color": _ink("#0b1f33", "#e7f9ff"), "width": 1.6},
                    "thickness": 0.72,
                    "value": float(value),
                },
            },
        )
    )
    return _finish(fig, height=height, title=None)


def risk_gauge(probability: float, height: int = 210) -> go.Figure:
    """Jauge de risque 0–100 % avec les zones de décision de l'application."""
    pct = max(0.0, min(1.0, float(probability))) * 100
    if pct >= 75:
        color = COLORS["red"]
    elif pct >= 50:
        color = COLORS["orange"]
    elif pct >= FAILURE_THRESHOLD * 100:
        color = COLORS["amber"]
    else:
        color = COLORS["green"]
    steps = [
        (0, FAILURE_THRESHOLD * 100, "rgba(52,211,153,.14)"),
        (FAILURE_THRESHOLD * 100, 50, "rgba(251,191,36,.14)"),
        (50, 75, "rgba(251,146,60,.14)"),
        (75, 100, "rgba(248,113,113,.16)"),
    ]
    fig = gauge(
        pct,
        min_value=0,
        max_value=100,
        title="PROBABILITÉ DE PANNE",
        unit=" %",
        steps=steps,
        color=color,
        height=height,
        decimals=1,
    )
    return fig


def donut(
    labels: list[str],
    values: list[float],
    *,
    title: str,
    center_label: str = "",
    center_value: str = "",
    colors: list[str] | None = None,
    height: int = 320,
) -> go.Figure:
    colors = colors or COLORWAY
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.66,
            sort=False,
            textinfo="none",
            marker=dict(
                colors=colors,
                line=dict(color=_ink("#ffffff", "#050a13"), width=2),
            ),
            hovertemplate="<b>%{label}</b><br>%{value} · %{percent}<extra></extra>",
        )
    )
    if center_value:
        fig.add_annotation(
            text=(
                f"<b>{center_value}</b><br>"
                f"<span style='color:{_ink('#556b82', '#8da2bb')};font-size:11px'>"
                f"{center_label}</span>"
            ),
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=22, color=_ink("#0b1f33", "#f4faff")),
        )
    fig.update_layout(showlegend=True, title=dict(text=title))
    return _finish(fig, height=height)


def bar(
    labels: list[str],
    values: list[float],
    *,
    title: str,
    horizontal: bool = False,
    color: str | list[str] | None = None,
    height: int = 320,
    text_suffix: str = "",
) -> go.Figure:
    color = color or COLORS["cyan"]
    text = [f"{v:,.0f}{text_suffix}".replace(",", " ") for v in values]
    if horizontal:
        trace = go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker=dict(color=color, line=dict(width=0)),
            text=text,
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>%{x}<extra></extra>",
        )
    else:
        trace = go.Bar(
            x=labels,
            y=values,
            marker=dict(color=color, line=dict(width=0)),
            text=text,
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>%{y}<extra></extra>",
        )
    fig = go.Figure(trace)
    fig.update_layout(title=dict(text=title), bargap=0.38)
    return _finish(fig, height=height)


def grouped_bar(
    categories: list[str],
    series: dict[str, list[float]],
    *,
    title: str,
    height: int = 320,
) -> go.Figure:
    fig = go.Figure()
    for index, (name, values) in enumerate(series.items()):
        fig.add_trace(
            go.Bar(
                x=categories,
                y=values,
                name=name,
                marker=dict(color=COLORWAY[index % len(COLORWAY)], line=dict(width=0)),
                hovertemplate="<b>%{x}</b><br>" + name + " : %{y}<extra></extra>",
            )
        )
    fig.update_layout(barmode="group", title=dict(text=title), bargap=0.32, bargroupgap=0.08)
    return _finish(fig, height=height)


def line_series(
    x,
    series: list[dict],
    *,
    title: str,
    height: int = 320,
    y_title: str | None = None,
    hover_suffix: str = "",
) -> go.Figure:
    """series = [{name, y, color, fill?}]."""
    fig = go.Figure()
    for index, item in enumerate(series):
        color = item.get("color", COLORWAY[index % len(COLORWAY)])
        fill = "tozeroy" if item.get("fill") else None
        fig.add_trace(
            go.Scatter(
                x=x,
                y=item["y"],
                name=item.get("name", f"Série {index + 1}"),
                mode="lines",
                line=dict(color=color, width=2.1, shape="spline", smoothing=0.55),
                fill=fill,
                fillcolor=_hex_to_rgba(color, 0.10) if fill else None,
                hovertemplate="%{x}<br><b>%{y:.2f}" + hover_suffix + "</b><extra>"
                + item.get("name", "")
                + "</extra>",
            )
        )
    fig.update_layout(
        title=dict(text=title),
        hovermode="x unified",
        yaxis_title=y_title,
    )
    return _finish(fig, height=height)


def histogram(
    values,
    *,
    title: str,
    color: str | None = None,
    bins: int = 32,
    height: int = 300,
    x_title: str | None = None,
) -> go.Figure:
    fig = go.Figure(
        go.Histogram(
            x=values,
            nbinsx=bins,
            marker=dict(
                color=color or COLORS["blue"],
                line=dict(color=_ink("#ffffff", "#050a13"), width=0.5),
            ),
            opacity=0.9,
        )
    )
    fig.update_layout(title=dict(text=title), bargap=0.04, xaxis_title=x_title)
    return _finish(fig, height=height)


def scatter(
    x,
    y,
    *,
    title: str,
    color_values=None,
    text=None,
    x_title: str | None = None,
    y_title: str | None = None,
    height: int = 340,
    colorbar_title: str = "",
) -> go.Figure:
    if color_values is None:
        marker = dict(color=COLORS["cyan"], size=6, opacity=0.7)
    else:
        marker = dict(
            color=color_values,
            size=7,
            opacity=0.8,
            colorscale=[[0, COLORS["green"]], [0.45, COLORS["amber"]], [1, COLORS["red"]]],
            colorbar=dict(
                title=dict(
                    text=colorbar_title,
                    font=dict(size=10, color=_ink("#33475b", "#8da2bb")),
                ),
                thickness=10,
                len=0.7,
                tickfont=dict(size=9, color=_ink("#4b6076", "#7f93ab")),
                outlinewidth=0,
            ),
        )
    fig = go.Figure(
        go.Scatter(
            x=x,
            y=y,
            mode="markers",
            marker=marker,
            text=text,
            hovertemplate="%{text}<br>x=%{x:.2f} · y=%{y:.2f}<extra></extra>"
            if text is not None
            else "x=%{x:.2f} · y=%{y:.2f}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(text=title),
        xaxis_title=x_title,
        yaxis_title=y_title,
    )
    return _finish(fig, height=height)


def heatmap(
    z,
    x,
    y,
    *,
    title: str,
    colorscale: str = "Tealgrn",
    height: int = 380,
    zmin: float | None = None,
    zmax: float | None = None,
) -> go.Figure:
    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=x,
            y=y,
            colorscale=colorscale,
            zmin=zmin,
            zmax=zmax,
            hovertemplate="%{y} / %{x}<br><b>%{z}</b><extra></extra>",
            colorbar=dict(
                thickness=10,
                len=0.75,
                tickfont=dict(size=9, color=_ink("#4b6076", "#7f93ab")),
                outlinewidth=0,
            ),
        )
    )
    fig.update_layout(title=dict(text=title))
    return _finish(fig, height=height)


def roc_curve_chart(metrics: dict, height: int = 340) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode="lines",
            name="Hasard",
            line=dict(color="rgba(148,163,184,.35)", dash="dash", width=1.2),
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=metrics["fpr"],
            y=metrics["tpr"],
            mode="lines",
            name=f"AUC-ROC {metrics['auc_roc']:.3f}",
            line=dict(color=COLORS["cyan"], width=2.4),
            fill="tozeroy",
            fillcolor="rgba(34,211,238,.08)",
        )
    )
    fig.update_layout(
        title=dict(text="Courbe ROC — jeu de test"),
        xaxis_title="Taux de faux positifs",
        yaxis_title="Taux de vrais positifs",
    )
    return _finish(fig, height=height)


def pr_curve_chart(metrics: dict, height: int = 340) -> go.Figure:
    fig = go.Figure(
        go.Scatter(
            x=metrics["recall"],
            y=metrics["precision"],
            mode="lines",
            name=f"AUC-PR {metrics['auc_pr']:.3f}",
            line=dict(color=COLORS["violet"], width=2.4),
            fill="tozeroy",
            fillcolor="rgba(167,139,250,.09)",
        )
    )
    fig.update_layout(
        title=dict(text="Courbe précision-rappel"),
        xaxis_title="Rappel",
        yaxis_title="Précision",
    )
    return _finish(fig, height=height)


def threshold_chart(metrics: dict, height: int = 360) -> go.Figure:
    table = metrics["threshold_df"]
    fig = go.Figure()
    for name, color in (
        ("Précision", COLORS["violet"]),
        ("Rappel", COLORS["cyan"]),
        ("F1", COLORS["green"]),
    ):
        fig.add_trace(
            go.Scatter(
                x=table["Seuil"],
                y=table[name],
                mode="lines+markers",
                name=name,
                line=dict(color=color, width=2),
                marker=dict(size=4),
                hovertemplate="Seuil %{x:.2f}<br>" + name + " : %{y:.3f}<extra></extra>",
            )
        )
    fig.add_vline(
        x=FAILURE_THRESHOLD,
        line=dict(color=_ink("#b45309", COLORS["amber"]), dash="dot", width=1.6),
        annotation_text="Seuil app · 0.111",
        annotation_position="top",
        annotation_font=dict(
            size=10,
            color=_ink("#b45309", COLORS["amber"]),
        ),
    )
    fig.update_layout(
        title=dict(text="Arbitrage précision / rappel selon le seuil"),
        xaxis_title="Seuil de décision",
        yaxis_title="Score",
        yaxis_range=[0, 1.02],
    )
    return _finish(fig, height=height)


def confusion_chart(metrics: dict, height: int = 340) -> go.Figure:
    confusion = metrics["confusion"]
    z = [[confusion["tn"], confusion["fp"]], [confusion["fn"], confusion["tp"]]]
    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=["Prédit normal", "Prédit panne"],
            y=["Réel normal", "Réel panne"],
            colorscale=[[0, "#08111f"], [0.35, "#0e7490"], [1, "#22d3ee"]],
            text=[[str(v) for v in row] for row in z],
            texttemplate="<b>%{text}</b>",
            textfont=dict(size=18, color="#eefaff"),
            showscale=False,
            hovertemplate="%{y} / %{x}<br><b>%{z}</b><extra></extra>",
        )
    )
    fig.update_layout(title=dict(text="Matrice de confusion — seuil 0.111"))
    fig.update_yaxes(autorange="reversed")
    return _finish(fig, height=height)


def correlation_heatmap(df: pd.DataFrame, height: int = 430) -> go.Figure:
    numeric = df.select_dtypes(include=[np.number]).drop(columns=["failure"], errors="ignore")
    corr = numeric.corr().round(2)
    fig = go.Figure(
        go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.index,
            colorscale="RdBu",
            zmin=-1,
            zmax=1,
            hovertemplate="%{y} / %{x}<br><b>%{z}</b><extra></extra>",
            colorbar=dict(
                thickness=10,
                len=0.75,
                tickfont=dict(size=9, color=_ink("#4b6076", "#7f93ab")),
                outlinewidth=0,
            ),
        )
    )
    fig.update_layout(title=dict(text="Corrélations des variables capteurs"))
    return _finish(fig, height=height)
