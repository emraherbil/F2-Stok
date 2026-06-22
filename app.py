import streamlit as st
import pandas as pd
import os
import base64
from pathlib import Path
from st_keyup import st_keyup

# ==========================================
# 1. SAYFA YAPILANDIRMASI VE KÜRESEL STİLLER
# ==========================================
st.set_page_config(
    page_title="F2 ICT - Ofis Stok İzleme Paneli", 
    page_icon="📦",
    layout="wide"
)

# Görsel stabilite, milimetrik hizalama ve ZIPLAMA KİLİDİ CSS kuralları
st.markdown("""
    <style>
        footer {visibility: hidden !important; display: none !important;}
        .viewerBadge_container {display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}
        .stDeployButton {display: none !important;}
        header {visibility: hidden !important; display: none !important;}
        
        html, body, .stApp { background-color: #ffffff !important; }
        
        .block-container { 
            display: block !important;
            padding-top: 1.5rem !important; 
            padding-bottom: 1.5rem !important; 
            max-width: 100% !important;
        }
        
        /* Üst başlık alanını sabitle */
        div[data-testid="stVerticalBlock"] > div:first-child {
            position: sticky !important;
            top: 0px !important;
            background-color: white !important;
            z-index: 9999 !important;
            padding-bottom: 15px !important;
        }
        
        .custom-header-container { 
            display: flex; 
            align-items: center; 
            gap: 25px; 
            padding-top: 5px;
            padding-bottom: 5px;
        }
        .custom-logo { height: 60px; object-fit: contain; }
        .custom-title-block { display: flex; flex-direction: column; justify-content: center; }
        
        /* Tüm form elemanlarının dikey çizgisini ve buton yüksekliğini eşitler */
        div[data-testid="column"] .stFormSubmitButton, 
        div[data-testid="column"] .stButton {
            margin-top: 0px !important;
        }

        /* Checkbox dikey hizalama sabitlemesi */
        div[data-testid="stCheckbox"] { 
            padding-top: 32px !important; 
        }

        /* Temizle Butonunun Tasarımı */
        .stButton > button { 
            background-color: #1C355E !important; 
            color: white !important; 
            border: 1px solid #1C355E !important; 
            border-radius: 6px !important;
            height: 42px !important; 
            width: 100% !important; 
            font-weight: 500 !important;
            transition: all 0.2s !important;
        }
        
        .stButton > button:hover { 
            background-color: #12223c !important;
            border: 1px solid #12223c !important;
            color: white !important; 
        }

        /* 🎯 KESİN ÇÖZÜM: ST_KEYUP KUTUSUNUN ZIPLAMASINI FİZİKSEL OLARAK KİLİTLEYEN CSS 🎯 */
        /* Kutu yüksekliğini tam bir selectbox (etiket+kutu = ~73px) boyutunda betonluyoruz */
        div[data-testid="element-container"]:has(iframe[title*="st_keyup"]) {
            min-height: 73px !important;
            margin-bottom: 0px !important;
            display: block !important;
        }
        
        div[data-testid="stCustomComponentV1"]:has(iframe[title*="st_keyup"]) {
            min-height: 73px !important;
            padding: 0 !important;
        }
        
        iframe[title*="st_keyup"] {
            min-height: 73px !important;
            border: none !important;
        }
        
        /* Girdi kutularının sınır yarıçapı */
        div[data-baseweb="input"] {
            border-radius: 6px !important;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOGO VE VERİ YÜKLEME FONKSİYONLARI
# ==========================================
def logo_to_base64(img_path):
    try:
        if os.path.exists(img_path):
            img_bytes = Path(img_path).read_bytes()
            return base64.b64encode(img_bytes).decode()
    except Exception:
        pass
    return None

logo_data = logo_to_base64("logo.png") or logo_to_base64("logo.jpg")

@st.cache_data(ttl=600)
def load_data():
    return pd.read_excel('Stok Sayım Arşivi-v3.1-Web.xlsm', sheet_name='Stok', engine='openpyxl')

# ==========================================
# 3. ANA PANEL DÜZENİ
# ==========================================
try:
    df = load_data()
    df.columns = [str(c).strip() for c in df.columns]
    
    c_kod = df.columns[1]     
    c_tanim = df.columns[2] 
    c_marka = df.columns[3]         
    c_grup = df.columns[4]          
    c_fiyat = df.columns[12]        
    c_maliyet = df.columns[13]      
    
    sayim_cols = list(df.columns[14:]) 
    c_stok = sayim_cols[-1] if sayim_cols else df.columns[-1]

    df[c_stok] = pd.to_numeric(df[c_stok], errors='coerce').fillna(0)
    df[c_maliyet] = pd.to_numeric(df[c_maliyet], errors='coerce').fillna(0)
    df[c_fiyat] = pd.to_numeric(df[c_fiyat], errors='coerce').fillna(0)

    if logo_data:
        logo_html = f'<img src="data:image/png;base64,{logo_data}" class="custom-logo">'
    else:
        logo_html = '<div style="font-size: 2.5rem;">📦</div>'

    st.markdown(f"""
        <div class="custom-header-container">
            {logo_html}
            <div class="custom-title-block">
                <h2 style="margin:0; padding:0; font-size:1.85rem; color:#262730; font-weight:700; line-height:1.2;">Ofis Stok İzleme Paneli</h2>
                <span style="color:#7d7f87; font-size:0.85rem; margin-top:4px;">📅 <b>Son Güncelleme / Sayım Tarihi:</b> {c_stok}</span>
            </div>
        </div>
        <div style="margin-top:10px;"></div>
    """, unsafe_allow_html=True)

    # ==========================================
    # 4. FRAGMENT ALANI (SABİT FORM MİMARİSİ)
    # ==========================================
    @st.fragment
    def stok_paneli_icerik(data_frame):
        # Temizle butonu için versiyon takibi
        if "clear_version" not in st.session_state: st.session_state.clear_version = 0
        if "q_search" not in st.session_
