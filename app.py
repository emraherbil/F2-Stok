import streamlit as st
import pandas as pd
import os
import base64
from pathlib import Path

# 1. Sayfa Düzeni ve Başlık Ayarları
st.set_page_config(
    page_title="F2 ICT - Ofis Stok İzleme Paneli", 
    page_icon="📦",
    layout="wide"
)

# Yerel logoyu Base64'e çeviren fonksiyon
def logo_to_base64(img_path):
    try:
        if os.path.exists(img_path):
            img_bytes = Path(img_path).read_bytes()
            encoded = base64.b64encode(img_bytes).decode()
            return f"data:image/png;base64,{encoded}"
    except Exception:
        pass
    return None

# Excel Dosyasını Yükleme Fonksiyonu
@st.cache_data
def load_data():
    df = pd.read_excel('Stok Sayım Arşivi-v3.1-Web.xlsm', sheet_name='Stok', engine='openpyxl')
    return df

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

    # --- DURUM YÖNETİMİ (SESSION STATE) ---
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

    # --- GÖRSEL HATALARI DÜZELTEN VE ÜST PANELİ SABİTLEYEN GELİŞMİŞ CSS ---
    st.markdown("""
        <style>
            /* Sayfa genel boşluklarını optimize et */
            .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
            
            /* Üst paneli kesilme olmadan ekrana sabitleyen (Sticky) kurallar */
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
            
            /* Filtre bileşenleri dikey hizalamaları */
            .stCheckbox { margin-top: 24px !important; }
            .stButton button { margin-top: 22px !important; }
            
            /* Sayfa içi çizgileri hafiflet */
            hr { margin: 0.5rem 0 !important; opacity: 0.6; }
        </style>
    """, unsafe_allow_html=True)

    # --- SABİT ÜST PANEL (HEADER + FİLTRELER + KPI KARTLARI) ---
    with st.container():
        # 1. Kurumsal Logo & Başlık Alanı
        logo_src = logo_to_base64("logo.png") or logo_to_base64("logo.jpg")
        
        header_col1, header_col2 = st.columns([2.5, 9.5])
        with header_col1:
            if logo_src:
                st.markdown(f'<img src="{logo_src}" style="width: 100%; max-height: 50px; object-fit: contain; margin-top: 2px;">', unsafe_allow_html=True)
            else:
                st.markdown("<h2 style='margin:0;'>📦</h2>", unsafe_allow_html=True)
        with header_col2:
            st.markdown(f"""
            <div style="display: flex; flex-direction: column; justify-content: center;">
                <h2 style="margin: 0; padding: 0; font-size: 1.7rem; color: #262730; line-height: 1.1;">Ofis Stok İzleme Paneli</h2>
                <span style="color: #7d7f87; font-size: 0.85rem; margin-top: 3px;">📅 <b>Son Güncelleme / Sayım Tarihi:</b> {guncel_stok_col}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # 2. İstenen Sırada Düzenlenmiş Filtre Alanı (Ürün Ara -> Marka -> Ürün Grubu)
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

        # Veri Filtreleme Kuralları
        filtered_df = df.copy()
        if search_query:
            filtered_df = filtered_df[
                filtered_df[urun_kodu_col].astype(str).str.contains(search_query, case=False) | 
                filtered_df[urun_aciklama_col].astype(str).str.contains(search_query, case=False)
            ]
        if secilen_marka != "Tümü":
            filtered_df = filtered_df[filtered_df[marka_col] == secilen_marka]
        if secilen_grup != "Tümü":
            filtered_df = filtered_df[filtered_df[grup_col] == secilen_grup]
        if stokta_olanlar:
            filtered_df = filtered_df[filtered_df[guncel_stok_col] > 0]

        # 3. Şerit Tipi Kompakt KPI Kartları
        total_products = len(filtered_df)
        total_stock = int(filtered_df[guncel_stok_col].sum())
        total_cost = filtered_df[maliyet_col].sum()
        
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.markdown(f"""
            <div style='background-color: rgba(28, 31, 46, 0.04); padding: 8px 15px; border-radius: 6px; border-left: 4px solid #1E88E5; display: flex; justify-content: space-between; align-items: center; margin-top: 5px;'>
                <span style='font-size:12px; color:#555; font-weight:bold;'>📋 Toplam Çeşit:</span>
                <span style='font-size:1.1rem; font-weight: bold; color:#111;'>{total_products:,} Adet</span>
            </div>
            """.replace(",", "."), unsafe_allow_html=True)
            
        with kpi2:
            st.markdown(f"""
            <div style='background-color: rgba(28, 31, 46, 0.04); padding: 8px 15px; border-radius: 6px; border-left: 4px solid #4CAF
