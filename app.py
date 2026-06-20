import streamlit as st
import pandas as pd
import os
import base64
from pathlib import Path

# --- RESMİ CANLI ARAMA EKLENTİSİ ---
try:
    from st_keyup import st_keyup
except ImportError:
    st.error("Lütfen terminalde 'pip install streamlit-keyup' çalıştırın veya requirements.txt dosyanıza 'streamlit-keyup' ekleyin.")
    st.stop()
# -----------------------------------

# ==========================================
# 1. LOGO DÖNÜŞTÜRÜCÜ
# ==========================================
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

# ==========================================
# 2. SAYFA YAPILANDIRMASI
# ==========================================
st.set_page_config(
    page_title="F2 ICT - Ofis Stok İzleme Paneli", 
    page_icon="📦",
    layout="wide"
)

# Yönlendirmeleri ve varsayılan Streamlit rozetlerini gizleyen CSS
st.markdown("""
    <style>
        footer {visibility: hidden !important; display: none !important;}
        .viewerBadge_container {display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}
        .stDeployButton {display: none !important;}
        header {visibility: hidden !important; display: none !important;}
        
        /* --- ZIPLAMAYI %100 BİTİREN FRAGMENT CSS YAMASI --- */
        /* Filtre parçası içindeki sütunların yüksekliğini betonluyoruz. */
        /* Kutu temizlenirken silinse bile yuvası asla çökmez, zıplama tamamen biter! */
        div[data-testid="stFragment"] div[data-testid="column"] {
            min-height: 90px !important;
        }
    </style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

VALID_USERNAME = "admin"
VALID_PASSWORD = "f2"
logo_data = logo_to_base64("logo.png") or logo_to_base64("logo.jpg")

# ==========================================
# 3. KUSURSUZ GİRİŞ EKRANI
# ==========================================
if not st.session_state.logged_in:
    st.markdown("""
    <style>
        html, body, [data-testid="stAppViewContainer"], .stApp {
            overflow: hidden !important; 
            background-color: #f8fafc !important;
            margin: 0 !important; 
            padding: 0 !important;
            height: 100vh !important;
        }
        .block-container {
            padding: 0 !important;
            max-width: 100% !important;
        }
        [data-testid="stForm"] {
            position: fixed !important;
            top: 50% !important;
            left: 50% !important;
            transform: translate(-50%, -50%) !important;
            width: 380px !important;
            max-width: 90vw !important;
            height: auto !important;
            padding: 40px 30px !important;
            background-color: #ffffff !important;
            border-radius: 12px !important;
            box-shadow: 0px 10px 40px rgba(0, 0, 0, 0.08) !important;
            border: 1px solid #e2e8f0 !important;
            margin: 0 !important;
            z-index: 99999 !important;
        }
        [data-baseweb="input"] {
            background-color: #f1f5f9 !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 6px !important;
        }
        [data-testid="stFormSubmitButton"] button {
            background-color: #1e293b !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
            height: 45px !important;
            width: 100% !important;
            transition: background-color 0.3s;
        }
        [data-testid="stFormSubmitButton"] button:hover {
            background-color: #0f172a !important;
        }        
    </style>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        if logo_data:
            st.markdown(f'<div style="text-align: center; margin-bottom: 15px;"><img src="data:image/png;base64,{logo_data}" style="max-width: 200px; height: auto;"></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align: center; font-size: 2.5rem; margin-bottom: 15px;">📦</div>', unsafe_allow_html=True)
            
        st.markdown('<div style="text-align: center; font-size: 17px; color: #64748b; margin-bottom: 15px; font-weight: 500;">Ofis Stok İzleme Paneli</div>', unsafe_allow_html=True)
        
        username_input = st.text_input("Kullanıcı Adı", placeholder="Kullanıcı adınızı yazın", label_visibility="collapsed")
        password_input = st.text_input("Şifre", type="password", placeholder="Şifrenizi yazın", label_visibility="collapsed")
        
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True) 
        col1, col2, col3 = st.columns([1, 1.5, 1]) 
        
        with col2:
            submit_button = st.form_submit_button("Sisteme Giriş Yap", use_container_width=True)
        
        if submit_button:
            if username_input == VALID_USERNAME and password_input == VALID_PASSWORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Hatalı kullanıcı adı veya şifre!")

