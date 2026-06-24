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

# 🎯 MİLİMETRİK HİZALAMA VE EZİLMEYİ SIFIRLAYAN CSS
st.markdown("""
    <style>
        footer {visibility: hidden !important; display: none !important;}
        .viewerBadge_container {display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}
        .stDeployButton {display: none !important;}
        header {visibility: hidden !important; display: none !important;}
        
        html, body, .stApp { background-color: transparent !important; }
        
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
            background-color: transparent !important;
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
        
        /* Kolon yapısı */
        div[data-testid="column"] {
            display: block !important;
        }
        
        /* Form elemanlarının genişliklerini eşitle */
        div[data-testid="column"] .stFormSubmitButton, 
        div[data-testid="column"] .stButton,
        div[data-testid="column"] .stTextInput,
        div[data-testid="column"] .stSelectbox {
            margin-bottom: 0px !important;
            width: 100% !important;
        }

               div[data-testid="stCustomComponentV1"] {
            overflow: visible !important;
            position: relative !important;
        }
        
        .arama-label {
    font-size: 14px;
    color: rgb(49,51,63);
    font-weight: 400;
    margin-bottom: 2px;
    line-height: 1.4;
}

div[data-testid="stCustomComponentV1"] {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

iframe[title*="st_keyup"] {
    height: 70px !important;
    background: transparent !important;
}
            div[data-testid="stCustomComponentV1"] {
            background-color: transparent !important;
            background: transparent !important;
        }

        /* Checkbox dikey hizalaması */
        div[data-testid="stCheckbox"] { 
            padding-top: 24px !important;
            padding-bottom: 0px !important; 
        }

        /* Temizle Butonunun Dikey Konumu */
        div[data-testid="column"]:last-child .stButton {
            margin-top: 24px !important;
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
        <div style="margin-top:35px;"></div> """, unsafe_allow_html=True)

    # ==========================================
    # 4. FRAGMENT ALANI (ZANNETSİZ VE KİLİTLİ YAPI)
    # ==========================================
    @st.fragment
    def stok_paneli_icerik(data_frame):
        if "clear_ver" not in st.session_state: st.session_state.clear_ver = 0
        if "q_grup" not in st.session_state: st.session_state.q_grup = "Tümü"
        if "q_marka" not in st.session_state: st.session_state.q_marka = "Tümü"
        if "q_stok" not in st.session_state: st.session_state.q_stok = False
        
        def filtreleri_temizle():
            st.session_state.clear_ver += 1
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

    st.markdown("""
    <div class="arama-label">
        📝 Ürün Ara
    </div>
    """, unsafe_allow_html=True)

    v_search = st_keyup(
        "",
        key=f"search_box_{st.session_state.clear_ver}",
        placeholder="Yazmaya başlayın...",
        debounce=300
    )

        with col2:
            v_marka = st.selectbox("🏷️ Marka", marka_ops, key="q_marka")

        with col3:
            v_grup = st.selectbox("📂 Ürün Grubu", grup_ops, key="q_grup")

        with col4:
            v_stok = st.checkbox("🚫 Tükenenleri Gizle", key="q_stok")

        with col5:
            st.button("🧹 Temizle", on_click=filtreleri_temizle, use_container_width=True)

        # Filtreleme Algoritması
        f_df = data_frame.copy()
        if v_search:
            m1 = f_df[c_kod].astype(str).str.contains(v_search, case=False)
            m2 = f_df[c_tanim].astype(str).str.contains(v_search, case=False)
            f_df = f_df[m1 | m2]
        if v_marka != "Tümü": f_df = f_df[f_df[c_marka].astype(str) == v_marka]
        if v_grup != "Tümü": f_df = f_df[f_df[c_grup].astype(str) == v_grup]
        if v_stok: f_df = f_df[f_df[c_stok] > 0]

        # KPI Kartları Hesaplamaları
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
        
        # Veri Tablosu Çıktısı
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
            height=540
        )

    stok_paneli_icerik(df)

except Exception as e:
    st.error(f"Hata oluştu: {e}")
