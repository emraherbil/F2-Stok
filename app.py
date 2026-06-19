import streamlit as st
import pandas as pd
import os
import base64
from pathlib import Path

# ==========================================
# 1. BAĞIMSIZ GELİŞMİŞ GÖRSEL ŞABLONLAR
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
# 2. SAYFA YAPILANDIRMASI VE CSS SİHİRBAZI
# ==========================================

st.set_page_config(
    page_title="F2 ICT - Ofis Stok İzleme Paneli", 
    page_icon="📦",
    layout="wide"
)

logo_data = logo_to_base64("logo.png") or logo_to_base64("logo.jpg")

css_style = """
<style>
    .block-container { padding-top: 0rem !important; padding-bottom: 1rem !important; }
    
    div[data-testid="stMainBlockContainer"] > div:first-child {
        position: -webkit-sticky;
        position: sticky;
        top: 0;
        z-index: 9999992 !important;
        background-color: #ffffff !important;
        padding-top: 15px !important;
        padding-bottom: 10px !important;
        padding-right: 120px !important; /* Sağdaki menü çakışmasını engellemek için eklendi */
        border-bottom: 2px solid #eef1f6 !important;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.03);
    }
    
    .custom-header-container {
        display: flex;
        align-items: center;
        gap: 20px;
        padding-bottom: 5px;
    }
    .custom-logo { height: 50px; object-fit: contain; }
    .custom-title-block { display: flex; flex-direction: column; justify-content: center; }
    
    .stCheckbox { margin-top: 30px !important; }
    .stButton button { margin-top: 28px !important; height: 42px !important; }
    hr { margin: 0.6rem 0 !important; opacity: 0.4; }
</style>
"""
st.markdown(css_style, unsafe_allow_html=True)

# ==========================================
# 3. VERİ OKUMA VE ÖN İŞLEME
# ==========================================

try:
    df = load_data()
    df.columns = [str(c).strip() for c in df.columns]
    
    urun_kodu_col, urun_aciklama_col = df.columns[1], df.columns[2]
    marka_col, grup_col = df.columns[3], df.columns[4]
    fiyat_col, maliyet_col = df.columns[12], df.columns[13]
    
    sayim_sutunlari = list(df.columns[14:]) 
    guncel_stok_col = sayim_sutunlari[-1] if sayim_sutunlari else df.columns[-1]

    df[guncel_stok_col] = pd.to_numeric(df[guncel_stok_col], errors='coerce').fillna(0)
    df[maliyet_col] = pd.to_numeric(df[maliyet_col], errors='coerce').fillna(0)
    df[fiyat_col] = pd.to_numeric(df[fiyat_col], errors='coerce').fillna(0)

    # State Yönetimi
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
    # 4. TAMAMI SABİTLENMİŞ ÜST PANEL
    # ==========================================
    with st.container():
        header_html = f"""
        <div class="custom-header-container">
            {'<img src="data:image/png;base64,' + logo_data + '" class="custom-logo">' if logo_data else ''}
            <div class="custom-title-block">
                <h2 style="margin:0; padding:0; font-size:1.75rem; color:#262730; font-weight:700;">Ofis Stok İzleme Paneli</h2>
                <span style="color:#7d7f87; font-size:0.85rem; margin-top:2px;">📅 <b>Son Güncelleme:</b> {guncel_stok_col}</span>
            </div>
        </div>
        """
        st.markdown(header_html, unsafe_allow_html=True)
        st.markdown("---")

        filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns([3.2, 2.4, 2.4, 2.2, 1.2])
        with filter_col1: search_query = st.text_input("📝 Ürün Ara", key="search_query")
        with filter_col2: secilen_marka = st.selectbox("🏷️ Marka", ["Tümü"] + list(df[marka_col].dropna().unique()), key="secilen_marka")
        with filter_col3: secilen_grup = st.selectbox("📂 Ürün Grubu", ["Tümü"] + list(df[grup_col].dropna().unique()), key="secilen_grup")
        with filter_col4: stokta_olanlar = st.checkbox("🚫 Tükenenleri Gizle", key="stokta_olanlar")
        with filter_col5: st.button("🧹 Temizle", on_click=filtreleri_temizle, use_container_width=True)

        # Filtreleme
        filtered_df = df.copy()
        if search_query:
            filtered_df = filtered_df[filtered_df[urun_kodu_col].astype(str).str.contains(search_query, case=False) | filtered_df[urun_aciklama_col].astype(str).str.contains(search_query, case=False)]
        if secilen_marka != "Tümü": filtered_df = filtered_df[filtered_df[marka_col] == secilen_marka]
        if secilen_grup != "Tümü": filtered_df = filtered_df[filtered_df[grup_col] == secilen_grup]
        if stokta_olanlar: filtered_df = filtered_df[filtered_df[guncel_stok_col] > 0]

        # KPI
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("📋 Toplam Çeşit", f"{len(filtered_df):,}")
        kpi2.metric("📦 Toplam Stok", f"{int(filtered_df[guncel_stok_col].sum()):,}")
        kpi3.metric("💰 Toplam Maliyet", f"${filtered_df[maliyet_col].sum():,.0f}")

    # ==========================================
    # 5. VERİ TABLOSU
    # ==========================================
    st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
    out_df = filtered_df[[urun_kodu_col, urun_aciklama_col, marka_col, grup_col, guncel_stok_col, fiyat_col, maliyet_col]].copy()
    out_df.columns = ["Ürün Kodu", "Açıklama", "Marka", "Ürün Grubu", "Güncel Stok", "Birim Maliyet", "Toplam Maliyet"]
    
    st.dataframe(out_df, use_container_width=True, hide_index=True, height=600)

    # ==========================================
    # 6. ALT BÖLÜM
    # ==========================================
    st.markdown("---")
    with st.expander("🔄 Haftalık Stok Revizyon"):
        with st.form("stok_hareket_formu"):
            secilen_urun = st.selectbox("Ürün", filtered_df[urun_kodu_col].astype(str) + " - " + filtered_df[urun_aciklama_col].astype(str))
            if st.form_submit_button("Hareketi Kaydet"): st.success("Başarılı.")

except Exception as e:
    st.error(f"Hata: {e}")
