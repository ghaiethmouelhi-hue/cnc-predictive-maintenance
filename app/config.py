# -*- coding: utf-8 -*-
"""Configuration des secrets et détection du mode démonstration.

Ordre de résolution :
1. variables d'environnement (``.env`` en local, variables système) ;
2. ``st.secrets`` (Streamlit Community Cloud ou ``.streamlit/secrets.toml``).

Aucune clé n'est jamais écrite dans le code ni dans le dépôt Git.
"""

from __future__ import annotations

import os

_API_KEY_NAMES = ("GOOGLE_API_KEY", "GEMINI_API_KEY")


def get_secret(name: str) -> str | None:
    """Retourne un secret depuis l'environnement puis ``st.secrets``."""
    value = os.getenv(name)
    if value and value.strip():
        return value.strip()

    try:
        import streamlit as st

        if name in st.secrets:
            secret = str(st.secrets[name]).strip()
            return secret or None
    except Exception:
        # Hors contexte Streamlit ou fichier secrets absent : ce n'est pas une erreur.
        pass
    return None


def get_api_key() -> str | None:
    """Clé Google Gemini, quel que soit le nom utilisé."""
    for name in _API_KEY_NAMES:
        value = get_secret(name)
        if value:
            return value
    return None


def is_demo_mode() -> bool:
    """``True`` si aucune clé Gemini n'est disponible.

    Le modèle XGBoost, les seuils métier et la recherche vectorielle restent
    opérationnels ; seule la génération de texte par Gemini est désactivée.
    """
    return get_api_key() is None
