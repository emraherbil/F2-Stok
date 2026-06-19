import streamlit as st
import pandas as pd
import os
import base64
from pathlib import Path

# --- YARDIMCI FONKSİYONLAR ---
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

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="F2 ICT - Ofis Stok İzleme Paneli", page_icon="📦", layout="wide")

logo_data = logo_to_base64("logo.png") or logo_to_base64("logo.jpg")

# --- GÜVENLİ CSS (Yapıyı bozmaz) ---
css_style = """
<style>
    /* Üst menü çakışmasını engellemek için ana konteynerden biraz boşluk */
    .block-container { padding-top: 1rem !important; }
    
    /* Sticky alanın yapıyı bozmaması için min-height ve z-index düzeni */
    .sticky-header-wrapper {
        position: sticky;
        top: 0;
        z-index: 998;
        background-color: white;
        padding: 10px 0;
        border-bottom: 2px solid #eef1f6;
        margin-bottom: 15px;
    }
</style>
"""
st.markdown(css_style, unsafe_allow_html=True)

# --- PANEL YAPISI (Mükemmel dediğiniz yapının revizesi) ---
# Header'ı ayrı bir container içinde sticky sınıfıyla sarmalıyoruz
with st.container():
    st.markdown('<div class="sticky-header-wrapper">', unsafe_allow_html=True)
    
    col_logo, col_title = st.columns([1, 10])
    with col_logo:
        if logo_data:
            st.markdown(f'<img src="data:image/png;base64,{logo_data}" style="height:50px;">', unsafe_allow_html=True)
    with col_title:
        st.markdown('<h2 style="margin:0; padding:0;">Ofis Stok İzleme Paneli</h2>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Geri kalan kısım yine orijinal yapınızla devam eder
try:
    df = load_data()
    # ... buraya filtreleme ve tablonuz (hide_index=True ile) gelecek ...
    st.dataframe(df, use_container_width=True, hide_index=True)
except Exception as e:
    st.error(f"Hata: {e}")
