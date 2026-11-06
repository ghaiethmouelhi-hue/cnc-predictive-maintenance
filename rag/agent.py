# -*- coding: utf-8 -*-
# rag/agent.py

import math
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.config import get_api_key
from rag.vector_store import build_vector_store, search_knowledge

# Chargement de la clé API depuis .env (local). Sur Streamlit Cloud, la clé
# est lue depuis st.secrets via app.config.get_api_key().
load_dotenv()

# Seuil de décision identique à l'interface Streamlit (app/streamlit_app.py)
FAILURE_THRESHOLD = 0.111

def _get_llm(model_name: str = "gemini-3.8-flash"):
    """Crée le client Gemini uniquement si la clé API est disponible."""
    api_key = get_api_key()
    if not api_key:
        return None

    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0,
        max_retries=0,
        timeout=20,
        api_key=api_key,
    )


# Schéma de sortie structuré (Pydantic)
# Le LLM DOIT retourner exactement ces champs.
# Si l'IA hallucine un format → erreur capturée proprement.

class MaintenanceAdvice(BaseModel):
    niveau_risque: str = Field(
        description="CRITIQUE, ÉLEVÉ, MODÉRÉ, ou NORMAL"
    )
    type_panne_probable: str = Field(
        description="TWF, HDF, PWF, OSF, RNF, ou INDÉTERMINÉ"
    )
    explication: str = Field(
        description="Explication technique claire pour un opérateur"
    )
    action_immediate: str = Field(
        description="Ce que l'opérateur doit faire maintenant"
    )
    action_preventive: str = Field(
        description="Ce qu'il faut surveiller pour éviter la prochaine panne"
    )


# Configuration du parser
parser = JsonOutputParser(pydantic_object=MaintenanceAdvice)

# Le prompt système
# On définit précisément le rôle, les contraintes et le format attendu
SYSTEM_PROMPT = """Tu es un expert en maintenance prédictive CNC industrielle.
Tu assistes les opérateurs machine en interprétant les alertes du système ML.

DONNÉES DISPONIBLES :
- Mesures des capteurs en temps réel
- Probabilité de panne calculée par le modèle XGBoost
- Base de connaissances technique CNC

RÈGLES ABSOLUES :
1. Base tes recommandations UNIQUEMENT sur le contexte fourni.
2. Sois précis et actionnable. Un opérateur doit comprendre immédiatement.
3. Ne jamais minimiser un risque CRITIQUE ou ÉLEVÉ.
4. Si tu n'as pas assez de contexte : type_panne_probable = INDÉTERMINÉ.

{format_instructions}"""

def _build_advice_chain(llm):
    """Construit la chaîne de génération si un client LLM est disponible."""
    if llm is None:
        return None

    return ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", """MESURES CAPTEURS :
{sensor_data}

PRÉDICTION ML :
- Probabilité de panne : {failure_probability:.1%}
- Classe prédite : {predicted_class}

CONTEXTE BASE DE CONNAISSANCES :
{rag_context}

