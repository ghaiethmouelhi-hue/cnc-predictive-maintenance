# -*- coding: utf-8 -*-
"""Design system de CNC Sentinel.

Palette sombre industrielle, effets glassmorphism, typographie et composants
Plotly partagés par toutes les vues de l'application.
"""

from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio

COLORS = {
    "bg": "#050a13",
    "bg_2": "#070f1c",
    "panel": "#0b1424",
    "panel_2": "#0f1b2f",
    "text": "#e7eef9",
    "muted": "#8da2bb",
    "dim": "#5f7590",
    "cyan": "#22d3ee",
    "blue": "#3b82f6",
    "sky": "#38bdf8",
    "violet": "#a78bfa",
    "green": "#34d399",
    "amber": "#fbbf24",
    "orange": "#fb923c",
    "red": "#f87171",
    "pink": "#f472b6",
}

COLORWAY = [
    COLORS["cyan"],
    COLORS["blue"],
    COLORS["violet"],
    COLORS["green"],
    COLORS["amber"],
    COLORS["red"],
    COLORS["sky"],
    COLORS["pink"],
]

# Variante plus contrastée pour le mode clair.
LIGHT_COLORWAY = [
    "#0891b2",
    "#2563eb",
    "#7c3aed",
    "#059669",
    "#b45309",
    "#dc2626",
    "#0284c7",
    "#db2777",
]

