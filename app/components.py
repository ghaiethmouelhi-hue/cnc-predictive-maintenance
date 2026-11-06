# -*- coding: utf-8 -*-
"""Composants HTML réutilisables — CNC Sentinel.

Les composants renvoient du HTML injecté via ``st.markdown``. Ils partagent
les classes CSS définies dans :mod:`app.theme`.
"""

from __future__ import annotations

import html
from typing import Iterable, Sequence

import streamlit as st

from app.theme import COLORS, status_class, tone_for_level

LINKEDIN_URL = "https://www.linkedin.com/in/ghaith-mouelhi-a5b668278/"
PORTFOLIO_URL = "https://ghaieth-mouelhi.netlify.app/"
CHADI_LINKEDIN_URL = "https://www.linkedin.com/in/chadi-ammar/"

_FILLED_ICONS = {"linkedin"}

_ICON_PATHS = {
    "dashboard": '<rect x="3" y="3" width="7" height="9" rx="1.6"/><rect x="14" y="3" width="7" height="5" rx="1.6"/><rect x="14" y="12" width="7" height="9" rx="1.6"/><rect x="3" y="16" width="7" height="5" rx="1.6"/>',
    "monitoring": '<path d="M3 12h4l2.5-7 5 14 2.5-7H21"/>',
    "brain": '<path d="M9.5 4.5A3 3 0 0 0 6.5 7.5a3 3 0 0 0-1.4 5.6A3 3 0 0 0 8 18.5a3 3 0 0 0 5.5.9V4.5a3 3 0 0 0-4 0Z"/><path d="M14.5 4.5a3 3 0 0 1 3 3 3 3 0 0 1 1.4 5.6 3 3 0 0 1-2.9 5.4 3 3 0 0 1-5.5.9"/>',
    "checklist": '<path d="M9 6h11M9 12h11M9 18h11"/><path d="m3.5 6 1.2 1.2L7 4.8"/><path d="m3.5 12 1.2 1.2L7 10.8"/><path d="m3.5 18 1.2 1.2L7 16.8"/>',
    "history": '<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l3 2"/>',
    "analytics": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    "shield": '<path d="M12 3 4.5 6v5.5c0 4.4 3.2 7.8 7.5 9.5 4.3-1.7 7.5-5.1 7.5-9.5V6L12 3Z"/><path d="m9 12 2 2 4-4"/>',
    "user": '<circle cx="12" cy="8" r="3.5"/><path d="M4.5 20a7.5 7.5 0 0 1 15 0"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5"/><path d="M12 8h.01"/>',
    "alert": '<path d="M10.3 3.9 2.6 17a2 2 0 0 0 1.7 3h15.4a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    "critical": '<path d="M8 3h8l5 5v8l-5 5H8l-5-5V8l5-5Z"/><path d="M12 8v5"/><path d="M12 16h.01"/>',
    "check": '<circle cx="12" cy="12" r="9"/><path d="m8 12 2.5 2.5L16 9"/>',
    "activity": '<path d="M3 12h4l2-5 4 10 2-5h6"/>',
    "gauge": '<path d="M4 18a8 8 0 1 1 16 0"/><path d="M12 14 16 9"/><circle cx="12" cy="18" r="1"/>',
    "thermometer": '<path d="M14 14.8V5a2 2 0 1 0-4 0v9.8a4 4 0 1 0 4 0Z"/><path d="M12 9v6"/>',
    "rotate": '<path d="M21 12a9 9 0 1 1-3-6.7"/><path d="M21 3v6h-6"/>',
    "wrench": '<path d="M14.7 6.3a4.5 4.5 0 0 0 6 6L21 21l-3 .5-8.7-8.7a4.5 4.5 0 0 0-5.6-5.6l3 3-2.5 2.5-3-3a4.5 4.5 0 0 0 5.6 5.6L6 19.5 3 19l-.5-3L12 7.3Z"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "database": '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v6c0 1.7 3.6 3 8 3s8-1.3 8-3V5"/><path d="M4 11v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/>',
    "sparkles": '<path d="M12 3 13.8 8.2 19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3Z"/><path d="M19 15v4M17 17h4M5 3v3M3.5 4.5h3"/>',
    "external": '<path d="M14 4h6v6"/><path d="m20 4-9 9"/><path d="M20 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1h5"/>',
    "download": '<path d="M12 3v11"/><path d="m7 10 5 5 5-5"/><path d="M4 20h16"/>',
    "filter": '<path d="M3 5h18l-7 8v6l-4 2v-8L3 5Z"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "refresh": '<path d="M21 12a9 9 0 0 1-15.5 6.2L3 16"/><path d="M3 21v-5h5"/><path d="M3 12a9 9 0 0 1 15.5-6.2L21 8"/><path d="M21 3v5h-5"/>',
    "terminal": '<path d="m5 7 4 4-4 4"/><path d="M12 17h7"/>',
    "layers": '<path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="m3 13 9 5 9-5"/><path d="m3 18 9 5 9-5"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    "zap": '<path d="M13 2 4 14h7l-1 8 10-13h-7l1-7Z"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 11h18"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    "clipboard": '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4V3h6v1"/><path d="M9 10h6M9 14h6M9 18h4"/>',
    "git": '<circle cx="6" cy="6" r="2.5"/><circle cx="18" cy="18" r="2.5"/><circle cx="18" cy="6" r="2.5"/><path d="M8.5 6H15.5M18 8.5v7M6 8.5V15a3 3 0 0 0 3 3h6.5"/>',
    "linkedin": '<path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5ZM3 9h4v12H3V9Zm6 0h3.8v1.7h.05c.53-.95 1.83-1.95 3.77-1.95 4.03 0 4.78 2.5 4.78 5.75V21h-4v-5.6c0-1.34-.03-3.06-1.9-3.06-1.9 0-2.2 1.45-2.2 2.96V21H9V9Z"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3c2.7 2.6 2.7 15.4 0 18"/><path d="M12 3c-2.7 2.6-2.7 15.4 0 18"/>',
    "arrow": '<path d="M7 17 17 7"/><path d="M8 7h9v9"/>',
    "server": '<rect x="3" y="4" width="18" height="6" rx="2"/><rect x="3" y="14" width="18" height="6" rx="2"/><path d="M7 7h.01M7 17h.01"/>',
    "cpu": '<rect x="7" y="7" width="10" height="10" rx="2"/><path d="M9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3"/>',
    "file": '<path d="M6 3h8l4 4v14H6V3Z"/><path d="M14 3v5h5"/><path d="M9 13h6M9 17h6"/>',
    "pie": '<path d="M12 3a9 9 0 1 0 9 9h-9V3Z"/><path d="M15 3.5A9 9 0 0 1 20.5 9H15V3.5Z"/>',
    "grid": '<rect x="3" y="3" width="8" height="8" rx="1.5"/><rect x="13" y="3" width="8" height="8" rx="1.5"/><rect x="3" y="13" width="8" height="8" rx="1.5"/><rect x="13" y="13" width="8" height="8" rx="1.5"/>',
}


