import streamlit as st
import pandas as pd
import os

# 1. Sayfa Düzeni ve Başlık Ayarları (Geniş Ekran Modu)
st.set_page_config(
    page_title="Stockify - Ofis Stok Yönetimi", 
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

    # --- ÜST BAŞLIK & KURUMSAL LOGO ALANI ---
    header_col1, header_col2 = st.columns([2, 10])
    
    with header_col1:
        # GitHub'a yükleyeceğiniz logo dosyasının adını kontrol ediyoruz
        # Eğer logo.png veya logo.jpg varsa ekrana basar, yoksa şık bir depo ikonu koyar
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        elif os.path.exists("logo.jpg"):
            st.image("logo.jpg", use_container_width=True)
        else:
            st.markdown("<h1 style='text-align: center; margin:0;'>📦</h1>", unsafe_allow_html=True)
            st.caption("Not: logo.png bulunamadı")
            
    with header_col2:
        st.title("Stockify Ofis Stok Yönetim Paneli")
        st.caption(f"📅 **Son Güncelleme / Sayım Tarihi:** {guncel_stok_col}")

    st.markdown("---")

    # --- KPI KARTLARI ---
    total_products = len(df)
    total_stock = int(df[guncel_stok_col].sum())
    total_cost = df[maliyet_col].sum()
    
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
            <h2 style='margin:10px 0 0 0;'>{total_cost:,.0f} TL</h2>
        </div>
        """.replace(",", "."), unsafe_allow_html=True)
    
    st.markdown("---")

    # --- YATAY DİLİMLEYİCİLER (FİLTRELER) ---
    st.subheader("🔍 Filtre Paneli (Dilimleyiciler)")
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

    # --- TABLO VERİ FORMATLAMA VE SÜTUN SIRALAMA ---
    st.subheader("📊 Gelişmiş Stok Listesi")
    
    gosterilecek_df = filtered_df[[urun_kodu_col, urun_aciklama_col, marka_col, grup_col, guncel_stok_col, fiyat_col, maliyet_col]].copy()
    gosterilecek_df.columns = ["Ürün Kodu", "Açıklama", "Marka", "Ürün Grubu", "Güncel Stok", "Birim Fiyat", "Toplam Maliyet"]
    
    # Sayı biçimlendirme fonksiyonları
    def formatla_tl(val):
        return f"{val:,.0f} TL".replace(",", ".")

    def formatla_adet(val):
        return f"{int(val):,}".replace(",", ".")

    stok_orjinal_degerler = gosterilecek_df["Güncel Stok"].copy()

    gosterilecek_df["Birim Fiyat"] = gosterilecek_df["Birim Fiyat"].apply(formatla_tl)
    gosterilecek_df["Toplam Maliyet"] = gosterilecek_df["Toplam Maliyet"].apply(formatla_tl)
    gosterilecek_df["Güncel Stok"] = gosterilecek_df["Güncel Stok"].apply(formatla_adet)

    # Koşullu Renklendirme Fonksiyonu (Stok 0 ise hafif kırmızı arka plan)
    def satiri_renklendir(row):
        if stok_orjinal_degerler.loc[row.name] == 0:
            return ['background-color: rgba(255, 75, 75, 0.15)'] * len(row)
        return [''] * len(row)

    # Tabloyu ekrana basıyoruz
    st.dataframe(
        gosterilecek_df.style.apply(satiri_renklendir, axis=1),
        use_container_width=True,
        height=550
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
