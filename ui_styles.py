"""Styles CSS et bloc d'en-tete HTML pour l'interface Streamlit."""

CSS = """
<style>
    .stApp { background-color: #F5F7FA; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #003B73 0%, #0060B0 100%); }
    [data-testid="stSidebar"] * { color: white !important; }
    .header-zone { background: white; border-radius: 12px; padding: 16px 24px; margin-bottom: 24px; border-left: 6px solid #0060B0; box-shadow: 0 2px 8px rgba(0,60,176,0.08); }
    .reponse-box { background: white; border-left: 4px solid #0060B0; border-radius: 8px; padding: 16px 20px; margin-top: 16px; box-shadow: 0 2px 8px rgba(0,60,176,0.08); color: #1A1A2E; font-size: 15px; }
    .chunk-box { background: #F8F9FA; border-left: 4px solid #28A745; border-radius: 8px; padding: 12px 16px; margin: 8px 0; font-size: 14px; color: #1A1A2E; }
    .distance-bar { background: #E8F0FE; border-radius: 4px; height: 6px; margin-top: 4px; }
    .distance-fill { background: #0060B0; border-radius: 4px; height: 100%; }
    .cache-box { background: #E8F0FE; border-left: 4px solid #FFA500; border-radius: 8px; padding: 12px 16px; margin: 8px 0; font-size: 14px; color: #1A1A2E; }
    .stButton > button { background-color: #0060B0; color: white; border-radius: 8px; border: none; padding: 10px 24px; font-size: 15px; font-weight: bold; width: 100%; }
    .stButton > button:hover { background-color: #003B73; }
    .stTextInput > div > div > input { border: 2px solid #0060B0; border-radius: 8px; font-size: 15px; }
    [data-testid="stFileUploader"] { border: 2px dashed #0060B0; border-radius: 8px; background: white; }
    [data-testid="stMetric"] { background: rgba(255,255,255,0.15); border-radius: 8px; padding: 10px; }
</style>
"""

HEADER = """
<div class="header-zone">
    <span style="font-size:40px">factory</span>
    <div>
        <p style="font-size:26px;font-weight:bold;color:#003B73;margin:0;">Chat GCT</p>
        <p style="font-size:13px;color:#666;margin:0;">Assistant IA Local Groupe Chimique Tunisien | 100% hors ligne</p>
        <p style="font-size:11px;color:#999;margin:0;">Avec cache de questions/reponses</p>
        <p style="font-size:10px;color:#28A745;margin:0;">Nettoyage avance active</p>
    </div>
</div>
"""