GLOBAL_CSS = """
<style>
:root {
    --bg: #050a13;
    --bg-2: #070f1c;
    --panel: #0b1424;
    --panel-2: #0f1b2f;
    --panel-3: #111f36;
    --line: rgba(148, 163, 184, .14);
    --line-strong: rgba(34, 211, 238, .34);
    --text: #e7eef9;
    --muted: #8da2bb;
    --dim: #5f7590;
    --cyan: #22d3ee;
    --blue: #3b82f6;
    --sky: #38bdf8;
    --violet: #a78bfa;
    --green: #34d399;
    --amber: #fbbf24;
    --orange: #fb923c;
    --red: #f87171;
    --pink: #f472b6;
    --shadow: 0 22px 60px rgba(0, 0, 0, .38);
    --shadow-soft: 0 12px 34px rgba(0, 0, 0, .26);
    --radius: 18px;
}

html, body, .stApp {
    color: var(--text);
    font-family: "Inter", "Segoe UI", system-ui, -apple-system, sans-serif;
}

.stApp {
    background:
        radial-gradient(1100px 720px at 6% -12%, rgba(34, 211, 238, .13), transparent 62%),
        radial-gradient(920px 620px at 100% 0%, rgba(59, 130, 246, .12), transparent 58%),
        radial-gradient(760px 520px at 50% 112%, rgba(167, 139, 250, .08), transparent 60%),
        linear-gradient(rgba(148, 163, 184, .035) 1px, transparent 1px) 0 0 / 48px 48px,
        linear-gradient(90deg, rgba(148, 163, 184, .035) 1px, transparent 1px) 0 0 / 48px 48px,
        linear-gradient(180deg, #050a13 0%, #060d19 48%, #050a13 100%);
    background-attachment: fixed;
}

[data-testid="stAppViewContainer"] {
    color: var(--text);
}

[data-testid="stHeader"] {
    background: transparent;
}
[data-testid="stAppDeployButton"] {
    display: none;
}
[data-testid="stToolbar"] {
    right: 1.1rem;
}

[data-testid="stMainBlockContainer"] {
    max-width: 1460px;
    padding-top: 2.1rem;
    padding-bottom: 4.5rem;
}

/* ── Sidebar ─────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background:
        radial-gradient(420px 260px at 0% 0%, rgba(34, 211, 238, .10), transparent 70%),
        linear-gradient(180deg, rgba(9, 17, 31, .98), rgba(5, 11, 21, .99));
    border-right: 1px solid rgba(148, 163, 184, .12);
    box-shadow: 14px 0 44px rgba(0, 0, 0, .28);
}
[data-testid="stSidebarContent"] {
    padding-top: .55rem;
}
[data-testid="stSidebarNav"] {
    padding-top: .35rem;
}
[data-testid="stSidebarNav"]::before {
    content: "◈   CNC SENTINEL\\A MACHINE INTELLIGENCE";
    display: block;
    white-space: pre-line;
    margin: .35rem .9rem 1.1rem;
    padding: .7rem .8rem .7rem .9rem;
    color: #eafcff;
    font-size: .92rem;
    font-weight: 800;
    letter-spacing: .16em;
    line-height: 1.65;
    border: 1px solid rgba(34, 211, 238, .18);
    border-radius: 14px;
    background:
        radial-gradient(140px 80px at 6% 20%, rgba(34, 211, 238, .24), transparent 70%),
        linear-gradient(135deg, rgba(34, 211, 238, .10), rgba(59, 130, 246, .04));
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, .05), 0 10px 26px rgba(0, 0, 0, .22);
}
[data-testid="stSidebarNav"] > div:first-child {
    margin-top: -.15rem;
}
[data-testid="stSidebarNav"] a {
    border-radius: 12px;
    margin: 2px 10px;
    padding: .5rem .7rem;
    color: var(--muted) !important;
    transition: background .18s ease, color .18s ease, transform .18s ease;
}
[data-testid="stSidebarNav"] a:hover {
    background: rgba(34, 211, 238, .08);
    color: #dcf8ff !important;
    transform: translateX(2px);
}
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: linear-gradient(90deg, rgba(34, 211, 238, .17), rgba(59, 130, 246, .05));
    color: #edfdff !important;
    box-shadow: inset 0 0 0 1px rgba(34, 211, 238, .18);
    border-left: 3px solid var(--cyan);
}
[data-testid="stSidebarNav"] a[aria-current="page"] span {
    color: #edfdff !important;
}
[data-testid="stNavSectionHeader"] {
    margin: 1.1rem .95rem .35rem;
    color: var(--dim) !important;
    font-size: .68rem !important;
    font-weight: 800;
    letter-spacing: .16em;
    text-transform: uppercase;
}
[data-testid="stSidebarNavSeparator"] {
    border-color: rgba(148, 163, 184, .12);
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: .8rem;
    padding: .5rem .95rem 1rem;
}
.brand-mark {
    display: grid;
    place-items: center;
    width: 42px;
    height: 42px;
    border-radius: 13px;
    color: #04121a;
    font-size: .72rem;
    font-weight: 900;
    letter-spacing: -.04em;
    background: linear-gradient(135deg, #67e8f9 0%, #22d3ee 48%, #3b82f6 100%);
    box-shadow: 0 0 26px rgba(34, 211, 238, .38), inset 0 1px 0 rgba(255, 255, 255, .65);
}
.brand-name {
    color: #f3f9ff;
    font-size: 1.02rem;
    font-weight: 800;
    letter-spacing: .11em;
}
.brand-sub {
    margin-top: .1rem;
    color: var(--muted);
    font-size: .67rem;
    letter-spacing: .08em;
    text-transform: uppercase;
}

.sidebar-card {
    margin: .85rem .8rem .35rem;
    padding: .85rem .9rem;
    border: 1px solid var(--line);
    border-radius: 14px;
    background: linear-gradient(150deg, rgba(17, 31, 54, .88), rgba(9, 17, 31, .68));
    box-shadow: var(--shadow-soft);
}
.sidebar-card .status-line {
    display: flex;
    align-items: center;
    gap: .45rem;
    color: #d9f7ff;
    font-size: .76rem;
    font-weight: 700;
    letter-spacing: .03em;
}
.sidebar-card .status-meta {
    margin-top: .2rem;
    color: var(--muted);
    font-size: .68rem;
    line-height: 1.45;
}
.sidebar-dev {
    display: flex;
    align-items: center;
    gap: .6rem;
    padding: .75rem .95rem .35rem;
    border-top: 1px solid rgba(148, 163, 184, .10);
    margin-top: .65rem;
}
.sidebar-avatar {
    display: grid;
    place-items: center;
    width: 34px;
    height: 34px;
    border-radius: 50%;
    color: #031018;
    font-size: .72rem;
    font-weight: 900;
    background: linear-gradient(135deg, #67e8f9, #a78bfa);
    box-shadow: 0 0 18px rgba(34, 211, 238, .3);
}
.sidebar-dev-name {
    color: #e7eef9;
    font-size: .76rem;
    font-weight: 700;
}
.sidebar-dev-role {
    color: var(--muted);
    font-size: .65rem;
}

/* ── Typography ──────────────────────────────────────────── */
h1, h2, h3, h4, h5 {
    color: var(--text) !important;
    letter-spacing: -.03em;
    font-weight: 750;
}
p, li, label, .stMarkdown {
    color: #c9d7e8;
}
[data-testid="stWidgetLabel"] p {
    color: #b9c9dc !important;
    font-weight: 600;
}
[data-testid="stCaptionContainer"] p,
.stCaption {
    color: var(--muted) !important;
}
a {
    color: var(--cyan);
    text-decoration: none;
}
a:hover {
    color: #a5f3fc;
}
hr {
    border-color: rgba(148, 163, 184, .13);
    margin: 1.9rem 0;
}

.section-eyebrow {
    margin: 1.55rem 0 .45rem;
    color: var(--cyan);
    font-size: .71rem;
    font-weight: 800;
    letter-spacing: .18em;
    text-transform: uppercase;
}
.gradient-text {
    background: linear-gradient(100deg, #e7f9ff 0%, #67e8f9 42%, #60a5fa 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

/* ── Hero ────────────────────────────────────────────────── */
.hero {
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 1.5rem;
    padding: 1.85rem 2rem;
    margin: 0 0 1.35rem;
    border: 1px solid rgba(148, 163, 184, .18);
    border-radius: 22px;
    background:
        linear-gradient(120deg, rgba(15, 29, 50, .94) 0%, rgba(10, 21, 38, .88) 54%, rgba(8, 18, 33, .82) 100%);
    box-shadow: var(--shadow);
    animation: fadeUp .55s ease both;
}
.hero::before {
    content: "";
    position: absolute;
    inset: -60% -10% auto auto;
    width: 420px;
    height: 420px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(34, 211, 238, .22), transparent 66%);
    pointer-events: none;
}
.hero::after {
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(34, 211, 238, .55), rgba(59, 130, 246, .35), transparent);
}
.hero--violet::before { background: radial-gradient(circle, rgba(167, 139, 250, .22), transparent 66%); }
.hero--green::before { background: radial-gradient(circle, rgba(52, 211, 153, .20), transparent 66%); }
.hero--amber::before { background: radial-gradient(circle, rgba(251, 191, 36, .18), transparent 66%); }
.hero-copy { position: relative; z-index: 1; max-width: 820px; }
.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: .5rem;
    margin-bottom: .55rem;
    color: #8be9f5;
    font-size: .69rem;
    font-weight: 800;
    letter-spacing: .2em;
    text-transform: uppercase;
}
.hero-eyebrow .dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--cyan);
    box-shadow: 0 0 0 4px rgba(34, 211, 238, .12), 0 0 16px rgba(34, 211, 238, .8);
    animation: pulse 2.6s ease-in-out infinite;
}
.hero h1 {
    margin: 0;
    font-size: clamp(1.65rem, 2.7vw, 2.35rem);
    line-height: 1.08;
    letter-spacing: -.045em;
    color: #f6fbff !important;
}
.hero p {
    max-width: 720px;
    margin: .55rem 0 0;
    color: #a9bdd6 !important;
    font-size: .95rem;
    line-height: 1.55;
}
.hero-meta {
    position: relative;
    z-index: 1;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: .45rem;
    min-width: 150px;
}
.hero-chip {
    display: inline-flex;
    align-items: center;
    gap: .4rem;
    padding: .38rem .7rem;
    border: 1px solid rgba(34, 211, 238, .26);
    border-radius: 999px;
    color: #c9f8ff;
    background: rgba(34, 211, 238, .07);
    font-size: .69rem;
    font-weight: 700;
    letter-spacing: .06em;
    white-space: nowrap;
}
.hero-chip.muted {
    border-color: rgba(148, 163, 184, .18);
    color: var(--muted);
    background: rgba(148, 163, 184, .05);
}

/* ── KPI cards ───────────────────────────────────────────── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(165px, 1fr));
    gap: .8rem;
    margin: .35rem 0 1.3rem;
}
.kpi-card {
    position: relative;
    overflow: hidden;
    padding: .95rem 1rem .9rem;
    border: 1px solid var(--line);
    border-radius: 16px;
    background: linear-gradient(155deg, rgba(17, 31, 54, .90), rgba(9, 17, 31, .74));
    box-shadow: var(--shadow-soft);
    animation: fadeUp .5s ease both;
    transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease;
}
.kpi-card:hover {
    transform: translateY(-3px);
    border-color: var(--line-strong);
    box-shadow: 0 18px 42px rgba(0, 0, 0, .34), 0 0 26px rgba(34, 211, 238, .07);
}
.kpi-card::after {
    content: "";
    position: absolute;
    inset: auto 0 0 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--tone, var(--cyan)), transparent);
    opacity: .65;
}
.kpi-top {
    display: flex;
    align-items: center;
    gap: .5rem;
    margin-bottom: .55rem;
}
.kpi-icon {
    display: grid;
    place-items: center;
    width: 30px;
    height: 30px;
    border-radius: 9px;
    color: var(--tone, var(--cyan));
    background: rgba(34, 211, 238, .08);
    border: 1px solid rgba(34, 211, 238, .14);
}
.kpi-label {
    color: var(--muted);
    font-size: .69rem;
    font-weight: 700;
    letter-spacing: .07em;
    text-transform: uppercase;
}
.kpi-value {
    color: #f4faff;
    font-size: 1.62rem;
    font-weight: 800;
    line-height: 1.1;
    letter-spacing: -.045em;
    font-variant-numeric: tabular-nums;
}
.kpi-sub {
    margin-top: .32rem;
    color: var(--muted);
    font-size: .72rem;
    line-height: 1.4;
}
.kpi-sub strong { color: #c9d7e8; }
.tone-cyan { --tone: var(--cyan); }
.tone-blue { --tone: var(--blue); }
.tone-violet { --tone: var(--violet); }
.tone-green { --tone: var(--green); }
.tone-amber { --tone: var(--amber); }
.tone-orange { --tone: var(--orange); }
.tone-red { --tone: var(--red); }
.tone-slate { --tone: #94a3b8; }

/* ── Panels & cards ──────────────────────────────────────── */
.panel {
    position: relative;
    padding: 1.1rem 1.15rem;
    border: 1px solid var(--line);
    border-radius: var(--radius);
    background: linear-gradient(155deg, rgba(17, 31, 54, .82), rgba(8, 16, 29, .72));
    box-shadow: var(--shadow-soft);
    backdrop-filter: blur(16px);
    animation: fadeUp .5s ease both;
}
.panel-head {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: .55rem;
}
.panel-title {
    margin: 0;
    color: #eaf4ff;
    font-size: .98rem;
    font-weight: 750;
    letter-spacing: -.02em;
}
.panel-sub {
    margin: .18rem 0 0;
    color: var(--muted);
    font-size: .73rem;
    line-height: 1.45;
}
.panel-icon {
    display: grid;
    place-items: center;
    width: 32px;
    height: 32px;
    flex: 0 0 auto;
    border-radius: 9px;
    color: var(--cyan);
    background: rgba(34, 211, 238, .08);
    border: 1px solid rgba(34, 211, 238, .14);
}
.glass-card {
    position: relative;
    overflow: hidden;
    padding: 1.15rem 1.2rem;
    border: 1px solid var(--line);
    border-radius: var(--radius);
    background: linear-gradient(155deg, rgba(17, 31, 54, .84), rgba(8, 16, 29, .70));
    box-shadow: var(--shadow-soft);
    backdrop-filter: blur(16px);
    animation: fadeUp .5s ease both;
    transition: transform .2s ease, border-color .2s ease;
}
.glass-card:hover {
    transform: translateY(-2px);
    border-color: rgba(34, 211, 238, .28);
}
.glass-card h4 {
    margin: 0 0 .35rem;
    color: #eaf4ff;
    font-size: .95rem;
}
.glass-card p {
    margin: 0;
    color: #a9bdd6;
    font-size: .82rem;
    line-height: 1.55;
}
.card-eyebrow {
    margin-bottom: .35rem;
    color: var(--cyan);
    font-size: .65rem;
    font-weight: 800;
    letter-spacing: .16em;
    text-transform: uppercase;
}

/* ── Status pills ────────────────────────────────────────── */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: .42rem;
    padding: .32rem .68rem;
    border-radius: 999px;
    border: 1px solid transparent;
    font-size: .68rem;
    font-weight: 800;
    letter-spacing: .07em;
    text-transform: uppercase;
    white-space: nowrap;
}
.status-pill .dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: currentColor;
    box-shadow: 0 0 10px currentColor;
    animation: pulse 2.2s ease-in-out infinite;
}
.status-normal { color: #6ee7b7; border-color: rgba(52, 211, 153, .3); background: rgba(52, 211, 153, .09); }
.status-warning { color: #fcd34d; border-color: rgba(251, 191, 36, .3); background: rgba(251, 191, 36, .09); }
.status-elevated { color: #fdba74; border-color: rgba(251, 146, 60, .3); background: rgba(251, 146, 60, .09); }
.status-critical { color: #fca5a5; border-color: rgba(248, 113, 113, .32); background: rgba(248, 113, 113, .10); }
.status-idle { color: #a8b6c9; border-color: rgba(148, 163, 184, .24); background: rgba(148, 163, 184, .08); }
.status-info { color: #7dd3fc; border-color: rgba(56, 189, 248, .3); background: rgba(56, 189, 248, .09); }

/* ── Chips & tags ────────────────────────────────────────── */
.chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: .45rem;
    margin: .55rem 0 .2rem;
}
.chip {
    display: inline-flex;
    align-items: center;
    gap: .35rem;
    padding: .34rem .62rem;
    border: 1px solid rgba(148, 163, 184, .18);
    border-radius: 999px;
    color: #b9cce2;
    background: rgba(148, 163, 184, .06);
    font-size: .71rem;
    font-weight: 600;
    transition: border-color .18s ease, color .18s ease, background .18s ease;
}
.chip:hover {
    border-color: rgba(34, 211, 238, .35);
    color: #d9f8ff;
    background: rgba(34, 211, 238, .07);
}
.chip--accent {
    border-color: rgba(34, 211, 238, .3);
    color: #a5f3fc;
    background: rgba(34, 211, 238, .08);
}

/* ── Metric / progress bars ──────────────────────────────── */
.bar-list { display: grid; gap: .65rem; margin-top: .4rem; }
.bar-item .bar-head {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: .28rem;
    color: var(--muted);
    font-size: .72rem;
}
.bar-item .bar-head strong { color: #dbeafe; font-weight: 650; }
.bar-track {
    height: 7px;
    overflow: hidden;
    border-radius: 99px;
    background: rgba(148, 163, 184, .12);
}
.bar-fill {
    height: 100%;
    border-radius: 99px;
    background: linear-gradient(90deg, var(--tone, var(--cyan)), rgba(59, 130, 246, .8));
    box-shadow: 0 0 14px rgba(34, 211, 238, .25);
    animation: grow 1s cubic-bezier(.2, .8, .2, 1) both;
}

/* ── Alerts list ─────────────────────────────────────────── */
.alert-list { display: grid; gap: .5rem; margin-top: .35rem; }
.alert-item {
    display: flex;
    align-items: center;
    gap: .7rem;
    padding: .62rem .75rem;
    border: 1px solid var(--line);
    border-radius: 12px;
    background: rgba(9, 17, 31, .62);
    transition: border-color .18s ease, background .18s ease;
}
.alert-item:hover {
    border-color: rgba(34, 211, 238, .24);
    background: rgba(17, 31, 54, .72);
}
.alert-dot {
    width: 8px;
    height: 8px;
    flex: 0 0 auto;
    border-radius: 50%;
    background: var(--tone, var(--cyan));
    box-shadow: 0 0 10px var(--tone, var(--cyan));
}
.alert-main { flex: 1; min-width: 0; }
.alert-title { color: #dbeafe; font-size: .78rem; font-weight: 650; }
.alert-meta { margin-top: .08rem; color: var(--muted); font-size: .68rem; }
.alert-value { color: #f1f7ff; font-size: .78rem; font-weight: 750; font-variant-numeric: tabular-nums; }

/* ── Signal cards ────────────────────────────────────────── */
.signal-card {
    display: flex;
    gap: .75rem;
    padding: .8rem .85rem;
    border: 1px solid rgba(251, 191, 36, .18);
    border-radius: 13px;
    background: linear-gradient(150deg, rgba(251, 191, 36, .06), rgba(9, 17, 31, .55));
    margin-bottom: .5rem;
}
.signal-card.critical {
    border-color: rgba(248, 113, 113, .24);
    background: linear-gradient(150deg, rgba(248, 113, 113, .07), rgba(9, 17, 31, .55));
}
.signal-card.info {
    border-color: rgba(52, 211, 153, .20);
    background: linear-gradient(150deg, rgba(52, 211, 153, .05), rgba(9, 17, 31, .55));
}
.signal-icon {
    display: grid;
    place-items: center;
    width: 30px;
    height: 30px;
    flex: 0 0 auto;
    border-radius: 8px;
    color: var(--amber);
    background: rgba(251, 191, 36, .1);
}
.signal-card.critical .signal-icon { color: var(--red); background: rgba(248, 113, 113, .1); }
.signal-card.info .signal-icon { color: var(--green); background: rgba(52, 211, 153, .1); }
.signal-title { color: #eaf4ff; font-size: .8rem; font-weight: 700; }
.signal-detail { margin-top: .16rem; color: var(--muted); font-size: .72rem; line-height: 1.45; }
.signal-action { margin-top: .26rem; color: #b9cce2; font-size: .72rem; }

/* ── Recommendation cards ────────────────────────────────── */
.rec-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: .7rem;
    margin-top: .65rem;
}
.rec-card {
    padding: .9rem .95rem;
    border: 1px solid var(--line);
    border-radius: 14px;
    background: rgba(9, 17, 31, .62);
}
.rec-card h5 {
    margin: 0 0 .3rem;
    color: var(--cyan);
    font-size: .68rem;
    font-weight: 800;
    letter-spacing: .12em;
    text-transform: uppercase;
}
.rec-card p {
    margin: 0;
    color: #c2d3e6;
    font-size: .8rem;
    line-height: 1.55;
}

/* ── Profile ─────────────────────────────────────────────── */
.profile-card {
    position: relative;
    overflow: hidden;
    padding: 1.5rem 1.4rem;
    border: 1px solid rgba(34, 211, 238, .2);
    border-radius: 22px;
    background:
        radial-gradient(420px 260px at 100% 0%, rgba(34, 211, 238, .15), transparent 65%),
        linear-gradient(155deg, rgba(17, 31, 54, .92), rgba(7, 14, 26, .86));
    box-shadow: var(--shadow);
    animation: fadeUp .55s ease both;
}
.profile-card::after {
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(34, 211, 238, .6), transparent);
}
.profile-head { display: flex; align-items: center; gap: 1rem; }
.profile-photo {
    position: relative;
    display: grid;
    place-items: center;
    width: 92px;
    height: 92px;
    flex: 0 0 auto;
    border-radius: 24px;
    color: #04121a;
    font-size: 1.65rem;
    font-weight: 900;
    letter-spacing: -.05em;
    background: linear-gradient(135deg, #67e8f9, #22d3ee 45%, #a78bfa);
    box-shadow: 0 0 38px rgba(34, 211, 238, .28), inset 0 1px 0 rgba(255, 255, 255, .5);
}
.profile-photo img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 24px;
}
.profile-name {
    margin: 0;
    color: #f6fbff;
    font-size: 1.45rem;
    font-weight: 800;
    letter-spacing: -.035em;
}
.profile-role {
    margin-top: .18rem;
    color: var(--cyan);
    font-size: .8rem;
    font-weight: 650;
}
.profile-edu {
    margin-top: .12rem;
    color: var(--muted);
    font-size: .75rem;
}
.profile-bio {
    margin: 1.1rem 0 .9rem;
    color: #b9cce2;
    font-size: .86rem;
    line-height: 1.65;
}
.social-row { display: flex; flex-wrap: wrap; gap: .55rem; margin-top: 1rem; }
.social-btn {
    display: inline-flex;
    align-items: center;
    gap: .48rem;
    padding: .62rem .9rem;
    border: 1px solid rgba(34, 211, 238, .28);
    border-radius: 11px;
    color: #d9f8ff !important;
    background: rgba(34, 211, 238, .08);
    font-size: .72rem;
    font-weight: 750;
    letter-spacing: .05em;
    transition: transform .18s ease, box-shadow .18s ease, background .18s ease;
}
.social-btn:hover {
    transform: translateY(-2px);
    background: rgba(34, 211, 238, .14);
    box-shadow: 0 10px 26px rgba(34, 211, 238, .14);
}
.social-btn.linkedin {
    border-color: rgba(59, 130, 246, .34);
    color: #dbeafe !important;
    background: rgba(59, 130, 246, .1);
}
.social-btn.linkedin:hover {
    background: rgba(59, 130, 246, .17);
    box-shadow: 0 10px 26px rgba(59, 130, 246, .16);
}
.social-btn svg { width: 15px; height: 15px; }

/* ── Co-developer compact card ───────────────────────────── */
.codev-card {
    display: flex;
    align-items: center;
    gap: .75rem;
    margin-top: .8rem;
    padding: .68rem .8rem;
    border: 1px solid var(--line);
    border-radius: 14px;
    background: linear-gradient(150deg, rgba(17, 31, 54, .78), rgba(8, 16, 29, .62));
    box-shadow: var(--shadow-soft);
    transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease;
}
.codev-card:hover {
    transform: translateY(-1px);
    border-color: rgba(34, 211, 238, .28);
    box-shadow: 0 14px 32px rgba(0, 0, 0, .30), 0 0 22px rgba(34, 211, 238, .06);
}
.codev-avatar {
    display: grid;
    place-items: center;
    width: 42px;
    height: 42px;
    flex: 0 0 auto;
    border-radius: 12px;
    color: #04121a;
    font-size: .74rem;
    font-weight: 900;
    letter-spacing: -.03em;
    background: linear-gradient(135deg, #67e8f9, #3b82f6 60%, #a78bfa);
    box-shadow: 0 0 20px rgba(59, 130, 246, .26), inset 0 1px 0 rgba(255, 255, 255, .45);
}
.codev-main { flex: 1; min-width: 0; }
.codev-badge {
    margin-bottom: .12rem;
    color: var(--cyan);
    font-size: .58rem;
    font-weight: 800;
    letter-spacing: .16em;
    text-transform: uppercase;
}
.codev-name {
    color: #f1f9ff;
    font-size: .86rem;
    font-weight: 750;
    letter-spacing: -.01em;
}
.codev-role {
    margin-top: .1rem;
    color: var(--muted);
    font-size: .7rem;
    line-height: 1.35;
}
.codev-link {
    display: grid;
    place-items: center;
    width: 34px;
    height: 34px;
    flex: 0 0 auto;
    border: 1px solid rgba(59, 130, 246, .32);
    border-radius: 9px;
    color: #dbeafe !important;
    background: rgba(59, 130, 246, .1);
    transition: transform .16s ease, background .16s ease, box-shadow .16s ease;
}
.codev-link:hover {
    transform: translateY(-1px);
    background: rgba(59, 130, 246, .2);
    box-shadow: 0 8px 20px rgba(59, 130, 246, .18);
}

/* ── Timeline / pipeline ─────────────────────────────────── */
.pipeline {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: .55rem;
    margin: .6rem 0 .4rem;
}
.pipeline-step {
    position: relative;
    padding: .8rem .85rem;
    border: 1px solid var(--line);
    border-radius: 13px;
    background: rgba(9, 17, 31, .58);
}
.pipeline-step .step-index {
    color: var(--cyan);
    font-size: .64rem;
    font-weight: 800;
    letter-spacing: .14em;
}
.pipeline-step .step-title {
    margin-top: .2rem;
    color: #e7eef9;
    font-size: .78rem;
    font-weight: 700;
}
.pipeline-step .step-desc {
    margin-top: .18rem;
    color: var(--muted);
    font-size: .69rem;
    line-height: 1.45;
}

/* ── Footer ──────────────────────────────────────────────── */
.app-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: .8rem;
    margin-top: 2.6rem;
    padding: 1rem 1.2rem;
    border-top: 1px solid rgba(148, 163, 184, .13);
    color: var(--muted);
    font-size: .72rem;
}
.footer-brand {
    color: #dbeafe;
    font-weight: 800;
    letter-spacing: .13em;
}
.footer-brand span { color: var(--cyan); }
.footer-credit a, .footer-links a {
    color: #b9e9f5 !important;
    font-weight: 650;
}
.footer-links { display: flex; gap: .55rem; align-items: center; }
.footer-links .sep { color: rgba(148, 163, 184, .35); }

/* ── Streamlit widget overrides ──────────────────────────── */
[data-testid="stForm"] {
    padding: 1.1rem 1.2rem .9rem;
    border: 1px solid var(--line);
    border-radius: var(--radius);
    background: linear-gradient(155deg, rgba(17, 31, 54, .74), rgba(8, 16, 29, .62));
    box-shadow: var(--shadow-soft);
    backdrop-filter: blur(14px);
}
[data-testid="stVerticalBlockBorderWrapper"] > div {
    border-color: var(--line) !important;
    border-radius: var(--radius) !important;
    background: linear-gradient(155deg, rgba(17, 31, 54, .72), rgba(8, 16, 29, .58)) !important;
    box-shadow: var(--shadow-soft);
}
div[data-testid="stMetric"] {
    min-height: 92px;
    padding: .85rem .95rem;
    border: 1px solid var(--line);
    border-radius: 14px;
    background: linear-gradient(155deg, rgba(17, 31, 54, .78), rgba(8, 16, 29, .62));
    box-shadow: var(--shadow-soft);
}
div[data-testid="stMetricLabel"] p {
    color: var(--muted) !important;
    font-size: .7rem;
    font-weight: 700;
    letter-spacing: .06em;
    text-transform: uppercase;
}
div[data-testid="stMetricValue"] {
    color: #f4faff !important;
    font-size: 1.4rem;
    font-weight: 800;
    letter-spacing: -.03em;
}
div[data-testid="stMetricDelta"] {
    color: var(--cyan) !important;
    font-size: .7rem;
}
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: .25rem;
    border-bottom: 1px solid rgba(148, 163, 184, .12);
}
[data-testid="stTabs"] button[data-baseweb="tab"] {
    padding: .55rem .85rem;
    color: var(--muted);
    font-weight: 700;
    font-size: .8rem;
}
[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
    color: #bdf7ff;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    background: var(--cyan);
}
[data-testid="stTabs"] [data-baseweb="tab-border"] {
    background: rgba(148, 163, 184, .12);
}
.stButton > button,
[data-testid="stFormSubmitButton"] > button,
[data-testid="stDownloadButton"] > button {
    min-height: 2.7rem;
    border-radius: 11px;
    border: 1px solid rgba(34, 211, 238, .3);
    color: #d9f8ff;
    background: rgba(34, 211, 238, .08);
    font-weight: 700;
    letter-spacing: .02em;
    transition: transform .16s ease, box-shadow .16s ease, background .16s ease;
}
.stButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover,
[data-testid="stDownloadButton"] > button:hover {
    transform: translateY(-1px);
    background: rgba(34, 211, 238, .14);
    box-shadow: 0 10px 24px rgba(34, 211, 238, .12);
    border-color: rgba(34, 211, 238, .45);
}
.stButton > button[kind="primary"],
[data-testid="stFormSubmitButton"] > button[kind="primary"],
[data-testid="stDownloadButton"] > button[kind="primary"] {
    color: #03131c;
    border-color: transparent;
    background: linear-gradient(100deg, #67e8f9 0%, #22d3ee 48%, #38bdf8 100%);
    box-shadow: 0 12px 30px rgba(34, 211, 238, .22);
}
.stButton > button[kind="primary"]:hover,
[data-testid="stFormSubmitButton"] > button[kind="primary"]:hover {
    box-shadow: 0 16px 36px rgba(34, 211, 238, .3);
}
[data-baseweb="input"],
[data-baseweb="select"] > div,
[data-testid="stNumberInputContainer"],
[data-testid="stTextInput"] input,
[data-testid="stDateInput"] input {
    border-radius: 10px !important;
    border-color: rgba(148, 163, 184, .2) !important;
    background: rgba(7, 14, 26, .72) !important;
    color: #e7eef9 !important;
}
[data-baseweb="input"]:focus-within,
[data-baseweb="select"] > div:focus-within,
[data-testid="stNumberInputContainer"]:focus-within {
    border-color: rgba(34, 211, 238, .55) !important;
    box-shadow: 0 0 0 3px rgba(34, 211, 238, .10) !important;
}
[data-testid="stNumberInputField"],
[data-testid="stTextInput"] input,
[data-baseweb="select"] input,
[data-baseweb="select"] span {
    color: #e7eef9 !important;
    background: transparent !important;
}
[data-testid="stNumberInput"] button {
    color: var(--muted) !important;
    border-color: rgba(148, 163, 184, .14) !important;
    background: rgba(148, 163, 184, .05) !important;
}
[role="listbox"], [role="option"] {
    color: #e7eef9 !important;
    background: #0f1b2f !important;
}
[data-testid="stAlert"] {
    border-radius: 13px;
    border-width: 1px;
}
[data-testid="stAlert"] p { color: inherit; }
[data-testid="stExpander"] {
    border: 1px solid var(--line) !important;
    border-radius: 13px !important;
    background: rgba(9, 17, 31, .55) !important;
    overflow: hidden;
}
[data-testid="stExpander"] summary {
    color: #c9d7e8 !important;
    font-weight: 650;
}
[data-testid="stDataFrame"] {
    overflow: hidden;
    border: 1px solid var(--line);
    border-radius: 13px;
    background: rgba(9, 17, 31, .55);
}
[data-testid="stDataFrame"] * {
    font-family: "Inter", "Segoe UI", system-ui, sans-serif;
}
[data-testid="stProgress"] > div > div > div {
    background: linear-gradient(90deg, #22d3ee, #3b82f6) !important;
}
[data-testid="stCode"] {
    border: 1px solid var(--line);
    border-radius: 12px;
    background: rgba(3, 8, 16, .72);
}
code {
    color: #a5f3fc;
    background: rgba(34, 211, 238, .08);
    border-radius: 5px;
    padding: .1rem .3rem;
}
[data-testid="stImage"] img {
    border-radius: 13px;
    border: 1px solid var(--line);
}
[data-testid="stCaptionContainer"] {
    color: var(--muted);
}

/* ── Animations ──────────────────────────────────────────── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(14px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: .55; transform: scale(.86); }
}
@keyframes grow {
    from { width: 0; }
}
@keyframes shimmer {
    0% { background-position: -220% 0; }
    100% { background-position: 220% 0; }
}
.scan-line {
    position: relative;
    overflow: hidden;
}
.scan-line::after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(100deg, transparent 30%, rgba(34, 211, 238, .08) 50%, transparent 70%);
    background-size: 220% 100%;
    animation: shimmer 4.5s linear infinite;
    pointer-events: none;
}

/* ── Responsive ──────────────────────────────────────────── */
@media (max-width: 900px) {
    [data-testid="stMainBlockContainer"] { padding: 1.1rem .9rem 3rem; }
    .hero { flex-direction: column; align-items: flex-start; padding: 1.35rem 1.2rem; }
    .hero-meta { flex-direction: row; align-items: center; flex-wrap: wrap; }
    .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .profile-head { flex-direction: column; align-items: flex-start; }
}
@media (max-width: 560px) {
    .kpi-grid { grid-template-columns: minmax(0, 1fr); }
    .hero h1 { font-size: 1.55rem; }
    .app-footer { flex-direction: column; align-items: flex-start; }
}
</style>
"""