# ==========================================
# 4. ANA PANEL (BAŞARILI GİRİŞ SONRASI)
# ==========================================
else:
    main_panel_css = """
    <style>
        html, body, [data-testid="stAppViewContainer"] { overflow: auto !important; }
        [data-testid="stForm"] {
            position: relative !important;
            top: auto !important;
            left: auto !important;
            transform: none !important;
            width: 100% !important;
            max-width: 100% !important;
            padding: 20px !important;
            box-shadow: none !important;
            border: 1px solid #e2e8f0 !important;
        }
        .block-container { 
            display: block !important;
            padding-top: 2rem !important; 
            padding-bottom: 2rem !important; 
            background-color: #ffffff !important; 
        }
        div[data-testid="stVerticalBlock"] > div:first-child {
            position: sticky !important;
            top: 0px !important;
            background-color: white !important;
            z-index: 9999 !important;
            padding-bottom: 15px !important;
            border-bottom: 1px solid #eef1f6 !important;
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
        .stCheckbox { margin-top: 35px !important; }
        .stButton button { 
            margin-top: 28px !important; 
            height: 42px !important; 
            width: auto !important; 
            background-color: #1e293b !important; 
            color: white !important; 
            border: none !important; 
        }
        hr { margin: 0.6rem 0 !important; opacity: 0.2; }
    </style>
    """
    st.markdown(main_panel_css, unsafe_allow_html=True)

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

        # --- SABİT HEADER BÖLÜMÜ (ASLA YENİLENMEZ) ---
        if logo_data:
            header_html = f"""
            <div class="custom-header-container">
                <img src="data:image/png;base64,{logo_data}" class="custom-logo">
                <div class="custom-title-block">
                    <h2 style="margin:0; padding:0; font-size:1.85rem; color:#262730; font-weight:700; line-height:1.2;">Ofis Stok İzleme Paneli</h2>
                    <span style="color:#7d7f87; font-size:0.85rem; margin-top:4px;">📅 <b>Son Güncelleme / Sayım Tarihi:</b> {c_stok}</span>
                </div>
            </div>
            """
        else:
            header_html = f"""
            <div class="custom-header-container">
                <h1 style="margin:0;">📦</h1>
                <div class="custom-title-block">
                    <h2 style="margin:0; padding:0; font-size:1.85rem; color:#262730; font-weight:700;">Ofis Stok İzleme Paneli</h2>
                    <span style="color:#7d7f87; font-size:0.85rem; margin-top:4px;">📅 <b>Son Güncelleme / Sayım Tarihi:</b> {c_stok}</span>
                </div>
            </div>
            """
        st.markdown(header_html, unsafe_allow_html=True)
        st.markdown("---")

        # =================================================================
        # 5. SİHİRLİ PARÇA (FRAGMENT) ALANI
        # =================================================================
        @st.fragment
        def stok_paneli_icerik(data_frame):
            if "q_grup" not in st.session_state: st.session_state.q_grup = "Tümü"
            if "q_marka" not in st.session_state: st.session_state.q_marka = "Tümü"
            if "q_stok" not in st.session_state: st.session_state.q_stok = False
            if "search_key" not in st.session_state: st.session_state.search_key = 0 

            def filtreleri_temizle():
                st.session_state.search_key += 1 
                st.session_state.q_grup = "Tümü"
                st.session_state.q_marka = "Tümü"
                st.session_state.q_stok = False

            col1, col2, col3, col4, col5 = st.columns([3.2, 2.4, 2.4, 2.2, 1.2])
            
            current_marka = st.session_state.q_marka
            current_grup = st.session_state.q_grup

            if current_grup != "Tümü":
                df_for_marka = data_frame[data_frame[c_grup].astype(str) == current_grup]
            else:
                df_for_marka = data_frame
            marka_ops = ["Tümü"] + sorted([str(x) for x in df_for_marka[c_marka].dropna().unique() if str(x).lower() != 'nan'])

            if current_marka != "Tümü":
                df_for_grup = data_frame[data_frame[c_marka].astype(str) == current_marka]
            else:
                df_for_grup = data_frame
            grup_ops = ["Tümü"] + sorted([str(x) for x in df_for_grup[c_grup].dropna().unique() if str(x).lower() != 'nan'])

            if current_marka not in marka_ops: st.session_state.q_marka = "Tümü"
            if current_grup not in grup_ops: st.session_state.q_grup = "Tümü"
                
            with col1: 
                v_search = st_keyup(
                    label="📝 Ürün Ara", 
                    key=f"q_search_{st.session_state.search_key}", 
                    placeholder="Kod veya açıklama ara...", 
                    debounce=300
                )
                
            with col2: v_marka = st.selectbox("🏷️ Marka", marka_ops, key="q_marka")
            with col3: v_grup = st.selectbox("📂 Ürün Grubu", grup_ops, key="q_grup")
            with col4: v_stok = st.checkbox("🚫 Tükenenleri Gizle", key="q_stok")
            with col5: st.button("🧹 Temizle", on_click=filtreleri_temizle, use_container_width=True)

            # Tablo Filtreleme Mantığı
            f_df = data_frame.copy()
            if v_search:
                m1 = f_df[c_kod].astype(str).str.contains(v_search, case=False)
                m2 = f_df[c_tanim].astype(str).str.contains(v_search, case=False)