def icon(name: str, size: int = 17, color: str = "currentColor") -> str:
    """Retourne une icône SVG inline."""
    paths = _ICON_PATHS.get(name, _ICON_PATHS["info"])
    if name in _FILLED_ICONS:
        return (
            f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" '
            f'fill="{color}" aria-hidden="true">{paths}</svg>'
        )
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="1.8" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true">{paths}</svg>'
    )


def _esc(text: object) -> str:
    return html.escape(str(text), quote=True)


def hero(
    eyebrow: str,
    title: str,
    subtitle: str,
    *,
    accent: str = "cyan",
    chips: Sequence[str] | None = None,
) -> None:
    """Bandeau d'accroche propre à chaque page."""
    chips_html = ""
    if chips:
        chips_html = "".join(
            f'<span class="hero-chip">{_esc(chip)}</span>' for chip in chips
        )
    st.markdown(
        f'<section class="hero hero--{_esc(accent)}">'
        f'<div class="hero-copy">'
        f'<div class="hero-eyebrow"><span class="dot"></span>{_esc(eyebrow)}</div>'
        f"<h1>{_esc(title)}</h1>"
        f"<p>{_esc(subtitle)}</p>"
        f"</div>"
        f'<div class="hero-meta">{chips_html}</div>'
        f"</section>",
        unsafe_allow_html=True,
    )


def section_label(text: str) -> None:
    st.markdown(
        f'<p class="section-eyebrow">{_esc(text)}</p>',
        unsafe_allow_html=True,
    )


def kpi_grid(cards: Sequence[dict]) -> None:
    """Affiche une grille de cartes KPI.

    Chaque carte accepte : label, value, sub, tone, icon.
    """
    items = []
    for index, card in enumerate(cards):
        tone = card.get("tone", "cyan")
        icon_name = card.get("icon", "activity")
        items.append(
            f'<article class="kpi-card tone-{_esc(tone)}" '
            f'style="animation-delay:{index * 0.045:.3f}s">'
            f'<div class="kpi-top">'
            f'<span class="kpi-icon">{icon(icon_name, 15)}</span>'
            f'<span class="kpi-label">{_esc(card.get("label", ""))}</span>'
            f"</div>"
            f'<div class="kpi-value">{_esc(card.get("value", "—"))}</div>'
            f'<div class="kpi-sub">{card.get("sub", "")}</div>'
            f"</article>"
        )
    st.markdown(
        '<div class="kpi-grid">' + "".join(items) + "</div>",
        unsafe_allow_html=True,
    )


