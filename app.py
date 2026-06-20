import streamlit as st
import pandas as pd
import os
import base64
from pathlib import Path

# ==========================================
# 1. BAĞIMSIZ YARDIMCI FONKSİYONLAR
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
# 2. SAYFA YAPILANDIRMASI VE OTURUM KONTROLÜ
# ==========================================

st.set_page_config(
    page_title="F2 ICT - Ofis Stok İzleme Paneli", 
    page_icon="📦",
    layout="wide"
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

VALID_USERNAME = "admin"
VALID_PASSWORD = "f2"

logo_data = logo_to_base64("logo.png") or logo_to_base64("logo.jpg")

# ==========================================
# 3. KUSURSUZ VE HARİCİ KUTUSUZ GİRİŞ EKRANI
# ==========================================
if not st.session_state.logged_in:
    # Sayfadaki tüm hayalet çerçeveleri yıkan saf CSS sihirbazı
    login_css = """
    <style>
        /* Arka planı temiz soft bir tona eşitle */
        .stApp {
            background-color: #f6f8fa !important;
        }
        
        /* Tüm formu kapsayan tek ve gerçek beyaz kurumsal kart */
        .custom-login-card {
            max-width: 480px;
            margin: 120px auto 0 auto;
            padding: 40px;
            background-color: #ffffff !important;
            border-radius: 12px;
            box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.05);
            border: 1px solid #e1e4e8;
            text-align: center;
        }
        
        /* Logonun taşmasını önleyen ve kibar (300px) tutan kontrol alanı */
        .login-logo-container {
            width: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .login-logo-img {
            width: 100%;
            max-width: 300px !important; /* Logo büyüklüğünü masaüstü için ideal sınıra çektik */
            height: auto;
            object-fit: contain;
        }
        
        .login-subtitle {
            font-size: 0.85rem;
            color: #586069;
            margin-bottom: 25px;
            font-weight: 500;
            letter-spacing: 0.3px;
        }

        /* Streamlit input kutularını ve butonunu tam 300px (Logo genişliği) boyutuna sabitleme */
        div[data-testid="stColumn"] div[data-testid="stWidgetLabel"] {
            display: none !important;
        }
        
        div[data-testid="stColumn"] .stTextInput, 
        div[data-testid="stColumn"] .stButton,
        div[data-testid="stColumn"] .stButton button {
            max-width: 300px !important;
            margin: 0 auto !important;
        }
        
        /* Butonun tasarımını metin kutularıyla pürüzsüzce eşitleme */
        div[data-testid="stColumn"] .stButton button {
            width: 100% !important;
            height: 42px !important;
            background-color: #ffffff !important;
            color: #24292e !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease;
        }
        
        div[data-testid="stColumn"] .stButton button:hover {
            border-color: #1e293b !important;
            background-color: #f8fafc !important;
        }
    </style>
    """
    st.markdown(login_css, unsafe_allow_html=True)
    
    # Giriş Kartı Başlangıcı (Logo artık doğrudan bu kartın İÇİNDEDİR)
    st.markdown('<div class="custom-login-card">', unsafe_allow_html=True)
    
    if logo_data:
        st.markdown(f'<div class="login-logo-container"><img src="data:image/png;base64,{logo_data}" class="login-logo-img"></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size: 3rem; margin-bottom: 10px;">📦</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 1.4rem; font-weight:700; color:#24292e; margin-bottom:3px;">F2 ICT</div>', unsafe_allow_html=True)
        
    st.markdown('<div class="login-subtitle">Ofis Stok İzleme Paneli</div>', unsafe_allow_html=True)
    
    # st.form kullanmadan, elemanları dikeyde hizalamak için tekli sütun mimarisi kullanıyoruz
    # Bu sayede hayalet üst kutu %100 yok edilir.
    _, center_col, _ = st.columns([1, 10, 1])
    
    with center_col:
        username_input = st.text_input("Kullanıcı Adı", placeholder="Kullanıcı adınızı yazın", label_visibility="collapsed")
        st.markdown('<div style="margin-top: 12px;"></div>', unsafe_allow_html=True)
        password_input = st.text_input("Şifre", type="password", placeholder="Şifrenizi yazın", label_visibility="collapsed")
        
        st.markdown('<div style="margin-top: 22px;"></div>', unsafe_allow_html=True)
        login_button = st.button("Sisteme Giriş Yap", use_container_width=True)
        
        if login_button:
            if username_input == VALID_USERNAME and password_input == VALID_PASSWORD:
                st.session_state.logged_in = True
                st.success("Giriş başarılı!")
                st.rerun()
            else:
                st.error("Hatalı kullanıcı adı veya şifre!")
                
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 4. ANA PANEL (YALNIZCA LOGGED_IN = TRUE İSE ÇALIŞIR)
# ==========================================
else:
    css_style = """
    <style>
        .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; background-color: #ffffff !important; }
        
        div[data-testid="stVerticalBlock"] > div:first-child {
            position: sticky !important;
            top: 0px !important;
            background-color: white !important;
            z-index: 9999 !important;
            padding-bottom: 15px !important;
            border-bottom: 1px solid #eef1f6 !important;
        }
        
        [data-baseweb="popover"], div[data-baseweb="select"] {
            z-index: 999999 !important;
        }
        
        .custom-header-container { 
            display: flex; 
            align-items: center; 
            gap: 25px; 
            padding-top: 5px;
            padding-bottom: 5px;
        }
        .custom-logo { 
            height: 60px; 
            object-fit: contain; 
        }
        .custom-title-block { 
            display: flex; 
            flex-direction: column; 
            justify-content: center; 
        }
        
        .stCheckbox { margin-top: 35px !important; }
        .stButton button { margin-top: 28px !important; height: 42px !important; }
        hr { margin: 0.6rem 0 !important; opacity: 0.2; }
    </style>
    """
    st.markdown(css_style, unsafe_allow_html=True)

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

        if "q_search" not in st.session_state: st.session_state.q_search = ""
        if "q_grup" not in st.session_state: st.session_state.q_grup = "Tümü"
        if "q_marka" not in st.session_state: st.session_state.q_marka = "Tümü"
        if "q_stok" not in st.session_state: st.session_state.q_stok = False

        def filtreleri_temizle():
            st.session_state.q_search = ""
            st.session_state.q_grup = "Tümü"
            st.session_state.q_marka = "Tümü"
            st.session_state.q_stok = False

        # LOGO + BAŞLIK PANELİ
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

        # FİLTRELER
        col1, col2, col3, col4, col5 = st.columns([3.2, 2.4, 2.4, 2.2, 1.2])
        
        with col1: 
            v_search = st.text_input("📝 Ürün Ara", key="q_search", placeholder="Kod veya açıklama ara...")
        with col2: 
            marka_ops = ["Tümü"] + sorted([str(x) for x in df[c_marka].dropna().unique() if str(x).lower() != 'nan'])
            v_marka = st.selectbox("🏷️ Marka", marka_ops, key="q_marka")
        with col3: 
            grup_ops = ["Tümü"] + sorted([str(x) for x in df[c_grup].dropna().unique() if str(x).lower() != 'nan'])
            v_grup = st.selectbox("📂 Ürün Grubu", grup_ops, key="q_grup")
        with col4: 
            v_stok = st.checkbox("🚫 Tükenenleri Gizle", key="q_stok")
        with col5: 
            st.button("🧹 Temizle", on_click=filtreleri_temizle, use_container_width=True)

        # Filtreleme Algoritması
        f_df = df.copy()
        if v_search:
            m1 = f_df[c_kod].astype(str).str.contains(v_search, case=False)
            m2 = f_df[c_tanim].astype(str).str.contains(v_search, case=False)
            f_df = f_df[m1 | m2]
        if v_marka != "Tümü": 
            f_df = f_df[f_df[c_marka].astype(str) == v_marka]
        if v_grup != "Tümü": 
            f_df = f_df[f_df[c_grup].astype(str) == v_grup]
        if v_stok: 
            f_df = f_df[f_df[c_stok] > 0]

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

        # AKAN VERİ TABLOSU
        st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
        
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

    except Exception as e:
        st.error(f"Hata olustu: {e}")
