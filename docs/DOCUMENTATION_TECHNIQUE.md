# Documentation technique — CNC Sentinel

Document d'évaluation universitaire : il décrit le fonctionnement global, l'architecture,
le traitement des données, l'entraînement XGBoost, la prédiction, le module RAG,
les résultats obtenus, puis les limites et perspectives.

**Données citées** : toutes les métriques proviennent du modèle sauvegardé
(`models/xgboost_model.pkl`) et du jeu de test réel (split 80/20, `random_state=42`).
Aucun résultat n'est estimé ou inventé.

---

## 1. Fonctionnement global du système

CNC Sentinel répond à une question simple : *une machine CNC donnée va-t-elle tomber
en panne dans l'heure suivante ?* Le système enchaîne six étapes :

```
Mesures capteurs (5)
   → Features physiques dérivées (5)
   → Normalisation (StandardScaler)
   → Score XGBoost (probabilité binaire de panne)
   → Causes possibles (seuils métier TWF / HDF / PWF / OSF)
   → Recommandation d'action (RAG + Gemini, ou mode démo)
```

**Principe de transparence** : aucune donnée simulée. Chaque écran affiche soit une
observation réelle du dataset AI4I 2020, soit la sortie du modèle entraîné, soit un
diagnostic effectivement lancé par l'utilisateur (journalisé dans
`data/processed/diagnostics_log.csv`). En l'absence de clé Gemini, le système bascule en
**mode démonstration** : la recherche vectorielle s'exécute, la génération de texte est
désactivée et l'interface le signale explicitement (carte *DEMO MODE* dans la sidebar,
bandeau dans AI Prediction, encadré dans le résultat). Aucun conseil n'est jamais inventé.

**Pages de l'application** (navigation par groupes) :

| Groupe | Pages | Rôle |
|---|---|---|
| OPERATIONS | Overview, Machine Monitoring, Maintenance History | Supervision du parc et des interventions |
| INTELLIGENCE | AI Prediction, Diagnostics, Analytics, Reliability | Prédiction, journal, métriques, fiabilité |
| PROFILE | Developer Profile, About | Auteurs, architecture, limites |

## 2. Architecture du projet

```
cnc-predictive-maintenance/
├── app/
│   ├── streamlit_app.py      point d'entrée, navigation st.Page, sidebar, pied de page
│   ├── config.py             résolution des secrets (.env → st.secrets), détection mode démo
│   ├── data_access.py        chargement modèle/scaler/données, inférence, métriques, seuils
│   ├── history_store.py      journaux diagnostics / maintenance (CSV locaux)
│   ├── charts.py             graphiques Plotly (jauges, donut, barres)
│   ├── theme.py              design system (thème sombre + surcharge clair)
│   ├── components.py         composants HTML (cartes, pipeline, footer, auteurs)
│   ├── report_view.py        rendu natif du rapport de fiabilité
│   └── pages/                une fonction render() par page (9 pages)
├── rag/
│   ├── agent.py              MaintenanceAgent : LLM Gemini + repli démo + gestion d'erreurs
│   └── vector_store.py       ChromaDB : chargement/construction, embeddings, recherche
├── models/
│   ├── data_loader.py        téléchargement UCI AI4I 2020, nettoyage K→°C
│   ├── feature_engineering.py features + scaler (StandardScaler)
│   ├── train.py              XGBoost
│   └── evaluate.py           ROC / PR / seuils / figures
├── data/
│   ├── raw/ai4i2020.csv      dataset UCI (CC BY 4.0)
│   ├── knowledge/cnc_knowledge.md  base de connaissances RAG
│   └── processed/            CSVs, scaler.pkl, reliability_summary.json,
│                             figures, chroma_db/ (base vectorielle persistée)
├── assets/                   portrait optionnel (profile.jpg, repli initiales "GM")
├── reliability_analysis.py   Kaplan-Meier, lois, MTBF, coût optimal
├── prepare_data.py           conversion K→°C + features (pipeline minimal reproductible)
├── rapport_fiabilite_cnc.html rapport HTML autonome (téléchargeable depuis Reliability)
├── requirements.txt · runtime.txt · run_app.sh · start_app.bat
└── docs/                     documentation, guide de démo, captures, déploiement
```

**Choix d'architecture remarquables**

- **Chemins relatifs robustes** : `data_access.py` et `vector_store.py` utilisent
  `Path(__file__).resolve().parent.parent` comme racine ; les scripts de `models/`
  remontent d'un niveau (`parents[1]`). L'application lance depuis n'importe quel
  répertoire courant — condition nécessaire sous Linux/Streamlit Cloud.
- **Cache Streamlit** : modèle, scaler et jeux de données chargés via
  `@st.cache_resource` / `@st.cache_data` (chargement unique par session serveur).
