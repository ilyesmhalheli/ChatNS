"""Chat GCT - Assistant IA local (RAG) du Groupe Chimique Tunisien.

Point d'entree Streamlit. Lancer avec :
    streamlit run app.py
"""
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import shutil
import time
from pathlib import Path
import html
from string import Template

import streamlit as st

from config import (
    DOSSIER_BASE, FICHIER_FAISS_BASE, TOPICS,
    CACHE_SEUIL_SIMILARITE, CHUNKS_SEUIL_DISTANCE, CHUNKS_MAX_AFFICHES,
)
from ollama_utils import verifier_ollama
from vectorstore import compter_pdf, charger_vecteur, ajouter_pdf
from chain import creer_chaine, get_chunks_adaptatifs
from cache_questions import CacheQuestions
from ui_styles import CSS
from debug_utils import etape, logger, horodatage

cache = CacheQuestions()
TEMPLATE_PATH = Path(__file__).resolve().parent / "templates" / "ui_templates.html"


def charger_bloc_html(nom):
    contenu = TEMPLATE_PATH.read_text(encoding="utf-8")
    debut = f"<!-- BEGIN {nom} -->"
    fin = f"<!-- END {nom} -->"
    if debut not in contenu or fin not in contenu:
        raise ValueError(f"Bloc HTML introuvable : {nom}")
    bloc = contenu.split(debut, 1)[1].split(fin, 1)[0].strip()
    return Template(bloc)


def rendre_html(nom, **variables):
    bloc = charger_bloc_html(nom)
    valeurs = {
        cle: html.escape(str(valeur), quote=True) if isinstance(valeur, str) else valeur
        for cle, valeur in variables.items()
    }
    return bloc.safe_substitute(valeurs)

# --- Configuration de la page ---
st.set_page_config(page_title="Chat GCT", page_icon="factory", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)
st.markdown(rendre_html("header"), unsafe_allow_html=True)

# --- Verification Ollama ---
ollama_ok, ollama_err = verifier_ollama()
if not ollama_ok:
    st.error(f"Ollama non disponible\n\nLance : ollama serve\n\nErreur : {ollama_err}")
    st.stop()

# --- Sidebar ---
with st.sidebar:
    st.markdown("## Chat GCT")
    st.markdown("Groupe Chimique Tunisien")
    st.markdown("---")
    st.markdown("### Topic")
    topic = st.selectbox("Topic", list(TOPICS.keys()), label_visibility="collapsed")
    st.markdown("---")
    st.markdown("### Statistiques")
    total = sum(compter_pdf(os.path.join(DOSSIER_BASE, t["dossier"])) for t in TOPICS.values())
    st.metric("Total PDF", total)
    st.metric("PDF dans ce topic", compter_pdf(os.path.join(DOSSIER_BASE, TOPICS[topic]["dossier"])))

    stats_cache = cache.get_stats()
    st.markdown("---")
    st.markdown("### Cache de reponses")
    st.metric("Questions memorisees", stats_cache["total"])
    if stats_cache["total"] > 0:
        st.caption(f"Derniere : {stats_cache['derniere'][:10]} {stats_cache['derniere'][11:16]}")

    st.markdown("---")
    st.success("Donnees 100% locales\nAucun envoi vers le cloud")
    st.info("Modele : Mistral 7B\n\nEmbedding : nomic-embed-text\n\nCache : Questions/Reponses")
    st.markdown("---")

    col_clean, col_cache = st.columns(2)
    with col_clean:
        if st.button("Nettoyer index", use_container_width=True):
            if os.path.exists(FICHIER_FAISS_BASE):
                shutil.rmtree(FICHIER_FAISS_BASE)
            for k in ["vectorstore", "chain", "topic_courant"]:
                st.session_state.pop(k, None)
            st.success("Index nettoye !")
            st.rerun()
    with col_cache:
        if st.button("Vider cache", use_container_width=True):
            cache.cache = {"questions": [], "reponses": [], "embeddings": [], "dates": [], "topics": []}
            cache.sauvegarder_cache()
            st.success("Cache vide !")
            st.rerun()

# --- Zone principale : topic + upload PDF ---
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown(f"### Topic : {topic}")
    st.caption(f"Dossier : {os.path.join(DOSSIER_BASE, TOPICS[topic]['dossier'])}")

with col2:
    st.markdown('<div class="section-title section-title-upload">Ajouter un PDF</div>', unsafe_allow_html=True)
    pdf = st.file_uploader("Upload PDF", type="pdf", label_visibility="collapsed", key="pdf_uploader")

    if pdf is not None:
        fichier_id = f"{pdf.name}_{pdf.size}"
        if st.session_state.get("dernier_fichier") != fichier_id:
            with st.spinner("Indexation avec nettoyage avance..."):
                try:
                    ajouter_pdf(pdf, topic)
                    st.session_state.dernier_fichier = fichier_id
                    for k in ["vectorstore", "chain", "topic_courant"]:
                        st.session_state.pop(k, None)
                    st.success(f"{pdf.name} ajoute dans {topic} !")
                except Exception as e:
                    st.error(f"Erreur : {e}")
                    st.session_state.dernier_fichier = fichier_id
        else:
            st.info(f"{pdf.name} deja indexe.")

st.markdown("---")

