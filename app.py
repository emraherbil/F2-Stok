import streamlit as st
import pandas as pd
import os
import base64
from pathlib import Path

# 1. SAYFA VE STİL YAPILANDIRMASI
st.set_page_config(page_title="F2 ICT - Ofis Stok İzleme Paneli", layout="wide")

st.markdown("""
    <style>
        /* CSS İLE HİZALAMA KİLİDİ */
        div[data-testid="column"] { display: flex !important; align-items: flex-end !important; }
        .stButton > button { height: 42px !important; width: 100% !important; background-color: #1C355E !important; color: white !important; border-radius: 6px !important; }
        div[data-baseweb="input"] { border-radius: 6px !important; }
        .custom-header-container { display: flex; align-items: center; gap: 25px; margin-bottom: 20px; }
        /* Fragment zıplamasını engellemek için min-height */
        div[data-testid="stVerticalBlock"] { min-height: 100px; }
    </style>
""", unsafe_allow_html=True)

# 2. VERİ YÜKLEME
@st.cache_data(ttl=600)
def load_data():
    return pd.read_excel('Stok Sayım Arşivi-v3.1-Web.xlsm', sheet_name='Stok', engine='openpyxl')

df = load_data()
df.columns = [str(c).strip() for c in df.columns]
c_kod, c_tanim, c_marka, c_grup, c_stok = df.columns[1], df.columns[2], df.columns[3], df.columns[4], df.columns[-1]

# 3. BAŞLIK ALANI
st.markdown('<div class="custom-header-container"><h2>Ofis Stok İzleme Paneli</h2></div>', unsafe_allow_html=True)

# 4. KUSURSUZ FİLTRELEME VE TABLO (FRAGMENT)
@st.fragment
def stok_paneli():
    # Session State yönetimi
    if "s_text" not in st.session_state: st.session_state.s_text = ""
    
    def temizle():
        st.session_state.s_text = ""
        st.session_state.q_grup = "Tümü"
        st.session_state.q_marka = "Tümü"
        st.session_state.q_stok = False

    # Kolon hizalama: vertical_alignment="bottom" tüm elemanları tabana sabitler
    col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1], vertical_alignment="bottom")
    
    with col1:
        v_search = st.text_input("📝 Ürün Ara", value=st.session_state.s_text, key="s_text")
    with col2:
        v_marka = st.selectbox("🏷️ Marka", ["Tümü"] + sorted(df[c_marka].astype(str).unique().tolist()), key="q_marka")
    with col3:
        v_grup = st.selectbox("📂 Ürün Grubu", ["Tümü"] + sorted(df[c_grup].astype(str).unique().tolist()), key="q_grup")
    with col4:
        v_stok = st.checkbox("🚫 Tükenenleri Gizle", key="q_stok")
    with col5:
        st.button("🧹 Temizle", on_click=temizle, use_container_width=True)

    # Filtreleme mantığı
    f_df = df.copy()
    if v_search:
        f_df = f_df[f_df[c_kod].astype(str).str.contains(v_search, case=False) | f_df[c_tanim].astype(str).str.contains(v_search, case=False)]
    if v_marka != "Tümü": f_df = f_df[f_df[c_marka].astype(str) == v_marka]
    if v_grup != "Tümü": f_df = f_df[f_df[c_grup].astype(str) == v_grup]
    if v_stok: f_df = f_df[pd.to_numeric(f_df[c_stok], errors='coerce') > 0]
    
    st.dataframe(f_df, use_container_width=True, hide_index=True)

stok_paneli()