- **Chargement paresseux du RAG** : le modèle d'embeddings (~470 Mo) n'est instancié
  qu'au premier appel de `build_vector_store()`, jamais au démarrage de l'app.
- **Fallbacks explicites** : fichier de panne absent, ChromaDB absent → reconstruction
  depuis `cnc_knowledge.md` ; service Gemini surchargé (429/503) → modèle de secours
  puis message honnête ; aucune clé → mode démo.

## 3. Traitement des données

1. **Source** : AI4I 2020 (UCI, id 601), synthétique, 10 000 lignes × 14 colonnes,
   339 pannes (3,39 %). Modes : TWF 46, HDF 115, PWF 95, OSF 98, RNF 19.
2. **Nettoyage** (`models/data_loader.py`) : conversion Kelvin → °C, renommage
   canonique (`air_temp_c`, `process_temp_c`, `rpm`, `torque`, `tool_wear_min`,
   `failure`, `machine_type`), contrôle des valeurs aberrantes et des NaN.
3. **Features physiques** (`models/feature_engineering.py`) — voir tableau :

| Feature | Définition | Justification physique |
|---|---|---|
| `temp_diff` | ΔTemp process − air | Seuil HDF du dataset : < 8,6 °C |
| `power` | rpm × torque | Proxy de la puissance (P = C·ω) |
| `wear_rate` | wear / (rpm+1) | Usure normalisée par usage |
| `rpm_torque_ratio` | rpm / (torque+1) | Rapport vitesse/couple (clef du modèle) |
| `wear_temp_stress` | wear × temp_diff | Interaction usure × thermique |

4. **Normalisation** : `StandardScaler` sur les 10 numériques ; type de machine encodé
   en binaire (`type_M`, référence L). Le scaler est sauvegardé (`scaler.pkl`) et réutilisé
   tel quel à l'inférence.
5. **Artefacts versionnés** : `ai4i2020_clean.csv`, `ai4i2020_features.csv`,
   `scaler.pkl`, `reliability_summary.json`, figures — régénérables via `prepare_data.py`,
   `models/*.py` et `reliability_analysis.py`.

> **Limite documentée** : dans le pipeline d'origine, le scaler est ajusté sur
> l'ensemble du dataset *avant* le split train/test — une fuite d'information légère
> (les statistiques du test influencent la normalisation). C'est une limite assumée,
> affichée dans la page About ; une correction consisterait à ajuster le scaler
> uniquement sur le train.

## 4. Entraînement du modèle XGBoost