def status_pill(level: str, label: str | None = None) -> str:
    text = label if label is not None else level
    return (
        f'<span class="status-pill {status_class(level)}">'
        f'<span class="dot"></span>{_esc(text)}</span>'
    )


def chip_row(items: Iterable[str], accent_first: bool = False) -> None:
    chips = []
    for index, item in enumerate(items):
        klass = "chip chip--accent" if accent_first and index == 0 else "chip"
        chips.append(f'<span class="{klass}">{_esc(item)}</span>')
    st.markdown(
        '<div class="chip-row">' + "".join(chips) + "</div>",
        unsafe_allow_html=True,
    )


def panel_header(title: str, subtitle: str = "", icon_name: str = "grid") -> None:
    st.markdown(
        f'<div class="panel-head">'
        f"<div>"
        f'<p class="panel-title">{_esc(title)}</p>'
        f'<p class="panel-sub">{subtitle}</p>'
        f"</div>"
        f'<span class="panel-icon">{icon(icon_name, 16)}</span>'
        f"</div>",
        unsafe_allow_html=True,
    )


def bar_list(items: Sequence[tuple]) -> None:
    """Barres de progression.

    Chaque item : (label, valeur affichée, pourcentage 0-100, tone).
    """
    rows = []
    for item in items:
        label, value, pct, tone = item
        safe_pct = max(0.0, min(100.0, float(pct)))
        rows.append(
            f'<div class="bar-item">'
            f'<div class="bar-head"><span>{_esc(label)}</span>'
            f"<strong>{_esc(value)}</strong></div>"
            f'<div class="bar-track">'
            f'<div class="bar-fill tone-{_esc(tone)}" style="width:{safe_pct:.1f}%"></div>'
            f"</div></div>"
        )
    st.markdown('<div class="bar-list">' + "".join(rows) + "</div>", unsafe_allow_html=True)


def alert_list(alerts: Sequence[dict], empty_message: str = "Aucune alerte enregistrée.") -> None:
    if not alerts:
        empty_state("check", "Aucune alerte", empty_message, tone="green")
        return
    rows = []
    for alert in alerts:
        tone = alert.get("tone", "cyan")
        rows.append(
            f'<div class="alert-item">'
            f'<span class="alert-dot" style="--tone: var(--{tone})"></span>'
            f'<div class="alert-main">'
            f'<div class="alert-title">{_esc(alert.get("title", ""))}</div>'
            f'<div class="alert-meta">{_esc(alert.get("meta", ""))}</div>'
            f"</div>"
            f'<div class="alert-value">{_esc(alert.get("value", ""))}</div>'
            f"</div>"
        )
    st.markdown('<div class="alert-list">' + "".join(rows) + "</div>", unsafe_allow_html=True)


def signal_cards(signals: Sequence[dict]) -> None:
    if not signals:
        empty_state(
            "check",
            "Aucun seuil déclenché",
            "Les mesures ne franchissent aucun des seuils de surveillance du dataset.",
            tone="green",
        )
        return
    cards = []
    for signal in signals:
        severity = signal.get("severity", "warning")
        css = "critical" if severity == "critical" else ("info" if severity == "info" else "")
        icon_name = "critical" if severity == "critical" else ("check" if severity == "info" else "alert")
        cards.append(
            f'<div class="signal-card {css}">'
            f'<span class="signal-icon">{icon(icon_name, 15)}</span>'
            f"<div>"
            f'<div class="signal-title">{_esc(signal.get("title", ""))}</div>'
            f'<div class="signal-detail">{_esc(signal.get("detail", ""))}</div>'
            f'<div class="signal-action">{_esc(signal.get("action", ""))}</div>'
            f"</div></div>"
        )
    st.markdown("".join(cards), unsafe_allow_html=True)


def recommendation_cards(explication: str, immediate: str, preventive: str) -> None:
    st.markdown(
        '<div class="rec-grid">'
        f'<div class="rec-card"><h5>Analyse</h5><p>{_esc(explication)}</p></div>'
        f'<div class="rec-card"><h5>Action immédiate</h5><p>{_esc(immediate)}</p></div>'
        f'<div class="rec-card"><h5>Prévention</h5><p>{_esc(preventive)}</p></div>'
        "</div>",
        unsafe_allow_html=True,
    )


