"""Cache des questions/reponses, base sur une similarite cosinus entre
embeddings, pour eviter de re-interroger le LLM sur des questions proches."""
import json
import os
from datetime import datetime

import numpy as np

from config import CACHE_QUESTIONS, EMBEDDING_MODEL, CACHE_SEUIL_SIMILARITE
from ollama_utils import OllamaEmbeddingsDirect
from debug_utils import etape, logger


class CacheQuestions:
    def __init__(self, fichier_cache=CACHE_QUESTIONS):
        self.fichier_cache = fichier_cache
        self.cache = self.charger_cache()
        self.embeddings = None

    def charger_cache(self):
        if os.path.exists(self.fichier_cache):
            try:
                with open(self.fichier_cache, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {"questions": [], "reponses": [], "embeddings": [], "dates": [], "topics": []}
        return {"questions": [], "reponses": [], "embeddings": [], "dates": [], "topics": []}

    def sauvegarder_cache(self):
        with open(self.fichier_cache, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)

    def get_embeddings(self):
        if self.embeddings is None:
            self.embeddings = OllamaEmbeddingsDirect(model=EMBEDDING_MODEL)
        return self.embeddings

    def trouver_question_similaire(self, nouvelle_question, topic, seuil=CACHE_SEUIL_SIMILARITE):
        logger.info(f"=== Recherche cache pour question : '{nouvelle_question[:60]}...' (topic={topic}) ===")
        if not self.cache["questions"]:
            logger.debug("Cache vide, aucune comparaison possible")
            return None, 0, -1

        with etape("Embedding de la question (pour cache)"):
            embeddings = self.get_embeddings()
            nouveau_vect = np.array(embeddings.embed_query(nouvelle_question))
            norm = np.linalg.norm(nouveau_vect)
            if norm > 0:
                nouveau_vect = nouveau_vect / norm

        meilleure_similarite = 0
        meilleur_index = -1

        with etape("Comparaison cosinus avec le cache", nb_entrees=len(self.cache["questions"])):
            for i in range(len(self.cache["questions"])):
                if self.cache["topics"][i] != topic:
                    continue

                if self.cache["embeddings"][i]:
                    ancien_vect = np.array(json.loads(self.cache["embeddings"][i]))
                    norm = np.linalg.norm(ancien_vect)
                    if norm > 0:
                        ancien_vect = ancien_vect / norm
                    similarite = float(np.dot(nouveau_vect, ancien_vect))

                    if similarite > meilleure_similarite:
                        meilleure_similarite = similarite
                        meilleur_index = i

        if meilleure_similarite >= seuil:
            logger.info(f"CACHE HIT (similarite={meilleure_similarite:.3f} >= seuil={seuil}) -> index {meilleur_index}")
            return self.cache["reponses"][meilleur_index], meilleure_similarite, meilleur_index

        logger.info(f"CACHE MISS (meilleure similarite={meilleure_similarite:.3f} < seuil={seuil})")
        return None, meilleure_similarite, -1

    def ajouter_question_reponse(self, question, reponse, topic):
        with etape("Ajout question/reponse au cache", topic=topic):
            embeddings = self.get_embeddings()
            vect = embeddings.embed_query(question)
            vect_str = json.dumps(vect)

            self.cache["questions"].append(question)
            self.cache["reponses"].append(reponse)
            self.cache["embeddings"].append(vect_str)
            self.cache["dates"].append(datetime.now().isoformat())
            self.cache["topics"].append(topic)

            self.sauvegarder_cache()
        logger.info(f"Cache mis a jour : {len(self.cache['questions'])} question(s) au total")

    def get_stats(self):
        return {
            "total": len(self.cache["questions"]),
            "derniere": self.cache["dates"][-1] if self.cache["dates"] else "Aucune"
        }