- **Algorithme** : `XGBClassifier` (gradient boosting d'arbres de décision), probabilité
  binaire de panne.
- **Hyperparamètres** : `n_estimators=100`, `max_depth=6`, `learning_rate=0.1`,
  `scale_pos_weight = n_normal / n_failure` (correction du déséquilibre 96,6 / 3,4),
  `random_state=42`.
- **Protocole** : split train/test 80/20 stratifié sur `failure` → train 8 000 lignes,
  test **2 000 lignes dont 68 pannes**.
- **Features** : 11 (5 capteurs + 5 dérivées + `type_M`).
- **Artefacts** : `models/xgboost_model.pkl` (modèle, avec les noms de features embarqués).

## 5. Méthode de prédiction

À l'exécution, `predict_failure()` applique **exactement les mêmes transformations**
(`compute_features` → `scaler.transform` → colonne `type_M` → `predict_proba`).

- **Seuil de décision : 0,111**, volontairement bas (vs 0,5 par défaut). En maintenance,
  un faux négatif (panne manquée → arrêt non préparé) coûte bien plus cher qu'un faux
  positif (inspection inutile). Au seuil 0,111 : **rappel 0,8824** (8 pannes manquées
  sur 68), précision 0,4511.
- **Niveaux de risque affichés** : NORMAL (< 0,111), MODÉRÉ (0,111–0,5), ÉLEVÉ (0,5–0,75),
  CRITIQUE (≥ 0,75).
- **Causes possibles** — heuristiques de seuils issues du dataset, distinctes de la
  classification XGBoost (qui ne prédit pas la cause) :
  - **TWF** : usure ≥ 180 min (replacement d'outil) ;
  - **HDF** : `temp_diff` < 8,6 °C (refroidissement) ;
  - **PWF** : puissance physique `P = C·ω` hors [3 500 ; 9 000] W ;
  - **OSF** : `usure × couple` > 11 000 min·Nm.
- **Garde-fous** : valeurs hors plage physique = saisie bloquée ; hors plage
  d'entraînement = avertissement affiché. Presets = observations réelles du dataset.

## 6. Fonctionnement du module RAG

1. **Base de connaissances** : `data/knowledge/cnc_knowledge.md` (procédures par mode de panne).
2. **Vectorisation** : découpage Markdown par en-têtes puis par fragments de 800 caractères
   (chevauchement 100) ; embeddings `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
   (multilingue, 384 dimensions).
3. **Persistance** : ChromaDB dans `data/processed/chroma_db/` — chargé si présent,
   reconstruit sinon (premier chargement : téléchargement du modèle d'embeddings).
4. **Requête enrichie** : composée à partir de la probabilité et des signaux
   (ex. « usure outil TWF remplacement » si `wear > 180`).
5. **Génération** : les 4 chunks les plus proches (similarité cosinus) sont injectés dans
   un prompt système strict ; Gemini (`gemini-3.8-flash`, repli `gemini-3.6-flash`)
   retourne un JSON validé par schéma Pydantic : `niveau_risque`, `type_panne_probable`,
   `explication`, `action_immediate`, `action_preventive`.
6. **Mode démonstration** (sans clé) : même recherche vectorielle, **aucune génération** —
   les extraits retrouvés sont affichés tels quels, encadrés « Mode démonstration ».
7. **Gestion d'erreurs** : quota/serveur temporairement indisponible → tentative sur le
   modèle de secours → sinon message honnête, jamais de texte inventé.

**Configuration des secrets** (jamais de clé dans Git) :

```python
# app/config.py — ordre de résolution
os.getenv("GOOGLE_API_KEY")      # 1. .env local / variables système
st.secrets["GOOGLE_API_KEY"]     # 2. Streamlit Cloud → App settings → Secrets
```

## 7. Résultats obtenus

### Classification (jeu de test : 2 000 lignes, 68 pannes)

| Métrique | Valeur |
|---|---|
| AUC-ROC | **0,9853** |
| AUC-PR | **0,8752** |
| Seuil application 0,111 | P 0,4511 · R 0,8824 · F1 0,5970 · TN 1859 · FP 73 · FN 8 · TP 60 |
| Seuil 0,5 | P 0,7342 · R 0,8529 · F1 0,7891 |
| Meilleur F1 | 0,8438 (seuil 0,8653) |

**Importances des variables (gain)** : `rpm_torque_ratio` 0,3380 · `tool_wear_min` 0,1607 ·
`torque` 0,1127 · `power` 0,1110 · `rpm` 0,0842 · `wear_rate` 0,0739 · `temp_diff` 0,0508 ·
`process_temp_c` 0,0231 · `air_temp_c` 0,0168 · `wear_temp_stress` 0,0160 · `type_M` 0,0128.
Pages Analytics et AI Prediction montrent ces courbes (ROC, PR, barres de seuils,
matrice de confusion, importance).

### Fiabilité (dataset complet : 10 000 h-machine, 339 pannes)

| Indicateur | Valeur |
|---|---|
| Fiabilité R(1 h) Kaplan-Meier | 96,61 % |
| Taux de panne | 3,39 % |
| MTBF | 29,50 h |
| Disponibilité (MTTR supposé 4 h) | 88,06 % |
| MTBF par mode | TWF 217,4 h · HDF 87,0 h · PWF 105,3 h · OSF 102,0 h · RNF 526,3 h |
| Politique optimale (Cp 500 € / Cf 20 000 €) | run-to-failure + surveillance conditionnelle |
| Conclusion prioritaire | HDF est le mode le plus fréquent → surveiller `temp_diff` en priorité |

*Note méthodologique* : AI4I 2020 étant un snapshot horaire, seules une loi exponentielle
et une Weibull contrainte (β = 1) sont identifiables ; le script le documente et
n'estime pas de paramètre non identifiable.

## 8. Limites et perspectives d'amélioration

| Limite | Impact | Perspective |
|---|---|---|
| Données synthétiques AI4I 2020 | Scores optimistes vs atelier réel | Valider/réentraîner sur données GMAO internes |
| Scaler ajusté avant split (fuite légère) | Métriques légèrement optimistes | Fit sur train uniquement |
| Classification binaire unique | Cause non prédite par le ML | Modèle multi-classes par mode (avec labels observés quand disponibles) |
| Pas de télémétrie temps réel | Journaux locaux seulement | Connecter OPC-UA/MQTT et stocker en base de données |
| Seuil unique global | Sensibilité identique partout | Seuil par type de machine, analyse coût réelle |
| RAG dépend de Gemini | Indisponible hors ligne | LLM local (Ollama) ou réponses par gabarit |
| Embeddings ~470 Mo | Premier chargement long sur Cloud | Modèle plus léger / embeddings pré-calculés |
| Seuil OSF simplifié | Ignore les variantes H/M | Seuils 11 000/12 000/13 000 par type de produit |
| MTTR supposé (4 h), coûts forfaitaires | Disponibilité et politique indicatives | MTTR mesuré, coûts par machine |

---

*Développé par Ghaith Mouelhi et Chadi Ammar. Dataset : AI4I 2020, UCI (CC BY 4.0).*
