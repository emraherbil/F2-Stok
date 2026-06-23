import streamlit as st
import pandas as pd
import os
import base64
from pathlib import Path
from st_keyup import st_keyup

# 1. SAYFA YAPILANDIRMASI
st.set_page_config(page_title="F2 ICT - Ofis Stok İzleme Paneli", page_icon="📦", layout="wide")

# CSS: Sabit ve kararlı hizalama
st.markdown("""
    <style>
        footer {visibility: hidden !important; display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}
        div[data-testid="column"] { display: flex !important; flex-direction: column !important; justify-content: flex-end !important; }
        .stButton > button { background-color: #1C355E !important; color: white !important; height: 42px !important; width: 100% !important; }
    </style>
""", unsafe_allow_html=True)

# 2. VERİ YÜKLEME
@st.cache_data(ttl=600)
def load_data():
    return pd.read_excel('Stok Sayım Arşivi-v3.1-Web.xlsm', sheet_name='Stok', engine='openpyxl')

# 3. UYGULAMA MANTIĞI
try:
    df = load_data()
    df.columns = [str(c).strip() for c in df.columns]
    c_kod, c_tanim, c_marka, c_grup, c_maliyet = df.columns[1], df.columns[2], df.columns[3], df.columns[4], df.columns[13]
    c_stok = list(df.columns[14:])[-1] if len(df.columns) > 14 else df.columns[-1]

    @st.fragment
    def stok_paneli():
        if "clear_ver" not in st.session_state: st.session_state.clear_ver = 0
        
        def temizle():
            st.session_state.clear_ver += 1
            st.session_state.q_grup = "Tümü"
            st.session_state.q_marka = "Tümü"
            st.session_state.q_stok = False

        c1, c2, c3, c4, c5 = st.columns([3.2, 2.4, 2.4, 2.2, 1.2], vertical_alignment="bottom")
        
        with c1: v_search = st_keyup("📝 Ürün Ara", key=f"s_{st.session_state.clear_ver}", placeholder="Yazmaya başlayın...", debounce=300)
        with c2: v_marka = st.selectbox("🏷️ Marka", ["Tümü"] + sorted(df[c_marka].dropna().unique().tolist()), key="q_marka")
        with c3: v_grup = st.selectbox("📂 Ürün Grubu", ["Tümü"] + sorted(df[c_grup].dropna().unique().tolist()), key="q_grup")
        with c4: v_stok = st.checkbox("🚫 Tükenenleri Gizle", key="q_stok")
        with c5: st.button("🧹 Temizle", on_click=temizle, use_container_width=True)

        # Filtreleme
        f_df = df.copy()
        if v_search: f_df = f_df[f_df[c_kod].astype(str).str.contains(v_search, case=False) | f_df[c_tanim].astype(str).str.contains(v_search, case=False)]
        if v_marka != "Tümü": f_df = f_df[f_df[c_marka] == v_marka]
        if v_grup != "Tümü": f_df = f_df[f_df[c_grup] == v_grup]
        if v_stok: f_df = f_df[f_df[c_stok] > 0]

        # Metrikler
        k1, k2, k3 = st.columns(3)
        k1.metric("Toplam Çeşit", f"{len(f_df):,} Adet")
        k2.metric("Toplam Stok", f"{int(f_df[c_stok].sum()):,} Adet")
        k3.metric("Toplam Maliyet", f"${f_df[c_maliyet].sum():,.0f}")

        st.dataframe(f_df, use_container_width=True, hide_index=True)

    stok_paneli()
except Exception as e:
    st.error(f"Hata: {e}")
