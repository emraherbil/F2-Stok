import streamlit as st
import pandas as pd
import os
import base64
from pathlib import Path
from st_keyup import st_keyup

# 1. SAYFA YAPILANDIRMASI
st.set_page_config(page_title="F2 ICT - Ofis Stok İzleme Paneli", page_icon="📦", layout="wide")

# 2. CSS - Zıplamayı ve Hizalamayı Sabitleyen Kilitli Yapı
st.markdown("""
    <style>
        footer, .viewerBadge_container, [data-testid="stToolbar"], .stDeployButton, header {visibility: hidden !important; display: none !important;}
        html, body, .stApp { background-color: #ffffff !important; }
        .block-container { padding-top: 1.5rem !important; padding-bottom: 1.5rem !important; max-width: 100% !important; }
        div[data-testid="stVerticalBlock"] > div:first-child { position: sticky !important; top: 0px !important; background-color: white !important; z-index: 9999 !important; padding-bottom: 15px !important; }
        
        /* Kolon yapısını serbest bırak ve eleman bazlı hizala */
        div[data-testid="column"] { display: block !important; }
        
        /* Arama Kutusu İskelet Kilidi */
        div[data-testid="column"]:first-child div.element-container:has(iframe) { min-height: 42px !important; height: 42px !important; margin-top: 2px !important; }
        div[data-testid="stCustomComponentV1"] { min-height: 42px !important; height: 42px !important; }
        iframe[title*="st_keyup"] { height: 42px !important; min-height: 42px !important; }
        
        /* Checkbox ve Buton Dikey Hiza */
        div[data-testid="stCheckbox"] { padding-top: 25px !important; }
        div[data-testid="column"]:last-child .stButton { margin-top: 23px !important; }
        
        .stButton > button { background-color: #1C355E !important; color: white !important; border-radius: 6px !important; height: 42px !important; width: 100% !important; }
        div[data-baseweb="input"] { border-radius: 6px !important; }
    </style>
""", unsafe_allow_html=True)

# 3. YARDIMCI FONKSİYONLAR
def logo_to_base64(img_path):
    try:
        if os.path.exists(img_path):
            img_bytes = Path(img_path).read_bytes()
            return base64.b64encode(img_bytes).decode()
    except Exception: pass
    return None

logo_data = logo_to_base64("logo.png") or logo_to_base64("logo.jpg")

@st.cache_data(ttl=600)
def load_data():
    return pd.read_excel('Stok Sayım Arşivi-v3.1-Web.xlsm', sheet_name='Stok', engine='openpyxl')

# 4. UYGULAMA MANTIĞI
try:
    df = load_data()
    df.columns = [str(c).strip() for c in df.columns]
    c_kod, c_tanim, c_marka, c_grup, c_maliyet = df.columns[1], df.columns[2], df.columns[3], df.columns[4], df.columns[13]
    c_stok = list(df.columns[14:])[-1] if len(df.columns) > 14 else df.columns[-1]

    # Başlık
    logo_html = f'<img src="data:image/png;base64,{logo_data}" style="height:60px;">' if logo_data else '<div style="font-size: 2.5rem;">📦</div>'
    st.markdown(f'<div style="display:flex; align-items:center; gap:25px;">{logo_html}<div><h2 style="margin:0;">Ofis Stok İzleme Paneli</h2><span>📅 <b>Son Güncelleme:</b> {c_stok}</span></div></div>', unsafe_allow_html=True)

    @st.fragment
    def stok_paneli():
        if "clear_ver" not in st.session_state: st.session_state.clear_ver = 0
        
        def temizle():
            st.session_state.clear_ver += 1
            st.session_state.q_grup = "Tümü"
            st.session_state.q_marka = "Tümü"
            st.session_state.q_stok = False

        c1, c2, c3, c4, c5 = st.columns([3.2, 2.4, 2.4, 2.2, 1.2])
        
        # Filtreler
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

        # KPI
        k1, k2, k3 = st.columns(3)
        k1.metric("Toplam Çeşit", f"{len(f_df):,} Adet")
        k2.metric("Toplam Stok", f"{int(f_df[c_stok].sum()):,} Adet")
        k3.metric("Toplam Maliyet", f"${f_df[c_maliyet].sum():,.0f}")

        # Tablo
        st.dataframe(f_df, use_container_width=True, hide_index=True)

    stok_paneli()

except Exception as e:
    st.error(f"Hata: {e}")
