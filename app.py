import streamlit as st
import pandas as pd
import datetime

# Sayfa Genişlik ve Başlık Ayarları
st.set_page_config(page_title="Stockify - Ofis Stok Yönetimi", layout="wide")

# Excel Dosyasını Yükleme Fonksiyonu
@st.cache_data
def load_data():
    # Yüklediğiniz 'Stok Sayım Arşivi-v3.1-Web.xlsm' dosyasını okuyoruz
    # İlk satır başlık olduğu için header=0 veya gerekirse 1 yapılır.
    df = pd.read_excel('Stok Sayım Arşivi-v3.1-Web.xlsm', sheet_name='Stok')
    return df

try:
    df = load_data()
    
    # Sütun İsimlerini Sizin Tarifinize Göre Eşleştiriyoruz
    # B: Ürün Kodu, C: Ürün Açıklaması, D: Marka, E: Ürün Grubu, M: Birim Fiyat, N: Toplam Maliyet
    # Excel sütun endeksleri (0'dan başlar): B=1, C=2, D=3, E=4, M=12, N=13
    
    # Dinamik olarak sütun isimlerini temizleyelim (Boşlukları vb. uçurmak için)
    df.columns = [str(c).strip() for c in df.columns]
    
    # Sizin belirttiğiniz kritik sütunların tespiti
    urun_kodu_col = df.columns[1] # B Sütunu
    urun_aciklama_col = df.columns[2] # C Sütunu
    marka_col = df.columns[3] # D Sütunu
    grup_col = df.columns[4] # E Sütunu
    fiyat_col = df.columns[12] # M Sütunu
    maliyet_col = df.columns[13] # N Sütunu
    
    # O ile DE arasındaki sütunlar sayım miktarları (14. sütundan sonrası)
    sayim_sutunlari = list(df.columns[14:]) 
    # En son yapılan sayım sütununu güncel stok kabul edelim
    guncel_stok_col = sayim_sutunlari[-1] if sayim_sutunlari else df.columns[-1]

    # --- ÜST MENÜ / BAŞLIK ---
    st.title("📦 Stockify Ofis Stok Yönetim Paneli")
    st.write(f"**Son Güncelleme / Sayım Tarihi:** {guncel_stok_col}")
    st.markdown("---")

    # --- KPI KARTLARI (ÖZET EKRANI) ---
    total_products = len(df)
    total_stock = int(df[guncel_stok_col].sum())
    total_cost = df[maliyet_col].sum()
    
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Toplam Ürün Çeşidi", f"{total_products} Adet")
    kpi2.metric("Toplam Stok Miktarı", f"{total_stock} Adet")
    kpi3.metric("Toplam Stok Maliyeti", f"₺{total_cost:,.2f}")
    
    st.markdown("---")

    # --- DİLİMLEYİCİLER / FİLTRELER (PİVOT MANTIĞI) ---
    st.sidebar.header("🔍 Filtre Paneli (Dilimleyiciler)")
    
    # Arama Kutusu
    search_query = st.sidebar.text_input("Ürün Kodu veya Açıklama Ara")
    
    # Grup ve Marka Filtreleri
    tum_gruplar = ["Tümü"] + list(df[grup_col].dropna().unique())
    secilen_grup = st.sidebar.selectbox("Ürün Grubu Seçin", tum_gruplar)
    
    tum_markalar = ["Tümü"] + list(df[marka_col].dropna().unique())
    secilen_marka = st.sidebar.selectbox("Marka Seçin", tum_markalar)

    # Veriyi Filtreleme
    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[
            filtered_df[urun_kodu_col].astype(str).str.contains(search_query, case=False) | 
            filtered_df[urun_aciklama_col].astype(str).str.contains(search_query, case=False)
        ]
    if secilen_grup != "Tümü":
        filtered_df = filtered_df[filtered_df[grup_col] == secilen_grup]
    if secilen_maraka != "Tümü":
        filtered_df = filtered_df[filtered_df[marka_col] == secilen_marka]

    # --- ANA TABLO GÖRÜNÜMÜ ---
    st.subheader("📊 Stok Takip Listesi")
    
    # Sadece ihtiyacımız olan sütunları ekranda şıkça gösterelim
    gosterilecek_df = filtered_df[[urun_kodu_col, urun_aciklama_col, marka_col, grup_col, fiyat_col, guncel_stok_col, maliyet_col]]
    gosterilecek_df.columns = ["Ürün Kodu", "Açıklama", "Marka", "Ürün Grubu", "Birim Fiyat", "Güncel Stok", "Toplam Maliyet"]
    
    st.dataframe(gosterilecek_df, use_container_width=True)

    # --- HAFTALIK HAREKET / REVİZYON GİRİŞİ ---
    st.markdown("---")
    st.subheader("🔄 Haftalık Stok Revizyon / Hareket Girişi")
    
    with st.form("stok_hareket_formu"):
        secilen_urun = st.selectbox("Hareket Görecek Ürün", filtered_df[urun_kodu_col].astype(str) + " - " + filtered_df[urun_aciklama_col].astype(str))
        islem_turu = st.selectbox("İşlem Türü", ["Stok Girişi (+)", "Stok Çıkışı (-)"])
        miktar = st.number_input("Miktar", min_value=1, value=1)
        notlar = st.text_input("Açıklama / Not")
        
        submit_btn = st.form_submit_with_button("Hareketi Kaydet ve Stok Güncelle")
        
        if submit_btn:
            st.success(f"Başarılı: {secilen_urun} için {miktar} adetlik {islem_turu} sisteme işlendi! (Not: {notlar})")
            st.info("Gerçek zamanlı Excel üzerine yazma işlemi için veritabanı bağlantısı bir sonraki adımda entegre edilecektir.")

except Exception as e:
    st.error(f"Excel dosyası okunurken bir hata oluştu. Lütfen dosya adının ve sütun yapısının doğruluğunu kontrol edin. Hata: {e}")