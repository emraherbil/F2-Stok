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

# --- SAYFA VE CSS (Sizin mükemmel dediğiniz tasarım) ---
st.set_page_config(page_title="F2 ICT - Ofis Stok İzleme Paneli", page_icon="📦", layout="wide")
logo_data = logo_to_base64("logo.png") or logo_to_base64("logo.jpg")

css_style = """
<style>
    .block-container { padding-top: 1.5rem !important; }
    .custom-header-container { display: flex; align-items: center; gap: 20px; margin-bottom: 15px; }
    .custom-logo { height: 55px !important; object-fit: contain; }
    .custom-title-block { display: flex; flex-direction: column; justify-content: center; }
    .stCheckbox { margin-top: 32px !important; }
    .stButton button { margin-top: 28px !important; height: 42px !important; }
    hr { margin: 0.5rem 0 !important; opacity: 0.3; }
</style>
"""
st.markdown(css_style, unsafe_allow_html=True)

# --- ANA MANTIKSAL AKIŞ ---
try:
    df = load_data()
    df.columns = [str(c).strip() for c in df.columns]
    
    # Sütun eşleştirmeleri
    c_kod, c_tanim = df.columns[1], df.columns[2]
    c_marka, c_grup = df.columns[3], df.columns[4]
    c_maliyet = df.columns[13]
    c_stok = df.columns[-1]

    # Filtre State
    if "q_search" not in st.session_state: st.session_state.q_search = ""
    if "q_marka" not in st.session_state: st.session_state.q_marka = "Tümü"
    if "q_grup" not in st.session_state: st.session_state.q_grup = "Tümü"
    
    def filtreleri_temizle():
        for key in ["q_search", "q_marka", "q_grup"]: st.session_state[key] = "" if key == "q_search" else "Tümü"

    # HEADER (Logo + Başlık)
    header_html = f"""
    <div class="custom-header-container">
        {'<img src="data:image/png;base64,' + logo_data + '" class="custom-logo">' if logo_data else ''}
        <div class="custom-title-block">
            <h2 style="margin:0; font-size:1.75rem; font-weight:700;">Ofis Stok İzleme Paneli</h2>
            <span style="color:#7d7f87; font-size:0.85rem;">📅 <b>Son Güncelleme:</b> {c_stok}</span>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
    st.markdown("---")

    # FİLTRELER
    c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 1])
    with c1: st.text_input("📝 Ürün Ara", key="q_search")
    with c2: st.selectbox("🏷️ Marka", ["Tümü"] + list(df[c_marka].dropna().unique()), key="q_marka")
    with c3: st.selectbox("📂 Ürün Grubu", ["Tümü"] + list(df[c_grup].dropna().unique()), key="q_grup")
    with c5: st.button("🧹 Temizle", on_click=filtreleri_temizle, use_container_width=True)

    # FİLTRELEME VE KPI
    f_df = df.copy()
    if st.session_state.q_search: f_df = f_df[f_df[c_kod].astype(str).str.contains(st.session_state.q_search, case=False)]
    if st.session_state.q_marka != "Tümü": f_df = f_df[f_df[c_marka] == st.session_state.q_marka]
    if st.session_state.q_grup != "Tümü": f_df = f_df[f_df[c_grup] == st.session_state.q_grup]

    k1, k2, k3 = st.columns(3)
    k1.metric("📋 Toplam Çeşit", f"{len(f_df):,}")
    k2.metric("📦 Toplam Stok", f"{int(f_df[c_stok].sum()):,}")
    k3.metric("💰 Toplam Maliyet", f"${f_df[c_maliyet].sum():,.0f}")

    # TABLO (İndeks Gizli)
    out_df = f_df[[c_kod, c_tanim, c_marka, c_grup, c_stok, c_maliyet]]
    st.dataframe(out_df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Bir hata oluştu: {e}")
