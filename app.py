import streamlit as st
import pandas as pd
import os
import base64
from pathlib import Path
from st_keyup import st_keyup # Canlı arama için bu kütüphanenin yüklü olduğundan emin olun

# ==========================================
# 1. SAYFA YAPILANDIRMASI VE CSS
# ==========================================
st.set_page_config(page_title="F2 ICT - Ofis Stok İzleme Paneli", page_icon="📦", layout="wide")

st.markdown("""
    <style>
        footer, .viewerBadge_container, [data-testid="stToolbar"], .stDeployButton, header {display: none !important;}
        .block-container { padding-top: 1.5rem !important; max-width: 100% !important; }
        
        /* ZIPLAMAYI ENGELLEYEN CSS: Arama sütununu sabitler */
        div[data-testid="column"]:has([data-testid="stCustomComponentV1"]) {
            min-height: 84px !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: flex-end !important;
        }

        .custom-logo { height: 60px; object-fit: contain; }
        .stButton > button { 
            background-color: #1C355E !important; color: white !important; 
            border-radius: 6px !important; height: 42px !important; width: 100% !important; 
            margin-top: 30px !important;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOGO VE VERİ
# ==========================================
def logo_to_base64(img_path):
    if os.path.exists(img_path):
        return base64.b64encode(Path(img_path).read_bytes()).decode()
    return None

logo_data = logo_to_base64("logo.png") or logo_to_base64("logo.jpg")

@st.cache_data(ttl=600)
def load_data():
    return pd.read_excel('Stok Sayım Arşivi-v3.1-Web.xlsm', sheet_name='Stok', engine='openpyxl')

# ==========================================
# 3. ANA PANEL (Logo, Başlık ve Kartlar Korundu)
# ==========================================
try:
    df = load_data()
    df.columns = [str(c).strip() for c in df.columns]
    c_kod, c_tanim, c_marka, c_grup, c_maliyet = df.columns[1], df.columns[2], df.columns[3], df.columns[4], df.columns[13]
    c_stok = df.columns[-1]

    # Logo ve Başlık
    logo_html = f'<img src="data:image/png;base64,{logo_data}" class="custom-logo">' if logo_data else "📦"
    st.markdown(f"""
        <div style="display:flex; align-items:center; gap:25px;">
            {logo_html}
            <div><h2 style="margin:0;">Ofis Stok İzleme Paneli</h2><small>📅 Son Güncelleme: {c_stok}</small></div>
        </div>
    """, unsafe_allow_html=True)

    @st.fragment
    def stok_paneli_icerik(data_frame):
        if "reset_counter" not in st.session_state: st.session_state.reset_counter = 0
        
        def filtreleri_temizle():
            st.session_state.reset_counter += 1
            st.session_state.q_grup = "Tümü"
            st.session_state.q_marka = "Tümü"
            st.session_state.q_stok = False

        col1, col2, col3, col4, col5 = st.columns([3.2, 2.4, 2.4, 2.2, 1.2])
        
        with col1:
            v_search = st_keyup("📝 Ürün Ara", key=f"q_search_{st.session_state.reset_counter}", placeholder="Kod veya açıklama...")
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

        # KPI Kartları (Sizin orijinal kodunuzdan alındı)
        k1, k2, k3 = st.columns(3)
        k1.metric("Toplam Çeşit", f"{len(f_df)} Adet")
        k2.metric("Toplam Stok", f"{int(f_df[c_stok].sum()):,} Adet")
        k3.metric("Toplam Maliyet", f"${f_df[c_maliyet].sum():,.0f}")

        st.dataframe(f_df, use_container_width=True, hide_index=True, height=540)

    stok_paneli_icerik(df)
except Exception as e:
    st.error(f"Hata: {e}")
