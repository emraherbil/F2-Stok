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
    # Test ortamınızda hata almamak için örnek veri üretiyoruz (Sizde excel dosyasını okuyacaktır)
    try:
        return pd.read_excel('Stok Sayım Arşivi-v3.1-Web.xlsm', sheet_name='Stok', engine='openpyxl')
    except Exception:
        # Excel yoksa uygulamanın çökmemesi için geçici örnek veri (Geliştirme amaçlı)
        return pd.DataFrame({
            "Stok Kodu": ["STK-001", "STK-002", "STK-003", "STK-004"],
            "Ürün Adı": ["Laptop Dell", "Kablosuz Mouse", "Mekanik Klavye", "27 Inc Monitör"],
            "Kategori": ["Bilgisayar", "Aksesuar", "Aksesuar", "Ekran"],
            "Miktar": [15, 50, 30, 12]
        })

# ==========================================
# 2. SAYFA YAPILANDIRMASI
# ==========================================
st.set_page_config(
    page_title="F2 ICT - Ofis Stok İzleme Paneli", 
    page_icon="📦",
    layout="wide"
)

# Yönlendirmeleri gizlemek ve ARAMA KUTUSUNUN DARALMASINI/DALGALANMASINI ÖNLEMEK için CSS
st.markdown("""
    <style>
        footer {visibility: hidden !important; display: none !important;}
        .viewerBadge_container {display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}
        .stDeployButton {display: none !important;}
        header {visibility: hidden !important; display: none !important;}

        /* --- KUSURSUZ SABİTLEME KALIBI --- */
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) { 
            min-height: 80px !important;
        }
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) div[data-testid="element-container"] {
            min-height: 75px !important;
            height: 75px !important;
        }
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) iframe {
            min-height: 75px !important;
            height: 75px !important;
            width: 100% !important;
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

    # Veriyi Yükle ve Temizle
    df = load_data()
    df.columns = [str(c).strip() for c in df.columns]

    # Üst Başlık Alanı (SABİT)
    if logo_data:
        logo_html = f'<img src="data:image/png;base64,{logo_data}" class="custom-logo">'
    else:
        logo_html = '<div style="font-size: 2.5rem;">📦</div>'

    st.markdown(f"""
        <div class="custom-header-container">
            {logo_html}
            <div class="custom-title-block">
                <span style="font-size: 22px; font-weight: 700; color: #1e293b; line-height: 1.2;">F2 ICT</span>
                <span style="font-size: 14px; color: #64748b; font-weight: 500;">Ofis Stok İzleme Paneli</span>
            </div>
        </div>
        <hr>
    """, unsafe_allow_html=True)

    # --- KUSURSUZ ZIPLAMA ÖNLEYİCİ MİMARİ (FRAGMENT) ---
    @st.fragment
    def canli_arama_motoru(veri_seti):
        # Arama kutusu ve Ek filtreler için yan yana sütunlar
        sol_col, sag_col = st.columns([2, 1])
        
        with sol_col:
            # st_keyup eklentisi artık sadece bu fragment'ı tetikler, sayfa yukarı zıplamaz
            arama_kelimesi = st_keyup(
                "Ürün veya Stok Kodu Ara", 
                placeholder="Yazmaya başlayın...", 
                key="canli_stok_arama"
            )
            
        with sag_col:
            # Örnek bir kategori seçici filtre (Opsiyonel)
            kategoriler = ["Tümü"] + list(veri_seti.get("Kategori", pd.Series([""])).unique())
            secilen_kat = st.selectbox("Kategori Filtresi", kategoriler, key="kat_filtresi")

        # Canlı Filtreleme Mantığı
