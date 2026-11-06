# -*- coding: utf-8 -*-
"""Developer Profile — carte premium et présentation du développeur."""

from __future__ import annotations

import base64

import streamlit as st

from app.components import (
    CHADI_LINKEDIN_URL,
    chip_row,
    co_developer_card,
    hero,
    icon,
    profile_card,
    section_label,
    social_buttons,
)
from app.data_access import ROOT_DIR

PHOTO_CANDIDATES = [
    ROOT_DIR / "assets" / "profile.jpg",
    ROOT_DIR / "assets" / "profile.jpeg",
    ROOT_DIR / "assets" / "profile.png",
    ROOT_DIR / "assets" / "profile.webp",
]

BIO = (
    "Electrical and Automation Engineer focused on the intersection of "
    "industrial systems and artificial intelligence. I design predictive "
    "maintenance pipelines that turn raw sensor signals into actionable "
    "decisions: feature engineering, XGBoost risk scoring, reliability "
    "analysis, and retrieval-augmented maintenance guidance. I care about "
    "systems that are measurable, explainable, and safe to operate on a real "
    "shop floor."
)

INTERESTS = [
    "Industrial Automation",
    "Artificial Intelligence",
    "Predictive Maintenance",
    "Embedded Systems & IoT",
    "PLC Programming",
]

STACK = [
    "Python",
    "Streamlit",
    "XGBoost",
    "scikit-learn",
    "Plotly",
    "Pandas",
    "LangChain",
    "Gemini",
    "ChromaDB",
    "Reliability Engineering",
    "PLC / Automation",
    "Embedded & IoT",
]


def _photo_data_uri() -> str | None:
    for path in PHOTO_CANDIDATES:
        if path.exists():
            mime = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".webp": "image/webp",
            }[path.suffix.lower()]
            encoded = base64.b64encode(path.read_bytes()).decode("ascii")
            return f"data:{mime};base64,{encoded}"
    return None


def render() -> None:
    hero(
        "Profile · Co-developers",
        "Ghaith Mouelhi & Chadi Ammar",
        "Electrical & Automation engineers building CNC Sentinel — AI for "
        "industrial reliability. Two complementary profiles, one predictive "
        "maintenance platform.",
        accent="violet",
        chips=["Tunisia", "AI · Automation", "Co-developers"],
    )

    left, right = st.columns([1.35, 1], gap="large")

    with left:
        profile_card(
            name="Ghaith Mouelhi",
            role="Electrical & Automation Engineer",
            education="Génie Électrique et Automatique · Industrial AI & Predictive Maintenance",
            bio=BIO,
            photo_url=_photo_data_uri(),
            initials="GM",
        )
        social_buttons()

        co_developer_card(
            name="Chadi Ammar",
            role="Electrical and Automation Engineering Student",
            linkedin_url=CHADI_LINKEDIN_URL,
            initials="CA",
        )

        section_label("Interests")
        chip_row(INTERESTS, accent_first=True)

        section_label("Stack & tools")
        chip_row(STACK)

    with right:
        section_label("Focus areas")
        focus = [
            (
                "brain",
                "Industrial AI",
                "Supervised learning on sensor data, threshold tuning, and "
                "explainability for maintenance teams.",
            ),
            (
                "shield",
                "Reliability engineering",
                "MTBF, availability, Kaplan-Meier and Weibull reasoning to "
                "choose the right maintenance policy.",
            ),
            (
                "cpu",
                "Automation & embedded",
                "PLC logic, industrial networks and edge acquisition — from "
                "signal to dashboard.",
            ),
        ]
        cards = "".join(
            f'<div class="glass-card" style="margin-bottom:.65rem">'
            f'<div style="display:flex;align-items:center;gap:.55rem;margin-bottom:.35rem;'
            f'color:var(--cyan)">{icon(icon_name, 16)}'
            f'<h4 style="margin:0;color:#eaf4ff">{title}</h4></div>'
            f'<p>{description}</p></div>'
            for icon_name, title, description in focus
        )
        st.markdown(cards, unsafe_allow_html=True)

        section_label("About this build")
        st.markdown(
            f'<div class="panel">'
            f'<p class="panel-sub" style="margin:0">'
            "CNC Sentinel is an end-to-end predictive maintenance workspace: "
            "real AI4I 2020 data, an XGBoost classifier, reliability analysis, "
            "a local diagnostic journal, and a RAG assistant grounded in "
            "maintenance knowledge. The interface is built with Streamlit and "
            "Plotly, with a custom design system. Built by Ghaith Mouelhi and "
            "Chadi Ammar."
            f"</p></div>",
            unsafe_allow_html=True,
        )

        section_label("Contact")
        st.caption(
            "LinkedIn and portfolio links open in a new tab. "
            "Place a photo at assets/profile.jpg to display it on the card."
        )
