"""Nettoyage avance du texte extrait des PDF + correction d'un bug
d'encodage de police connu dans certains documents."""
import re
import unicodedata


def nettoyer_texte_avance(texte):
    """Nettoie le texte extrait d'un PDF : corrige les problemes
    d'encodage courants, normalise les accents, supprime les caracteres
    de controle, les points de suite (sommaires), etc."""
    if not texte:
        return ""

    corrections = {
        'Â´': 'E', 'Â´': 'e', 'AÂ´': 'A', 'aÂ´': 'a',
        'EÂ´': 'E', 'eÂ´': 'e', 'IÂ´': 'I', 'iÂ´': 'i',
        'OÂ´': 'O', 'oÂ´': 'o', 'UÂ´': 'U', 'uÂ´': 'u',
        'Â': '', 'Â°': '°', 'Â«': '"', 'Â»': '"',
        'â€™': "'", 'â€œ': '"', 'â€\x9d': '"', 'â€˜': "'",
        '`': "'", '´': "'", 'â€š': ',', 'â€ž': '"',
        'â€¦': '...', '…': '...',
        'â™‚': '', 'â˜…': '*', 'â€¢': '*',
        'â€°': '%', 'â€¹': '<', 'â€º': '>',
    }
    for ancien, nouveau in corrections.items():
        texte = texte.replace(ancien, nouveau)

    texte = unicodedata.normalize('NFKD', texte)
    texte = re.sub(r'[\u0300-\u036f]', '', texte)
    texte = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', ' ', texte)
    texte = re.sub(r'\s+', ' ', texte)
    texte = re.sub(r'\s+', ' ', texte)

    # Supprime les points de suite (sommaires/tables des matieres : ". . . . . .")
    texte = re.sub(r'\.(\s*\.){2,}', ' ', texte)

    lignes = [l for l in texte.split('\n') if l.strip()]
    texte = '\n'.join(lignes)
    texte = re.sub(r'\s+([.,;:!?])', r'\1', texte)
    texte = re.sub(r'([.,;:!?])\s*', r'\1 ', texte)
    texte = re.sub(r'[-]{2,}', '', texte)
    texte = re.sub(r'[|]{2,}', ' ', texte)

    mots_majuscules = ['gct', 'tuneps', 'cae', 'cme', 'cra', 'dar', 'dca']
    texte = texte.lower()
    for mot in mots_majuscules:
        texte = texte.replace(mot, mot.upper())

    texte = re.sub(r'\s+', ' ', texte)
    texte = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', texte)

    return texte.strip()


# Correction manuelle d'un bug d'encodage de police connu dans ce PDF :
# certaines pages (ex: Annexe n°2, fiche CROOA) contiennent une police dont
# la table ToUnicode est corrompue : le glyphe affiche visuellement "0" mais
# le texte extrait donne "2". Confirme par comparaison pdfplumber vs pymupdf
# (memes resultats errones dans les deux cas) + verification visuelle du PDF.
# Corrections verifiees manuellement contre le document source :
CORRECTIONS_SEUILS_CONNUES = [
    # Annexe n°2 / CROOA : travaux et fourniture de biens (≥ 22 -> ≥ 20)
    (r'(≥\s*)22(\s*et\s*<\s*2000)', r'\g<1>20\g<2>'),
    # Annexe n°2 / CROOA : etudes (< 222 -> < 200)
    (r'(<\s*)222(\s*\))', r'\g<1>200\g<2>'),
]


def corriger_bug_encodage_connu(texte):
    """Applique des corrections ciblees pour un bug d'encodage de police
    identifie dans ce document precis (voir CORRECTIONS_SEUILS_CONNUES).
    A adapter si d'autres pages/documents presentent le meme type de bug."""
    for motif, remplacement in CORRECTIONS_SEUILS_CONNUES:
        texte = re.sub(motif, remplacement, texte)
    return texte
