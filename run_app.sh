#!/usr/bin/env bash
# Lancement local sous Linux / macOS.
set -euo pipefail
cd "$(dirname "$0")"
python -m streamlit run app/streamlit_app.py "$@"
