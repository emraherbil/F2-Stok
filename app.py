import streamlit as st
import pandas as pd
import os
import base64
from pathlib import Path

# 1. FONKSİYONLAR EN ÜSTTE TANIMLI OLMALI
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

# 2. SAYFA AYARLARI
st.set_page_config(page_title="F2 ICT - Ofis Stok İzleme Paneli", page_icon="📦", layout="wide")

# 3. CSS VE LOGO (Fonksiyonun tanımlandığından emin olarak)
logo_data = logo_to_base64("logo.png") or logo_to_base64("logo.jpg")

css_style = """
<style>
    .block-container { padding-top: 1rem !important; }
    .sticky-header {
        position: fixed; top: 0; left: 0; width: 100%;
        background-color: white; z-index: 998;
        padding: 10px 5%; border-bottom: 2px solid #eef1f6;
    }
    .main-content { margin-top: 100px; }
    .custom-header-container { display: flex; align-items: center; gap: 20px; }
    .custom-logo { height: 45px; object-fit: contain; }
</style>
"""
st.markdown(css_style, unsafe_allow_html=True)

# 4. UYGULAMA MANTIĞI
try:
    # Header kısmı
    header_html = f"""
    <div class="sticky-header">
        <div class="custom-header-container">
            {'<img src="data:image/png;base64,' + logo_data + '" class="custom-logo">' if logo_data else ''}
            <h2 style="margin:0;">Ofis Stok İzleme Paneli</h2>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
    
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    df = load_data()
    # Filtreleme ve tablo işlemleriniz buraya gelecek
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Uygulama Hatası: {e}")
