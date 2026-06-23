import streamlit as st
import pandas as pd
from st_keyup import st_keyup

# 1. SAYFA YAPILANDIRMASI
st.set_page_config(page_title="F2 ICT - Ofis Stok İzleme Paneli", layout="wide")

# 2. VERİ YÜKLEME
@st.cache_data(ttl=600)
def load_data():
    return pd.read_excel('Stok Sayım Arşivi-v3.1-Web.xlsm', sheet_name='Stok', engine='openpyxl')

# 3. UYGULAMA MANTIĞI
try:
    df = load_data()
    # Sütun isimlerini temizle
    df.columns = [str(c).strip() for c in df.columns]
    
    # Sütun eşleşmeleri
    c_kod, c_tanim, c_marka, c_grup, c_maliyet = df.columns[1], df.columns[2], df.columns[3], df.columns[4], df.columns[13]
    c_stok = list(df.columns[14:])[-1] if len(df.columns) > 14 else df.columns[-1]

    # Fragment Yapısı
    @st.fragment
    def stok_paneli():
        # Session State tanımları
        if "clear_ver" not in st.session_state: st.session_state.clear_ver = 0
        if "q_grup" not in st.session_state: st.session_state.q_grup = "Tümü"
        if "q_marka" not in st.session_state: st.session_state.q_marka = "Tümü"
        if "q_stok" not in st.session_state: st.session_state.q_stok = False
        
        def filtreleri_temizle():
            st.session_state.clear_ver += 1
            st.session_state.q_grup = "Tümü"
            st.session_state.q_marka = "Tümü"
            st.session_state.q_stok = False

        # Kolonlar
        c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 1], vertical_alignment="bottom")
        
        with c1:
            v_search = st_keyup("📝 Ürün Ara", key=f"search_{st.session_state.clear_ver}", placeholder="Aramak için yazın...")
        with c2:
            v_marka = st.selectbox("🏷️ Marka", ["Tümü"] + sorted(df[c_marka].dropna().unique().tolist()), key="q_marka")
        with c3:
            v_grup = st.selectbox("📂 Ürün Grubu", ["Tümü"] + sorted(df[c_grup].dropna().unique().tolist()), key="q_grup")
        with c4:
            v_stok = st.checkbox("🚫 Tükenenleri Gizle", key="q_stok")
        with c5:
            st.button("🧹 Temizle", on_click=filtreleri_temizle)

        # Filtreleme Mantığı
        f_df = df.copy()
        if v_search:
            f_df = f_df[f_df[c_kod].astype(str).str.contains(v_search, case=False) | f_df[c_tanim].astype(str).str.contains(v_search, case=False)]
        if v_marka != "Tümü": f_df = f_df[f_df[c_marka] == v_marka]
        if v_grup != "Tümü": f_df = f_df[f_df[c_grup] == v_grup]
        if v_stok: f_df = f_df[f_df[c_stok] > 0]

        st.dataframe(f_df, use_container_width=True)

    stok_paneli()

except Exception as e:
    st.error(f"Bir hata oluştu: {e}")
