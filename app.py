import streamlit as st
import pandas as pd
import os
import base64
from pathlib import Path
from st_keyup import st_keyup

# 1. SAYFA YAPILANDIRMASI
st.set_page_config(page_title="F2 ICT - Ofis Stok İzleme Paneli", page_icon="📦", layout="wide")

# 2. CSS - ZIPLAMAYI VE HİZALAMAYI KİLİTLEYEN TASARIM
st.markdown("""
    <style>
        footer, .viewerBadge_container, [data-testid="stToolbar"], .stDeployButton, header {display: none !important;}
        .block-container { padding-top: 1.5rem !important; max-width: 100% !important; }
        
        /* Zıplamayı engelleyen kilit: Sütun yüksekliğini sabit tutar */
        div[data-testid="column"] {
            min-height: 95px !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: flex-end !important;
        }

        .custom-logo { height: 60px; object-fit: contain; }
        .stButton > button { 
            background-color: #1C355E !important; color: white !important; 
            border-radius: 6px !important; height: 42px !important; width: 100% !important; 
        }
    </style>
""", unsafe_allow_html=True)

# 3. VERİ VE LOGO
def logo_to_base64(img_path):
    if os.path.exists(img_path): return base64.b64encode(Path(img_path).read_bytes()).decode()
    return None

logo_data = logo_to_base64("logo.png") or logo_to_base64("logo.jpg")

@st.cache_data(ttl=600)
def load_data():
    return pd.read_excel('Stok Sayım Arşivi-v3.1-Web.xlsm', sheet_name='Stok', engine='openpyxl')

# 4. ANA PANEL
try:
    df = load_data()
    df.columns = [str(c).strip() for c in df.columns]
    c_kod, c_tanim, c_marka, c_grup, c_maliyet = df.columns[1], df.columns[2], df.columns[3], df.columns[4], df.columns[13]
    c_stok = df.columns[-1]

    # Başlık ve Logo
    logo_html = f'<img src="data:image/png;base64,{logo_data}" class="custom-logo">' if logo_data else "📦"
    st.markdown(f"""
        <div style="display:flex; align-items:center; gap:25px; margin-bottom:20px;">
            {logo_html}
            <div><h2 style="margin:0;">Ofis Stok İzleme Paneli</h2><span>📅 Son Güncelleme: {c_stok}</span></div>
        </div>
    """, unsafe_allow_html=True)

    @st.fragment
    def render_panel(df):
        if "reset" not in st.session_state: st.session_state.reset = 0
        
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
        
        with col1:
            query = st_keyup("📝 Ürün Ara", key=f"q_{st.session_state.reset}", placeholder="Kod veya açıklama...")
        with col2:
            marka = st.selectbox("🏷️ Marka", ["Tümü"] + sorted(df[c_marka].dropna().unique().tolist()))
        with col3:
            grup = st.selectbox("📂 Ürün Grubu", ["Tümü"] + sorted(df[c_grup].dropna().unique().tolist()))
        with col4:
            gizle = st.checkbox("🚫 Tükenenleri Gizle")
        with col5:
            if st.button("🧹 Temizle"): 
                st.session_state.reset += 1
                st.rerun()

        # Filtreleme
        f_df = df.copy()
        if query: f_df = f_df[f_df[c_kod].astype(str).str.contains(query, case=False) | f_df[c_tanim].astype(str).str.contains(query, case=False)]
        if marka != "Tümü": f_df = f_df[f_df[c_marka] == marka]
        if grup != "Tümü": f_df = f_df[f_df[c_grup] == grup]
        if gizle: f_df = f_df[pd.to_numeric(f_df[c_stok], errors='coerce') > 0]

        # Kartlar
        k1, k2, k3 = st.columns(3)
        k1.metric("Toplam Çeşit", f"{len(f_df)} Adet")
        k2.metric("Toplam Stok", f"{int(f_df[c_stok].sum()):,} Adet")
        k3.metric("Toplam Maliyet", f"${f_df[c_maliyet].sum():,.0f}")

        st.dataframe(f_df, use_container_width=True, hide_index=True, height=500)

    render_panel(df)
except Exception as e:
    st.error(f"Hata: {e}")
