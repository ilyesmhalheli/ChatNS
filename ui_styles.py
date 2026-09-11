"""Styles CSS pour l'interface Streamlit."""

CSS = """
<style>
    /* --- FOND GENERAL --- */
    .stApp { background-color: #F5F7FA; color: #1A1A2E; }
    .stApp, .stApp p, .stApp li, .stApp label, .stApp span, .stApp div { color: #1A1A2E; }

    /* --- BARRE LATERALE (SIDEBAR) --- */
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #003B73 0%, #0060B0 100%); }
    [data-testid="stSidebar"] * { color: white !important; }

    /* --- CHAMPS DE SAISIE (fond bleu clair) --- */
    div[data-testid="stTextInput"] input,
    .stTextInput > div > div > input {
        background-color: #E8F0FE !important;
        color: #003B73 !important;
        border: 2px solid #0060B0 !important;
        border-radius: 8px !important;
        font-size: 15px !important;
        caret-color: #003B73 !important;
    }
    div[data-testid="stTextInput"] input:focus,
    .stTextInput > div > div > input:focus {
        border-color: #003B73 !important;
        box-shadow: 0 0 0 2px rgba(0,96,176,0.25) !important;
        outline: none !important;
    }
    div[data-testid="stTextInput"] input::placeholder,
    .stTextInput > div > div > input::placeholder {
        color: #6C8EBF !important;
    }

    /* --- UPLOAD PDF : correction complete --- */
    /* Conteneur principal */
    [data-testid="stFileUploader"] {
        background-color: #DCEBFF !important;
        border: 2px dashed #0060B0 !important;
        border-radius: 8px !important;
        padding: 12px !important;
    }
    [data-testid="stFileUploader"]:hover {
        background-color: #C7DEFF !important;
        border-color: #003B73 !important;
    }

    /* Zone interne (la partie sombre par defaut) */
    [data-testid="stFileUploader"] section,
    [data-testid="stFileUploader"] > div,
    [data-testid="stFileUploader"] > div > div,
    [data-testid="stFileUploadDropzone"] {
        background-color: #DCEBFF !important;
        color: #003B73 !important;
        border: none !important;
    }

    /* Texte a l'interieur de la dropzone */
    [data-testid="stFileUploader"] section *,
    [data-testid="stFileUploaderDropzone"] *,
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] span {
        color: #003B73 !important;
    }

    /* Bouton "Browse files" / "Parcourir" */
    [data-testid="stFileUploader"] button,
    [data-testid="baseButton-secondary"] {
        background-color: #0060B0 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 6px !important;
    }
    [data-testid="stFileUploader"] button:hover {
        background-color: #003B73 !important;
    }

    /* --- HEADER --- */
    .header-zone { background: white; border-radius: 12px; padding: 16px 24px; margin-bottom: 24px; border-left: 6px solid #0060B0; box-shadow: 0 2px 8px rgba(0,60,176,0.08); color: #1A1A2E; }
    .header-zone p, .header-zone span, .header-zone div { color: inherit; }
    .section-title { font-size: 1.15rem; font-weight: 700; margin: 0 0 0.5rem 0; }
    .section-title-upload { color: #0060B0; }

    /* --- REPONSES ET CHUNKS --- */
    .reponse-box { background: white; border-left: 4px solid #0060B0; border-radius: 8px; padding: 16px 20px; margin-top: 16px; box-shadow: 0 2px 8px rgba(0,60,176,0.08); color: #1A1A2E; font-size: 15px; }
    .chunk-box { background: #F8F9FA; border-left: 4px solid #28A745; border-radius: 8px; padding: 12px 16px; margin: 8px 0; font-size: 14px; color: #1A1A2E; }
    .distance-bar { background: #E8F0FE; border-radius: 4px; height: 6px; margin-top: 4px; }
    .distance-fill { background: #0060B0; border-radius: 4px; height: 100%; }
    .cache-box { background: #E8F0FE; border-left: 4px solid #FFA500; border-radius: 8px; padding: 12px 16px; margin: 8px 0; font-size: 14px; color: #1A1A2E; }

    /* --- BOUTONS --- */
    .stButton > button { background-color: #0060B0; color: white; border-radius: 8px; border: none; padding: 10px 24px; font-size: 15px; font-weight: bold; width: 100%; }
    .stButton > button:hover { background-color: #003B73; }

    /* --- LABELS ET CAPTIONS --- */
    .stTextInput label, .stSelectbox label, .stFileUploader label, .stMetric label { color: #1A1A2E !important; }
    .stCaption, .stMarkdown, .stInfo, .stWarning, .stSuccess, .stError { color: #1A1A2E; }
    [data-testid="stMetric"] { background: rgba(255,255,255,0.15); border-radius: 8px; padding: 10px; }
</style>
"""