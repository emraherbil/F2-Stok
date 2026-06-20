import streamlit as st
import pandas as pd
import os
import base64
from pathlib import Path

# --- RESMİ CANLI ARAMA EKLENTİSİ ---
try:
    from st_keyup import st_keyup
except ImportError:
    st.error("Lütfen terminalde 'pip install streamlit-keyup' çalıştırın veya requirements.txt dosyanıza 'streamlit-keyup' ekleyin.")
    st.stop()
# -----------------------------------

# ==========================================
# 1. LOGO DÖNÜŞTÜRÜCÜ
# ==========================================
def logo_to_base64(img_path):
    try:
        if os.path.exists(img_path):
            img_bytes = Path(img_path).read_bytes()
            return base64.b64encode(img_bytes).decode()
    except Exception:
        pass
    return None

@st.cache_data
def load_data():
    return pd.read_excel('Stok Sayım Arşivi-v3.1-Web.xlsm', sheet_name='Stok', engine='openpyxl')

# ==========================================
# 2. SAYFA YAPILANDIRMASI
# ==========================================
st.set_page_config(
    page_title="F2 ICT - Ofis Stok İzleme Paneli", 
    page_icon="📦",
    layout="wide"
)

# Genel arayüz temizliği için temel CSS kurallaranı yüklüyoruz
st.markdown("""
    <style>
        footer {visibility: hidden !important; display: none !important;}
        .viewerBadge_container {display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}
        .stDeployButton {display: none !important;}
        header {visibility: hidden !important; display: none !important;}
        hr { display: none !important; visibility: hidden !important; }
        
        div[data-testid="stHorizontalBlock"] {
            align-items: flex-start !important;
        } 
        
        div[data-testid="stFragment"] div[data-testid="column"] {
            min-height: 75px !important;
        }

        div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(1) iframe {
            height: 76px !important;
            width: 100% !important;
        }
    </style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

VALID_USERNAME = "admin"
VALID_PASSWORD = "f2"
logo_data = logo_to_base64("logo.png") or logo_to_base64("logo.jpg")

# ==========================================
# 3. KUSURSUZ GİRİŞ EKRANI (TAM ORTALANMIŞ)
# ==========================================
if not st.session_state.logged_in:
    st.markdown("""
    <style>
        /* Ekranın kaymasını engelleyen maske */
        html, body, [data-testid="stAppViewContainer"], .stApp {
            overflow: hidden !important; 
            background-color: #f8fafc !important;
            margin: 0 !important; 
            padding: 0 !important;
            height: 100vh !important;
        }
        .block-container {
            padding: 0 !important;
            max-width: 100% !important;
        }
        /* Beyaz çerçeveyi ekrana tam ortalayan ve gereksiz uzamayı bitiren mutlak konumlandırma */
        [data-testid="stForm"] {
            position: fixed !important;
            top: 50% !important;
            left: 50% !important;
            transform: translate(-50%, -50%) !important;
            width: 380px !important;
            max-width: 90vw !important;
            height: auto !important;
            min-height: auto !important;
            padding: 35px 30px !important;
            background-color: #ffffff !important;
            border-radius: 12px !important;
            box-shadow: 0px 10px 40px rgba(0, 0, 0, 0.08) !important;
            border: 1px solid #e2e8f0 !important;
            margin: 0 !important;
            z-index: 99999 !important;
        }
        /* Şifre göz butonunu bozmayan girdi gövdesi */
        [data-baseweb="input"] {
            background-color: #f1f5f9 !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 6px !important;
        }
        /* Göz ikonu düzeltmesi */
        [data-baseweb="input"] button {
            background-color: transparent !important;
            border: none !important;
            width: auto !important;
            height: auto !important;
        }
        /* Giriş butonunu tam sığdıran ayar */
        [data-testid="stFormSubmitButton"] button {
            background-color: #1e293b !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
            height: 45px !important;
            width: 100% !important;
            transition: background-color 0.3s;
        }
        [data-testid="stFormSubmitButton"] button:hover {
            background-color: #0f172a !important;
        }        
    </style>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        if logo_data:
            st.markdown(f'<div style="text-align: center; margin-bottom: 15px;"><img src="data:image/png;base64,{logo_data}" style="max-width: 200px; height: auto;"></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align: center; font-size: 2.5rem; margin-bottom: 15px;">📦</div>', unsafe_allow_html=True)
            
        st.markdown('<div style="text-align: center; font-size: 17px; color: #64748b; margin-bottom: 15px; font-weight: 500;">Ofis Stok İzleme Paneli</div>', unsafe_allow_html=True)
        
        username_input = st.text_input("Kullanıcı Adı", placeholder="Kullanıcı adınızı yazın", label_visibility="collapsed")
        password_input = st.text_input("Şifre", type="password", placeholder="Şifrenizi yazın", label_visibility="collapsed")
        
        st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True) 
        
        submit_button = st.form_submit_button("Sisteme Giriş Yap")
        
        if submit_button:
            if username_input == VALID_USERNAME and password_input == VALID_PASSWORD:
                st.session_state.logged_in = True
                st.
