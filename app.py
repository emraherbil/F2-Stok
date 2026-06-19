import streamlit as st
import pandas as pd
import os
import base64
from pathlib import Path

# ==========================================
# 1. BAĞIMSIZ YARDIMCI FONKSİYONLAR
# ==========================================

def get_header_html(guncel_stok_col):
    return f"""
    <div style="display: flex; flex-direction: column; justify-content: center;">
        <h2 style="margin: 0; padding: 0; font-size: 1.7rem; color: #262730; line-height: 1.1;">Ofis Stok İzleme Paneli</h2>
        <span style="color: #7d7f87; font-size: 0.85rem; margin-top: 3px;">📅 <b>Son Güncelleme / Sayım Tarihi:</b> {guncel_stok_col}</span>
    </div>
    """

def get_kpi_html(label, value, color):
    # Sayısal değerleri Türkiye formatına (. binlik ayracı) çevirir
    formatted_value = f"{value:,}".replace(",", ".") if isinstance(value, (int, float)) else value
    return f"""
    <div style='background-color: rgba(28, 31, 46, 0.04); padding: 8px 15px; border-radius: 6px; border-left: 4px solid {color}; display: flex; justify-content: space-between; align-items: center; margin-top: 5px;'>
        <span style='font-size:12px; color:#555; font-weight:bold;'>{label}</span>
        <span style='font-size:1.1rem; font-weight: bold; color:#111;'>{formatted_value}</span>
    </div>
    """

def logo_to_base64(img_path):
    try:
        if os.path.exists(img_path):
            img_bytes = Path(img_path).read_bytes()
            encoded = base64.b64encode(img_bytes).decode()
            return f"data:image/png;base64,{encoded}"
    except Exception:
        pass
    return None

@st.cache_data
def load_data():
    df = pd.read_excel('Stok Sayım Arşivi-v3.1-Web.xlsm', sheet_name='Stok', engine='openpyxl')
    return df

# ==========================================
# 2. PANOLAR VE STİL (STICKY) DÜZENLEMELERİ
# ==========================================

st.set_page_config(
    page_title="F2 ICT - Ofis Stok İzleme Paneli", 
    page_icon="📦",
    layout="wide"
)

# Üst paneli kesilme olmadan ekrana sabitleyen (Sticky) kurallar
st.markdown("""
<style>
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    div[data-testid="stMainBlockContainer"] > div:first-child {
        position: -webkit-sticky;
        position: sticky;
        top: 0;
        z-index: 99999;
        background-color: white;
        padding-top: 10px;
        padding-bottom: 15px;
        border-bottom: 2px solid #eef1f6;
    }
    .stCheckbox { margin-top: 24px !important; }
    .stButton button { margin-top: 22px !important; }
    hr { margin: 0.5rem 0 !important; opacity: 0.6; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. VERİ YÜKLEME VE ANALİZ HESAPLAMALARI
# ==========================================

# Olası hataları yakalamak için try-except tüm akışı güvenle sarar
try:
    df = load_data()
    df.columns = [str(c).strip() for c in df.columns]
    
    urun_kodu_col = df.columns[1]     # B Sütunu
    urun_aciklama_col = df.columns[2] # C Sütunu
    marka_col = df.columns[3]         # D Sütunu
    grup_col = df.columns[4]          # E Sütunu
    fiyat_col = df.columns[12]        # M Sütunu
    maliyet_col = df.columns[13]      # N Sütunu
    
    sayim_sutunlari = list(df.columns[14:]) 
    guncel_stok_col = sayim_sutunlari[-1] if sayim_sutunlari else df.columns[-1]

    df[guncel_stok_col] = pd.to_numeric(df[guncel_stok_col], errors='coerce').fillna(0)
    df[maliyet_col] = pd.to_numeric(df[maliyet_col], errors='coerce').fillna(0)
    df[fiyat_col] = pd.to_numeric(df[fiyat_col], errors='coerce').fillna(0)

    # Durum Yönetimi (Session State)
    if "search_query" not in st.session_state:
        st.session_state.search_query = ""
    if "secilen_grup" not in st.session_state:
        st.session_state.secilen_grup = "Tümü"
    if "secilen_marka" not in st.session_state:
        st.session_state.secilen_marka = "Tümü"
    if "stokta_olanlar" not in st.session_state:
        st.session_state.stokta_olanlar = False

    def filtreleri_temizle():
        st.session_state.search_query = ""
        st.session_state.secilen_grup = "Tümü"
        st.session_state.secilen_marka = "Tümü"
        st.session_state.stokta_olanlar = False

    # --- SABİT ÜST PANEL CONTAINER'I ---
    with st.container():
        # Logo ve Başlık Hizalaması
        logo_src = logo_to_base64("logo.png") or logo_to_base64("logo.jpg")
        header_col1, header_col2 = st.columns([2.5, 9.5])
        
        with header_col1:
            if logo_src:
                st.markdown(f'<img src="{logo_src}" style="width: 100%; max-height: 50
