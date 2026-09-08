import streamlit as st
import pandas as pd
import os
import base64
from pathlib import Path

# ==========================================
# 1. SAYFA YAPILANDIRMASI
# ==========================================
st.set_page_config(
    page_title="F2 ICT - Ofis Stok İzleme Paneli", 
    page_icon="📦",
    layout="wide"
)

# 🎯 DARK / LIGHT MOD DURUMU VE GELİŞMİŞ CSS FİX
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

is_dark = st.session_state.dark_mode

# Renk Paleti Tanımlamaları
bg_color = "#0E1117" if is_dark else "#FFFFFF"
input_bg = "#1E222A" if is_dark else "#FFFFFF"
input_border = "#383E4A" if is_dark else "#D3D3D3"
text_color = "#FAFAFA" if is_dark else "#262730"
subtext_color = "#A3A8B4" if is_dark else "#7D7F87"
card_bg = "rgba(255, 255, 255, 0.05)" if is_dark else "rgba(28, 31, 46, 0.03)"
card_text = "#FFFFFF" if is_dark else "#111111"
card_label = "#AAAAAA" if is_dark else "#555555"

st.markdown(f"""
    <style>
        footer {{visibility: hidden !important; display: none !important;}}
        .viewerBadge_container {{display: none !important;}}
        header {{visibility: hidden !important; display: none !important;}}
        
        /* STREAMLIT GLOBAL CSS DEĞİŞKENLERİ */
        :root {{
            --background-color: {bg_color} !important;
            --secondary-background-color: {input_bg} !important;
            --text-color: {text_color} !important;
        }}

        html, body, .stApp {{ 
            background-color: {bg_color} !important; 
            color: {text_color} !important;
        }}
        
        .block-container {{ 
            padding-top: 1.5rem !important; 
            padding-bottom: 1.5rem !important; 
            max-width: 100% !important;
        }}
        
        /* GİRDİ KUTUSU ETİKETLERİ */
        div[data-testid="stWidgetLabel"] label, 
        div[data-testid="stWidgetLabel"] p,
        label[data-testid="stWidgetLabel"] {{
            color: {text_color} !important;
            font-weight: 600 !important;
        }}

        /* TEXT INPUT VE SELECTBOX KUTULARININ ARKA PLANI */
        div[data-baseweb="input"], 
        div[data-baseweb="select"] > div {{
            background-color: {input_bg} !important;
            color: {text_color} !important;
            border-color: {input_border} !important;
        }}

        div[data-baseweb="input"] input {{
            color: {text_color} !important;
        }}

        /* SELECTBOX OK SİMGESİ VE METİNLERİ */
        div[data-baseweb="select"] span, 
        div[data-baseweb="select"] svg {{
            color: {text_color} !important;
            fill: {text_color} !important;
        }}

        /* SELECTBOX AÇILAN LİSTE MENÜSÜ */
        div[data-baseweb="popover"] div,
        div[data-baseweb="option"] {{
            background-color: {input_bg} !important;
            color: {text_color} !important;
        }}
        div[data-baseweb="option"]:hover {{
            background-color: {"#2D323E" if is_dark else "#EAEAEA"} !important;
        }}

        /* CHECKBOX YAZILARI */
        div[data-testid="stCheckbox"] label span {{
            color: {text_color} !important;
        }}
        div[data-testid="stCheckbox"] {{
            margin-bottom: -15px !important;
        }}

        /* 🟢 KESİN ÇÖZÜM: KARANLIK MOD TOGGLE BUTONU RENGİ (#68A2B9) */
        div[data-testid="stToggle"] div[role="switch"] {{
            background-color: rgba(104, 162, 185, 0.3) !important;
        }}
        div[data-testid="stToggle"] div[role="switch"][aria-checked="true"] {{
            background-color: #68A2B9 !important;
        }}

        .custom-header-container {{ 
            display: flex; 
            align-items: center; 
            justify-content: space-between;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .custom-header-left {{
            display: flex;
            align-items: center;
            gap: 25px;
        }}
        .custom-logo {{ height: 60px; object-fit: contain; }}
        .custom-title-block {{ display: flex; flex-direction: column; justify-content: center; }}

        .stButton > button {{ 
            background-color: #1C355E !important; 
            color: white !important; 
            border: 1px solid #1C355E !important; 
            border-radius: 6px !important;
            height: 40px !important;
            width: 100% !important; 
            font-weight: 500 !important;
            transition: all 0.2s !important;
        }}
        .stButton > button:hover {{ 
            background-color: #12223c !important;
            border: 1px solid #12223c !important;
            color: white !important; 
        }}
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

    header_col1, header_col2 = st.columns([8.5, 1.5])
    
    with header_col1:
        st.markdown(f"""
            <div class="custom-header-container" style="border-bottom:none; margin-bottom:0; padding-bottom:0;">
                <div class="custom-header-left">
                    {logo_html}
                    <div class="custom-title-block">
                        <h2 style="margin:0; padding:0; font-size:1.85rem; color:{text_color}; font-weight:700; line-height:1.2;">Ofis Stok İzleme Paneli</h2>
                        <span style="color:{subtext_color}; font-size:0.85rem; margin-top:4px;">📅 <b>Son Güncelleme / Sayım Tarihi:</b> {c_stok}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with header_col2:
        st.toggle("🌙 Karanlık Mod", key="dark_mode")

    st.markdown(f"<hr style='margin-top:10px; margin-bottom:20px; border-color:{'#333333' if is_dark else '#e0e0e0'};'>", unsafe_allow_html=True)

    # ==========================================
    # 4. FRAGMENT ALANI 
    # ==========================================
    @st.fragment
    def stok_paneli_icerik(data_frame):
        if "clear_ver" not in st.session_state: st.session_state.clear_ver = 0
        if "q_grup" not in st.session_state: st.session_state.q_grup = "Tümü"
        if "q_marka" not in st.session_state: st.session_state.q_marka = "Tümü"
        if "q_stok" not in st.session_state: st.session_state.q_stok = False
        if "q_sifir_stok" not in st.session_state: st.session_state.q_sifir_stok = False
        
        def filtreleri_temizle():
            st.session_state.clear_ver += 1
            st.session_state.q_grup = "Tümü"
            st.session_state.q_marka = "Tümü"
            st.session_state.q_stok = False
            st.session_state.q_sifir_stok = False

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
            v_search = st.text_input(
                label="📝 Ürün Ara", 
                key=f"search_box_{st.session_state.clear_ver}",
                placeholder="Ürün adı veya kodu yazıp Enter'a basın..."
            )

        with col2:
            v_marka = st.selectbox("🏷️ Marka", marka_ops, key="q_marka")

        with col3:
            v_grup = st.selectbox("📂 Ürün Grubu", grup_ops, key="q_grup")

        with col4:
            st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
            v_stok = st.checkbox("🚫 Tükenenleri Gizle", key="q_stok")
            v_sifir_stok = st.checkbox("⚠️ Sadece Tükenenleri Listele", key="q_sifir_stok")

        with col5:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            st.button("🧹 Temizle", on_click=filtreleri_temizle, use_container_width=True)

        f_df = data_frame.copy()
        if v_search:
            m1 = f_df[c_kod].astype(str).str.contains(v_search, case=False)
            m2 = f_df[c_tanim].astype(str).str.contains(v_search, case=False)
            f_df = f_df[m1 | m2]
        if v_marka != "Tümü": f_df = f_df[f_df[c_marka].astype(str) == v_marka]
        if v_grup != "Tümü": f_df = f_df[f_df[c_grup].astype(str) == v_grup]
        
        if v_stok: f_df = f_df[f_df[c_stok] > 0]
        if v_sifir_stok: f_df = f_df[f_df[c_stok] == 0]

        t_prod = len(f_df)
        t_stok = int(f_df[c_stok].sum())
        t_cost = f_df[c_maliyet].sum()
        
        def kpi_card(label, val, color):
            return f"""
            <div style='background-color: {card_bg}; padding: 12px 15px; border-radius: 6px; border-left: 5px solid {color}; display: flex; justify-content: space-between; align-items: center; margin-top: 10px;'>
                <span style='font-size:13px; color:{card_label}; font-weight:bold;'>{label}</span>
                <span style='font-size:1.15rem; font-weight: 800; color:{card_text};'>{val}</span>
            </div>
            """

        k1, k2, k3 = st.columns(3)
        with k1: st.markdown(kpi_card("📋 Toplam Çesit:", f"{t_prod:,}".replace(",", ".") + " Adet", "#1E88E5"), unsafe_allow_html=True)
        with k2: st.markdown(kpi_card("📦 Toplam Stok:", f"{t_stok:,}".replace(",", ".") + " Adet", "#4CAF50"), unsafe_allow_html=True)
        with k3: st.markdown(kpi_card("💰 Toplam Maliyet:", f"${t_cost:,.0f}".replace(",", "."), "#FFC107"), unsafe_allow_html=True)

        st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
        
        out_df = f_df[[c_kod, c_tanim, c_marka, c_grup, c_stok, c_fiyat, c_maliyet]].copy()
        out_df.columns = ["Ürün Kodu", "Açıklama", "Marka", "Ürün Grubu", "Güncel Stok", "Birim Maliyet", "Toplam Maliyet"]
        
        out_df["Ürün Kodu"] = out_df["Ürün Kodu"].astype(str)
        out_df = out_df.reset_index(drop=True)
        raw_stok = out_df["Güncel Stok"].copy()

        out_df["Birim Maliyet"] = out_df["Birim Maliyet"].apply(
            lambda v: f"${v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        out_df["Toplam Maliyet"] = out_df["Toplam Maliyet"].apply(
            lambda v: f"${v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        
        out_df["Güncel Stok"] = out_df["Güncel Stok"].apply(lambda v: f"{int(v):,}".replace(",", "."))

        # 🟢 TABLO İÇİ DİNAMİK RENKLENDİRME (Hafif ve Uyumlu Tonlar)
        def row_style(row):
            is_zero = raw_stok.loc[row.name] == 0
            
            if is_dark:
                # Karanlık mod: Tükenenler için #68A2B9 tonunun hafif şeffaf versiyonu (arka planı boğmaz)
                bg = 'rgba(104, 162, 185, 0.18)' if is_zero else '#1E222A'
                color = '#F5F5F5'
                return [f'background-color: {bg}; color: {color}'] * len(row)
            else:
                # Aydınlık mod: Tükenenler için hafif kırmızı/pembe
                if is_zero:
                    return ['background-color: rgba(255, 75, 75, 0.15); color: #000000'] * len(row)
                return [''] * len(row)

        st.dataframe(
            out_df.style.apply(row_style, axis=1), 
            use_container_width=True, 
            hide_index=True,
            height=540,
            column_config={
                "Marka": st.column_config.Column(alignment="center"),
                "Ürün Grubu": st.column_config.Column(alignment="center"),
                "Güncel Stok": st.column_config.Column(alignment="center"),
                "Birim Maliyet": st.column_config.Column(alignment="right"),
                "Toplam Maliyet": st.column_config.Column(alignment="right")
            }
        )

    stok_paneli_icerik(df)

except Exception as e:
    st.error(f"Hata oluştu: {e}")