# --- Chargement du vectorstore / de la chaine ---
if "vectorstore" not in st.session_state or st.session_state.get("topic_courant") != topic:
    with st.spinner("Chargement des documents..."):
        try:
            st.session_state.vectorstore = charger_vecteur(topic)
            st.session_state.topic_courant = topic
            st.session_state.chain = None
        except Exception as e:
            st.error(f"Erreur chargement : {e}")
            st.session_state.vectorstore = None

if st.session_state.get("vectorstore") and not st.session_state.get("chain"):
    with st.spinner("Initialisation de Mistral..."):
        try:
            st.session_state.chain = creer_chaine(st.session_state.vectorstore)
            nb = st.session_state.vectorstore.index.ntotal
            st.info(f"Assistant pret {nb} chunks indexes dans {topic}")
        except Exception as e:
            st.error(f"Erreur modele : {e}")
            st.session_state.chain = None

# --- Zone de question ---
st.markdown("### Votre question")
question = st.text_input(
    "Question",
    placeholder=f"Posez une question sur {topic}...",
    label_visibility="collapsed"
)
envoyer = st.button("Envoyer")

if envoyer:
    debut_total = time.perf_counter()
    debut_total_h = horodatage()
    logger.info("#" * 60)
    logger.info(f"NOUVELLE QUESTION recue : '{question}' (topic={topic})")
    if not question:
        st.warning("Veuillez entrer une question.")
    elif not st.session_state.get("chain"):
        st.error("Modele non disponible.")
        logger.error("Chaine non disponible, impossible de repondre")
    else:
        with etape("Recherche dans le cache"):
            reponse_cache, similarite, index_cache = cache.trouver_question_similaire(question, topic, seuil=CACHE_SEUIL_SIMILARITE)

        if reponse_cache:
            st.markdown(rendre_html(
                "cache_box",
                title="Reponse du cache",
                similarite=f"{similarite:.2%}"
            ), unsafe_allow_html=True)

            st.markdown(rendre_html(
                "response_box",
                titre="Reponse",
                contenu=reponse_cache
            ), unsafe_allow_html=True)

            with st.expander("Voir la question originale"):
                st.write(f"Question originale : {cache.cache['questions'][index_cache]}")
                st.write(f"Date : {cache.cache['dates'][index_cache]}")

            duree_totale = time.perf_counter() - debut_total
            fin_total_h = horodatage()
            logger.info(
                f"TEMPS TOTAL REPONSE (cache) | debut={debut_total_h} | fin={fin_total_h} | "
                f"duree={duree_totale:.2f}s"
            )
            st.caption(f"Temps total de reponse : {duree_totale:.2f}s")
        else:
            with st.spinner("Generation de la reponse..."):
                try:
                    with etape("Traitement complet de la question (retrieval + LLM)"):
                        question_enrichie = TOPICS[topic]["prefix"] + question
                        reponse = st.session_state.chain.invoke({"query": question_enrichie})
                        reponse_texte = reponse["result"]

                    cache.ajouter_question_reponse(question, reponse_texte, topic)

                    st.markdown(rendre_html(
                        "response_box",
                        titre="Reponse",
                        contenu=reponse_texte
                    ), unsafe_allow_html=True)

                    st.caption("Cette question/reponse a ete ajoutee au cache")

                    st.markdown("---")
                    st.markdown("### Chunks pertinents utilises")
                    st.caption(f"Seuil de distance: {CHUNKS_SEUIL_DISTANCE} | Maximum: {CHUNKS_MAX_AFFICHES} chunks")

                    chunks, nb_chunks_trouves = get_chunks_adaptatifs(
                        st.session_state.chain,
                        question,
                        seuil=CHUNKS_SEUIL_DISTANCE,
                        max_chunks=CHUNKS_MAX_AFFICHES
                    )

                    if not chunks:
                        st.warning(f"Aucun chunk pertinent trouve (distance > {CHUNKS_SEUIL_DISTANCE})")
                    else:
                        for chunk in chunks:
                            if chunk["distance"] < 0.3:
                                niveau = "Tres proche"
                            elif chunk["distance"] < 0.4:
                                niveau = "Proche"
                            else:
                                niveau = "Moyennement proche"

                            distance_pourcent = (1 - chunk["distance"]) * 100

                            st.markdown(rendre_html(
                                "chunk_box",
                                numero=chunk["numero"],
                                source=chunk["source"],
                                page=chunk["page"],
                                distance=f"{chunk['distance']:.4f}",
                                similarite=f"{chunk['similarite']:.4f}",
                                niveau=niveau,
                                distance_pourcent=f"{distance_pourcent:.1f}",
                                contenu=chunk["contenu"]
                            ), unsafe_allow_html=True)

                        st.caption(f"{len(chunks)} chunks utilises sur {nb_chunks_trouves} trouves")

                    duree_totale = time.perf_counter() - debut_total
                    fin_total_h = horodatage()
                    logger.info(
                        f"TEMPS TOTAL REPONSE (LLM) | debut={debut_total_h} | fin={fin_total_h} | "
                        f"duree={duree_totale:.2f}s"
                    )
                    st.caption(f"Temps total de reponse : {duree_totale:.2f}s")

                except Exception as e:
                    st.error(f"Erreur : {str(e)}")
