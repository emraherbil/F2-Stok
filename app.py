import streamlit as st
import pandas as pd
import os
import base64
from pathlib import Path
from st_keyup import st_keyup

st.set_page_config(page_title="F2 ICT - Ofis Stok İzleme Paneli", page_icon="📦", layout="wide")

# Zıplamayı engelleyen ve görseli sabitleyen CSS
st.markdown("""
    <style>
        footer, .viewerBadge_container, [data-testid="stToolbar"], .stDeployButton, header {display: none !important;}
        
        /* Zıplamayı engelleyen sihirli dokunuş: */
        /* Arama kutusunun olduğu sütunu her durumda sabit yükseklikte tutar */
        div[data-testid="column"]:has(iframe), 
        div[data-testid="column"]:has([data-testid="stCustomComponentV1"]) {
            min-height: 84px !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: flex-end !important;
        }

        .stButton > button { 
            background-color: #1C355E !important; 
            color: white !important; 
            border-radius: 6px !important;
            height: 42px !important; 
            width: 100% !important; 
            margin-top: 30px !important;
        }
    </style>
""", unsafe_allow_html=True)

# Veri yükleme
@st.cache_data(ttl=600)
def load_data():
    return pd.read_excel('Stok Sayım Arşivi-v3.1-Web.xlsm', sheet_name='Stok', engine='openpyxl')

# Ana Panel
try:
    df = load_data()
    df.columns = [str(c).strip() for c in df.columns]
    c_kod, c_tanim, c_marka, c_grup, c_maliyet = df.columns[1], df.columns[2], df.columns[3], df.columns[4], df.columns[13]
    c_stok = df.columns[-1]

    @st.fragment
    def stok_paneli_icerik(data_frame):
        if "reset_counter" not in st.session_state: st.session_state.reset_counter = 0
        
        # Filtreleri yöneten session state
        if "q_grup" not in st.session_state: st.session_state.q_grup = "Tümü"
        if "q_marka" not in st.session_state: st.session_state.q_marka = "Tümü"
        if "q_stok" not in st.session_state: st.session_state.q_stok = False
        
        def filtreleri_temizle():
            st.session_state.reset_counter += 1
            st.session_state.q_grup = "Tümü"
            st.session_state.q_marka = "Tümü"
            st.session_state.q_stok = False

        col1, col2, col3, col4, col5 = st.columns([3.2, 2.4, 2.4, 2.2, 1.2])
        
        with col1:
            # Canlı arama - Her harfte tetiklenir, zıplamaz
            v_search = st_keyup(
                label="📝 Ürün Ara", 
                key=f"q_search_{st.session_state.reset_counter}",
                placeholder="Kod veya açıklama yaz..."
            )

        with col2: v_marka = st.selectbox("🏷️ Marka", ["Tümü"] + sorted(data_frame[c_marka].dropna().unique().tolist()), key="q_marka")
        with col3: v_grup = st.selectbox("📂 Ürün Grubu", ["Tümü"] + sorted(data_frame[c_grup].dropna().unique().tolist()), key="q_grup")
        with col4: v_stok = st.checkbox("🚫 Tükenenleri Gizle", key="q_stok")
        with col5: st.button("🧹 Temizle", on_click=filtreleri_temizle, use_container_width=True)

        # Filtreleme
        f_df = data_frame.copy()
        if v_search:
            f_df = f_df[f_df[c_kod].astype(str).str.contains(v_search, case=False) | f_df[c_tanim].astype(str).str.contains(v_search, case=False)]
        if v_marka != "Tümü": f_df = f_df[f_df[c_marka] == v_marka]
        if v_grup != "Tümü": f_df = f_df[f_df[c_grup] == v_grup]
        if v_stok: f_df = f_df[pd.to_numeric(f_df[c_stok], errors='coerce') > 0]

        st.dataframe(f_df, use_container_width=True, hide_index=True, height=540)

    stok_paneli_icerik(df)
except Exception as e:
    st.error(f"Sistem hatası: {e}")
