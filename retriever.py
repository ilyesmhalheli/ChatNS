"""Retriever hybride : recherche vectorielle FAISS + recherche exacte par
mots-cles pour les references du type "annexe n°X"."""
import re
from typing import Any

from langchain_core.retrievers import BaseRetriever


class RetrieverHybride(BaseRetriever):
    """Combine la recherche vectorielle (FAISS) avec une recherche par
    mots-cles exacte pour les references du type "annexe n°X".

    Utile car les embeddings distinguent mal les identifiants numeriques
    precis.
    """
    vectorstore: Any
    k: int = 15

    def _get_relevant_documents(self, query, *, run_manager=None):
        # 1. Recherche vectorielle classique (comportement d'origine)
        docs_vectoriels = self.vectorstore.similarity_search(query, k=self.k)

        match = re.search(r'annexe\s*n?\s*°?\s*(\d+)', query.lower())
        docs_mots_cles = []
        if match:
            numero = match.group(1)
            # Motif souple : "annexe" puis eventuellement "n" et "°",
            # puis le numero exact suivi d'une limite de mot (evite de
            # matcher "annexe n°140" quand on cherche "annexe n°14")
            motif = re.compile(r'annexe\s*n?\s*°?\s*' + re.escape(numero) + r'\b')

            # Parcourt tous les documents indexes pour trouver une
            # correspondance textuelle exacte, en plus de la recherche
            # vectorielle
            docstore_dict = self.vectorstore.docstore._dict
            for doc in docstore_dict.values():
                if motif.search(doc.page_content.lower()):
                    docs_mots_cles.append(doc)

        # 3. Fusion : les resultats par mots-cles sont places en tete
        #    (priorite), suivis des resultats vectoriels, en dedoublonnant
        docs_combines = []
        contenus_vus = set()
        for doc in docs_mots_cles + docs_vectoriels:
            cle = doc.page_content[:100]
            if cle not in contenus_vus:
                docs_combines.append(doc)
                contenus_vus.add(cle)

        return docs_combines[:self.k]
