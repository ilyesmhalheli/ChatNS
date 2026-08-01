"""Wrappers Ollama : embeddings custom, LLM custom, verification du serveur."""
import urllib.request
from typing import List

import ollama
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import LLM

from config import OLLAMA_URL, LLM_MODEL, EMBEDDING_MODEL
from debug_utils import etape, logger


def verifier_ollama():
    """Verifie que le serveur Ollama repond bien a l'URL configuree."""
    with etape("Verification serveur Ollama", url=OLLAMA_URL):
        try:
            urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=3)
            logger.info("Ollama disponible")
            return True, None
        except Exception as e:
            logger.error(f"Ollama indisponible : {e}")
            return False, str(e)


class OllamaEmbeddingsDirect(Embeddings):
    def __init__(self, model: str = EMBEDDING_MODEL, host: str = OLLAMA_URL):
        self.model = model
        self.client = ollama.Client(host=host)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        with etape("Embedding batch (documents)", nb_textes=len(texts), modele=self.model):
            results = []
            for text in texts:
                resp = self.client.embeddings(model=self.model, prompt=text)
                results.append(resp["embedding"])
        return results

    def embed_query(self, text: str) -> List[float]:
        resp = self.client.embeddings(model=self.model, prompt=text)
        logger.debug(f"Embedding calcule ({len(text)} caracteres, modele={self.model})")
        return resp["embedding"]


class OllamaLLMDirect(LLM):
    model: str = LLM_MODEL
    host: str = OLLAMA_URL

    @property
    def _llm_type(self) -> str:
        return "ollama_direct"

    def _call(self, prompt: str, stop=None, run_manager=None, **kwargs) -> str:
        with etape("Generation LLM (Ollama)", modele=self.model, longueur_prompt=len(prompt)):
            client = ollama.Client(host=self.host)
            resp = client.generate(model=self.model, prompt=prompt)
        return resp["response"]


def get_embeddings():
    """Instance par defaut des embeddings utilises dans toute l'appli."""
    return OllamaEmbeddingsDirect(model=EMBEDDING_MODEL, host=OLLAMA_URL)
