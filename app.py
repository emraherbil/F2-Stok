import streamlit as st
import pandas as pd
import os
import base64
from pathlib import Path

# 1. SAYFA YAPILANDIRMASI
st.set_page_config(page_title="F2 ICT - Ofis Stok İzleme Paneli", page_icon="📦", layout="wide")

# 2. CSS (Zıplamayı önleyen kilit)
st.markdown("""
    <style>
        div[data-testid="column"] { display: flex; align-items: flex-end; }
        .stButton > button { height: 42px !important; width: 100% !important; background-color: #1C355E !important; color: white !important; border-radius: 6px !important; }
        div[data-baseweb="input"] { border-radius: 6px !important; }
    </style>
""", unsafe_allow_html=True)

# 3. VERİ YÜKLEME
@st.cache_data(ttl=600)
def load_data():
    return pd.read_excel('Stok Sayım Arşivi-v3.1-Web.xlsm', sheet_name='Stok', engine='openpyxl')

df = load_data()
df.columns = [str(c).strip() for c in df.columns]
c_kod, c_tanim, c_marka, c_grup, c_stok = df.columns[1], df.columns[2], df.columns[3], df.columns[4], df.columns[-1]

# 4. FRAGMENT (İçinde "filtreleri_temizle" fonksiyonu doğru girintiyle yer almalı)
@st.fragment
def stok_paneli_icerik(data_frame):
    # State Yönetimi
    if "search_text" not in st.session_state: st.session_state.search_text = ""
    if "q_grup" not in st.session_state: st.session_state.q_grup = "Tümü"
    if "q_marka" not in st.session_state: st.session_state.q_marka = "Tümü"
    
    # Doğru girintili fonksiyon
    def filtreleri_temizle():
        st.session_state.search_text = ""
        st.session_state.q_grup = "Tümü"
        st.session_state.q_marka = "Tümü"

    col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1], vertical_alignment="bottom")
    
    with col1:
        v_search = st.text_input("📝 Ürün Ara", value=st.session_state.search_text, key="search_text")
    with col2:
        v_marka = st.selectbox("🏷️ Marka", ["Tümü"] + sorted(data_frame[c_marka].astype(str).unique().tolist()), key="q_marka")
    with col3:
        v_grup = st.selectbox("📂 Ürün Grubu", ["Tümü"] + sorted(data_frame[c_grup].astype(str).unique().tolist()), key="q_grup")
    with col4:
        v_stok = st.checkbox("🚫 Tükenenleri Gizle")
    with col5:
        st.button("🧹 Temizle", on_click=filtreleri_temizle, use_container_width=True)

    # Filtreleme
    f_df = data_frame.copy()
    if v_search:
        f_df = f_df[f_df[c_kod].astype(str).str.contains(v_search, case=False) | f_df[c_tanim].astype(str).str.contains(v_search, case=False)]
    if v_marka != "Tümü": f_df = f_df[f_df[c_marka].astype(str) == v_marka]
    if v_grup != "Tümü": f_df = f_df[f_df[c_grup].astype(str) == v_grup]
    if v_stok: f_df = f_df[pd.to_numeric(f_df[c_stok], errors='coerce') > 0]
    
    st.dataframe(f_df, use_container_width=True, hide_index=True)

stok_paneli_icerik(df)
