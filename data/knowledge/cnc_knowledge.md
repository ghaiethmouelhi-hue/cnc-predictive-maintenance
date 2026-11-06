# Base de connaissances — Maintenance Prédictive CNC

## Types de pannes — Dataset AI4I 2020

### TWF — Tool Wear Failure (Casse par usure outil)
- **Fréquence** : 46 cas sur 10 000 (0.46%)
- **Cause** : L'outil de coupe dépasse sa durée de vie nominale
- **Indicateurs** : tool_wear_min élevé (> 200 min), souvent sans signal thermique fort
- **Caractéristique** : Panne "silencieuse" — les autres capteurs semblent normaux jusqu'à la casse
- **Action** : Remplacer l'outil immédiatement. Vérifier le programme de remplacement préventif.
- **Prévention** : Définir un seuil de remplacement à 180 min pour anticiper.

### HDF — Heat Dissipation Failure (Défaut dissipation thermique)
- **Fréquence** : 115 cas sur 10 000 (1.15%) — le plus fréquent
- **Cause** : La différence de température process/ambiant est trop faible (< 8.6°C)
  Le système de refroidissement ne dissipe pas suffisamment la chaleur
- **Indicateurs** : temp_diff faible, process_temp_c élevée
- **Action** : Vérifier le circuit de refroidissement (liquide de coupe, ventilation)
  Nettoyer les filtres du système de refroidissement.
- **Prévention** : Maintenir temp_diff > 10°C en opération normale.

### PWF — Power Failure (Défaut puissance)
- **Fréquence** : 95 cas sur 10 000 (0.95%)
- **Cause** : La puissance mécanique sort des limites opérationnelles :
  puissance physique < 3 500 W ou > 9 000 W.
  Le risque apparaît aux extrêmes de fonctionnement :
  régime très faible sous charge, ou surcharge extrême.
- **Calcul** : puissance physique (W) = couple × vitesse angulaire
  = rpm × torque × 2π / 60.
  La feature `power` du modèle vaut seulement rpm × torque (unité rpm·Nm) :
  **ce n'est pas une puissance en watts**.
- **Plage normale (puissance physique)** : ≈ 1 150 – 10 470 W.
  Le proxy `power` correspondant vaut ≈ 11 000 – 100 000 rpm·Nm.
- **Indicateurs** : puissance physique hors [3 500 ; 9 000] W, soit
  approximativement `power` < 33 400 ou > 86 000 rpm·Nm.
  Valeur nominale : ≈ 6 280 W physiques (proxy ≈ 60 000 rpm·Nm).
- **Action** : Réduire la profondeur de passe ou la vitesse d'avance.
  Vérifier l'alimentation électrique de la broche.
- **Prévention** : Maintenir la puissance physique entre 3 500 W et 9 000 W.
  Éviter les combinaisons rpm très bas + torque très élevé.

### OSF — Overstrain Failure (Surcharge mécanique)
- **Fréquence** : 98 cas sur 10 000 (0.98%)
- **Cause** : La force exercée sur l'outil dépasse sa résistance mécanique
  tool_wear_min × torque > 13 000 (produit critique)
- **Indicateurs** : torque élevé + tool_wear_min élevé simultanément
- **Action** : Réduire immédiatement le couple (vitesse de broche ou avance).
  Inspecter l'outil pour déformation ou micro-fissures.
- **Prévention** : Ne jamais combiner outil usé (> 150 min) et couple élevé (> 50 Nm).

### RNF — Random Failure (Panne aléatoire)
- **Fréquence** : 19 cas sur 10 000 (0.19%) — le plus rare
- **Cause** : Défaillance non corrélée aux paramètres process
  Peut être électrique, vibratoire, ou défaut matière
- **Indicateurs** : Aucun signal clair — panne imprévisible par nature
- **Action** : Diagnostic complet de la machine. Contacter le service technique.
- **Prévention** : Maintenance préventive complète régulière.

---

## Plages de fonctionnement normal

### Températures
- air_temp_c : 22°C – 31°C (nominal : 26.85°C)
- process_temp_c : 32°C – 41°C (nominal : 36.86°C)
- temp_diff normal : 8.6°C – 12°C

### Mécanique
- rpm : 1168 – 2886 tr/min (nominal : 1538 tr/min)
- torque : 3.8 – 76.6 Nm (nominal : 39.99 Nm)
- tool_wear_min : 0 – 253 min (remplacement recommandé : 180 min)

### Features dérivées
- power (rpm × torque) : proxy en rpm·Nm, **pas** des watts.
  Plage observée ≈ 11 000 – 100 000 rpm·Nm (nominal ≈ 60 000).
  Puissance physique équivalente : power × 2π / 60 ≈ 1 150 – 10 470 W.
  Attention si la puissance physique sort de [3 500 ; 9 000] W.
- rpm_torque_ratio : signal dominant du modèle ML (33.8% importance)
  Ratio élevé = régime léger (OK)
  Ratio faible = régime chargé (attention)

---

## Interprétation du modèle ML

### Feature Importance — Top 5
1. rpm_torque_ratio (33.8%) : équilibre vitesse/couple
2. tool_wear_min (16.1%) : usure cumulative de l'outil
3. torque (11.3%) : couple exercé sur la broche
4. power (11.1%) : proxy de puissance (rpm × couple)
5. rpm (8.4%) : vitesse de rotation

### Lecture de la probabilité de panne
- 0% – 30% : Fonctionnement normal. Surveillance standard.
- 30% – 60% : Zone d'attention. Augmenter la fréquence de contrôle.
- 60% – 85% : Risque élevé. Planifier une intervention préventive.
- 85% – 100% : Risque critique. Arrêt recommandé en fin de cycle.

### Seuil de décision recommandé
- Seuils 0.80 – 0.86 → F1-Score maximal (précision 90%, rappel 79%)
- Seuil 0.50 → Rappel 85%, précision 73%
- Seuil 0.111 (retenu dans l'application) → Rappel 88%, précision 45%,
  fausses alarmes 3.8% — compromis orienté détection des pannes.
- Choix selon la tolérance au risque et les coûts réels du site.