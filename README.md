# 🤖 Assistant IA Local — Assistant IA RAG pour Entreprises

> ⚠️ **CONFIDENTIEL** — Les documents traités par cet assistant peuvent contenir des informations internes et confidentielles. Leur accès et leur utilisation doivent être limités aux personnes autorisées par l'entreprise. Voir la section [Confidentialité & Sécurité](#-confidentialité--sécurité) pour le détail des mesures en place.

## 📋 Description
Ce projet est un assistant IA local destiné aux entreprises. Il permet aux employés de poser des questions en langage naturel sur des documents internes (PDF), et d'obtenir des réponses générées par un modèle de langage local.

**Avantage principal :** toutes les données peuvent rester sur l'infrastructure locale de l'entreprise — aucun document confidentiel n'est envoyé vers un cloud externe.

---

## 🏗️ Architecture

```
Documents PDF (internes)
        ↓
pdfplumber  →  Extraction du texte et des tableaux
        ↓
Data Cleaning  →  Nettoyage avancé du texte (accents, encodage,
                   points de suite, corrections de police connues)
        ↓
Découpage en chunks (RecursiveCharacterTextSplitter)
        ↓
nomic-embed-text  →  Vectorisation (768 dimensions)
        ↓
FAISS  →  Stockage local des vecteurs sur disque
        ↓
Question utilisateur
        ↓
Mémoire des questions/réponses  →  réponse instantanée si question déjà posée
        ↓ (sinon)
Recherche vectorielle (FAISS)
        ↓
Mistral 7B  →  Génération de la réponse en français
        ↓
Streamlit  →  Interface web locale (templates HTML externalisés)
```

Chaque étape du pipeline est chronométrée et journalisée (voir `debug_utils.py`) pour faciliter le suivi et le diagnostic en cas de lenteur ou d'erreur.

---

## 🛠️ Stack Technologique

| Composant | Outil | Rôle |
|---|---|---|
| LLM local | Mistral 7B (via Ollama) | Génération des réponses |
| Embedding | nomic-embed-text (via Ollama) | Vectorisation des documents |
| Base vectorielle | FAISS | Stockage et recherche des vecteurs |
| Extraction PDF | pdfplumber | Lecture des documents PDF et des tableaux |
| Data Cleaning | Python (re, unicodedata) | Nettoyage et correction du texte extrait |
| Recherche | Vectorielle (FAISS) | Recherche par similarité sémantique |
| Orchestration | LangChain | Pipeline RAG |
| Interface | Streamlit + templates HTML | Interface web utilisateur |
| Logging | Module interne (`debug_utils.py`) | Suivi détaillé et chronométrage de chaque étape |

---

## ✨ Fonctionnalités principales

- **Extraction et nettoyage avancé** des PDF (texte + tableaux), avec corrections ciblées des défauts d'encodage de police connus
- **Mémoire des questions/réponses** : les questions déjà posées (même reformulées) sont reconnues automatiquement et la réponse est renvoyée instantanément depuis le cache, sans repasser par le modèle
- **Prompt renforcé** contre les erreurs d'interprétation sur les seuils à paliers multiples et les hallucinations de chiffres
- **Chunks pertinents affichés** avec leur score de similarité, pour vérifier la source de chaque réponse
- **Journalisation détaillée** de chaque étape du pipeline (extraction, embeddings, recherche, génération) avec temps d'exécution, via `debug_utils.py`
- **Interface découplée du HTML** : les blocs d'affichage (en-tête, réponse, cache, chunks) sont définis dans `templates/ui_templates.html` et injectés dynamiquement, avec échappement automatique des variables
- **Configuration entièrement externalisée** (modèles, tailles de chunks, seuils, prompt) via `config.py` et un fichier `.env` optionnel — aucune modification du code nécessaire pour ajuster le comportement

---

## 📁 Structure du projet

Le projet est organisé en modules, chacun avec une responsabilité unique :

