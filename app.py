import streamlit as st
import pandas as pd
import os

# 1. Sayfa Düzeni ve Başlık Ayarları (Geniş Ekran Modu)
st.set_page_config(
    page_title="F2 ICT - Ofis Stok İzleme Paneli", 
    page_icon="📦",
    layout="wide"
)

# Excel Dosyasını Yükleme Fonksiyonu
@st.cache_data
def load_data():
    df = pd.read_excel('Stok Sayım Arşivi-v3.1-Web.xlsm', sheet_name='Stok', engine='openpyxl')
    return df

try:
    df = load_data()
    
    # Sütun İsimlerini Temizleme
    df.columns = [str(c).strip() for c in df.columns]
    
    # Sütunların Tespiti (B, C, D, E, M, N)
    urun_kodu_col = df.columns[1]     # B Sütunu
    urun_aciklama_col = df.columns[2] # C Sütunu
    marka_col = df.columns[3]         # D Sütunu
    grup_col = df.columns[4]          # E Sütunu
    fiyat_col = df.columns[12]        # M Sütunu
    maliyet_col = df.columns[13]      # N Sütunu
    
    # En son sayım yapılan sütunu bulma
    sayim_sutunlari = list(df.columns[14:]) 
    guncel_stok_col = sayim_sutunlari[-1] if sayim_sutunlari else df.columns[-1]

    # Sayısal veri tiplerini temizleme ve garantiye alma
    df[guncel_stok_col] = pd.to_numeric(df[guncel_stok_col], errors='coerce').fillna(0)
    df[maliyet_col] = pd.to_numeric(df[maliyet_col], errors='coerce').fillna(0)
    df[fiyat_col] = pd.to_numeric(df[fiyat_col], errors='coerce').fillna(0)

    # --- ÜST BAŞLIK & KURUMSAL LOGO ALANI (CSS FLEXBOX İLE KUSURSUZ HİZALAMA) ---
    logo_yolu = "logo.png" if os.path.exists("logo.png") else ("logo.jpg" if os.path.exists("logo.jpg") else "")
    
    if logo_yolu:
        # Logo ve başlığı Flexbox yapısıyla yan yana ve dikeyde tam ortalanmış (align-items: center) olarak hizalıyoruz
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 30px; margin-bottom: 10px;">
            <div style="flex: 0 0 250px;">
                <img src="app/static/{logo_yolu}" style="width: 100%; max-height: 80px; object-fit: contain;">
            </div>
            <div>
                <h1 style="margin: 0; padding: 0; font-size: 2.5rem; line-height: 1.2;">Ofis Stok İzleme Paneli</h1>
                <p style="margin: 5px 0 0 0; padding: 0; color: gray; font-size: 0.95rem;">📅 <b>Son Güncelleme / Sayım Tarihi:</b> {guncel_stok_col}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Eğer logo yüklenmemişse standart başlık düzeni çalışır
        header_col1, header_col2 = st.columns([1, 11])
        with header_col1:
            st.markdown("<h1 style='text-align: left; margin:0;'>📦</h1>", unsafe_allow_html=True)
        with header_col2:
            st.title("Ofis Stok İzleme Paneli")
            st.caption(f"📅 **Son Güncelleme / Sayım Tarihi:** {guncel_stok_col}")

    st.markdown("---")

    # --- YATAY DİLİMLEYİCİLER (FİLTRELER) ---
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        search_query = st.text_input("📝 Ürün Kodu veya Açıklama Ara", placeholder="Örn: STK-001...")
        
    with filter_col2:
        tum_gruplar = ["Tümü"] + list(df[grup_col].dropna().unique())
        secilen_grup = st.selectbox("📂 Ürün Grubu Seçin", tum_gruplar)
        
    with filter_col3:
        tum_markalar = ["Tümü"] + list(df[marka_col].dropna().unique())
        secilen_maraka = st.selectbox("🏷️ Marka Seçin", tum_markalar)

    # Veriyi Filtreleme Kuralları
    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[
            filtered_df[urun_kodu_col].astype(str).str.contains(search_query, case=False) | 
            filtered_df[urun_aciklama_col].astype(str).str.contains(search_query, case=False)
        ]
    if secilen_grup != "Tümü":
        filtered_df = filtered_df[filtered_df[grup_col] == secilen_grup]
    if secilen_maraka != "Tümü":
        filtered_df = filtered_df[filtered_df[marka_col] == secilen_maraka]

    # --- DINAMIK KPI KARTLARI ---
    total_products = len(filtered_df)
    total_stock = int(filtered_df[guncel_stok_col].sum())
    total_cost = filtered_df[maliyet_col].sum()
    
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.markdown(f"""
        <div style='background-color: rgba(28, 31, 46, 0.05); padding: 20px; border-radius: 10px; border-left: 5px solid #1E88E5;'>
            <p style='margin:0; font-size:14px; color:gray;'>📋 Toplam Ürün Çeşidi</p>
            <h2 style='margin:10px 0 0 0;'>{total_products:,} Adet</h2>
        </div>
        """.replace(",", "."), unsafe_allow_html=True)
        
    with kpi2:
        st.markdown(f"""
        <div style='background-color: rgba(28, 31, 46, 0.05); padding: 20px; border-radius: 10px; border-left: 5px solid #4CAF50;'>
            <p style='margin:0; font-size:14px; color:gray;'>📦 Toplam Stok Miktarı</p>
            <h2 style='margin:10px 0 0 0;'>{total_stock:,} Adet</h2>
        </div>
        """.replace(",", "."), unsafe_allow_html=True)
        
    with kpi3:
        st.markdown(f"""
        <div style='background-color: rgba(28, 31, 46, 0.05); padding: 20px; border-radius: 10px; border-left: 5px solid #FFC107;'>
            <p style='margin:0; font-size:14px; color:gray;'>💰 Toplam Stok Maliyeti</p>
            <h2 style='margin:10px 0 0 0;'>${total_cost:,.0f}</h2>
        </div>
        """.replace(",", "."), unsafe_allow_html=True)
    
    st.markdown("---")

    # --- TABLO VERİ FORMATLAMA VE SÜTUN SIRALAMA ---
    st.subheader("📊 Güncel Stok Listesi")
    
    gosterilecek_df = filtered_df[[urun_kodu_col, urun_aciklama_col, marka_col, grup_col, guncel_stok_col, fiyat_col, maliyet_col]].copy()
    gosterilecek_df.columns = ["Ürün Kodu", "Açıklama", "Marka", "Ürün Grubu", "Güncel Stok", "Birim Maliyet", "Toplam Maliyet"]
    
    # Sayı biçimlendirme fonksiyonları
    def formatla_dolar(val):
        return f"${val:,.0f}".replace(",", ".")

    def formatla_adet(val):
        return f"{int(val):,}".replace(",", ".")

    stok_orjinal_degerler = gosterilecek_df["Güncel Stok"].copy()

    gosterilecek_df["Birim Maliyet"] = gosterilecek_df["Birim Maliyet"].apply(formatla_dolar)
    gosterilecek_df["Toplam Maliyet"] = gosterilecek_df["Toplam Maliyet"].apply(formatla_dolar)
    gosterilecek_df["Güncel Stok"] = gosterilecek_df["Güncel Stok"].apply(formatla_adet)

    # Koşullu Renklendirme Fonksiyonu
    def satiri_renklendir(row):
        if stok_orjinal_degerler.loc[row.name] == 0:
            return ['background-color: rgba(255, 75, 75, 0.15)'] * len(row)
        return [''] * len(row)

    # Hizalama ve Sütun Yapılandırması
    sutun_ayarlari = {
        "Ürün Kodu": st.column_config.
