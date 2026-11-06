# Attribution des données et des composants

## Dataset

**AI4I 2020 Predictive Maintenance Dataset**  
UCI Machine Learning Repository — identifiant 601  
Auteur : Stephan Matzka  
DOI : [10.24432/C5HS5C](https://doi.org/10.24432/C5HS5C)  
Licence : **Creative Commons Attribution 4.0 International (CC BY 4.0)**  
Source : <https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset>

Le fichier `data/raw/ai4i2020.csv` est redistribué tel quel avec cette
attribution. Toute réutilisation doit conserver la mention de l'auteur, du
DOI et de la licence CC BY 4.0.

> Le dataset est **synthétique** : il reproduit des motifs industriels
> réalistes mais ne remplace pas des mesures d'atelier.

## Bibliothèques principales

| Composant | Licence |
|---|---|
| Streamlit | Apache 2.0 |
| Plotly | MIT |
| XGBoost | Apache 2.0 |
| scikit-learn | BSD-3-Clause |
| pandas / NumPy / SciPy | BSD-3-Clause |
| LangChain | MIT |
| ChromaDB | Apache 2.0 |
| sentence-transformers | Apache 2.0 |
| Gemma / Gemini SDK | Apache 2.0 (client) |
| lifelines | MIT |
| Matplotlib | PSF-based |
| Seaborn | BSD-3-Clause |

Les licences complètes de chaque paquet sont disponibles dans leurs dépôts
respectifs et dans l'environnement Python installé.

## Modèle d'embeddings

`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
(UKPLab / sentence-transformers), licence Apache 2.0.