def empty_state(icon_name: str, title: str, message: str, tone: str = "cyan") -> None:
    st.markdown(
        f'<div class="glass-card tone-{_esc(tone)}" style="text-align:center;padding:1.5rem 1.2rem">'
        f'<div style="display:inline-grid;place-items:center;width:44px;height:44px;'
        f'border-radius:13px;margin-bottom:.55rem;color:var(--{_esc(tone)});'
        f'background:rgba(34,211,238,.07);border:1px solid rgba(34,211,238,.16)">'
        f"{icon(icon_name, 20)}</div>"
        f'<h4>{_esc(title)}</h4>'
        f'<p style="max-width:520px;margin:0 auto">{_esc(message)}</p>'
        f"</div>",
        unsafe_allow_html=True,
    )


def pipeline(steps: Sequence[tuple[str, str, str]]) -> None:
    items = []
    for index, (title, desc, icon_name) in enumerate(steps):
        items.append(
            f'<div class="pipeline-step">'
            f'<div class="step-index">0{index + 1} · {icon(icon_name, 13)}</div>'
            f'<div class="step-title">{_esc(title)}</div>'
            f'<div class="step-desc">{_esc(desc)}</div>'
            f"</div>"
        )
    st.markdown('<div class="pipeline">' + "".join(items) + "</div>", unsafe_allow_html=True)


def social_buttons() -> None:
    st.markdown(
        f'<div class="social-row">'
        f'<a class="social-btn linkedin" href="{LINKEDIN_URL}" target="_blank" '
        f'rel="noopener noreferrer">{icon("linkedin", 16)} CONNECT WITH ME</a>'
        f'<a class="social-btn" href="{PORTFOLIO_URL}" target="_blank" '
        f'rel="noopener noreferrer">{icon("globe", 16)} VISIT MY PORTFOLIO</a>'
        f"</div>",
        unsafe_allow_html=True,
    )


def profile_card(
    *,
    name: str,
    role: str,
    education: str,
    bio: str,
    photo_url: str | None = None,
    initials: str = "GM",
) -> None:
    if photo_url:
        photo = f'<div class="profile-photo"><img src="{_esc(photo_url)}" alt="{_esc(name)}"></div>'
    else:
        photo = f'<div class="profile-photo">{_esc(initials)}</div>'
    st.markdown(
        f'<div class="profile-card">'
        f'<div class="profile-head">'
        f"{photo}"
        f"<div>"
        f'<h2 class="profile-name">{_esc(name)}</h2>'
        f'<div class="profile-role">{_esc(role)}</div>'
        f'<div class="profile-edu">{_esc(education)}</div>'
        f"</div></div>"
        f'<p class="profile-bio">{_esc(bio)}</p>'
        f"</div>",
        unsafe_allow_html=True,
    )


def co_developer_card(
    *,
    name: str,
    role: str,
    linkedin_url: str,
    initials: str = "CA",
) -> None:
    """Carte compacte pour un co-développeur, avec lien LinkedIn."""
    st.markdown(
        f'<div class="codev-card">'
        f'<div class="codev-avatar">{_esc(initials)}</div>'
        f'<div class="codev-main">'
        f'<div class="codev-badge">Co-developer</div>'
        f'<div class="codev-name">{_esc(name)}</div>'
        f'<div class="codev-role">{_esc(role)}</div>'
        f"</div>"
        f'<a class="codev-link" href="{_esc(linkedin_url)}" target="_blank" '
        f'rel="noopener noreferrer" aria-label="LinkedIn de {_esc(name)}" '
        f'title="LinkedIn — {_esc(name)}">{icon("linkedin", 16)}</a>'
        f"</div>",
        unsafe_allow_html=True,
    )


def footer() -> None:
    st.markdown(
        f'<footer class="app-footer">'
        f'<div class="footer-brand">CNC <span>SENTINEL</span></div>'
        f'<div class="footer-credit">Developed by '
        f'<a href="{LINKEDIN_URL}" target="_blank" rel="noopener noreferrer">Ghaith Mouelhi</a>'
        f' &amp; '
        f'<a href="{CHADI_LINKEDIN_URL}" target="_blank" rel="noopener noreferrer">Chadi Ammar</a>'
        f" · AI | Industrial Automation | Predictive Maintenance</div>"
        f'<div class="footer-links">'
        f'<a href="{LINKEDIN_URL}" target="_blank" rel="noopener noreferrer">Ghaith · LinkedIn</a>'
        f'<span class="sep">|</span>'
        f'<a href="{PORTFOLIO_URL}" target="_blank" rel="noopener noreferrer">Ghaith · Portfolio</a>'
        f'<span class="sep">|</span>'
        f'<a href="{CHADI_LINKEDIN_URL}" target="_blank" rel="noopener noreferrer">Chadi · LinkedIn</a>'
        f"</div></footer>",
        unsafe_allow_html=True,
    )


def tone_var(tone: str) -> str:
    """Retourne la valeur CSS d'une couleur de la palette."""
    return COLORS.get(tone, COLORS["cyan"])


def level_tone(level: str) -> str:
    return tone_for_level(level)