```
assistant-ia-entreprise/
├── app.py                     # Point d'entree Streamlit (interface uniquement)
├── config.py                  # Configuration centrale : modeles, chemins, seuils, prompt
├── debug_utils.py             # Logging detaille + chronometrage de chaque etape du pipeline
├── ollama_utils.py            # Embeddings/LLM Ollama + verification du serveur
├── text_cleaning.py           # Nettoyage du texte extrait des PDF
├── pdf_extraction.py          # Extraction texte/tableaux depuis les PDF
├── vectorstore.py             # Chargement/creation/mise a jour des index FAISS
├── chain.py                   # Chaine RAG (RetrievalQA) + chunks adaptatifs
├── cache_questions.py         # Cache questions/reponses par similarite cosinus
├── ui_styles.py                # CSS de l'interface
├── templates/
│   └── ui_templates.html       # Blocs HTML de l'interface (en-tete, reponse, cache, chunks)
├── requirements.txt            # Dependances Python
├── .env.example                 # Exemple de configuration surchargeable
├── .gitignore                   # Fichiers exclus du depot
├── README.md                    # Ce fichier
├── images/                       # Captures d'ecran de l'interface
├── documents/                     # Dossier des PDF (non versionne — confidentiel)
├── faiss_documents/                # Index vectoriel (non versionne, genere automatiquement)
└── cache_questions.json             # Memoire des questions/reponses (non versionne)
```

---

## ⚙️ Installation

### Prérequis

