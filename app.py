import streamlit as st
import pandas as pd
import os
import base64
from pathlib import Path

# ==========================================
# 1. BAĞIMSIZ YARDIMCI FONKSİYONLAR
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
# 2. SAYFA YAPILANDIRMASI VE KIRPILMA ÖNLEYİCİ CSS
# ==========================================

st.set_page_config(
    page_title="F2 ICT - Ofis Stok İzleme Paneli", 
    page_icon="📦",
    layout="wide"
)

logo_data = logo_to_base64("logo.png") or logo_to_base64("logo.jpg")

# Sıkışmayı ve kırpılmayı tamamen bitiren, orijinal oranları koruyan temiz CSS
css_style = """
<style>
    /* Üstten baskıyı kaldırmak için temiz bir alan tanımı */
    .block-container { padding-top: 2.5rem !important; padding-bottom: 2rem !important; }
    
    /* Logo ve Başlık Yan Yana Esnek Hizalama (Kırpılmayı Önler) */
    .custom-header-container { 
        display: flex; 
        align-items: center; 
        gap: 25px;
        margin-bottom: 10px;
    }
    .custom-logo { 
        height: 65px !important; /* Logoyu tam boy gösterir, dikeyde ezmez */
        object-fit: contain; 
    }
    .custom-title-block { 
        display: flex; 
        flex-direction: column; 
        justify-content: center; 
    }
    
    /* Filtre elemanlarının alt hizalamaları */
    .stCheckbox { margin-top: 35px !important; }
    .stButton button { margin-top: 28px !important; height: 42px !important; }
    hr { margin: 0.6rem 0 !important; opacity: 0.2; }
</style>
"""
st.markdown(css_style, unsafe_allow_html=True)

# ==========================================
# 3. VERİ OKUMA VE ÖN İŞLEME
# ==========================================

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

    if "q_search" not in st.session_state: st.session_state.q_search = ""
    if "q_grup" not in st.session_state: st.session_state.q_grup = "Tümü"
    if "q_marka" not in st.session_state: st.session_state.q_marka = "Tümü"
    if "q_stok" not in st.session_state: st.session_state.q_stok = False

    def filtreleri_temizle():
        st.session_state.q_search = ""
        st.session_state.q_grup = "Tümü"
        st.session_state.q_marka = "Tümü"
        st.session_state.q_stok = False

    # ==========================================
    # 4. ÜST PANEL (FERAH VE DÜZGÜN BAŞLIK ALANI)
    # ==========================================
    
    if logo_data:
        header_html = f"""
        <div class="custom-header-container">
            <img src="data:image/png;base64,{logo_data}" class="custom-logo">
            <div class="custom-title-block">
                <h2 style="margin:0; padding:0; font-size:1.95rem; color:#262730; font-weight:700; line-height:1.2;">Ofis Stok İzleme Paneli</h2>
                <span style="color:#7d7f87; font-size:0.85rem; margin-top:4px;">📅 <b>Son Güncelleme / Sayım Tarihi:</b> {c_stok}</span>
            </div>
        </div>
        """
    else:
        header_html = f"""
        <div class="custom-header-container">
            <h1 style="margin:0;">📦</h1>
            <div class="custom-title-block">
                <h2 style="margin:0; padding:0; font-size:1.95rem; color:#262730; font-weight:700;">Ofis Stok İzleme Paneli</h2>
                <span style="color:#7d7f87; font-size:0.85rem; margin-top:4px;">📅 <b>Son Güncelleme / Sayım Tarihi:</b> {c_stok}</span>
            </div>
        </div>
        """
    st.markdown(header_html, unsafe_allow_html=True)
    st.markdown("---")

    # Filtre Blokları (Orijinal Düzen)
    col1, col2, col3, col4, col5 = st.columns([3.2, 2.4, 2.4, 2.2, 1.2])
    
    with col1: 
        v_search = st.text_input("📝 Ürün Ara", key="q_search
