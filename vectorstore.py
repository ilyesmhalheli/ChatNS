"""Gestion des index vectoriels FAISS : chargement, creation, ajout de PDF."""
import os
import shutil

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from config import (
    DOSSIER_BASE, FICHIER_FAISS_BASE, TOPICS,
    CHUNK_SIZE_INDEXATION, CHUNK_OVERLAP_INDEXATION,
    CHUNK_SIZE_AJOUT, CHUNK_OVERLAP_AJOUT,
)
from ollama_utils import get_embeddings
from pdf_extraction import extraire_pdf
from debug_utils import etape, logger


def compter_pdf(dossier):
    if os.path.exists(dossier):
        return len([f for f in os.listdir(dossier) if f.endswith('.pdf')])
    return 0


def charger_vecteur(topic):
    """Charge l'index FAISS existant pour un topic, ou le recree a partir
    des PDF presents dans le dossier correspondant."""
    logger.info(f"=== Chargement du topic : {topic} ===")
    with etape("Init embeddings"):
        embeddings = get_embeddings()

    dossier = os.path.join(DOSSIER_BASE, TOPICS[topic]["dossier"])
    faiss_path = os.path.join(FICHIER_FAISS_BASE, f"faiss_{TOPICS[topic]['dossier']}")

    os.makedirs(dossier, exist_ok=True)
    os.makedirs(FICHIER_FAISS_BASE, exist_ok=True)

    if os.path.exists(faiss_path):
        try:
            with etape("Chargement index FAISS existant", topic=topic):
                vectorstore = FAISS.load_local(faiss_path, embeddings, allow_dangerous_deserialization=True)
            logger.info(f"Index charge : {vectorstore.index.ntotal} chunks")
            return vectorstore
        except Exception as e:
            logger.warning(f"Index corrompu, recreation : {e}")
            shutil.rmtree(faiss_path, ignore_errors=True)

    logger.info(f"Aucun index existant, creation d'un nouvel index pour {topic}")
    docs = []
    fichiers = [f for f in os.listdir(dossier) if f.endswith('.pdf')] if os.path.exists(dossier) else []
    logger.info(f"{len(fichiers)} fichier(s) PDF trouve(s) dans {dossier}")

    with etape("Extraction de tous les PDF du topic", nb_fichiers=len(fichiers)):
        for fichier in fichiers:
            try:
                docs.extend(extraire_pdf(os.path.join(dossier, fichier)))
            except Exception as e:
                logger.error(f"Erreur avec {fichier}: {e}")

    if not docs:
        docs = [Document(page_content=f"Aucun document disponible pour {topic}")]

    with etape("Decoupage en chunks (splitter)", taille=CHUNK_SIZE_INDEXATION, overlap=CHUNK_OVERLAP_INDEXATION):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE_INDEXATION, chunk_overlap=CHUNK_OVERLAP_INDEXATION,
        )
        chunks = splitter.split_documents(docs)
    logger.info(f"{len(chunks)} chunks crees a partir de {len(docs)} pages")

    with etape("Calcul des embeddings + creation index FAISS", nb_chunks=len(chunks)):
        vectorstore = FAISS.from_documents(chunks, embeddings)

    with etape("Sauvegarde index FAISS sur disque"):
        vectorstore.save_local(faiss_path)

    logger.info(f"Index sauvegarde pour {topic} ({vectorstore.index.ntotal} chunks)")
    return vectorstore


def ajouter_pdf(fichier, topic):
    """Ajoute un nouveau PDF (uploade) a l'index FAISS d'un topic."""
    logger.info(f"=== Ajout PDF '{fichier.name}' au topic {topic} ===")
    embeddings = get_embeddings()
    dossier = os.path.join(DOSSIER_BASE, TOPICS[topic]["dossier"])
    faiss_path = os.path.join(FICHIER_FAISS_BASE, f"faiss_{TOPICS[topic]['dossier']}")

    os.makedirs(dossier, exist_ok=True)
    chemin = os.path.join(dossier, fichier.name)
    with etape("Sauvegarde du fichier uploade sur disque", fichier=fichier.name):
        with open(chemin, "wb") as f:
            f.write(fichier.getbuffer())

    docs = extraire_pdf(chemin)

    with etape("Decoupage en chunks (splitter)", taille=CHUNK_SIZE_AJOUT, overlap=CHUNK_OVERLAP_AJOUT):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE_AJOUT, chunk_overlap=CHUNK_OVERLAP_AJOUT,
        )
        chunks = splitter.split_documents(docs)
    logger.info(f"{len(chunks)} chunks crees a partir de {len(docs)} pages")

    if os.path.exists(faiss_path):
        with etape("Chargement index FAISS existant"):
            existing = FAISS.load_local(faiss_path, embeddings, allow_dangerous_deserialization=True)
        with etape("Calcul des embeddings du nouveau PDF", nb_chunks=len(chunks)):
            new_vs = FAISS.from_documents(chunks, embeddings)
        with etape("Fusion (merge) dans l'index existant"):
            existing.merge_from(new_vs)
        with etape("Sauvegarde index FAISS sur disque"):
            existing.save_local(faiss_path)
        logger.info(f"PDF ajoute, index total : {existing.index.ntotal} chunks")
        return existing
    else:
        with etape("Calcul des embeddings + creation index FAISS", nb_chunks=len(chunks)):
            vectorstore = FAISS.from_documents(chunks, embeddings)
        with etape("Sauvegarde index FAISS sur disque"):
            vectorstore.save_local(faiss_path)
        logger.info(f"Nouvel index cree : {vectorstore.index.ntotal} chunks")
        return vectorstore