- Python 3.10+
- [Ollama](https://ollama.com/download) installé et en cours d'exécution
- Windows 10/11 ou Linux

### 1. Cloner le dépôt

```bash
git clone https://github.com/ilyesmhalheli-stack/chat-gct.git
cd chat-gct
```

### 2. Installer les dépendances Python

Idéalement dans un environnement virtuel :

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
```

### 3. Télécharger les modèles Ollama

```bash
ollama pull mistral
ollama pull nomic-embed-text
```

### 4. Ajouter vos documents PDF

Créez un dossier `documents/` à la racine du projet et placez-y vos fichiers PDF, organisés par service ou thème (`Achats`, `RH`, `Finance`, `Technique`, `Production`, `General`) :

```
assistant-ia-entreprise/
└── documents/
    └── Finance/
        ├── document1.pdf
        └── document2.pdf
```

> ⚠️ Ce dossier est exclu du dépôt Git (voir `.gitignore`) — les documents confidentiels ne sont jamais versionnés.

### 5. (Optionnel) Personnaliser la configuration

Copiez `.env.example` en `.env` pour surcharger les valeurs par défaut de `config.py` (modèle utilisé, tailles de chunks, seuils...) sans toucher au code :

```bash
copy .env.example .env      # Windows
cp .env.example .env         # Linux/Mac
```

### 6. Lancer l'application

Aucune configuration de chemin n'est nécessaire : le script détecte automatiquement son propre emplacement et cherche les dossiers `documents/` et `faiss_documents/` à côté de lui.

```bash
streamlit run app.py
```

Ouvrez votre navigateur sur : **http://localhost:8501**

---

## 🚀 Utilisation

1. Lancez l'application avec `streamlit run app.py`
2. Ouvrez **http://localhost:8501** dans votre navigateur
3. Sélectionnez un topic dans la barre latérale
4. Posez vos questions en français dans le champ de texte
5. L'assistant cherche dans vos documents et génère une réponse, avec les chunks sources affichés en dessous

### Espaces client et administrateur

- **Client** : accès à la sélection des topics et aux questions/réponses.
- **Administrateur** : saisissez le mot de passe dans la barre latérale pour ajouter des PDF, nettoyer un index ou vider le cache.
- Le mot de passe se configure avec `ADMIN_PASSWORD` dans `.env` (la valeur par défaut locale est `admin123`).

**Exemples de questions :**
- *"Quelles sont les procédures de sécurité ?"*
- *"Qui contacter en cas de panne ?"*
- *"Quel est le délai de maintenance préventive ?"*

---

## 🪵 Logs et diagnostic

Chaque étape du pipeline (vérification Ollama, embeddings, recherche vectorielle, génération LLM, cache) est journalisée dans le terminal avec un horodatage précis et son temps d'exécution, via `debug_utils.py`.

Le niveau de détail est configurable via la variable d'environnement `DEBUG_LEVEL` (`DEBUG`, `INFO`, `WARNING`...), par défaut `DEBUG` :

```bash
# Exemple : réduire la verbosité
set DEBUG_LEVEL=INFO          # Windows
export DEBUG_LEVEL=INFO       # Linux/Mac
```

Le temps total de réponse (cache ou génération LLM) est également affiché directement dans l'interface Streamlit, sous chaque réponse.

---

## 🔧 Configuration

Toutes les constantes (modèle LLM, modèle d'embedding, tailles de chunks, seuils, prompt...) sont centralisées dans **`config.py`**. Deux façons de les modifier :

1. **Éditer `config.py` directement** (valeurs par défaut en clair).
2. **Sans toucher au code** : créer un fichier `.env` (voir `.env.example`) et y définir uniquement les valeurs voulues, par exemple :
   ```
   LLM_MODEL=llama3
   CHUNKS_SEUIL_DISTANCE=0.4
   ```
   Le fichier `.env` est chargé automatiquement au démarrage et prend le pas sur les valeurs par défaut de `config.py`.

Principales options disponibles (voir `.env.example` pour la liste complète) :

| Variable | Rôle |
|---|---|
| `LLM_MODEL` | Modèle Ollama de génération (ex: `mistral`, `llama3`) |
| `EMBEDDING_MODEL` | Modèle Ollama d'embedding (ex: `nomic-embed-text`) |
| `OLLAMA_URL` | URL du serveur Ollama |
| `CHUNK_SIZE_INDEXATION` / `CHUNK_OVERLAP_INDEXATION` | Découpage lors de la (re)création complète d'un index |
| `CHUNK_SIZE_AJOUT` / `CHUNK_OVERLAP_AJOUT` | Découpage lors de l'ajout d'un seul PDF |
| `RETRIEVER_K` | Nombre max de chunks récupérés par le retriever |
| `CHUNKS_SEUIL_DISTANCE` / `CHUNKS_MAX_AFFICHES` | Filtrage des chunks affichés sous la réponse |
| `CACHE_SEUIL_SIMILARITE` | Seuil au-delà duquel une question est considérée "déjà posée" |
| `PROMPT_TEMPLATE` | Prompt système envoyé au LLM |
| `DEBUG_LEVEL` | Niveau de verbosité des logs (`DEBUG`, `INFO`, `WARNING`...) |

---

## ⚠️ Limitations connues

- Le modèle Mistral 7B peut occasionnellement halluciner des détails ou des chiffres non présents dans le contexte, malgré les règles strictes du prompt. Toujours vérifier la réponse avec les chunks sources affichés.
- Certains PDF avec des polices personnalisées corrompues peuvent produire des extractions de chiffres erronées (bug identifié et corrigé au cas par cas dans `corriger_bug_encodage_connu()` — nécessite une vérification manuelle pour tout nouveau document).
- Les tableaux PDF à cellules fusionnées ou avec diagonales peuvent être mal extraits par `pdfplumber`.
- Le cache de questions/réponses n'est pas invalidé automatiquement si les documents sources sont mis à jour (utiliser le bouton "Vider cache" après modification des documents).
- La recherche s'appuie uniquement sur la similarité vectorielle ; les références précises (numéros d'annexe, de décret, de contrat) peuvent être moins bien retrouvées que par une recherche par mots-clés exacte.

---

## 🔒 Confidentialité & Sécurité

**Les données traitées par cet assistant peuvent être confidentielles et doivent être protégées conformément aux règles de l'entreprise.** Les mesures suivantes sont en place pour les protéger :

- **Aucune donnée n'est envoyée sur internet** — Ollama exécute les modèles entièrement en local, aucun document ni aucune question n'est transmise à un service externe ou à un cloud
- Le dossier `documents/`, la base vectorielle `faiss_documents/` (qui contient une copie du texte extrait des documents), le fichier `cache_questions.json` (qui mémorise les questions/réponses) et le fichier `.env` (configuration locale) sont **tous exclus du dépôt Git** via `.gitignore` — aucun contenu confidentiel n'est versionné ni poussé sur GitHub
- Le dépôt GitHub doit rester **privé** si le projet contient de la configuration interne ou du code sensible (accès restreint aux personnes autorisées) — ne jamais le rendre public
- Le système fonctionne sans connexion internet une fois les modèles téléchargés
- Aucun nom d'employé, chemin système, ou adresse réseau interne n'est présent dans ce dépôt
- Toute entreprise clonant ce dépôt doit fournir ses propres documents dans `documents/` — aucun document réel d'une entreprise n'est inclus dans le code source

---

## 💻 Configuration Matérielle Recommandée

| Composant | Minimum recommandé |
|---|---|
| RAM | 16 GB |
| Stockage | 10 GB libres (modèles Ollama) |
| OS | Windows 10/11 ou Linux |
| GPU | Optionnel (accélère les réponses) |

---

## 👤 Auteur

**Projet académique / professionnel — 2026**
École Nationale des Sciences de l'Informatique (ENSI)
Projet : Développement d'un Assistant IA Local Généralisé pour les Entreprises

---

## 📄 Licence

Projet développé dans le cadre d'un stage interne.
Usage destiné aux entreprises et organisations selon leur politique interne de sécurité et de confidentialité.
