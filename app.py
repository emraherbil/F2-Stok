import streamlit as st
import pandas as pd
import os
import base64
from pathlib import Path
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode # YENİ EKLENEN KÜTÜPHANE

# ==========================================
# 1. SAYFA YAPILANDIRMASI VE KÜRESEL STİLLER
# ==========================================
st.set_page_config(
    page_title="F2 ICT - Ofis Stok İzleme Paneli", 
    page_icon="📦",
    layout="wide"
)

st.markdown("""
    <style>
        footer {visibility: hidden !important; display: none !important;}
        .viewerBadge_container {display: none !important;}
        header {visibility: hidden !important; display: none !important;}
        
        html, body, .stApp { background-color: transparent !important; }
        
        .block-container { 
            padding-top: 1.5rem !important; 
            padding-bottom: 1.5rem !important; 
            max-width: 100% !important;
        }
        
        .custom-header-container { 
            display: flex; 
            align-items: center; 
            gap: 25px; 
            padding-bottom: 10px;
            border-bottom: 1px solid #e0e0e0;
            margin-bottom: 20px;
        }
        .custom-logo { height: 60px; object-fit: contain; }
        .custom-title-block { display: flex; flex-direction: column; justify-content: center; }
        
        div[data-testid="stCheckbox"] {
            margin-bottom: -15px !important;
        }
        div[data-testid="stCheckbox"] label {
            font-size: 0.9rem !important;
        }

        .stButton > button { 
            background-color: #1C355E !important; 
            color: white !important; 
            border: 1px solid #1C355E !important; 
            border-radius: 6px !important;
            height: 40px !important;
            width: 100% !important; 
            font-weight: 500 !important;
            transition: all 0.2s !important;
        }
        .stButton > button:hover { 
            background-color: #12223c !important;
            border: 1px solid #12223c !important;
            color: white !important; 
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOGO VE VERİ YÜKLEME
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
    
    # 🎯 Sizin belirttiğiniz gibi L sütununa denk gelen 12. İndeks
    c_not = df.columns[12]          
    
    c_fiyat = df.columns[12] # Excel'inizdeki asıl fiyat/maliyet sütun indisleri
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
        """, unsafe_allow_html=True)

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
        
        # Filtreleme UI Kısımları (Önceki kodla aynı)
        current_marka = st.session_state.q_marka
        current_grup = st.session_state.q_grup

        df_for_marka = data_frame[data_frame[c_grup].astype(str) == current_grup] if current_grup != "Tümü" else data_frame
        marka_ops = ["Tümü"] + sorted([str(x) for x in df_for_marka[c_marka].dropna().unique() if str(x).lower() != 'nan'])

        df_for_grup = data_frame[data_frame[c_marka].astype(str) == current_marka] if current_marka != "Tümü" else data_frame
        grup_ops = ["Tümü"] + sorted([str(x) for x in df_for_grup[c_grup].dropna().unique() if str(x).lower() != 'nan'])

        if current_marka not in marka_ops: st.session_state.q_marka = "Tümü"
        if current_grup not in grup_ops: st.session_state.q_grup = "Tümü"

        with col1: v_search = st.text_input("📝 Ürün Ara", key=f"search_box_{st.session_state.clear_ver}", placeholder="Ürün adı veya kodu yazıp Enter'a basın...")
        with col2: v_marka = st.selectbox("🏷️ Marka", marka_ops, key="q_marka")
        with col3: v_grup = st.selectbox("📂 Ürün Grubu", grup_ops, key="q_grup")
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
        
        # KPI Kartları
        k1, k2, k3 = st.columns(3)
        def kpi_card(label, val, color):
            return f"<div style='background-color: rgba(28, 31, 46, 0.03); padding: 12px 15px; border-radius: 6px; border-left: 5px solid {color}; display: flex; justify-content: space-between; align-items: center; margin-top: 10px;'><span style='font-size:13px; color:#555; font-weight:bold;'>{label}</span><span style='font-size:1.15rem; font-weight: 800; color:#111;'>{val}</span></div>"
        with k1: st.markdown(kpi_card("📋 Toplam Çesit:", f"{t_prod:,}".replace(",", ".") + " Adet", "#1E88E5"), unsafe_allow_html=True)
        with k2: st.markdown(kpi_card("📦 Toplam Stok:", f"{t_stok:,}".replace(",", ".") + " Adet", "#4CAF50"), unsafe_allow_html=True)
        with k3: st.markdown(kpi_card("💰 Toplam Maliyet:", f"${t_cost:,.0f}".replace(",", "."), "#FFC107"), unsafe_allow_html=True)

        st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
        
        # 🎯 Veri Çerçevesini Hazırlama (Metne ÇEVİRMİYORUZ ki sıralama çalışsın)
        out_df = f_df[[c_kod, c_tanim, c_marka, c_grup, c_stok, c_not, c_fiyat, c_maliyet]].copy()
        out_df.columns = ["Ürün Kodu", "Açıklama", "Marka", "Ürün Grubu", "Güncel Stok", "Notlar", "Birim Maliyet", "Toplam Maliyet"]
        out_df["Ürün Kodu"] = out_df["Ürün Kodu"].astype(str)
        out_df["Notlar"] = out_df["Notlar"].fillna("").astype(str)
        
        # 🎯 AG-GRID İLE TABLO YAPILANDIRMASI
        gb = GridOptionsBuilder.from_dataframe(out_df)
        
        # Hizalamalar
        gb.configure_column("Ürün Kodu", cellStyle={'textAlign': 'left'})
        gb.configure_column("Açıklama", cellStyle={'textAlign': 'left'})
        gb.configure_column("Marka", cellStyle={'textAlign': 'center'})
        gb.configure_column("Ürün Grubu", cellStyle={'textAlign': 'center'})
        
        # 🎯 MUCİZENİN GERÇEKLEŞTİĞİ YER: STOK SÜTUNUNDA NOTLARI BALONCUK YAPMA
        gb.configure_column("Güncel Stok", 
                            cellStyle={'textAlign': 'center'}, 
                            tooltipField="Notlar", 
                            type=["numericColumn", "numberColumnFilter"])
        
        # Notlar sütununu tablodan gizliyoruz (sadece baloncuk için arka planda kalıyor)
        gb.configure_column("Notlar", hide=True)
        
        # 🎯 Fiyatları sayısal bırakıp AgGrid'in Javascript motoruyla formatlıyoruz (Böylece sıralama kusursuz çalışır)
        currency_format = "value != null ? '$' + value.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) : '$0,00'"
        
        gb.configure_column("Birim Maliyet", 
                            cellStyle={'textAlign': 'right'}, 
                            type=["numericColumn"], 
                            valueFormatter=currency_format)
                            
        gb.configure_column("Toplam Maliyet", 
                            cellStyle={'textAlign': 'right'}, 
                            type=["numericColumn"], 
                            valueFormatter=currency_format)

        gridOptions = gb.build()
        gridOptions['enableBrowserTooltips'] = True # Baloncuğun görünmesi için zorunlu

        # Tabloyu Ekrana Bas
        AgGrid(
            out_df,
            gridOptions=gridOptions,
            allow_unsafe_jscode=True,
            columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
            theme="streamlit",
            height=540
        )

    stok_paneli_icerik(df)

except Exception as e:
    st.error(f"Hata oluştu: {e}")
