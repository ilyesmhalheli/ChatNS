"""Extraction du contenu (texte + tableaux) des fichiers PDF."""
import os

import pdfplumber
from langchain_core.documents import Document

from text_cleaning import nettoyer_texte_avance, corriger_bug_encodage_connu


def extraire_pdf(chemin_pdf):
    """Extrait le texte et les tableaux d'un PDF, page par page, en
    appliquant le nettoyage de texte et les corrections d'encodage connues."""
    print(f"pdfplumber: {os.path.basename(chemin_pdf)}")
    documents = []
    try:
        with pdfplumber.open(chemin_pdf) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                texte = page.extract_text() or ""
                tableaux_text = ""
                for t_idx, tableau in enumerate(page.extract_tables(), 1):
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
                if contenu.strip():
                    documents.append(Document(
                        page_content=contenu,
                        metadata={"source": chemin_pdf, "page": page_num, "total_pages": len(pdf.pages)}
                    ))
        print(f"OK {len(documents)} pages extraites")
        return documents
    except Exception as e:
        print(f"Erreur pdfplumber: {e}")
        return []
