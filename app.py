import streamlit as st
import pandas as pd
import os
import base64
from pathlib import Path

# --- YARDIMCI FONKSİYONLAR ---
def logo_to_base64(img_path):
    try:
        if os.path.exists(img_path):
            img_bytes = Path(img_path).read_bytes()
            return base64.b64encode(img_bytes).decode()
    except Exception:
        pass
    return None

@st.cache_data
def load_data():
    return pd.read_excel('Stok Sayım Arşivi-v3.1-Web.xlsm', sheet_name='Stok', engine='openpyxl')

# --- SAYFA VE CSS ---
st.set_page_config(page_title="F2 ICT - Ofis Stok İzleme Paneli", page_icon="📦", layout="wide")
logo_data = logo_to_base64("logo.png") or logo_to_base64("logo.jpg")

css_style = """
<style>
    .block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; }
    .custom-header-container { display: flex; align-items: center; gap: 20px; margin-bottom: 15px; }
    .custom-logo { height: 52px !important; object-fit: contain; margin-top: -5px; }
    .custom-title-block { display: flex; flex-direction: column; justify-content: center; }
    .stCheckbox { margin-top: 35px !important; }
    .stButton button { margin-top: 28px !important; height: 42px !important; }
    hr { margin: 0.6rem 0 !important; opacity: 0.2; }
</style>
"""
st.markdown(css_style, unsafe_allow_html=True)

# --- ANA MANTIKSAL AKIŞ ---
try:
    df = load_data()
    df.columns = [str(c).strip() for c in df.columns]
    
    c_kod, c_tanim = df.columns[1], df.columns[2]
    c_marka, c_grup = df.columns[3], df.columns[4]
    c_fiyat, c_maliyet = df.columns[12], df.columns[13]
    sayim_cols = list(df.columns[14:]) 
    c_stok = sayim_cols[-1] if sayim_cols else df.columns[-1]

    df[c_stok] = pd.to_numeric(df[c_stok], errors='coerce').fillna(0)
    df[c_maliyet] = pd.to_numeric(df[c_maliyet], errors='coerce').fillna(0)

    if "q_search" not in st.session_state: st.session_state.q_search = ""
    if "q_grup" not in st.session_state: st.session_state.q_grup = "Tümü"
    if "q_marka" not in st.session_state: st.session_state.q_marka = "Tümü"
    if "q_stok" not in st.session_state: st.session_state.q_stok = False

    def filtreleri_temizle():
        st.session_state.q_search = ""
        st.session_state.q_grup = "Tümü"
        st.session_state.q_marka = "Tümü"
        st.session_state.q_stok = False

    # HEADER
    header_html = f"""
    <div class="custom-header-container">
        {'<img src="data:image/png;base64,' + logo_data + '" class="custom-logo">' if logo_data else ''}
        <div class="custom-title-block">
            <h2 style="margin:0; padding:0; font-size:1.95rem; font-weight:700;">Ofis Stok İzleme Paneli</h2>
            <span style="color:#7d7f87; font-size:0.85rem;">📅 <b>Son Güncelleme:</b> {c_stok}</span>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
    st.markdown("---")

    # FİLTRELER
    col1, col2, col3, col4, col5 = st.columns([3.2, 2.4, 2.4, 2.2, 1.2])
    with col1: v_search = st.text_input("📝 Ürün Ara", key="q_search")
    with col2: v_marka = st.selectbox("🏷️ Marka", ["Tümü"] + list(df[c_marka].dropna().unique()), key="q_marka")
    with col3: v_grup = st.selectbox("📂 Ürün Grubu", ["Tümü"] + list(df[c_grup].dropna().unique()), key="q_grup")
    with col4: v_stok = st.checkbox("🚫 Tükenenleri Gizle", key="q_stok")
    with col5: st.button("🧹 Temizle", on_click=filtreleri_temizle, use_container_width=True)

    # FİLTRELEME
    f_df = df.copy()
    if v_search: f_df = f_df[f_df[c_kod].astype(str).str.contains(v_search, case=False) | f_df[c_tanim].astype(str).str.contains(v_search, case=False)]
    if v_marka != "Tümü": f_df = f_df[f_df[c_marka] == v_marka]
    if v_grup != "Tümü": f_df = f_df[f_df[c_grup] == v_grup]
    if v_stok: f_df = f_df[f_df[c_stok] > 0]

    # KPI VE TABLO
    k1, k2, k3 = st.columns(3)
    k1.metric("📋 Toplam Çeşit", f"{len(f_df):,}")
    k2.metric("📦 Toplam Stok", f"{int(f_df[c_stok].sum()):,}")
    k3.metric("💰 Toplam Maliyet", f"${f_df[c_maliyet].sum():,.0f}")

    out_df = f_df[[c_kod, c_tanim, c_marka, c_grup, c_stok, c_maliyet]].copy()
    out_df.columns = ["Ürün Kodu", "Açıklama", "Marka", "Ürün Grubu", "Stok", "Maliyet"]
    st.dataframe(out_df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Hata oluştu: {e}")
