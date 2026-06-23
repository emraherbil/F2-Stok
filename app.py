import streamlit as st
import pandas as pd
import os
import base64
from pathlib import Path
from st_keyup import st_keyup

# ==========================================
# 1. SAYFA YAPILANDIRMASI VE KÜRESEL STİLLER
# ==========================================
st.set_page_config(
    page_title="F2 ICT - Ofis Stok İzleme Paneli", 
    page_icon="📦",
    layout="wide"
)

# 🎯 ZIPLAMAYI VE KAYMAYI ENGELLEYEN MİLİMETRİK HİZALAMA CSS'İ
st.markdown("""
    <style>
        footer {visibility: hidden !important; display: none !important;}
        .viewerBadge_container {display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}
        .stDeployButton {display: none !important;}
        header {visibility: hidden !important; display: none !important;}
        
        html, body, .stApp { background-color: #ffffff !important; }
        
        .block-container { 
            display: block !important;
            padding-top: 1.5rem !important; 
            padding-bottom: 1.5rem !important; 
            max-width: 100% !important;
        }
        
        /* Üst başlık alanını sabitle */
        div[data-testid="stVerticalBlock"] > div:first-child {
            position: sticky !important;
            top: 0px !important;
            background-color: white !important;
            z-index: 9999 !important;
            padding-bottom: 15px !important;
        }
        
        .custom-header-container { 
            display: flex; 
            align-items: center; 
            gap: 25px; 
            padding-top: 5px;
            padding-bottom: 5px;
        }
        .custom-logo { height: 60px; object-fit: contain; }
        .custom-title-block { display: flex; flex-direction: column; justify-content: center; }
        
        /* 🎯 Kolon yapısını serbest bırakıp eleman bazlı hizalama yapıyoruz */
        div[data-testid="column"] {
            display: block !important;
        }
        
        /* Form elemanlarının genişliklerini eşitle */
        div[data-testid="column"] .stFormSubmitButton, 
        div[data-testid="column"] .stButton,
        div[data-testid="column"] .stTextInput,
        div[data-testid="column"] .stSelectbox {
            margin-bottom: 0px !important;
            width: 100% !important;
        }

        /* 🎯 ARAMA KUTUSU ALANINI KİLİTLEME (MİLİMETRİK HİZALAMA): 
           st_keyup iframe'i silinse bile altındaki taşıyıcı kutuyu selectbox'larla 
           aynı dikey hizaya (baseline) oturtmak için üstten 2px boşluk verip alanı kilitliyoruz. */
        div[data-testid="column"]:first-child div.element-container:has(iframe) {
            min-height: 42px !important;
            height: 42px !important;
            max-height: 42px !important;
            margin-top: 2px !important;
        }

        div[data-testid="stCustomComponentV1"] {
            min-height: 42px !important;
            height: 42px !important;
            margin-bottom: 0px !important;
            width: 100% !important;
        }
        
        iframe[title*="st_keyup"] {
            height: 42px !important;
            min-height: 42px !important;
            margin-bottom: 0px !important;
            display: block !important;
        }

        /* Checkbox dikey hizalaması: Diğer kutuların üst çizgisiyle kusursuz hizalanması için */
        div[data-testid="stCheckbox"] { 
            padding-top: 25px !important;
            padding-bottom: 0px !important; 
        }

        /* Temizle Butonunun Dikey Konumu: Üst