QUESTION OPÉRATEUR : {question}""")
    ]).partial(
        format_instructions=parser.get_format_instructions()
    ) | llm | parser


def _is_temporary_service_error(error: Exception) -> bool:
    message = str(error).lower()
    return any(marker in message for marker in (
        "429", "resource_exhausted", "rate limit", "quota",
        "500", "502", "503", "unavailable", "high demand", "overloaded",
        "504", "deadline_exceeded",
    ))


def _service_error_advice(message: str) -> dict:
    return {
        "niveau_risque": "INDÉTERMINÉ",
        "type_panne_probable": "INDÉTERMINÉ",
        "explication": message,
        "action_immediate": "La recommandation IA est indisponible. Utilisez la probabilité ML affichée et les procédures de maintenance habituelles.",
        "action_preventive": "Réessayez la recommandation IA plus tard.",
        "service_error": True,
    }


def _demo_advice(rag_context: str, failure_probability: float) -> dict:
    """Réponse explicite du mode démonstration, sans génération de texte.

    Aucune recommandation n'est inventée : seuls le score XGBoost et les
    extraits réellement retrouvés dans la base de connaissances sont exposés.
    """
    if failure_probability >= 0.5:
        level = "ÉLEVÉ"
    elif failure_probability >= FAILURE_THRESHOLD:
        level = "MODÉRÉ"
    else:
        level = "NORMAL"

    return {
        "niveau_risque": level,
        "type_panne_probable": "INDÉTERMINÉ",
        "explication": (
            "Mode démonstration : aucune clé API Gemini n'est configurée. "
            "Le score XGBoost, les seuils métier et la recherche vectorielle "
            "fonctionnent, mais aucun texte n'est généré par le LLM."
        ),
        "action_immediate": (
            "Utilisez la probabilité XGBoost affichée et les seuils TWF/HDF/"
            "PWF/OSF pour décider de l'intervention."
        ),
        "action_preventive": (
            "Ajoutez GOOGLE_API_KEY dans les secrets Streamlit Cloud pour "
            "activer la recommandation rédigée par Gemini."
        ),
        "demo_mode": True,
        "rag_context": rag_context,
    }


class MaintenanceAgent:
    """
    Agent de maintenance prédictive.

    Il combine :
    1. Les mesures capteurs temps réel
    2. La prédiction du modèle ML XGBoost
    3. La recherche RAG dans la base de connaissances
    4. Le LLM Gemini pour générer une recommandation structurée

    """

    def __init__(self):
        print("[INFO] Initialisation de l'agent maintenance...")
        self.llm = _get_llm()
        self.advice_chain = _build_advice_chain(self.llm)
        self.fallback_chain = _build_advice_chain(_get_llm("gemini-3.6-flash"))
        self.vector_db = build_vector_store()
        if self.llm is None:
            print("[WARN] Aucune cle API Gemini : mode demonstration actif (RAG retrieve-only, sans generation).")
        else:
            print("[OK] Agent pret")

    def get_advice(
        self,
        sensor_data: dict,
        failure_probability: float,
        question: str = "Analysez la situation et donnez vos recommandations."
    ) -> dict:
        """
        Génère une recommandation de maintenance complète.

        PARAMÈTRES :
        sensor_data         : dict des mesures capteurs normalisées + brutes
        failure_probability : float entre 0 et 1 (sortie du modèle ML)
        question            : question libre de l'opérateur (optionnel)

        RETOURNE :
        dict avec niveau_risque, type_panne_probable, explication,
        action_immediate, action_preventive
        """
        # Détermination de la classe prédite selon le seuil recommandé
        predicted_class = (
            "PANNE PROBABLE"
            if failure_probability >= FAILURE_THRESHOLD
            else "NORMAL"
        )

        # Formatage des mesures capteurs pour le prompt
        sensor_text = self._format_sensor_data(sensor_data, failure_probability)

        # Recherche RAG : on construit une requête enrichie
        # pour trouver les chunks les plus pertinents
        rag_query = self._build_rag_query(sensor_data, failure_probability)
        rag_context = search_knowledge(self.vector_db, rag_query, k=4)

        if self.llm is None or self.advice_chain is None:
            return _demo_advice(rag_context, failure_probability)

        request = {
            "sensor_data": sensor_text,
            "failure_probability": failure_probability,
            "predicted_class": predicted_class,
            "rag_context": rag_context,
            "question": question,
        }

        try:
            return self.advice_chain.invoke(request)
        except Exception as error:
            if not _is_temporary_service_error(error):
                print(f"[ERROR] Gemini advice failed: {type(error).__name__}")
                return _service_error_advice(
                    "Le service Gemini n'a pas pu générer le conseil. Vérifiez la configuration ou réessayez plus tard."
                )

            print("[WARN] Gemini principal temporairement indisponible; essai du modèle de secours.")
            if self.fallback_chain is not None:
                try:
                    return self.fallback_chain.invoke(request)
                except Exception as fallback_error:
                    print(f"[WARN] Gemini de secours indisponible: {type(fallback_error).__name__}")

            return _service_error_advice(
                "Gemini est temporairement surchargé ou indisponible. Aucun conseil IA n'a été généré; réessayez dans quelques minutes."
            )

    def _format_sensor_data(self, sensor_data: dict, proba: float) -> str:
        """Formate les données capteurs en texte lisible pour le LLM."""
        lines = []
        label_map = {
            "air_temp_c":        ("Température air",     "°C"),
            "process_temp_c":    ("Température process", "°C"),
            "rpm":               ("Vitesse rotation",    "tr/min"),
            "torque":            ("Couple",              "Nm"),
            "tool_wear_min":     ("Usure outil",         "min"),
            "temp_diff":         ("Écart thermique",     "°C"),
            "power":             ("Puissance (rpm×couple)", "rpm·Nm (proxy)"),
            "rpm_torque_ratio":  ("Ratio rpm/torque",    "(feature clé ML)"),
        }
        for key, (label, unit) in label_map.items():
            if key in sensor_data:
                lines.append(f"  {label:<25} : {sensor_data[key]:.2f} {unit}")

        return "\n".join(lines)

    def _build_rag_query(self, sensor_data: dict, proba: float) -> str:
        """
        Construit une requête enrichie pour la recherche RAG.
        Plus la requête est précise, plus les chunks trouvés sont pertinents.
        """
        parts = []

        if proba >= FAILURE_THRESHOLD:
            parts.append("panne machine CNC type cause")

        # On guide la recherche vers les sections pertinentes
        # selon les valeurs des capteurs
        wear = sensor_data.get("tool_wear_min", 0)
        torque = sensor_data.get("torque", 0)
        power = sensor_data.get("power", 0)
        temp_diff = sensor_data.get("temp_diff", 10)

        if wear > 180:
            parts.append("usure outil TWF remplacement")
        if torque > 50:
            parts.append("surcharge mécanique OSF couple élevé")

        # La feature "power" vaut rpm × couple (proxy), pas des watts.
        # La règle PWF du dataset s'applique à la puissance physique :
        # P(W) = couple × vitesse angulaire = rpm × couple × 2π / 60.
        power_w = power * 2 * math.pi / 60
        if power_w < 3500 or power_w > 9000:
            parts.append("défaut puissance PWF limites opérationnelles")

        if temp_diff < 8.6:
            parts.append("dissipation thermique HDF refroidissement")

        if not parts:
            parts.append("fonctionnement normal surveillance préventive")

        return " ".join(parts)