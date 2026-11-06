# Guide de démonstration — CNC Sentinel

Durée estimée : **10 minutes**. Aucune installation Python nécessaire si la démo en
ligne est accessible ; sinon, suivre le README (installation locale).

## Avant de commencer

- Ouvrir l'application (lien en ligne fournis par les auteurs, ou `python -m streamlit run app/streamlit_app.py` en local).
- **Mode démonstration** : si aucune clé Gemini n'est configurée, la carte *DEMO MODE*
  apparaît dans la sidebar. C'est normal : la probabilité XGBoost, les causes et la
  recherche RAG fonctionnent ; seul le texte rédigé par Gemini est remplacé par les
  extraits de la base de connaissances.

## Étape 1 — Overview (1 min)

1. Lire le titre et les chips : 10 000 observations, XGBoost seuil 0,111, AI4I 2020.
2. Observer les KPI : à la première ouverture (aucun diagnostic lancé), l'en-tête indique
   *Aucune machine enregistrée* — normal, les machines apparaissent après un diagnostic.
3. Descendre : *Répartition des défaillances* (modes réels du dataset) et *Dernières
   alertes* (initialement vide).

## Étape 2 — AI Prediction : diagnostic normal (2 min)

1. Menu gauche → **AI Prediction**.
2. Laisser le preset *Médianes du dataset* (26,95 °C / 36,95 °C / 1503 tr/min / 40,1 Nm /
   108 min) et cliquer **RUN AI DIAGNOSTIC**.
3. Vérifier : jauge de probabilité ≈ 0,1 %, décision **NORMAL**, *Aucun seuil documenté
   franchi*, graphique *Importance des variables* (`rpm_torque_ratio` en tête).
4. Message de confirmation : *Diagnostic enregistré dans l'historique local.*

## Étape 3 — AI Prediction : cas de panne (2 min)

1. Changer le preset en **Panne usure outil (TWF)** puis en **Panne dissipation
   thermique (HDF)** : les champs se remplissent avec une observation réelle du dataset.
2. Relancer **RUN AI DIAGNOSTIC** à chaque fois.
3. Vérifier : probabilité élevée, *Causes possibles* → TWF (usure ≥ 180 min) ou HDF
   (`temp_diff` < 8,6 °C), cartes *Décision*, *Écart thermique*, *Puissance*.

## Étape 4 — Recommandation RAG (2 min)

1. Après un diagnostic, cliquer **Générer la recommandation IA (RAG)**.
   Le premier appel charge les embeddings (~30–60 s la première fois).
2. **Sans clé API (mode démo)** : vérifier l'encadré *Mode démonstration — génération
   Gemini désactivée*, le niveau de risque, l'action immédiate et les **extraits
   réellement retrouvés** dans la base de connaissances.
3. **Avec clé** : vérifier les trois cartes *Analyse / Action immédiate / Prévention*
   et le type de panne probable.

## Étape 5 — Diagnostics et Maintenance History (1 min)

1. **Diagnostics** : la liste contient les diagnostics lancés aux étapes 2–3
   (filtres par machine/niveau, export CSV disponible).
2. **Maintenance History** : ajouter une intervention de test
   (ex. *Remplacement outil*, machine *CNC-01*) — elle apparaît immédiatement
   et est exportable. *Penser à la supprimer ou l'effacer après la démo.*
3. **Overview** : les KPI et alertes reflètent maintenant les diagnostics lancés.

## Étape 6 — Analytics (1 min)

1. Onglets : *Dataset* (distribution des types L/M/H, corrélations capteurs-pannes).
2. *Modèle* : courbes ROC (AUC **0,9853**), PR (AUC **0,8752**), matrice de confusion au
   seuil 0,111 (TN 1859 / FP 73 / FN 8 / TP 60) et tableau précision/rappel par seuil.

## Étape 7 — Reliability (1 min)

1. Lire : R(1 h) **96,61 %**, MTBF **29,50 h**, disponibilité **88,06 %**, taux de panne 3,39 %.
2. Onglets : *Fiabilité R(t)* (Kaplan-Meier), *Modes de défaillance* (HDF prioritaire, 115),
   *Maintenance & coûts* (run-to-failure + surveillance conditionnelle), *Méthode & limites*.
3. Télécharger le **rapport HTML** complet si besoin.

## Étape 8 — About & profils (1 min)

1. **About** : pipeline en 5 étapes, provenance des données (AI4I 2020, UCI), limites
   assumées (données synthétiques, binaire, fuite scaler, dépendance Gemini) et
   **carte des deux auteurs**.
2. **Developer Profile** : biographies, LinkedIn et portfolio cliquables.

## Bonus — Thème clair

Sidebar → bascule **☀️ Light mode** : toute l'interface (dont jauges et graphiques Plotly)
s'adapte au thème clair. Rebasculer pour revenir au thème sombre.

## Points d'attention pendant la démonstration

- **Aucune télémétrie temps réel** : les vues reflètent les diagnostics lancés pendant
  la démo, pas une flotte connectée (c'est documenté dans About).
- **Le score est réel** : chaque diagnostic est journalisé localement ; l'export CSV
  permet de le vérifier.
- **Mode démo assumé** : sans clé, aucun texte n'est inventé — les extraits RAG sont
  affichés tels quels, identifiés comme tels.
