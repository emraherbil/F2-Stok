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

    # --- KUSURSUZ SABİTLEME (STICKY) VE KESİLMEYİ ÖNLEYEN CSS ---
    st.markdown("""
        <style>
            .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
            
            /* Üst paneli tamamen kapsayan ve ekrana sabitleyen (Sticky) konteyner */
            div[data-testid="stVerticalBlock"] > div:first-child {
                position: -webkit-sticky;
                position: sticky;
                top: 2.8rem;
                z-index: 999;
                background-color: white;
                padding-bottom: 10px;
                border-bottom: 2px solid #f0f2f6;
            }
            
            .stCheckbox { margin-top: 22px !important; }
            .stButton button { margin-top: 20px !important; }
        </style>
    """, unsafe_allow_html=True)

    # --- SABİT ÜST PANEL BAŞLANGICI ---
    with st.container():
        logo_src = logo_to_base64("logo.png") or logo_to_base64("logo.jpg")
        
        header_col1, header_col2 = st.columns([2.5, 9.5])
        with header_col1:
            if logo_src:
                st.markdown(f'<img src="{logo_src}" style="width: 100%; max-height: 55px; object-fit: contain; margin-top: 5px;">', unsafe_allow_html=True)
            else:
                st.markdown("<h2 style='margin:0;'>📦</h2>", unsafe_allow_html=True)
        with header_col2:
            st.markdown(f"""
            <div style="display: flex; flex-direction: column; justify-content: center;">
                <h2 style="margin: 0; padding: 0; font-size: 1.8rem; color: #262730; line-height: 1.2;">Ofis Stok İzleme Paneli</h2>
                <span style="color: #7d7f87; font-size: 0.85rem; margin-top: 2px;">📅 <b>Son Güncelleme:</b> {guncel_stok_col}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Filtreler
        filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns([3.2, 2.4, 2.4, 2.2, 1.2])
        
        with filter_col1:
            search_query = st.text_input("📝 Ürün Ara", key="search_query", placeholder="Kod veya açıklama ara...")
            
        with filter_col2:
            tum_gruplar = ["Tümü"] + list(df[grup_col].dropna().unique())
            secilen_grup = st.selectbox("📂 Ürün Grubu", tum_gruplar, key="secilen_grup")
            
        with filter_col3:
            tum_markalar = ["Tümü"] + list(df[marka_col].dropna().unique())
            secilen_marka = st.selectbox("🏷️ Marka", tum_markalar, key="secilen_marka")

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
        if secilen_grup != "Tümü":
            filtered_df = filtered_df[filtered_df[grup_col] == secilen_grup]
        if secilen_marka != "Tümü":
            filtered_df = filtered_df[filtered_df[marka_col] == secilen_marka]
        if stokta_olanlar:
            filtered_df = filtered_df[filtered_df[guncel_stok_col] > 0]

        # Şerit Tipi Kompakt KPI Kartları
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
            <div style='background-color: rgba(28, 31, 46, 0.04); padding: 8px 15px; border-radius: 6px; border-left: 4px solid #4CAF50; display: flex; justify-content: space-between; align-items: center; margin-top: 5px;'>
                <span style='font-size:12px; color:#555; font-weight:bold;'>📦 Toplam Stok:</span>
                <span style='font-size:1.1rem; font-weight: bold; color:#111;'>{total_stock:,} Adet</span>
            </div>
            """.replace(",", "."), unsafe_allow_html=True)
            
        with kpi3:
            st.markdown(f"""
            <div style='background-color: rgba(28, 31, 46, 0.04); padding: 8px 15px; border-radius: 6px; border-left: 4px solid #FFC107; display: flex; justify-content: space-between; align-items: center; margin-top: 5px;'>
                <span style='font-size:12px; color:#555; font-weight:bold;'>💰 Toplam Maliyet:</span>
                <span style='font-size:1.1rem; font-weight: bold; color:#111;'>${total_cost:,.0f}</span>
            </div>
            """.replace(",", "."), unsafe_allow_html=True)
            
    # --- SABİT ÜST PANEL BİTİŞİ ---

    # --- AKICI VERİ TABLOSU ALANI ---
    st.markdown("<br>", unsafe_allow_html=True)
    
    gosterilecek_df = filtered_df[[urun_kodu_col, urun_aciklama_col, marka_col, grup_col, guncel_stok_col, fiyat_col, maliyet_col]].copy()
    gosterilecek_df.columns = ["Ürün Kodu", "Açıklama", "Marka", "Ürün Grubu", "Güncel Stok", "Birim Maliyet", "Toplam Maliyet"]
    
    def formatla_dolar(val):
        return f"${val:,.0f}".replace(",", ".")

    def formatla_adet(val):
        return f"{int(val):,}".replace(",", ".")

    stok_orjinal_degerler = gosterilecek_df["Güncel Stok"].copy()

    gosterilecek_df["Birim Maliyet"] = gosterilecek_df["Birim Maliyet"].apply(formatla_dolar)
    gosterilecek_df["Toplam Maliyet"] = gosterilecek_df["Toplam Maliyet"].apply(formatla_dolar)
    gosterilecek_df["Güncel Stok"] = gosterilecek_df["Güncel Stok"].apply(formatla_adet)

    def satiri_renklendir(row):
        if stok_orjinal_degerler.loc[row.name] == 0:
            return ['background-color: rgba(255, 75, 75, 0.1)'] * len(row)
        return [''] * len(row)

    sutun_ayarlari = {
        "Ürün Kodu": st.column_config.TextColumn("Ürün Kodu", alignment="left"),
        "Açıklama": st.column_config.TextColumn("Açıklama", alignment="left"),
        "Marka": st.column_config.TextColumn("Marka", alignment="left"),
        "Ürün Grubu": st.column_config.TextColumn("Ürün Grubu", alignment="left"),
        "Güncel Stok": st.column_config.TextColumn("Güncel Stok", alignment="center"),
        "Birim Maliyet": st.column_config.TextColumn("Birim Maliyet", alignment="right"),
        "Toplam Maliyet": st.column_config.TextColumn("Toplam Maliyet", alignment="right")
    }

    # Tabloyu ekrana basıyoruz
    st.dataframe(
        gosterilecek_df.style.apply(satiri_renklendir, axis=1),
        column_config=sutun_ayarlari,
        use_container_width=True,
        height=600
    )

    # --- HAFTALIK HAREKET GİRİŞ FORMU ---
    st.markdown("---")
    with st.expander("🔄 Haftalık Stok Revizyon / Hareket Giriş Formu"):
        with st.form("stok_hareket_formu"):
            secilen_urun = st.selectbox("Hareket Görecek Ürün", filtered_df[urun_kodu_col].astype(str) + " - " + filtered_df[urun_aciklama_col].astype(str))
            islem_turu = st.selectbox("İşlem Türü", ["Stok Girişi (+)", "Stok Çıkışı (-)"])
            miktar = st.number_input("Miktar", min_value=1, value=1)
            notlar = st.text_input("Açıklama / Not")
            
            submit_btn = st.form_submit_with_button("Hareketi Kaydet")
            if submit_btn:
                st.success(f"Başarılı: {secilen_urun} için {miktar} adetlik {islem_turu} sisteme girildi.")

except Exception as e:
    st.error(f"Excel dosyası analiz edilirken bir hata oluştu: {e}")
