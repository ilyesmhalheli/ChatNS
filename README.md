# Chat GCT

Assistant IA local (RAG) du Groupe Chimique Tunisien, base sur Streamlit,
FAISS et Ollama (Mistral + nomic-embed-text).

## Structure du projet

```
chat_gct/
├── app.py               # Point d'entree Streamlit (UI uniquement)
├── config.py             # Constantes : chemins, dossiers, TOPICS
├── ollama_utils.py       # Embeddings/LLM Ollama + verification du serveur
├── text_cleaning.py      # Nettoyage du texte extrait des PDF
├── pdf_extraction.py     # Extraction texte/tableaux depuis les PDF
├── vectorstore.py        # Chargement/creation/mise a jour des index FAISS
├── retriever.py          # Retriever hybride (vectoriel + mots-cles "annexe n°X")
├── chain.py               # Chaine RAG (RetrievalQA) + chunks adaptatifs
├── cache_questions.py    # Cache questions/reponses par similarite cosinus
├── ui_styles.py           # CSS et en-tete HTML de l'interface
└── requirements.txt
```

## Lancement

1. Demarrer Ollama : `ollama serve`
2. S'assurer que les modeles sont disponibles :
   `ollama pull mistral` et `ollama pull nomic-embed-text`
3. Installer les dependances : `pip install -r requirements.txt`
4. Lancer l'application : `streamlit run app.py`

## Configuration

Toutes les constantes (modele LLM, modele d'embedding, tailles de chunks,
seuils, prompt...) sont centralisees dans **`config.py`**. Deux facons de
les modifier :

1. **Editer `config.py` directement** (valeurs par defaut en clair).
2. **Sans toucher au code** : copier `.env.example` en `.env` et y
   decommenter/modifier uniquement les valeurs voulues, par exemple :
   ```
   LLM_MODEL=llama3
   CHUNKS_SEUIL_DISTANCE=0.4
   ```
   Le fichier `.env` est charge automatiquement au demarrage et prend le
   pas sur les valeurs par defaut de `config.py`.

Principales options disponibles (voir `.env.example` pour la liste complete) :

| Variable | Role |
|---|---|
| `LLM_MODEL` | Modele Ollama de generation (ex: `mistral`, `llama3`) |
| `EMBEDDING_MODEL` | Modele Ollama d'embedding (ex: `nomic-embed-text`) |
| `OLLAMA_URL` | URL du serveur Ollama |
| `CHUNK_SIZE_INDEXATION` / `CHUNK_OVERLAP_INDEXATION` | Decoupage lors de la (re)creation complete d'un index |
| `CHUNK_SIZE_AJOUT` / `CHUNK_OVERLAP_AJOUT` | Decoupage lors de l'ajout d'un seul PDF |
| `RETRIEVER_K` | Nombre max de chunks recuperes par le retriever |
| `CHUNKS_SEUIL_DISTANCE` / `CHUNKS_MAX_AFFICHES` | Filtrage des chunks affiches sous la reponse |
| `CACHE_SEUIL_SIMILARITE` | Seuil au-dela duquel une question est consideree "deja posee" |
| `PROMPT_TEMPLATE` | Prompt systeme envoye au LLM |

## Dossiers generes automatiquement

- `documents/<Topic>/` : PDF uploades, ranges par topic (Achats, RH, Finance, Technique, General)
- `faiss_documents/faiss_<Topic>/` : index vectoriels FAISS par topic
- `cache_questions.json` : cache des questions/reponses deja traitees