LIGHT_CSS = """
<style>
:root {
    --bg: #f4f7fc;
    --bg-2: #edf3fa;
    --panel: #ffffff;
    --panel-2: #f7fafd;
    --panel-3: #eef4fb;
    --line: rgba(15, 42, 74, .12);
    --line-strong: rgba(8, 145, 178, .38);
    --text: #0f2438;
    --muted: #556b82;
    --dim: #7b8da1;
    --cyan: #0891b2;
    --blue: #2563eb;
    --sky: #0284c7;
    --violet: #7c3aed;
    --green: #059669;
    --amber: #b45309;
    --orange: #c2410c;
    --red: #dc2626;
    --pink: #db2777;
    --shadow: 0 22px 60px rgba(15, 42, 74, .10);
    --shadow-soft: 0 12px 34px rgba(15, 42, 74, .08);
}

html, body, .stApp {
    color: var(--text);
}
html, body {
    background: #f4f7fc;
}
[data-testid="stAppViewContainer"] {
    background: transparent;
    color: var(--text);
}

.stApp {
    background:
        radial-gradient(1100px 720px at 6% -12%, rgba(8, 145, 178, .10), transparent 62%),
        radial-gradient(920px 620px at 100% 0%, rgba(37, 99, 235, .08), transparent 58%),
        radial-gradient(760px 520px at 50% 112%, rgba(124, 58, 237, .06), transparent 60%),
        linear-gradient(rgba(15, 42, 74, .03) 1px, transparent 1px) 0 0 / 48px 48px,
        linear-gradient(90deg, rgba(15, 42, 74, .03) 1px, transparent 1px) 0 0 / 48px 48px,
        linear-gradient(180deg, #f7fafd 0%, #eef3fa 48%, #f7fafd 100%);
}

[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] {
    background:
        radial-gradient(420px 260px at 0% 0%, rgba(8, 145, 178, .10), transparent 70%),
        linear-gradient(180deg, #ffffff, #f1f6fb);
    border-right: 1px solid rgba(15, 42, 74, .10);
    box-shadow: 14px 0 44px rgba(15, 42, 74, .05);
}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
    color: #364b61 !important;
}
[data-testid="stSidebarNav"]::before {
    color: #0b2a40;
    border-color: rgba(8, 145, 178, .22);
    background:
        radial-gradient(140px 80px at 6% 20%, rgba(8, 145, 178, .14), transparent 70%),
        linear-gradient(135deg, rgba(8, 145, 178, .08), rgba(37, 99, 235, .04));
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, .8), 0 10px 26px rgba(15, 42, 74, .08);
}
[data-testid="stSidebarNav"] a {
    color: var(--muted) !important;
}
[data-testid="stSidebarNav"] a:hover {
    background: rgba(8, 145, 178, .08);
    color: #0e5f76 !important;
}
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: linear-gradient(90deg, rgba(8, 145, 178, .13), rgba(37, 99, 235, .05));
    color: #0b4f63 !important;
    box-shadow: inset 0 0 0 1px rgba(8, 145, 178, .2);
}
[data-testid="stSidebarNav"] a[aria-current="page"] span {
    color: #0b4f63 !important;
}
[data-testid="stSidebarNavSeparator"] {
    border-color: rgba(15, 42, 74, .10);
}
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarCollapseButton"] svg {
    color: #364b61 !important;
    fill: #364b61 !important;
}

.brand-name { color: #102a43; }
.brand-sub { color: var(--muted); }
.sidebar-card {
    background: linear-gradient(150deg, #ffffff, #f3f8fc);
    border-color: rgba(15, 42, 74, .12);
    box-shadow: var(--shadow-soft);
}
.sidebar-card .status-line { color: #0e5f76; }
.sidebar-card .status-meta { color: var(--muted); }
.sidebar-dev { border-top-color: rgba(15, 42, 74, .10); }
.sidebar-dev-name { color: #102a43; }
.sidebar-dev-role { color: var(--muted); }

p, li, label, .stMarkdown { color: #33475b; }
[data-testid="stWidgetLabel"] p { color: #364b61 !important; }
[data-testid="stCaptionContainer"] p, .stCaption { color: var(--muted) !important; }
a { color: var(--cyan); }
a:hover { color: #0e7490; }
hr { border-color: rgba(15, 42, 74, .12); }
.gradient-text {
    background: linear-gradient(100deg, #0f2438 0%, #0891b2 45%, #2563eb 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

.hero {
    border-color: rgba(15, 42, 74, .14);
    background: linear-gradient(120deg, #ffffff 0%, #f6fafd 54%, #eef4fb 100%);
    box-shadow: var(--shadow);
}
.hero::before {
    background: radial-gradient(circle, rgba(8, 145, 178, .16), transparent 66%);
}
.hero h1 { color: #0b1f33 !important; }
.hero p { color: #3c5268 !important; }
.hero-eyebrow { color: #0e7490; }
.hero-chip {
    border-color: rgba(8, 145, 178, .28);
    color: #0e7490;
    background: rgba(8, 145, 178, .07);
}
.hero-chip.muted {
    border-color: rgba(15, 42, 74, .16);
    color: var(--muted);
    background: rgba(15, 42, 74, .04);
}

.kpi-card {
    background: linear-gradient(155deg, #ffffff, #f5f9fd);
    box-shadow: var(--shadow-soft);
}
.kpi-card:hover {
    box-shadow: 0 18px 42px rgba(15, 42, 74, .12), 0 0 26px rgba(8, 145, 178, .07);
}
.kpi-icon {
    background: rgba(8, 145, 178, .08);
    border-color: rgba(8, 145, 178, .16);
}
.kpi-label { color: var(--muted); }
.kpi-value { color: #0b1f33; }
.kpi-sub { color: var(--muted); }
.kpi-sub strong { color: #33475b; }

.panel {
    background: linear-gradient(155deg, #ffffff, #f7fafd);
    box-shadow: var(--shadow-soft);
}
.panel-title { color: #102a43; }
.panel-sub { color: var(--muted); }
.panel-icon { background: rgba(8, 145, 178, .08); border-color: rgba(8, 145, 178, .16); }
.glass-card {
    background: linear-gradient(155deg, #ffffff, #f6fafd);
    box-shadow: var(--shadow-soft);
}
.glass-card h4 { color: #102a43; }
.glass-card p { color: #3c5268; }

.status-normal { color: #047857; border-color: rgba(5, 150, 105, .32); background: rgba(5, 150, 105, .10); }
.status-warning { color: #a16207; border-color: rgba(180, 83, 9, .32); background: rgba(180, 83, 9, .10); }
.status-elevated { color: #c2410c; border-color: rgba(194, 65, 12, .32); background: rgba(194, 65, 12, .10); }
.status-critical { color: #b91c1c; border-color: rgba(220, 38, 38, .34); background: rgba(220, 38, 38, .10); }
.status-idle { color: #475569; border-color: rgba(71, 85, 105, .26); background: rgba(71, 85, 105, .08); }
.status-info { color: #0369a1; border-color: rgba(3, 105, 161, .3); background: rgba(3, 105, 161, .09); }

.chip {
    border-color: rgba(15, 42, 74, .16);
    color: #33475b;
    background: rgba(15, 42, 74, .04);
}
.chip:hover {
    border-color: rgba(8, 145, 178, .38);
    color: #0e7490;
    background: rgba(8, 145, 178, .07);
}
.chip--accent {
    border-color: rgba(8, 145, 178, .32);
    color: #0e7490;
    background: rgba(8, 145, 178, .08);
}

.bar-item .bar-head strong { color: #1e3a52; }
.bar-track { background: rgba(15, 42, 74, .10); }

.alert-item {
    background: #ffffff;
    border-color: rgba(15, 42, 74, .12);
}
.alert-item:hover {
    border-color: rgba(8, 145, 178, .26);
    background: #f5f9fd;
}
.alert-title { color: #1e3a52; }
.alert-meta { color: var(--muted); }
.alert-value { color: #0b1f33; }

.signal-card {
    border-color: rgba(180, 83, 9, .22);
    background: linear-gradient(150deg, rgba(180, 83, 9, .06), #ffffff);
}
.signal-card.critical {
    border-color: rgba(220, 38, 38, .24);
    background: linear-gradient(150deg, rgba(220, 38, 38, .06), #ffffff);
}
.signal-card.info {
    border-color: rgba(5, 150, 105, .22);
    background: linear-gradient(150deg, rgba(5, 150, 105, .05), #ffffff);
}
.signal-title { color: #102a43; }
.signal-detail { color: var(--muted); }
.signal-action { color: #33475b; }

.rec-card { background: #ffffff; border-color: rgba(15, 42, 74, .12); }
.rec-card p { color: #33475b; }

.profile-card {
    border-color: rgba(8, 145, 178, .22);
    background:
        radial-gradient(420px 260px at 100% 0%, rgba(8, 145, 178, .12), transparent 65%),
        linear-gradient(155deg, #ffffff, #f5f9fd);
    box-shadow: var(--shadow);
}
.profile-name { color: #0b1f33; }
.profile-edu { color: var(--muted); }
.profile-bio { color: #33475b; }
.social-btn {
    color: #0e7490 !important;
    background: rgba(8, 145, 178, .07);
    border-color: rgba(8, 145, 178, .30);
}
.social-btn:hover {
    background: rgba(8, 145, 178, .13);
    box-shadow: 0 10px 26px rgba(8, 145, 178, .12);
}
.social-btn.linkedin {
    border-color: rgba(37, 99, 235, .32);
    color: #1d4ed8 !important;
    background: rgba(37, 99, 235, .08);
}
.social-btn.linkedin:hover { background: rgba(37, 99, 235, .14); }

.codev-card {
    background: linear-gradient(150deg, #ffffff, #f5f9fd);
    border-color: rgba(15, 42, 74, .12);
    box-shadow: var(--shadow-soft);
}
.codev-card:hover {
    border-color: rgba(8, 145, 178, .30);
    box-shadow: 0 14px 32px rgba(15, 42, 74, .10), 0 0 22px rgba(8, 145, 178, .05);
}
.codev-name { color: #102a43; }
.codev-role { color: var(--muted); }
.codev-link {
    border-color: rgba(37, 99, 235, .30);
    color: #1d4ed8 !important;
    background: rgba(37, 99, 235, .08);
}
.codev-link:hover {
    background: rgba(37, 99, 235, .16);
    box-shadow: 0 8px 20px rgba(37, 99, 235, .15);
}

.pipeline-step { background: #ffffff; border-color: rgba(15, 42, 74, .12); }
.pipeline-step .step-title { color: #1e3a52; }
.pipeline-step .step-desc { color: var(--muted); }

.app-footer { border-top-color: rgba(15, 42, 74, .12); color: var(--muted); }
.footer-brand { color: #1e3a52; }
.footer-credit a, .footer-links a { color: #0e7490 !important; }
.footer-links .sep { color: rgba(15, 42, 74, .3); }

[data-testid="stForm"] {
    background: linear-gradient(155deg, #ffffff, #f7fafd);
    box-shadow: var(--shadow-soft);
}
[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: linear-gradient(155deg, #ffffff, #f7fafd) !important;
    border-color: rgba(15, 42, 74, .12) !important;
    box-shadow: var(--shadow-soft);
}
div[data-testid="stMetric"] {
    background: linear-gradient(155deg, #ffffff, #f6fafd);
    border-color: rgba(15, 42, 74, .12);
    box-shadow: var(--shadow-soft);
}
div[data-testid="stMetricLabel"] p { color: var(--muted) !important; }
div[data-testid="stMetricValue"] { color: #0b1f33 !important; }
div[data-testid="stMetricDelta"] { color: var(--cyan) !important; }
[data-testid="stTabs"] [data-baseweb="tab-list"] { border-bottom-color: rgba(15, 42, 74, .12); }
[data-testid="stTabs"] button[data-baseweb="tab"] { color: var(--muted); }
[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] { color: #0e7490; }
[data-testid="stTabs"] [data-baseweb="tab-border"] { background: rgba(15, 42, 74, .12); }

.stButton > button,
[data-testid="stFormSubmitButton"] > button,
[data-testid="stDownloadButton"] > button {
    border-color: rgba(8, 145, 178, .32);
    color: #0e7490;
    background: rgba(8, 145, 178, .07);
}
.stButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover,
[data-testid="stDownloadButton"] > button:hover {
    background: rgba(8, 145, 178, .13);
    border-color: rgba(8, 145, 178, .48);
    box-shadow: 0 10px 24px rgba(8, 145, 178, .10);
}
.stButton > button[kind="primary"],
[data-testid="stFormSubmitButton"] > button[kind="primary"],
[data-testid="stDownloadButton"] > button[kind="primary"] {
    color: #ffffff;
    background: linear-gradient(100deg, #0891b2 0%, #0e7490 52%, #2563eb 100%);
    box-shadow: 0 12px 30px rgba(8, 145, 178, .22);
}
.stButton > button[kind="primary"]:hover,
[data-testid="stFormSubmitButton"] > button[kind="primary"]:hover {
    box-shadow: 0 16px 36px rgba(8, 145, 178, .28);
}

[data-baseweb="input"],
[data-baseweb="select"] > div,
[data-testid="stNumberInputContainer"],
[data-testid="stTextInput"] input,
[data-testid="stDateInput"] input {
    border-color: rgba(15, 42, 74, .18) !important;
    background: #ffffff !important;
    color: #102a43 !important;
}
[data-baseweb="input"]:focus-within,
[data-baseweb="select"] > div:focus-within,
[data-testid="stNumberInputContainer"]:focus-within {
    border-color: rgba(8, 145, 178, .55) !important;
    box-shadow: 0 0 0 3px rgba(8, 145, 178, .10) !important;
}
[data-testid="stNumberInputField"],
[data-testid="stTextInput"] input,
[data-baseweb="select"] input,
[data-baseweb="select"] span {
    color: #102a43 !important;
    background: transparent !important;
}
[data-testid="stNumberInput"] button {
    color: #556b82 !important;
    border-color: rgba(15, 42, 74, .14) !important;
    background: rgba(15, 42, 74, .04) !important;
}
[data-testid="stTextArea"] textarea {
    background: #ffffff !important;
    color: #102a43 !important;
    border-color: rgba(15, 42, 74, .18) !important;
}
[data-testid="stTextArea"] textarea::placeholder {
    color: #7b8da1 !important;
}
[data-testid="stRadio"] label,
[data-testid="stRadio"] p,
[data-testid="stCheckbox"] label,
[data-testid="stCheckbox"] p {
    color: #33475b !important;
}
[data-baseweb="calendar"] {
    background: #ffffff !important;
    color: #102a43 !important;
}
[data-baseweb="calendar"] button {
    color: #102a43 !important;
}
[data-baseweb="popover"] > div,
[data-baseweb="menu"] {
    background: #ffffff !important;
}
[data-baseweb="menu"] li { color: #102a43 !important; }
[data-baseweb="menu"] li:hover { background: rgba(8, 145, 178, .08) !important; }
[data-baseweb="tag"] {
    background: rgba(8, 145, 178, .10) !important;
    color: #0e7490 !important;
}
[role="listbox"], [role="option"] {
    color: #102a43 !important;
    background: #ffffff !important;
}
[role="option"]:hover { background: rgba(8, 145, 178, .08) !important; }

[data-testid="stAlertContainer"] {
    background: #ffffff !important;
    color: #102a43 !important;
    border: 1px solid rgba(15, 42, 74, .12) !important;
    box-shadow: var(--shadow-soft);
}
[data-testid="stAlertContentInfo"] { background: rgba(3, 105, 161, .08) !important; color: #075985 !important; }
[data-testid="stAlertContentSuccess"] { background: rgba(5, 150, 105, .09) !important; color: #047857 !important; }
[data-testid="stAlertContentWarning"] { background: rgba(180, 83, 9, .10) !important; color: #92400e !important; }
[data-testid="stAlertContentError"] { background: rgba(220, 38, 38, .08) !important; color: #b91c1c !important; }
[data-testid^="stAlertContent"] p,
[data-testid^="stAlertContent"] li,
[data-testid^="stAlertContent"] strong,
[data-testid^="stAlertContent"] code {
    color: inherit !important;
}
[data-testid="stAlertContainer"] a { color: inherit !important; }
[data-testid="stAlert"] {
    border-radius: 13px;
    border-color: rgba(15, 42, 74, .12);
    background: #ffffff;
}
[data-testid="stAlert"] p { color: #102a43 !important; }

[data-testid="stExpander"] {
    background: rgba(255, 255, 255, .8) !important;
    border-color: rgba(15, 42, 74, .12) !important;
}
[data-testid="stExpander"] summary { color: #33475b !important; }
[data-testid="stExpander"] summary svg { color: #556b82 !important; fill: #556b82 !important; }
[data-testid="stDataFrame"] {
    background: rgba(255, 255, 255, .8);
    border-color: rgba(15, 42, 74, .12);
}
[data-testid="stDataFrame"],
[data-testid="stDataFrame"] * {
    --gdg-bg-cell: #ffffff !important;
    --gdg-bg-cell-medium: #f6fafd !important;
    --gdg-bg-header: #eef4fb !important;
    --gdg-bg-header-has-focus: #e2eef8 !important;
    --gdg-bg-header-hovered: #e8f1f9 !important;
    --gdg-bg-bubble: #ffffff !important;
    --gdg-bg-bubble-selected: #e6f4f8 !important;
    --gdg-bg-search-result: #fff7d6 !important;
    --gdg-text-dark: #102a43 !important;
    --gdg-text-medium: #33475b !important;
    --gdg-text-light: #556b82 !important;
    --gdg-text-bubble: #102a43 !important;
    --gdg-text-header: #102a43 !important;
    --gdg-text-header-selected: #0e7490 !important;
    --gdg-text-group-header: #102a43 !important;
    --gdg-border-color: rgba(15, 42, 74, .12) !important;
    --gdg-horizontal-border-color: rgba(15, 42, 74, .10) !important;
    --gdg-accent-color: #0891b2 !important;
    --gdg-accent-fg: #ffffff !important;
    --gdg-accent-light: rgba(8, 145, 178, .10) !important;
    --gdg-link-color: #0e7490 !important;
}
[data-testid="stCode"] {
    background: #f2f7fb;
    border-color: rgba(15, 42, 74, .12);
}
code {
    color: #0e7490;
    background: rgba(8, 145, 178, .08);
}
[data-testid="stImage"] img { border-color: rgba(15, 42, 74, .12); }
[data-testid="stToolbar"] button,
[data-testid="stMainMenu"] button {
    color: #364b61 !important;
}
[data-testid="stToolbar"] button svg,
[data-testid="stMainMenu"] button svg {
    fill: #364b61 !important;
}
</style>
"""

