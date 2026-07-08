import os
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM
from langchain_classic.chains import RetrievalQA

DOSSIER_CV    = r"C:\Users\ilyes\Desktop\cvs"
FICHIER_FAISS = r"C:\Users\ilyes\Desktop\faiss_cvs"

def compter_pdf_dossier(dossier):
    if os.path.exists(dossier):
        return len([f for f in os.listdir(dossier) if f.endswith('.pdf')])
    return 0

@st.cache_resource
def charger_cvs():
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    if os.path.exists(FICHIER_FAISS):
        print("Base FAISS trouvee, chargement direct...")
        vectorstore = FAISS.load_local(FICHIER_FAISS, embeddings, allow_dangerous_deserialization=True)
        print("Base chargee avec succes.")
    else:
        print("Premiere creation de la base FAISS...")
        docs = []
        for fichier in os.listdir(DOSSIER_CV):
            if fichier.endswith(".pdf"):
                loader = PyPDFLoader(os.path.join(DOSSIER_CV, fichier))
                docs.extend(loader.load())
                print(f"OK : {fichier} charge")
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(docs)
        vectorstore = FAISS.from_documents([chunks[0]], embeddings)
        for i, chunk in enumerate(chunks[1:], start=2):
            vectorstore.add_documents([chunk])
        vectorstore.save_local(FICHIER_FAISS)
        print("Base FAISS sauvegardee.")
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    llm = OllamaLLM(model="mistral:7b-instruct-q4_K_M")
    chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    nb_chunks_faiss = vectorstore.index.ntotal
    return chain, nb_chunks_faiss

st.set_page_config(page_title="Assistant CV", page_icon="🤖")
st.title("🤖 Assistant CV")
st.caption("Posez vos questions sur les CV")

chain, total_chunks = charger_cvs()
total_pdf = compter_pdf_dossier(DOSSIER_CV)

with st.sidebar:
    st.header("📊 Statistiques des Données")
    st.metric(label="📄 Nombre de fichiers PDF", value=total_pdf)
    st.metric(label="🧩 Nombre total de Chunks", value=total_chunks)
    st.write("---")
    st.info("Les données sont indexées localement dans la base vectorielle FAISS.")

question = st.text_input("Votre question :")
if question:
    with st.spinner("Recherche en cours..."):
        reponse = chain.invoke({"query": question})
    st.write("**Réponse :**", reponse["result"])