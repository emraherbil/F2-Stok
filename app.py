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
    df = pd.read_excel('Stok Sayım Arşivi-v3.1-Web.xlsm', sheet_name='Stok', engine='openpyxl')
    return df

# ==========================================
# 2. SAYFA YAPILANDIRMASI VE GELİŞMİŞ CSS
# ==========================================

st.set_page_config(
    page_title="F2 ICT - Ofis Stok İzleme Paneli", 
    page_icon="📦",
    layout="wide"
)

logo_data = logo_to_base64("logo.png") or logo_to_base64("logo.jpg")

# Tüm Üst Paneli (Header + Filtreler + KPI) tek bir gövdede sabitleyen CSS
css_style = """
<style>
    /* Sayfa genel boşluklarını sıfırla */
    .block-container { padding-top: 0rem !important; padding-bottom: 1rem !important; }
    
    /* EN DIŞ ANA SARMALAYICIYI BUL VE İÇİNDEKİ İLK BÜYÜK BLOĞU SABİTLE */
    div[data-testid="stMainBlockContainer"] > div:first-child > div:first-child {
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 2.875rem !important;
        z-index: 999999 !important;
        background-color: #ffffff !important;
        padding-top: 20px !important;
        padding-bottom: 20px !important;
        border-bottom: 3px solid #eef1f6 !important;
        box-shadow: 0px 12px 30px rgba(0, 0, 0, 0.06) !important;
    }
    
    /* İçerideki alt bileşenlerin (tablonun) sızmasını kesin olarak önle */
    div[data-testid="stMainBlockContainer"] > div:first-child > div:first-child * {
        background-color: transparent;
    }
    
    /* Input kutuları ve kartların arka planlarını koru */
    div[data-testid="stMainBlockContainer"] > div:first-child > div:first-child .stTextInput div,
    div[data-testid="stMainBlockContainer"] > div:first-child > div:first-child .stSelectbox div,
    div[data-testid="stMainBlockContainer"] > div:first-child > div:first-child [data-testid="stMarkdownContainer"] div {
        background-color: inherit;
    }

    /* Logo ve Başlık Tasarımı */
    .custom-header-container { display: flex; align-items: center; gap: 20px; padding-bottom: 5px; background: #fff !important; }
    .custom-logo { height: 55px; object-fit: contain; background: #fff !important; }
    .custom-title-block { display: flex; flex-direction: column; justify-content: center; background: #fff !important; }
    
    /* Dikey Hizalama Ayarları */
    .stCheckbox { margin-top: 32px !important; }
    .stButton button { margin-top: 28px !important; height: 42px !important; }
    hr { margin: 0.5rem 0 !important; opacity: 0.3; }
</style>
"""
st.markdown(css_style, unsafe_allow_html=True)

# ==========================================
# 3. VERİ OKUMA VE ÖN İŞLEME
# ==========================================

try:
    df = load_data()
    df.columns = [str(c).strip() for c in df.columns]
    
    urun_kodu_col = df.columns[1]     
    urun_aciklama_col = df.columns[2] 
    marka_col = df.columns[3]         
    grup_col = df.columns[4]          
    fiyat_col = df.columns[12]        
    maliyet_col = df.columns[13]      
    
    sayim_sutunlari = list(df.columns[14:]) 
    guncel_stok_col = sayim_sutunlari[-1] if sayim_sutunlari else df.columns[-1]

    df[guncel_stok_col] = pd.to_numeric(df[guncel_stok_col], errors='coerce').fillna(0)
    df[maliyet_col] = pd.to_numeric(df[maliyet_col], errors='coerce').fillna(0)
    df[fiyat_col] = pd.to_numeric(df[fiyat_col], errors='coerce').fillna(0)

    if "search_query" not in st.session_state: st.session_state.search_query = ""
    if "secilen_grup" not in st.session_state: st.session_state.secilen_grup = "Tümü"
    if "secilen_marka" not in st.session_state: st.session_state.secilen_marka = "Tümü"
    if "stokta_olanlar" not in st.session_state: st.session_state.stokta_olanlar = False

    def filtreleri_temizle():
        st.session_state.search_query = ""
        st.session_state.secilen_grup = "Tümü"
        st.session_state.secilen_marka = "Tümü"
        st.session_state.stokta_olanlar = False

    # ==========================================
    # 4. TEK PARÇA HALİNDE DONAN PANEL (STICKY MASTER ZONE)
    # ==========================================
    # Bu dış container içindeki HER ŞEY (Logo, Filtreler, KPI) tek bir gövde olarak yukarıya kilitlenir.
    with st.container():
        
        # Logo & Başlık
        if logo_data:
            header_html = f"""
            <div class="custom-header-container">
                <img src="data:image/png;base64,{logo_data}" class="custom-logo">
                <div class="custom-title-block">
                    <h2 style="margin:0; padding:0; font-size:1.75rem; color:#262730; font-weight:700;">Ofis Stok İzleme Paneli</h2>
                    <span style="color:#7d7f87; font-size:0.85rem; margin-top:2px;">📅 <b>Son Güncelleme / Sayım Tarihi:</b> {guncel_stok_col}</span>
                </div>
            </div>
            """
        else:
            header_html = f"""
            <div class="custom-header-container">
                <h1 style="margin:0;">📦</h1>
                <div class="custom-title-block">
                    <h2 style="margin:0; padding:0; font-size:1.75rem; color:#262730; font-weight:700;">Ofis Stok İzleme Paneli</h2>
                    <span style="color:#7d7f87; font-size:0.85rem; margin-top:2px;">📅 <b>Son Güncelleme / Sayım Tarihi:</b> {guncel_stok_col}</span>
                </div>
            </div>
            """
        st.markdown(header_html, unsafe_allow_html=True)
        st.markdown("---")

        # Filtre Kolonları
        filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns([3.2, 2.4, 2.4, 2.2, 1.2])
        
        with filter_col1: search_query = st.text_input("📝 Ürün Ara", key="search_query", placeholder="Kod veya açıklama ara...")
        with filter_col2: secilen_marka = st.selectbox("🏷️ Marka", ["Tümü"] + list(df[marka_col].dropna().unique()), key="secilen_marka")
        with filter_col3: secilen_grup = st.selectbox("📂 Ürün Grubu", ["Tümü"] + list(df[grup_col].dropna().unique()), key="secilen_grup")
        with filter_col4: stokta_olanlar = st.checkbox("🚫 Tükenenleri Gizle", key="stokta_olanlar")
        with filter_col5: st.button("🧹 Temizle", on_click=filtreleri_temizle, use_container_width=True)

        # Filtreleme Mantığı
        filtered_df = df.copy()
        if search_query:
            c1 = filtered_df[urun_kodu_col].astype(str).str.contains(search_query, case=False)
            c2 = filtered_df[urun_aciklama_col].astype(str).str.contains(search_query, case=False)
            filtered_df = filtered_df[c1 | c2]
        if secilen_marka != "Tümü": filtered_df = filtered_df[filtered_df[marka_col] == secilen
