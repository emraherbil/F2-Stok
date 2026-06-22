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
# 1. SAYFA YAPILANDIRMASI VE SABİT CSS
# ==========================================
st.set_page_config(
    page_title="F2 ICT - Ofis Stok İzleme Paneli", 
    page_icon="📦",
    layout="wide"
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

VALID_USERNAME = "admin"
VALID_PASSWORD = "f2"

# Ortak elementleri ve Streamlit araç çubuklarını gizleyen CSS
st.markdown("""
    <style>
        footer {visibility: hidden !important; display: none !important;}
        .viewerBadge_container {display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}
        .stDeployButton {display: none !important;}
        header {visibility: hidden !important; display: none !important;}
        hr { display: none !important; visibility: hidden !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOGO VE ÖNBELLEK FONKSİYONLARI
# ==========================================
def logo_to_base64(img_path):
    try:
        if os.path.exists(img_path):
            img_bytes = Path(img_path).read_bytes()
            return base64.b64encode(img_bytes).decode()
    except Exception:
        pass
    return None

logo_data = logo_to_base64("logo.png") or logo_to_base64("logo.jpg")

@st.cache_data(ttl=600)
def load_data():
    return pd.read_excel('Stok Sayım Arşivi-v3.1-Web.xlsm', sheet_name='Stok', engine='openpyxl')

# ==========================================
# 3. GİRİŞ EKRANI (BEYAZ ÇERÇEVESİ DÜZELTİLMİŞ)
# ==========================================
if not st.session_state.logged_in:
    # Giriş ekranına özel kusursuz kart mimarisi
    st.markdown("""
    <style>
        html, body, .stApp { 
            background-color: #f8fafc !important; 
        }
        
        /* ORTAK KART YAPISI: Ortadaki sütunun kendisini beyaz karta dönüştürüyoruz */
        div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(2) {
            background-color: #ffffff !important;
            padding: 40px 35px !important;
            border-radius: 14px !important;
            box-shadow: 0px 10px 40px rgba(0, 0, 0, 0.05) !important;
            border: 1px solid #e2e8f0 !important;
        }
        
        /* Input alanlarını estetik gri yapıyoruz */
        [data-testid="stAppViewContainer"] [data-baseweb="input"] {
            background-color: #f1f5f9 !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 8px !important;
        }
        
        /* Butonun alt boşluklarını sıfırlıyoruz */
        div[data-testid="element-container"] {
            margin-bottom: 0px !important;
        }
        
        /* BUTONU KARTIN İÇİNDE TAM ORTALAYAN CSS */
        div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(2) div[data-testid="stButton"] {
            display: flex !important;
            justify-content: center !important;
            margin-top: 25px !important;
        }
        
        div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(2) div[data-testid="stButton"] button {
            width: fit-content !important;
            padding: 0 45px !important;
            background-color: #1e293b !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
            height: 44px !important;
            font-size: 14px !important;
            transition: background-color 0.2s !important;
        }
        
        div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(2) div[data-testid="stButton"] button:hover {
            background-color: #0f172a !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Dikeyde ortalama payı
    st.markdown("<div style='margin-top: 14vh;'></div>", unsafe_allow_html=True)
    
    # Sayfayı dengeli 3 sütuna bölüyoruz
    col_left, col_center, col_right = st.columns([5, 2.4, 5])
    
    with col_center:
        # Logo Alanı
        if logo_data:
            st.markdown(f'<div style="text-align: center; margin-bottom: 18px;"><img src="data:image/png;base64,{logo_data}" style="max-width: 210px; height: auto;"></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align: center; font-size: 2.5rem; margin-bottom: 18px;">📦</div>', unsafe_allow_html=True)
            
        # Başlık Bilgisi
        st.markdown('<div style="text-align: center; font-size: 17px; color: #475569; margin-bottom: 25px; font-weight: 600; font-family: sans-serif;">Ofis Stok İzleme Paneli</div>', unsafe_allow_html=True)
        
        # Giriş Elemanları (Ekstra hiçbir HTML div yok, tertemiz render edilir)
        username_input = st.text_input("Kullanıcı Adı", placeholder="Kullanıcı adınızı yazın", label_visibility="collapsed", key="login_user")
        password_input = st.text_input("Şifre", type="password", placeholder="Şifrenizi yazın", label_visibility="collapsed", key="login_pass")
        
        # Giriş Butonu
        submit_button = st.button("Sisteme Giriş Yap")

        # Doğrulama Kontrolü
        if submit_button:
            if username_input == VALID_USERNAME and password_input == VALID_PASSWORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                st.error("Hatalı kullanıcı adı veya şifre!")

# ==========================================
# 4. ANA PANEL (BAŞARILI GİRİŞ SONRASI)
# ==========================================
else:
    # Ana panel açıldığında arka planı beyaz yap ve genişlik kısıtlamalarını kaldır
    st.markdown("""
    <style>
        html, body, .stApp { background-color: #ffffff !important; }
        .block-container { 
            display: block !important;
            padding-top: 1.5rem !important; 
            padding-bottom: 1.5rem !important; 
            max-width: 100% !important;
        }
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
        
        div[data-testid="stHorizontalBlock"] { align-items: flex-start !important; } 
        div[data-testid="stHorizontalBlock"] div[data-testid="stCheckbox"] { margin-top: 32px !important; }

        /* Filtre alanındaki temizle butonu */
        .stButton button { 
            margin-top: 24px !important;
            height: 40px !important; 
            width: 100% !important; 
            background-color: #1e293b !important; 
            color: white !important; 
            border: none !important; 
            border-radius: 4px !important;
        }
    </style>
    """, unsafe_allow_html=True)

    try:
        df = load_data()
        df.columns = [str(c).strip() for c in df.columns]
        
        c_kod = df.columns[1]     
        c_tanim = df.columns[2] 
        c_marka = df.columns[3]         
        c_grup = df.columns[4]          
        c_fiyat = df.columns[12]        
        c_maliyet = df.columns[13]      
        
        sayim_cols = list(df.columns[14:]) 
        c_stok = sayim_cols[-1] if sayim_cols else df.columns[-1]

        df[c_stok] = pd.to_numeric(df[c_stok], errors='coerce').fillna(0)
        df[c_maliyet] = pd.to_numeric(df[c_maliyet], errors='coerce').fillna(0)
        df[c_fiyat] = pd.to_numeric(df[c_fiyat], errors='coerce').fillna(0)

        if logo_data:
