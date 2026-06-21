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

# Genel arayüz temizliği için temel CSS kuralları (Zıplatma yapmayan global kurallar)
st.markdown("""
    <style>
        footer {visibility: hidden !important; display: none !important;}
        .viewerBadge_container {display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}
        .stDeployButton {display: none !important;}
        header {visibility: hidden !important; display: none !important;}
        hr { display: none !important; visibility: hidden !important; }
        
        div[data-testid="stHorizontalBlock"] {
            align-items: flex-start !important;
        } 
        
        div[data-testid="stFragment"] div[data-testid="column"] {
            min-height: 75px !important;
        }

        div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(1) iframe {
            height: 76px !important;
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
# 3. KUSURSUZ GİRİŞ EKRANI (SPESİFİK CSS)
# ==========================================
if not st.session_state.logged_in:
    # Sadece giriş ekranını etkileyen, ana paneli asla kirletmeyen özel CSS
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
        
        /* Sadece giriş formunu yakalamak için hedefli seçici */
        div[data-testid="stAppViewContainer"] [data-testid="stForm"] {
            position: fixed !important;
            top: 50% !important;
            left: 50% !important;
            transform: translate(-50%, -50%) !important;
            width: 380px !important;
            max-width: 90vw !important;
            height: auto !important;
            min-height: auto !important;
            padding: 35px 30px !important;
            background-color: #ffffff !important;
            border-radius: 12px !important;
            box-shadow: 0px 10px 40px rgba(0, 0, 0, 0.08) !important;
            border: 1px solid #e2e8f0 !important;
            margin: 0 !important;
            z-index: 99999 !important;
        }
        
        /* Giriş formundaki girdiler */
        [data-testid="stForm"] [data-baseweb="input"] {
            background-color: #f1f5f9 !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 6px !important;
        }
        
        [data-testid="stForm"] [data-baseweb="input"] button {
            background-color: transparent !important;
            border: none !important;
            width: auto !important;
            height: auto !important;
        }
        
        /* Giriş butonunun genişliğini forma eşitleyip tam oturtma */
        [data-testid="stForm"] [data-testid="stFormSubmitButton"] {
            width: 100% !important;
            display: block !important;
            text-align: center !important;
        }
        
        [data-testid="stForm"] [data-testid="stFormSubmitButton"] button {
            background-color: #1e293b !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
            height: 45px !important;
            width: 100% !important;
            margin: 0 auto !important;
            display: block !important;
            transition: background-color 0.3s;
        }
        [data-testid="stForm"] [data-testid="stFormSubmitButton"] button:hover {
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
        
        st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True) 
        
        submit_button = st.form_submit_button("Sisteme Giriş Yap")
        
        if submit_button:
            if username_input == VALID_USERNAME and password_input == VALID_PASSWORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Hatalı kullanıcı adı veya şifre!")

# ==========================================
# 4. ANA PANEL (GİRİŞ SONRASI - ASLA ZIPLAMAZ)
# ==========================================
else:
    # Giriş yapıldıktan sonra sayfayı temizleyen ve zıplatmayan stabilizesi yüksek hafif CSS
    st.markdown("""
    <style>
        html, body, [data-testid="stAppViewContainer"] { 
            overflow: auto !important; 
            height: auto !important;
            background-color: #ffffff !important;
        }
        .block-container { 
            display: block !important;
            padding-top: 1.5rem !important; 
            padding-bottom: 1.5rem !important; 
            background-color: #ffffff !important; 
        }
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
        
        div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(4) .stCheckbox {
            margin-top: 24px !important;
        }

        .stButton button { 
            margin-top: 24px !important;
            height: 40px !important; 
            width: 100% !important; 
            background-color: #1e293b !important; 
            color: white !important; 
            border: none !important; 
            border-radius: 4px !important;
        }
    </style>
    """, unsafe_allow_html=True)

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

        # =================================================================
        # 5. FRAGMENT ALANI
        # =================================================================
        @st.fragment
        def stok_paneli_icerik(data_frame):
            if "q_grup" not in st.session_state: st.session_state.q_grup = "Tümü"
            if "q_marka" not in st.session_state: st.session_state.q_marka = "Tümü"
            if "q_stok" not in st.session_state: st.session_state.q_stok = False
            
            def filtreleri_temizle():
                st.session_state.q_search = ""
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
            grup_ops = ["Tümü"] + sorted([str(x) for x in data_frame[c_grup].dropna().unique() if str(x).lower() != 'nan'])

            if current_marka not in marka_ops:
                st.session_state.q_marka = "Tümü"

            if current_grup not in grup_ops:
                st.session_state.q_grup = "Tümü"

            with col1:
                if "q_search" not in st.session_state:
                    st.session_state.q_search = ""

                v_search = st_keyup(
                    label="📝 Ürün Ara",
                    key="q_search",
                    placeholder="Kod veya açıklama ara...",
                    debounce=500
                )

            with col2:
                v_marka = st.selectbox(
                    "🏷️ Marka",
                    marka_ops,
                    key="q_marka"
                )

            with col3:
                v_grup = st.selectbox(
                    "📂 Ürün Grubu",
                    grup_ops,
                    key="q_grup"
                )

            with col4:
                v_stok = st.checkbox(
                    "🚫 Tükenenleri Gizle",
                    key="q_stok"
                )

            with col5:
                st.button(
                    "🧹 Temizle",
                    on_click=filtreleri_temizle,
                    use_container_width=True
                )

            # Tablo Filtreleme Mantığı
            f_df = data_frame.copy()
            if v_search:
                m1 = f_df[c_kod].astype(str).str.contains(v_search, case=False)
                m2 = f_df[c_tanim].astype(str).str.contains(v_search, case=False)
                f_df = f_df[m1 | m2]
            if v_marka != "Tümü": f_df = f_df[f_df[c_marka].astype(str) == v_marka]
            if v_grup != "Tümü": f_df = f_df[f_df[c_grup].astype(str) == v_grup]
            if v_stok: f_df = f_df[f_df[c_stok] > 0]

            # KPI Hesaplamaları
            t_prod = len(f_df)
            t_stok = int(f_df[c_stok].sum())
            t_cost = f_df[c_maliyet].sum()
            
            def kpi_card(label, val, color):
                return f"""
                <div style='background-color: rgba(28, 31, 46, 0.03); padding: 12px 15px; border-radius: 6px; border-left: 5px solid {color}; display: flex; justify-content: space-between; align-items: center;'>
                    <span style='font-size:13px; color:#555; font-weight:bold;'>{label}</span>
                    <span style='font-size:1.15rem; font-weight: 800; color:#111;'>{val}</span>
                </div>
                """

            k1, k2, k3 = st.columns(3)
            with k1: st.markdown(kpi_card("📋 Toplam Çeşit:", f"{t_prod:,}".replace(",", ".") + " Adet", "#1E88E5"), unsafe_allow_html=True)
            with k2: st.markdown(kpi_card("📦 Toplam Stok:", f"{t_stok:,}".replace(",", ".") + " Adet", "#4CAF50"), unsafe_allow_html=True)
            with k3: st.markdown(kpi_card("💰 Toplam Maliyet:", f"${t_cost:,.0f}".replace(",", "."), "#FFC107"), unsafe_allow_html=True)

            st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
            
            # Tablo Çıktısı Formatlaması
            out_df = f_df[[c_kod, c_tanim, c_marka, c_grup, c_stok, c_fiyat, c_maliyet]].copy()
            out_df.columns = ["Ürün Kodu", "Açıklama", "Marka", "Ürün Grubu", "Güncel Stok", "Birim Maliyet", "Toplam Maliyet"]
            
            out_df = out_df.reset_index(drop=True)
            raw_stok = out_df["Güncel Stok"].copy()

            out_df["Birim Maliyet"] = out_df["Birim Maliyet"].apply(lambda v: f"${v:,.0f}".replace(",", "."))
            out_df["Toplam Maliyet"] = out_df["Toplam Maliyet"].apply(lambda v: f"${v:,.0f}".replace(",", "."))
            out_df["Güncel Stok"] = out_df["Güncel Stok"].apply(lambda v: f"{int(v):,}".replace(",", "."))

            def row_style(row):
                if raw_stok.loc[row.name] == 0:
                    return ['background-color: rgba(255, 75, 75, 0.08)'] * len(row)
                return [''] * len(row)

            st.dataframe(
                out_df.style.apply(row_style, axis=1), 
                use_container_width=True, 
                hide_index=True,
                height=480
            )

        stok_paneli_icerik(df)

    except Exception as e:
        st.error(f"Hata oluştu: {e}")
