import streamlit as st

# ==========================================
# 1. HAFIZA (SESSION STATE) AYARI
# ==========================================
# "Temizle" butonuna basıldığında kutunun içinin sıfırlanması için şarttır.
if "arama_kelimesi" not in st.session_state:
    st.session_state.arama_kelimesi = ""

# ==========================================
# 2. MİNİMAL HİZALAMA CSS'İ (SADECE BUTON İÇİN)
# ==========================================
# Native inputlar zaten kendi arasında milimetrik hizalanır. 
# Bu CSS sadece etiket başlığı olmayan "Temizle" butonunu aşağı indirmek içindir.
st.markdown("""
    <style>
        .buton-hizalama {
            margin-top: 28px;
        }
        @media screen and (max-width: 768px) {
            .buton-hizalama {
                margin-top: 0px; /* Mobil ekranlarda dikey düzen için boşluğu sıfırla */
            }
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. YAN YANA SÜTUN DÜZENİ (LAYOUT)
# ==========================================
# Sütun genişlik oranlarını [Arama, Selectbox1, Selectbox2, Buton] olarak ayarladık.
col_arama, col_select1, col_select2, col_buton = st.columns([3, 2, 2, 1])

with col_arama:
    # 🎯 ORİJİNAL ARAMA KUTUSU (Iframe DEĞİL!)
    # Selectbox'lar ile otomatik olarak aynı dikey kalınlıkta ve hizada başlar.
    aktif_girdi = st.text_input(
        label="📝 Ürün Ara",
        value=st.session_state.arama_kelimesi,
        placeholder="Ürün adını yazın ve Enter'a basın...",
        key="arama_kutusu_key" # Temizleme mekanizmasının bağlı olduğu sihirli anahtar
    )

with col_select1:
    # 🎯 SELECTBOX 1
    secilen_marka = st.selectbox("📂 Marka Seçin", ["Hepsi", "Apple", "Samsung", "Xiaomi"])

with col_select2:
    # 🎯 SELECTBOX 2
    secilen_kategori = st.selectbox("🏷️ Kategori Seçin", ["Hepsi", "Telefon", "Bilgisayar"])

with col_buton:
    # Butonun selectbox'ların altına tam oturması için yukarıda tanımladığımız boşluğu koyuyoruz
    st.markdown('<div class="buton-hizalama"></div>', unsafe_allow_html=True)
    
    # 🎯 TEMİZLE BUTONU
    if st.button("🗑️ Temizle", use_container_width=True):
        # Butona basıldığı an arama kutusunun içini session_state üzerinden sıfırlıyoruz
        st.session_state.arama_kutusu_key = ""
        st.rerun() # Sayfayı milisaniyeler içinde yeniler, kutu yerinden oynamadan tertemiz olur

# ==========================================
# 4. VERİ FİLTRELEME MANTIĞI
# ==========================================
# Filtreleme yaparken artık bu değişkeni kullanabilirsin.
arama_sorgusu = st.session_state.arama_kutusu_key

# Örnek kullanım (Kendi DataFrame yapına göre burayı açabilirsin):
if arama_sorgusu:
    st.info(f"🔍 Şu an listelenen sonuçlar: **{arama_sorgusu}**")
    # df_filtrelenmis = df[df['urun_adi'].str.contains(arama_sorgusu, case=False)]
