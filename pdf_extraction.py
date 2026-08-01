"""Extraction du contenu (texte + tableaux) des fichiers PDF."""
import os

import time

import pdfplumber
from langchain_core.documents import Document

from text_cleaning import nettoyer_texte_avance, corriger_bug_encodage_connu
from debug_utils import etape, logger


def extraire_pdf(chemin_pdf):
    """Extrait le texte et les tableaux d'un PDF, page par page, en
    appliquant le nettoyage de texte et les corrections d'encodage connues."""
    nom_fichier = os.path.basename(chemin_pdf)
    documents = []
    with etape(f"Extraction PDF", fichier=nom_fichier):
        try:
            with pdfplumber.open(chemin_pdf) as pdf:
                nb_pages = len(pdf.pages)
                logger.debug(f"[{nom_fichier}] {nb_pages} pages a traiter")
                for page_num, page in enumerate(pdf.pages, 1):
                    t0_page = time.perf_counter()
                    texte = page.extract_text() or ""
                    tableaux = page.extract_tables()
                    tableaux_text = ""
                    for t_idx, tableau in enumerate(tableaux, 1):
                        tableaux_text += f"\n[TABLEAU {t_idx}]\n"
                        for ligne in tableau:
                            ligne_propre = [str(c).strip() if c else "" for c in ligne]
                            tableaux_text += " | ".join(ligne_propre) + "\n"
                        tableaux_text += f"[/TABLEAU]\n"
                    contenu = texte
                    if tableaux_text:
                        contenu += f"\n\n--- TABLEAUX ---\n{tableaux_text}"
                    contenu = nettoyer_texte_avance(contenu)
                    contenu = corriger_bug_encodage_connu(contenu)
                    duree_page = time.perf_counter() - t0_page
                    if contenu.strip():
                        documents.append(Document(
                            page_content=contenu,
                            metadata={"source": chemin_pdf, "page": page_num, "total_pages": nb_pages}
                        ))
                        logger.debug(
                            f"[{nom_fichier}] page {page_num}/{nb_pages} : OK "
                            f"({len(tableaux)} tableau(x), {len(contenu)} caracteres, {duree_page:.3f}s)"
                        )
                    else:
                        logger.debug(f"[{nom_fichier}] page {page_num}/{nb_pages} : vide, ignoree ({duree_page:.3f}s)")
            logger.info(f"[{nom_fichier}] {len(documents)}/{nb_pages} pages retenues")
            return documents
        except Exception as e:
            logger.error(f"Erreur pdfplumber sur {nom_fichier}: {e}")
            return []
