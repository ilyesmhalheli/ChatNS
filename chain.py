"""Construction de la chaine RAG (RetrievalQA) et recuperation des chunks
pertinents avec filtrage adaptatif par distance."""
import os

import numpy as np
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import RetrievalQA

from config import OLLAMA_URL, LLM_MODEL, RETRIEVER_K, PROMPT_TEMPLATE
from ollama_utils import OllamaLLMDirect
from debug_utils import etape, logger


def creer_chaine(vectorstore):
    """Cree la chaine RetrievalQA (LLM + retriever hybride + prompt).
    Le modele LLM et le prompt sont definis dans config.py."""
    with etape("Creation de la chaine RAG", modele=LLM_MODEL, retriever_k=RETRIEVER_K):
        llm = OllamaLLMDirect(model=LLM_MODEL, host=OLLAMA_URL)
        retriever = vectorstore.as_retriever(search_kwargs={"k": RETRIEVER_K})
        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=PROMPT_TEMPLATE,
        )
        chaine = RetrievalQA.from_chain_type(
            llm=llm, retriever=retriever,
            chain_type_kwargs={"prompt": prompt}
        )
    logger.info("Chaine RAG prete")
    return chaine


def get_chunks_adaptatifs(chain, question, seuil=0.5, max_chunks=3):
    """Recupere les chunks utilises par le retriever, calcule leur distance
    cosinus a la question et filtre selon un seuil / un nombre maximum."""
    logger.info(f"=== Calcul des chunks adaptatifs pour : '{question[:60]}...' ===")
    with etape("Retrieval (recherche des chunks)"):
        docs = chain.retriever.invoke(question)
    logger.info(f"{len(docs)} chunk(s) recupere(s) par le retriever")

    vectorstore = chain.retriever.vectorstore
    embeddings = vectorstore.embeddings

    with etape("Embedding de la question"):
        question_vecteur = embeddings.embed_query(question)

    chunks_avec_distances = []

    for i, doc in enumerate(docs, 1):
        chunk_vecteur = embeddings.embed_query(doc.page_content)

        q_vect = np.array(question_vecteur)
        c_vect = np.array(chunk_vecteur)

        norm_q = np.linalg.norm(q_vect)
        norm_c = np.linalg.norm(c_vect)
        q_norm = q_vect / norm_q if norm_q > 0 else q_vect
        c_norm = c_vect / norm_c if norm_c > 0 else c_vect

        similarite = np.dot(q_norm, c_norm)
        distance = 1 - similarite

        source = doc.metadata.get("source", "Inconnue")
        nom_fichier = os.path.basename(source) if source != "Inconnue" else "Inconnue"

        chunks_avec_distances.append({
            "numero": i,
            "source": nom_fichier,
            "chemin": source,
            "page": doc.metadata.get("page", "N/A"),
            "contenu": doc.page_content,
            "distance": distance,
            "similarite": similarite
        })

    chunks_avec_distances.sort(key=lambda x: x["distance"])
    chunks_filtres = [c for c in chunks_avec_distances if c["distance"] < seuil]
    if len(chunks_filtres) > max_chunks:
        chunks_filtres = chunks_filtres[:max_chunks]

    logger.info(
        f"Filtrage chunks : {len(chunks_avec_distances)} calcules -> "
        f"{len(chunks_filtres)} retenus (seuil={seuil}, max={max_chunks})"
    )
    for c in chunks_filtres:
        logger.debug(f"  chunk #{c['numero']} {c['source']} p.{c['page']} distance={c['distance']:.4f}")

    return chunks_filtres, len(docs)
