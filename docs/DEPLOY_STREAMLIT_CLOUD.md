# Déploiement — Streamlit Community Cloud

Objectif : un professeur ouvre un lien web et utilise l'application sans installer Python.

## Vue d'ensemble

| Élément | État dans le dépôt |
|---|---|
| Point d'entrée | `app/streamlit_app.py` (défini dans les réglages de l'app) |
| Python | `runtime.txt` → `python-3.12` |
| Dépendances | `requirements.txt` (index CPU PyTorch pour les roues Linux) |
| Thème / serveur | `.streamlit/config.toml` (`headless = true`) |
| Modèle + scaler + données | `models/xgboost_model.pkl`, `data/processed/scaler.pkl`, CSVs, `chroma_db/` (versionnés) |
| Clé Gemini | **Secret Streamlit** `GOOGLE_API_KEY` (jamais dans Git) |
| Sans clé | Mode démonstration automatique (RAG retrieve-only) — vérifié |

## Compatibilité vérifiée avant déploiement

- ✅ Chemins relatifs à `Path(__file__)` (aucun chemin absolu Windows) — scripts
  `models/*.py` et `reliability_analysis.py` inclus.
- ✅ Aucun `.env`, aucune clé API, aucun secret dans le dépôt (`.gitignore` couvre `.env`
  et `.streamlit/secrets.toml`).
- ✅ `headless = true` pour l'environnement serveur Linux.
- ✅ Diagnostic XGBoost + mode démonstration RAG testés localement de bout en bout
  (9 pages, 0 exception).
- ⚠️ Premier chargement RAG : téléchargement du modèle d'embeddings (~470 Mo) puis
  chargement de ChromaDB — prévoir ~1–2 minutes la première fois, tentatives normales ensuite.

## Étapes de déploiement (une seule fois)

1. **Pousser le dépôt public sur GitHub** (voir commandes dans le rapport final).
2. Aller sur <https://share.streamlit.io> → **Sign in** → **Create app**.
3. Sélectionner le dépôt, la branche `main`.
4. **Main file path** : `app/streamlit_app.py`.
5. **Advanced settings** → Python 3.12.
6. Dans **Secrets** (ou *App settings → Secrets*), ajouter :

   ```toml
   GOOGLE_API_KEY = "votre_cle_google_ai_studio"
   ```

   (Omettre cette étape = mode démonstration, pleinement fonctionnel.)
7. Cliquer **Deploy** puis attendre la fin de l'installation des dépendances
   (`requirements.txt` inclut l'index CPU PyTorch pour Linux).
8. Ouvrir l'URL générée (`https://<nom>-<hash>.streamlit.app`), vérifier
   *SYSTEM READY* dans la sidebar, lancer un diagnostic (page **AI Prediction**),
   puis cliquer **Générer la recommandation IA (RAG)** (le premier appel peut prendre
   ~1 minute : chargement des embeddings).

## Après le déploiement

- **Partager le lien** avec le professeur (il est public si l'app est publique).
- Mettre à jour le badge/lien « démo » dans le `README.md` et `CITATION.cff`
  (`repository-code`).
- Les journaux de diagnostics écrits dans `data/processed/` sont éphémères sur Cloud
  (réinitialisés à chaque redémarrage) : comportement normal, l'app reste utilisable.

## Dépannage

| Symptôme | Cause probable | Action |
|---|---|---|
| `ModuleNotFoundError` | Dépendance absente | Vérifier `requirements.txt` ; relever l'erreur dans *Manage app → Logs* |
| App longue au démarrage | Embeddings non cachés | Voir *Logs* ; après la 1ʳᵉ exécution, le cache HF est monté sur le disque éphémère |
| RAG « service indisponible » | Quota Gemini ou réseau | Sans clé : mode démo attendu ; avec clé : réessayer dans quelques minutes |
| Fichier manquant (modèle, scaler) | Artefact ignoré par `.gitignore` | Vérifier que `models/xgboost_model.pkl` et `data/processed/scaler.pkl` sont bien dans le dépôt poussé |
| Échec d'installation `~=2.5` | Conflit d'index | L'index CPU PyTorch est en tête de `requirements.txt` (`--extra-index-url`) |
