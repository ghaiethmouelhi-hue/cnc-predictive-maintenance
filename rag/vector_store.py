# -*- coding: utf-8 -*-
# rag/vector_store.py

import os
from pathlib import Path
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Chemins
BASE_DIR       = Path(__file__).parent.parent
KNOWLEDGE_PATH = BASE_DIR / "data" / "knowledge" / "cnc_knowledge.md"
DB_PATH        = BASE_DIR / "data" / "processed" / "chroma_db"

# Modèle d'embeddings
# On utilise le même que ton projet ISO9001 : multilingue, léger, efficace
# Il transforme chaque chunk de texte en vecteur de 384 dimensions.
#
# Chargement paresseux : le modèle (~470 Mo) n'est instancié qu'au premier
# appel de build_vector_store(), et non à l'import du module. Cela évite de
# bloquer le démarrage de l'application Streamlit pendant ~1 minute.
_EMBED_MODEL = None


def _get_embeddings() -> HuggingFaceEmbeddings:
    global _EMBED_MODEL
    if _EMBED_MODEL is None:
        _EMBED_MODEL = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
    return _EMBED_MODEL


def build_vector_store() -> Chroma:
    """
    Construit ou charge la base vectorielle ChromaDB.

    LOGIQUE :
    - Si la base existe sur le disque → chargement instantané (cache)
    - Si elle n'existe pas → construction depuis le fichier Markdown

    """
    collection_name = "cnc_knowledge"

    # Chargement depuis le cache si disponible
    if DB_PATH.exists() and any(DB_PATH.iterdir()):
        print(f"[OK] Base vectorielle chargee depuis : {DB_PATH}")
        return Chroma(
            persist_directory=str(DB_PATH),
            embedding_function=_get_embeddings(),
            collection_name=collection_name
        )

    print("[INFO] Construction de la base vectorielle...")

    # Lecture du fichier Markdown
    if not KNOWLEDGE_PATH.exists():
        raise FileNotFoundError(f"Knowledge base introuvable : {KNOWLEDGE_PATH}")

    with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
        markdown_text = f.read()

    # ÉTAPE 1 — Découpage par structure Markdown (H1, H2, H3)
    # Chaque section garde ses métadonnées (titre de section)
    # Ex: "TWF — Tool Wear Failure" reste dans le metadata du chunk
    headers_to_split_on = [
        ("#",   "section"),
        ("##",  "subsection"),
        ("###", "topic")
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on
    )
    md_splits = markdown_splitter.split_text(markdown_text)

    # ÉTAPE 2 — Découpage récursif si les chunks sont trop grands
    # chunk_size=800 : chaque morceau = max 800 caractères
    # chunk_overlap=100 : 100 caractères de chevauchement entre morceaux
    # pour ne pas couper une phrase en deux et perdre le contexte
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " "]
    )
    final_documents = text_splitter.split_documents(md_splits)

    print(f"   -> {len(final_documents)} segments crees")

    # ÉTAPE 3 — Vectorisation et stockage
    # Chaque segment est transformé en vecteur de 384 dimensions
    # et stocké dans ChromaDB avec ses métadonnées
    DB_PATH.mkdir(parents=True, exist_ok=True)
    vector_db = Chroma.from_documents(
        documents=final_documents,
        embedding=_get_embeddings(),
        persist_directory=str(DB_PATH),
        collection_name=collection_name
    )

    print(f"[OK] Base vectorielle construite et sauvegardee -> {DB_PATH}")
    return vector_db


def search_knowledge(vector_db: Chroma, query: str, k: int = 4) -> str:
    """
    Recherche les k segments les plus pertinents pour une requête.

    COMMENT ÇA FONCTIONNE :
    1. La requête est transformée en vecteur (même modèle d'embeddings)
    2. ChromaDB calcule la similarité cosinus entre ce vecteur
       et tous les vecteurs stockés
    3. Les k vecteurs les plus proches sont retournés
    4. On reconstitue le texte de ces segments

    La similarité cosinus mesure l'angle entre deux vecteurs.
    Angle proche de 0° = très similaires sémantiquement.
    Angle proche de 90° = non liés.
    """
    docs = vector_db.similarity_search(query, k=k)

    context_parts = []
    for doc in docs:
        # Récupération des métadonnées de section
        section    = doc.metadata.get("section", "")
        subsection = doc.metadata.get("subsection", "")
        topic      = doc.metadata.get("topic", "")

        header = " > ".join(filter(None, [section, subsection, topic]))
        context_parts.append(f"[{header}]\n{doc.page_content}")

    return "\n\n".join(context_parts)