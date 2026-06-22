import streamlit as st
import pandas as pd
import os
import base64
from pathlib import Path
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
# 1. SAYFA YAPILANDIRMASI VE SABİT CSS
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

# Standart araç çubuklarını gizle
st.markdown("""
    <style>
        footer {visibility: hidden !important; display: none !important;}
        .viewerBadge_container {display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}
        .stDeployButton {display: none !important;}
        header {visibility: hidden !important; display: none !important;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOGO VE ÖNBELLEK FONKSİYONLARI
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
# 3. GİRİŞ EKRANI (ZIPLAMAYAN & KAYMAYAN YENİ MİMARİ)
# ==========================================
if not st.session_state.logged_in:
    # Sayfadaki bileşenlerin kaymasını engelleyen, yerleşik input ve buton stilleri
    st.markdown("""
    <style>
        /* Arka plan yumuşak gri */
        html, body, .stApp { 
            background-color: #f8fafc !important; 
        }
        
        /* Girdileri daha estetik yap */
        [data-testid="stAppViewContainer"] [data-baseweb="input"] {
            background-color: #f1f5f9 !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 8px !important;
        }
        
        /* BUTON TASARIMI: Koyu lacivert, tam genişlik, kayma yapmaz */
        div[data-testid="stButton"] button {
            width: 100% !important;
            background-color: #1e293b !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            height: 45px !important;
            font-size: 14px !important;
            margin-top: 10px !important;
            transition: background-color 0.2s !important;
        }
        div[data-testid="stButton"] button:hover {
            background-color: #0f172a !important;
            color: white !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Sayfayı dikeyde ve yatayda kusursuz ortalamak için güvenli sütun yapısı
    st.markdown("<div style='margin-top: 10vh;'></div>", unsafe_allow_html=True)
    
    col_left, col_center, col_right = st.columns([4.4, 3.2, 4.4])
    
    with col_center:
        # Beyaz Kart yapısının üst sınırını HTML ile başlatıyoruz (Böylece iç kısımlar kaymıyor)
        st.markdown("""
            <div style="background-color: #ffffff; padding: 35px 30px; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0px 8px 30px rgba(0, 0, 0, 0.025);">
        """, unsafe_allow_html=True)
        
        # 1. Logo Alanı
        if logo_data:
            st.markdown(f'<div style="text-align: center; margin-bottom: 15px;"><img src="data:image/png;base64,{logo_data}" style="max-width: 210px; height: auto;"></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align: center; font-size: 2.5rem; margin-bottom: 15px;">📦</div>', unsafe_allow_html=True)
            
        # 2. Başlık Bilgisi
        st.markdown('<div style="text-align: center; font-size: 17px; color: #475569; margin-bottom: 25px; font-weight: 600; font-family: sans-serif;">Ofis Stok İzleme Paneli</div>', unsafe_allow_html=True)
        
        # 3. Giriş Elemanları (Streamlit yerleşik form yerine doğrudan temiz girdiler)
        username_input = st.text_input("Kullanıcı Adı", placeholder="Kullanıcı adınızı yazın", label_visibility="collapsed", key="login_user")
        password_input = st.text_input("Şifre", type="password", placeholder="Şifrenizi yazın", label_visibility="collapsed", key="login_pass")
        
        # 4. Giriş Butonu
        submit_button = st.button("Sisteme Giriş Yap")
        
        # HTML Kart Yapısını Kapatıyoruz
        st.markdown("</div>", unsafe_allow_html=True)

        # Doğrulama Kontrolü
        if submit_button:
            if username_input == VALID_USERNAME and password_input == VALID_PASSWORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                st.error("Hatalı kullanıcı adı veya şifre!")

# ==========================================
# 4. ANA PANEL (BAŞARILI GİRİŞ SONRASI)
# ==========================================
else:
    # Giriş yapıldığında arka planı tamamen beyaz yapıp, giriş ekranı kart stillerini temizle
    st.markdown("""
    <style>
        html, body, .stApp { background-color: #ffffff !important; }
        .block-container { 
            display: block !important;
            padding-top: 1.5rem !important; 
            padding-bottom: 1.5rem !important; 
            max-width: 100% !important;
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
        
        div[data-testid="stHorizontalBlock"] { align-items: flex-start !important; } 
        div[data-testid="stHorizontalBlock"] div[data-testid="stCheckbox"] { margin-top: 32px !important; }

        /* Filtre alanındaki temizle butonu ayarı */
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

        # ==========================================
        # 5. FRAGMENT ALANI (İLİŞKİLİ FİLTRELEME)
        # ==========================================
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
            grup_ops = ["Tümü"] + sorted([str(x) for x in df_for_grup[c_grup].dropna().unique() if str(x).lower() != 'nan'])

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
                v_marka = st.selectbox("🏷️ Marka", marka_ops, key="q_marka")

            with col3:
                v_grup = st.selectbox("📂 Ürün Grubu", grup_ops, key="q_grup")

            with col4:
                v_stok = st.checkbox("🚫 Tükenenleri Gizle", key="q_stok")

            with col5:
                st.button("🧹 Temizle", on_click=filtreleri_temizle, use_container_width=True)

            f_df = data_frame.copy()
            if v_search:
                m1 = f_df[c_kod].astype(str).str.contains(v_search, case=False)
                m2 = f_df[c_tanim].astype(str).str.contains(v_search, case=False)
                f_df = f_df[m1 | m2]
            if v_marka != "Tümü": f_df = f_df[f_df[c_marka].astype(str) == v_marka]
            if v_grup != "Tümü": f_df = f_df[f_df[c_grup].astype(str) == v_grup]
            if v_stok: f_df = f_df[f_df[c_stok] > 0]

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
# --- RESMİ CANLI ARAMA EKLENTİSİ ---
try:
    from st_keyup import st_keyup
except ImportError:
    st.error("Lütfen terminalde 'pip install streamlit-keyup' çalıştırın veya requirements.txt dosyanıza 'streamlit-keyup' ekleyin.")
    st.stop()
# -----------------------------------

# ==========================================
# 1. SAYFA YAPILANDIRMASI VE SABİT CSS
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

# Standart Streamlit üst/alt araç çubuklarını gizle
st.markdown("""
    <style>
        footer {visibility: hidden !important; display: none !important;}
        .viewerBadge_container {display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}
        .stDeployButton {display: none !important;}
        header {visibility: hidden !important; display: none !important;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOGO VE ÖNBELLEK FONKSİYONLARI
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
# 3. GİRİŞ EKRANI (GARANTİLİ FORM MİMARİSİ)
# ==========================================
if not st.session_state.logged_in:
    # Sayfa arka planını hafif gri yapıp, formu pürüzsüz beyaz bir karta dönüştüren CSS
    st.markdown("""
    <style>
        /* Arka plan yumuşak gri */
        html, body, .stApp { 
            background-color: #f8fafc !important; 
        }
        
        /* BEYAZ KART ÇERÇEVESİ (Streamlit Formunu şık bir karta dönüştürür) */
        div[data-testid="stForm"] {
            background-color: #ffffff !important;
            padding: 40px 35px !important;
            border-radius: 16px !important;
            box-shadow: 0px 10px 35px rgba(0, 0, 0, 0.03) !important;
            border: 1px solid #e2e8f0 !important;
        }
        
        /* Kullanıcı adı ve şifre kutularını estetik gri yap */
        [data-testid="stForm"] [data-baseweb="input"] {
            background-color: #f1f5f9 !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 8px !important;
        }
        
        /* KOYU LACİVERT VE TAM GENİŞLİKTE BUTON (Sıkışmayı önler) */
        div[data-testid="stForm"] button {
            width: 100% !important;
            background-color: #1e293b !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            height: 46px !important;
            font-size: 14px !important;
            margin-top: 10px !important;
            transition: background-color 0.2s !important;
        }
        
        div[data-testid="stForm"] button:hover {
            background-color: #0f172a !important;
            color: white !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Üstten dikey boşluk ayarı
    st.markdown("<div style='margin-top: 12vh;'></div>", unsafe_allow_html=True)
    
    # Sayfayı ortalamak için güvenli sütun yapısı
    col_left, col_center, col_right = st.columns([4.5, 3.0, 4.5])
    
    with col_center:
        # st.form her şeyi tek bir sınır (border) ve mantıksal bütünlük içinde tutar, zıplama yapmaz
        with st.form(key="login_form", clear_on_submit=False):
            
            # Logo Yapısı
            if logo_data:
                st.markdown(f'<div style="text-align: center; margin-bottom: 15px;"><img src="data:image/png;base64,{logo_data}" style="max-width: 210px; height: auto;"></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="text-align: center; font-size: 2.5rem; margin-bottom: 15px;">📦</div>', unsafe_allow_html=True)
                
            # Alt Başlık
            st.markdown('<div style="text-align: center; font-size: 17px; color: #475569; margin-bottom: 25px; font-weight: 600; font-family: sans-serif;">Ofis Stok İzleme Paneli</div>', unsafe_allow_html=True)
            
            # Form Girdileri
            username_input = st.text_input("Kullanıcı Adı", placeholder="Kullanıcı adınızı yazın", label_visibility="collapsed")
            password_input = st.text_input("Şifre", type="password", placeholder="Şifrenizi yazın", label_visibility="collapsed")
            
            # Formun kendi submit butonu (Asla kaymaz veya sıkışmaz)
            submit_button = st.form_submit_button("Sisteme Giriş Yap")

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
    # Giriş yapıldıktan sonra arka planı ve düzeni temizle
    st.markdown("""
    <style>
        html, body, .stApp { background-color: #ffffff !important; }
        .block-container { 
            display: block !important;
            padding-top: 1.5rem !important; 
            padding-bottom: 1.5rem !important; 
            max-width: 100% !important;
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
        
        div[data-testid="stHorizontalBlock"] { align-items: flex-start !important; } 
        div[data-testid="stHorizontalBlock"] div[data-testid="stCheckbox"] { margin-top: 32px !important; }

        /* Filtre alanındaki temizle butonu */
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

        # ==========================================
        # 5. FRAGMENT ALANI (İLİŞKİLİ FİLTRELEME)
        # ==========================================
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
            grup_ops = ["Tümü"] + sorted([str(x) for x in df_for_grup[c_grup].dropna().unique() if str(x).lower() != 'nan'])

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
                v_marka = st.selectbox("🏷️ Marka", marka_ops, key="q_marka")

            with col3:
                v_grup = st.selectbox("📂 Ürün Grubu", grup_ops, key="q_grup")

            with col4:
                v_stok = st.checkbox("🚫 Tükenenleri Gizle", key="q_stok")

            with col5:
                st.button("🧹 Temizle", on_click=filtreleri_temizle, use_container_width=True)

            f_df = data_frame.copy()
            if v_search:
                m1 = f_df[c_kod].astype(str).str.contains(v_search, case=False)
                m2 = f_df[c_tanim].astype(str).str.contains(v_search, case=False)
                f_df = f_df[m1 | m2]
            if v_marka != "Tümü": f_df = f_df[f_df[c_marka].astype(str) == v_marka]
            if v_grup != "Tümü": f_df = f_df[f_df[c_grup].astype(str) == v_grup]
            if v_stok: f_df = f_df[f_df[c_stok] > 0]

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