_LIGHT_MODE = False


def is_light_mode() -> bool:
    """Indique si le mode clair est actif pour la session courante."""
    try:
        import streamlit as st

        return bool(st.session_state.get("light_mode", _LIGHT_MODE))
    except Exception:
        return _LIGHT_MODE


def inject_theme(light: bool = False) -> None:
    """Injecte le CSS global (à appeler une fois par run)."""
    import streamlit as st

    global _LIGHT_MODE
    _LIGHT_MODE = light
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    if light:
        st.markdown(LIGHT_CSS, unsafe_allow_html=True)


def register_plotly_theme(light: bool = False) -> None:
    """Enregistre le template Plotly partagé (sombre ou clair)."""
    global _LIGHT_MODE
    _LIGHT_MODE = light

    if light:
        font_color = "#33475b"
        title_color = "#0b1f33"
        grid_color = "rgba(15,42,74,.10)"
        zero_color = "rgba(15,42,74,.12)"
        line_color = "rgba(15,42,74,.18)"
        tick_color = "#4b6076"
        axis_title_color = "#556b82"
        hover_bg = "#ffffff"
        hover_border = "rgba(8,145,178,.35)"
        hover_font = "#102a43"
        colorway = LIGHT_COLORWAY
    else:
        font_color = "#a9bbd1"
        title_color = "#e7eef9"
        grid_color = "rgba(148,163,184,.10)"
        zero_color = "rgba(148,163,184,.12)"
        line_color = "rgba(148,163,184,.18)"
        tick_color = "#7f93ab"
        axis_title_color = "#8da2bb"
        hover_bg = "#0b1424"
        hover_border = "rgba(34,211,238,.35)"
        hover_font = "#e7eef9"
        colorway = COLORWAY

    layout = go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter, Segoe UI, system-ui, sans-serif",
            size=12,
            color=font_color,
        ),
        colorway=colorway,
        title=dict(font=dict(size=15, color=title_color), x=0, xanchor="left"),
        xaxis=dict(
            gridcolor=grid_color,
            zerolinecolor=zero_color,
            linecolor=line_color,
            tickfont=dict(size=10, color=tick_color),
            title=dict(font=dict(size=11, color=axis_title_color)),
            automargin=True,
        ),
        yaxis=dict(
            gridcolor=grid_color,
            zerolinecolor=zero_color,
            linecolor=line_color,
            tickfont=dict(size=10, color=tick_color),
            title=dict(font=dict(size=11, color=axis_title_color)),
            automargin=True,
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(0,0,0,0)",
            font=dict(size=11, color=font_color),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        margin=dict(l=12, r=12, t=54, b=12),
        hoverlabel=dict(
            bgcolor=hover_bg,
            bordercolor=hover_border,
            font=dict(color=hover_font, size=12),
        ),
        polar=dict(bgcolor="rgba(0,0,0,0)"),
    )
    pio.templates["cnc_sentinel"] = go.layout.Template(layout=layout)
    pio.templates.default = "cnc_sentinel"


def format_fr(value: float, digits: int = 2) -> str:
    """Formate un nombre à la française : 1 234,56."""
    return f"{value:,.{digits}f}".replace(",", " ").replace(".", ",")


def format_pct(value: float, digits: int = 1, already_pct: bool = False) -> str:
    pct = value if already_pct else value * 100
    return f"{pct:.{digits}f} %".replace(".", ",")


def tone_for_level(level: str) -> str:
    return {
        "NORMAL": "green",
        "MODÉRÉ": "amber",
        "ÉLEVÉ": "orange",
        "CRITIQUE": "red",
        "En attente": "slate",
    }.get(level, "cyan")


def status_class(level: str) -> str:
    return {
        "NORMAL": "status-normal",
        "MODÉRÉ": "status-warning",
        "ÉLEVÉ": "status-elevated",
        "CRITIQUE": "status-critical",
        "En attente": "status-idle",
    }.get(level, "status-info")


def style_figure(fig: go.Figure, *, height: int = 320, title: str | None = None) -> go.Figure:
    """Applique le template et une hauteur cohérente à une figure."""
    fig.update_layout(template="cnc_sentinel", height=height)
    if title:
        fig.update_layout(title=dict(text=title))
    return fig
