"""Configuration centrale de ChatNS.

TOUTES les constantes de l'application (modeles Ollama, chemins, tailles de
chunks, seuils, prompt...) sont definies ici. Pour les modifier, deux
possibilites :

1. Editer directement les valeurs par defaut ci-dessous.
2. Sans toucher au code : creer un fichier ".env" (voir ".env.example")
   a la racine du projet et y surcharger uniquement les valeurs voulues,
   par exemple :
       LLM_MODEL=llama3
       CHUNKS_SEUIL_DISTANCE=0.4

Le fichier .env est automatiquement charge s'il existe.
"""
import os

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def _get_str(nom, defaut):
    return os.getenv(nom, defaut)


def _get_int(nom, defaut):
    return int(os.getenv(nom, defaut))


def _get_float(nom, defaut):
    return float(os.getenv(nom, defaut))


# ============================================================
# CHEMINS ET DOSSIERS
# ============================================================
DOSSIER_BASE = os.path.join(BASE_DIR, _get_str("DOSSIER_DOCUMENTS", "documents"))
FICHIER_FAISS_BASE = os.path.join(BASE_DIR, _get_str("DOSSIER_FAISS", "faiss_documents"))
CACHE_QUESTIONS = os.path.join(BASE_DIR, _get_str("FICHIER_CACHE", "cache_questions.json"))

# ============================================================
# OLLAMA : SERVEUR ET MODELES
# ============================================================
# URL du serveur Ollama
OLLAMA_URL = _get_str("OLLAMA_URL", "http://localhost:11434")

# Mot de passe de l'espace administrateur (a remplacer dans .env en production)
ADMIN_PASSWORD = _get_str("ADMIN_PASSWORD", "admin123")

# Modele de generation (LLM) utilise pour repondre aux questions.
# Exemples : "mistral", "llama3", "qwen2.5", "gemma2"...
LLM_MODEL = _get_str("LLM_MODEL", "mistral")

# Modele d'embedding utilise pour l'indexation FAISS et le cache de questions.
# Exemples : "nomic-embed-text", "mxbai-embed-large"...
EMBEDDING_MODEL = _get_str("EMBEDDING_MODEL", "nomic-embed-text")

# ============================================================
# DECOUPAGE DES DOCUMENTS (TEXT SPLITTER)
# ============================================================
# Utilise lors de la creation/reconstruction complete d'un index (charger_vecteur)
CHUNK_SIZE_INDEXATION = _get_int("CHUNK_SIZE_INDEXATION", 800)
CHUNK_OVERLAP_INDEXATION = _get_int("CHUNK_OVERLAP_INDEXATION", 100)

# Utilise lors de l'ajout d'un seul PDF a un index existant (ajouter_pdf)
CHUNK_SIZE_AJOUT = _get_int("CHUNK_SIZE_AJOUT", 500)
CHUNK_OVERLAP_AJOUT = _get_int("CHUNK_OVERLAP_AJOUT", 80)

# ============================================================
# RETRIEVER (RECHERCHE DE CHUNKS)
# ============================================================
# Nombre maximum de chunks renvoyes par le retriever hybride (vectoriel + mots-cles)
RETRIEVER_K = _get_int("RETRIEVER_K", 5)

# Seuil de distance en dessous duquel un chunk est considere pertinent
# et affiche a l'utilisateur (0 = identique, 1 = tres different)
CHUNKS_SEUIL_DISTANCE = _get_float("CHUNKS_SEUIL_DISTANCE", 0.5)

# Nombre maximum de chunks affiches sous la reponse
CHUNKS_MAX_AFFICHES = _get_int("CHUNKS_MAX_AFFICHES", 5)

# ============================================================
# CACHE DE QUESTIONS/REPONSES
# ============================================================
# Seuil de similarite cosinus (0 a 1) au-dessus duquel une question est
# consideree comme "deja posee" et la reponse est servie depuis le cache
CACHE_SEUIL_SIMILARITE = _get_float("CACHE_SEUIL_SIMILARITE", 0.85)

# ============================================================
# PROMPT DU MODELE
# ============================================================
PROMPT_TEMPLATE = _get_str("PROMPT_TEMPLATE", """Tu es ChatNS, un assistant intelligent.

REGLES STRICTES A RESPECTER IMPERATIVEMENT :
6. Quand le contexte mentionne un chiffre, un montant ou un seuil , verifie s'il est associe a UNE SEULE entite/commission ou si le contexte suggere qu'il existe plusieurs paliers/seuils geres par des entites differentes (par exemple une hierarchie du type: entite A < seuil 1, entite B entre seuil 1 et seuil 2, entite C >= seuil 2).
9. Si la question porte sur un tableau recapitulatif (ex: "seuils de competences", "grille tarifaire", "bareme") et que le contexte ne semble contenir que la fiche d'une seule entite plutot que le tableau complet, signale cette limite dans ta reponse plutot que de repondre comme si tu avais la vue complete.

Le contexte peut contenir des caracteres mal encodes ou des tableaux extraits de PDF : ignore les artefacts de formatage et concentre-toi sur le sens.

Contexte :
{context}

Question : {question}

Reponse en francais (strictement basee sur le contexte ci-dessus, en respectant scrupuleusement les regles 6 a 9 sur les chiffres et seuils) :""")

# ============================================================
# TOPICS (DOMAINES DOCUMENTAIRES)
# ============================================================
TOPICS = {
    "Achats": {
        "dossier": "Achats",
        "prefix": "En te basant sur les documents d'achats : ",
    },
    "RH": {
        "dossier": "RH",
        "prefix": "En te basant sur les documents RH : ",
    },
    "Finance": {
        "dossier": "Finance",
        "prefix": "En te basant sur les documents financiers : ",
    },
    "Technique": {
        "dossier": "Technique",
        "prefix": "En te basant sur les documents techniques : ",
    },
    "General": {
        "dossier": "General",
        "prefix": "",
    },
}
