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

# Base64 logo dönüşümü
logo_data = logo_to_base64("logo.png") or logo_to_base64("logo.jpg")

# Alanın ekranda donmasını (Sticky) sağlayan ve kayarken bozulmasını önleyen CSS injection
css_style = """
<style>
    /* Streamlit varsayılan üst boşluğunu kaldır */
    .block-container { padding-top: 0rem !important; padding-bottom: 1rem !important; }
    
    /* ÜST PANELİ EKRANA ÇİVİLEME VE GÖLGE EFEKTİ */
    div[data-testid="stMainBlockContainer"] > div:first-child {
        position: -webkit-sticky;
        position: sticky;
        top: 2.875rem !important;
        z-index: 999999 !important;
        background-color: #ffffff !important;
        padding-top: 20px !important;
        padding-bottom: 15px !important;
        border-bottom: 2px solid #f1f3f7 !important;
        box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.04) !important;
    }
    
    /* Logo ve Başlık Hizalama Şablonu */
    .custom-header-container {
        display: flex;
        align-items: center;
        gap: 20px;
        padding-bottom: 5px;
    }
    .custom-logo {
        height: 55px;
        object-fit: contain;
    }
    .custom-title-block {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    /* Form Elemanları ve Butonun Milimetrik Dikey Hizası */
    .stCheckbox { margin-top: 32px !important; }
    .stButton button { margin-top: 28px !important; height: 42px !important; }
    
    /* Ayırıcı Çizgileri Küçült */
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

    # State Yönetimi
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

    # ==========================================
    # 4. SABİTLENMİŞ ÜST KATMAN (STICKY CONTAINER)
    # ==========================================
    with st.container():
        
        # Flexbox Logo & Başlık
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

        # Filtre Sutünları (Sıralama: Ürün Ara -> Marka -> Ürün Grubu)
        filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns([3.2, 2.4, 2.4, 2.2, 1.2])
        
        with filter_col1:
            search_query = st.text_input("📝 Ürün Ara", key="search_query", placeholder="Kod veya açıklama ara...")
            
        with filter_col2:
            tum_markalar = ["Tümü"] + list(df[marka_col].dropna().unique())
            secilen_marka = st.selectbox("🏷️ Marka", tum_markalar, key="secilen_marka")
            
        with filter_col3:
            tum_gruplar = ["Tümü"] + list(df[grup_col].dropna().unique())
            secilen_grup = st.selectbox("📂 Ürün Grubu", tum_gruplar, key="secilen_grup")

        with filter_col4:
            stokta_olanlar = st.checkbox("🚫 Tükenenleri Gizle", key="stokta_olanlar")
            
        with filter_col5:
            st.button("🧹 Temizle", on_click=filtreleri_temizle, use_container_width=True)

        # Filtreleme İşlemleri
        filtered_df = df.copy()
        if search_query:
            c1 = filtered_df[urun_kodu_col].astype(str).str.contains(search_query, case=False)
            c2 = filtered_df[urun_aciklama_col].astype(str).str.contains(search_query, case=False)
            filtered_df = filtered_df[c1 | c2]
        if secilen_marka != "Tümü":
            filtered_df = filtered_df[filtered_df[marka_col] == secilen_marka]
        if secilen_grup != "Tümü":
            filtered_df = filtered_df[filtered_df[grup_col] == secilen_grup]
        if stokta_olanlar:
            filtered_df = filtered_df[filtered_df[guncel_stok_col] > 0]

        # Kompakt KPI Kart Tasarımları
        total_products = len(filtered_df)
        total_stock = int(filtered_df[guncel_stok_col].sum())
        total_cost = filtered_df[maliyet_col].sum()
        
        def generate_kpi_card(label, val_str, border_color):
            return f"""
            <div style='background-color: rgba(28, 31, 46, 0.03); padding: 10px 15px; border-radius: 6px; border-left: 5px solid {border_color}; display: flex; justify-content: space-between; align-items: center;'>
                <span style='font-size:13px; color:#555; font-weight:bold;'>{label}</span>
                <span style='font-size:1.15rem; font-weight: 800; color:#111;'>{val_str}</span>
            </div>
            """

        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.markdown(generate_kpi_card("📋 Toplam Çeşit:", f"{total_products:,}".replace(",", ".") + " Adet", "#1E88E5"), unsafe_allow_html=True)
        with kpi2:
            st.markdown(generate_kpi_card("📦 Toplam Stok:", f"{total_stock:,}".replace(",", ".") + " Adet", "#4CAF50"), unsafe_allow_html=True)
        with kpi3:
            st.markdown(generate_kpi_card("💰 Toplam Maliyet:", f"${total_cost:,.0f}".replace(",", "."), "#FFC107"), unsafe_allow_html=True)

    # ==========================================
    # 5. AKICI (SCROLL) TABLO ALANI
    # ==========================================
    st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)
    
    gosterilecek_df = filtered_df[[urun_kodu_col, urun_aciklama_col, marka_col, grup_col, guncel_stok_col, fiyat_col, maliyet_col]].copy()
    gosterilecek_df.columns = ["Ürün Kodu", "Açıklama", "Marka", "Ürün Grubu", "Güncel Stok", "Birim Maliyet", "Toplam Maliyet"]
    
    stok_orjinal_degerler = gosterilecek_df["Güncel Stok"].copy()

    gosterilecek_df["Birim Maliyet"] = gosterilecek_df["Birim Maliyet"].apply(lambda v: f"${v:,.0f}".replace(",", "."))
    gosterilecek_df["Toplam Maliyet"] = gosterilecek_df["Toplam Maliyet"].apply(lambda v: f"${v:,.0f}".replace(",", "."))
    gosterilecek_df["Güncel Stok"] = gosterilecek_df["Güncel Stok"].apply(lambda v: f"{int(v):,}".replace(",", "."))

    def satiri_renklendir(row):
        if stok_orjinal_degerler.loc[row.name] == 0:
            return ['background-color: rgba(255, 75, 75, 0.08)'] * len(row)
        return [''] * len(row)

    # Kesilmeyi önlemek için sütun konfigürasyonları tamamen tek satıra indirgendi
    sutun_ayarlari = {
        "Ürün Kodu": st.column_config.TextColumn("Ürün Kodu", alignment="left"),
        "Açıklama": st.column_config.TextColumn("Açıklama", alignment="left"),
        "Marka": st.column_config.TextColumn("Marka", alignment="left"),
        "Ürün Grubu": st.column_config.TextColumn("Ürün Grubu", alignment="left"),
