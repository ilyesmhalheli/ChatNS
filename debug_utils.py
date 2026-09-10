"""Outils de debug pour suivre l'avancement de chaque etape du pipeline RAG.

Utilisation :
    from debug_utils import etape, logger

    with etape("Extraction PDF"):
        docs = extraire_pdf(chemin)

    logger.debug(f"{len(docs)} documents extraits")

Active/desactive le niveau de detail via la variable d'environnement
DEBUG_LEVEL (DEBUG, INFO, WARNING...). Par defaut : DEBUG.

Les logs s'affichent dans le terminal avec :
- un timestamp precis (heure:min:sec.millisecondes)
- le nom de l'etape / du module
- le temps ecoule pour chaque etape (via le context manager `etape`)
"""
import logging
import os
import time
from contextlib import contextmanager

DEBUG_LEVEL = os.getenv("DEBUG_LEVEL", "DEBUG")

logger = logging.getLogger("chatns")
logger.setLevel(DEBUG_LEVEL)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03d | %(levelname)-7s | %(message)s",
        datefmt="%H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False


SEPARATEUR = "-" * 78


def barre_avancement(pourcentage, largeur=28):
    """Retourne une barre ASCII plus lisible pour le terminal."""
    pourcentage = max(0, min(100, int(pourcentage)))

    if pourcentage >= 100:
        return f"[{ '=' * largeur }] {pourcentage:3d}%"

    position = int((pourcentage / 100) * largeur)
    position = max(1, min(position, largeur - 1))

    gauche = "=" * (position - 1)
    curseur = ">"
    droite = "-" * (largeur - position)
    return f"[{gauche}{curseur}{droite}] {pourcentage:3d}%"


def horodatage(instant=None):
    """Formate une heure locale avec les millisecondes."""
    if instant is None:
        instant = time.time()
    secondes = int(instant)
    millisecondes = int((instant - secondes) * 1000)
    return time.strftime("%H:%M:%S", time.localtime(secondes)) + f".{millisecondes:03d}"


def formater_details(details):
    """Retourne les details d'une etape sur plusieurs lignes."""
    if not details:
        return "    (aucun detail)"
    lignes = []
    for cle, valeur in details.items():
        lignes.append(f"    - {cle}: {valeur}")
    return "\n".join(lignes)


@contextmanager
def etape(nom, **details):
    """Context manager qui logue le debut/fin d'une etape du pipeline avec
    son temps d'execution.

    Exemple :
        with etape("Chargement FAISS", topic=topic):
            vectorstore = FAISS.load_local(...)
    """
    suffixe = ""
    if details:
        suffixe = " (" + ", ".join(f"{k}={v}" for k, v in details.items()) + ")"

    debut = time.perf_counter()
    debut_horodatage = horodatage()
    logger.info(
        f"\n{SEPARATEUR}\n"
        f"DEBUT  : {nom}{suffixe}\n"
        f"HEURE  : {debut_horodatage}\n"
        f"PROGRE : {barre_avancement(0)}\n"
        f"DETAILS:\n{formater_details(details)}\n"
        f"{SEPARATEUR}"
    )
    try:
        yield
    except Exception as e:
        duree = time.perf_counter() - debut
        fin_horodatage = horodatage()
        logger.error(
            f"\n{SEPARATEUR}\n"
            f"ECHEC  : {nom}{suffixe}\n"
            f"HEURE  : {debut_horodatage} -> {fin_horodatage}\n"
            f"TEMPS D'EXECUTION : {duree:.2f}s\n"
            f"PROGRE : {barre_avancement(100)}\n"
            f"ERREUR : {e}\n"
            f"{SEPARATEUR}"
        )
        raise
    else:
        duree = time.perf_counter() - debut
        fin_horodatage = horodatage()
        logger.info(
            f"\n{SEPARATEUR}\n"
            f"FIN    : {nom}{suffixe}\n"
            f"HEURE  : {debut_horodatage} -> {fin_horodatage}\n"
            f"TEMPS D'EXECUTION : {duree:.2f}s\n"
            f"PROGRE : {barre_avancement(100)}\n"
            f"{SEPARATEUR}"
        )


def chrono(fonction_nom=None):
    """Decorateur equivalent a `etape` mais pour une fonction entiere.

    Exemple :
        @chrono("Recherche vectorielle FAISS")
        def similarity_search(...):
            ...
    """
    def decorateur(fn):
        nom = fonction_nom or fn.__name__

        def wrapper(*args, **kwargs):
            with etape(nom):
                return fn(*args, **kwargs)
        return wrapper
    return decorateur
