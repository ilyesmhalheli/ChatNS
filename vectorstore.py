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


def compter_pdf(dossier):
    if os.path.exists(dossier):
        return len([f for f in os.listdir(dossier) if f.endswith('.pdf')])
    return 0


def charger_vecteur(topic):
    """Charge l'index FAISS existant pour un topic, ou le recree a partir
    des PDF presents dans le dossier correspondant."""
    print(f"Chargement du topic: {topic}")
    embeddings = get_embeddings()
    dossier = os.path.join(DOSSIER_BASE, TOPICS[topic]["dossier"])
    faiss_path = os.path.join(FICHIER_FAISS_BASE, f"faiss_{TOPICS[topic]['dossier']}")

    os.makedirs(dossier, exist_ok=True)
    os.makedirs(FICHIER_FAISS_BASE, exist_ok=True)

    if os.path.exists(faiss_path):
        try:
            vectorstore = FAISS.load_local(faiss_path, embeddings, allow_dangerous_deserialization=True)
            print(f"Index charge : {vectorstore.index.ntotal} chunks")
            return vectorstore
        except Exception as e:
            print(f"Index corrompu, recreation : {e}")
            shutil.rmtree(faiss_path, ignore_errors=True)

    print(f"Creation d'un nouvel index pour {topic}")
    docs = []
    fichiers = [f for f in os.listdir(dossier) if f.endswith('.pdf')] if os.path.exists(dossier) else []
    print(f"{len(fichiers)} fichiers trouves")

    for fichier in fichiers:
        try:
            docs.extend(extraire_pdf(os.path.join(dossier, fichier)))
        except Exception as e:
            print(f"Erreur avec {fichier}: {e}")

    if not docs:
        docs = [Document(page_content=f"Aucun document disponible pour {topic}")]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE_INDEXATION, chunk_overlap=CHUNK_OVERLAP_INDEXATION,
    )
    chunks = splitter.split_documents(docs)
    print(f"{len(chunks)} chunks crees")

    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(faiss_path)
    print(f"Index sauvegarde")
    return vectorstore


def ajouter_pdf(fichier, topic):
    """Ajoute un nouveau PDF (uploade) a l'index FAISS d'un topic."""
    embeddings = get_embeddings()
    dossier = os.path.join(DOSSIER_BASE, TOPICS[topic]["dossier"])
    faiss_path = os.path.join(FICHIER_FAISS_BASE, f"faiss_{TOPICS[topic]['dossier']}")

    os.makedirs(dossier, exist_ok=True)
    chemin = os.path.join(dossier, fichier.name)
    with open(chemin, "wb") as f:
        f.write(fichier.getbuffer())

    docs = extraire_pdf(chemin)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE_AJOUT, chunk_overlap=CHUNK_OVERLAP_AJOUT,
    )
    chunks = splitter.split_documents(docs)

    if os.path.exists(faiss_path):
        existing = FAISS.load_local(faiss_path, embeddings, allow_dangerous_deserialization=True)
        new_vs = FAISS.from_documents(chunks, embeddings)
        existing.merge_from(new_vs)
        existing.save_local(faiss_path)
        return existing
    else:
        vectorstore = FAISS.from_documents(chunks, embeddings)
        vectorstore.save_local(faiss_path)
        return vectorstore
