import base64
import os
from pathlib import Path
import pandas as pd
import streamlit as st

# ==========================================
# 1. SAYFA YAPILANDIRMASI
# ==========================================
st.set_page_config(
    page_title="F2 ICT - Ofis Stok İzleme Paneli", page_icon="📦", layout="wide"
)

if "dark_mode" not in st.session_state:
  st.session_state.dark_mode = False

is_dark = st.session_state.dark_mode

# 🎨 LOGO RENK PALETİ ("Information Communication Technologies")
LOGO_COLOR = "#B5C1D0"  # Logo alt yazı rengi (Tablo Başlığı)

if is_dark:
  bg_color = "#0E1117"
  text_color = "#FAFAFA"
  subtext_color = "#A3A8B4"
  input_bg = LOGO_COLOR
  input_text = "#1E222A"
  input_border = "#383E4A"
  header_bg = LOGO_COLOR
  card_bg = "#2A2F3B"
  card_text = "#FFFFFF"
  card_label = "#D1D5DB"
  table_bg = "#1E222A"  # 🎯 Dark mod tablo satır ve arkaplan rengi
else:
  bg_color = "#FFFFFF"
  text_color = "#262730"
  subtext_color = "#7D7F87"
  input_bg = "#E2E8F0"
  input_text = "#1A202C"
  input_border = "#CBD5E0"
  header_bg = LOGO_COLOR
  card_bg = "rgba(28, 31, 46, 0.03)"
  card_text = "#111111"
  card_label = "#555555"
  table_bg = "#FFFFFF"  # 🎯 Açık mod tablo satır ve arkaplan rengi

st.markdown(
    f"""
    <style>
        footer {{visibility: hidden !important; display: none !important;}}
        .viewerBadge_container {{display: none !important;}}
        header {{visibility: hidden !important; display: none !important;}}
        
        /* 1. ROOT SEVİYESİNDE YALNIZCA ANA ARKA PLANLARI ETKİLE (Sızmayı Engeller) */
        :root, [data-testid="stAppViewContainer"], .stApp {{
            --background-color: {bg_color} !important;
            --text-color: {text_color} !important;
            background-color: {bg_color} !important;
            color: {text_color} !important;
        }}
        
        .block-container {{ 
            padding-top: 1.5rem !important; 
            padding-bottom: 1.5rem !important; 
            max-width: 100% !important;
        }}
        
        div[data-testid="stWidgetLabel"] label, 
        div[data-testid="stWidgetLabel"] p {{
            color: {text_color} !important;
            font-weight: 600 !important;
        }}

        div[data-testid="stTextInput"] > div > div,
        div[data-testid="stSelectbox"] > div > div,
        div[data-baseweb="base-input"],
        div[data-baseweb="select"] > div {{
            background-color: {input_bg} !important;
            border-color: {input_border} !important;
            border-radius: 6px !important;
        }}

        div[data-testid="stTextInput"] input {{
            color: {input_text} !important;
            -webkit-text-fill-color: {input_text} !important;
            font-weight: 600 !important;
        }}

        div[data-testid="stTextInput"] input::placeholder {{
            color: #4A5568 !important;
        }}

        div[data-testid="stSelectbox"] div[role="button"],
        div[data-baseweb="select"] span,
        div[data-baseweb="select"] svg {{
            color: {input_text} !important;
            fill: {input_text} !important;
            font-weight: 600 !important;
        }}

        div[data-baseweb="popover"] div,
        div[data-baseweb="menu"],
        div[data-baseweb="option"] {{
            background-color: {input_bg} !important;
            color: {input_text} !important;
        }}

        /* ========================================================
           2. DATAFRAME ÖZEL STİL KONTROLÜ (BEYAZ ŞERİT ÇÖZÜMÜ)
           ======================================================== */
        /* Sadece tabloya özel başlık rengi */
        div[data-testid="stDataFrame"] {{
            --secondary-background-color: {header_bg} !important;
        }}

        /* Tablonun kapsayıcı dış çerçevesi ve alt boşlukları satır rengiyle aynı olsun */
        div[data-testid="stDataFrame"] > div {{
            background-color: {table_bg} !important;
            border: 1px solid {input_border} !important;
            border-radius: 6px !important;
            overflow: hidden !important;
        }}

        /* Kaydırma çubuğu (scrollbar) arka planlarının beyaz görünmesini engelleme */
        div[data-testid="stDataFrame"] ::-webkit-scrollbar-track {{
            background: {table_bg} !important;
        }}
        div[data-testid="stDataFrame"] ::-webkit-scrollbar-corner {{
            background: {table_bg} !important;
        }}
        /* ======================================================== */

        div[data-testid="stCheckbox"] label span {{
            color: {text_color} !important;
        }}
        div[data-testid="stCheckbox"] {{
            margin-bottom: -15px !important;
        }}

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
""",
    unsafe_allow_html=True,
)


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
  return pd.read_excel(
      "Stok Sayım Arşivi-v3.1-Web.xlsm", sheet_name="Stok", engine="openpyxl"
  )


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

  df[c_stok] = pd.to_numeric(df[c_stok], errors="coerce").fillna(0)
  df[c_maliyet] = pd.to_numeric(df[c_maliyet], errors="coerce").fillna(0)
  df[c_fiyat] = pd.to_numeric(df[c_fiyat], errors="coerce").fillna(0)

  if logo_data:
    logo_html = (
        f'<img src="data:image/png;base64,{logo_data}" class="custom-logo">'
    )
  else:
    logo_html = '<div style="font-size: 2.5rem;">📦</div>'

  header_col1, header_col2 = st.columns([8.5, 1.5])

  with header_col1:
    st.markdown(
        f"""
            <div class="custom-header-container" style="border-bottom:none; margin-bottom:0; padding-bottom:0;">
                <div class="custom-header-left">
                    {logo_html}
                    <div class="custom-title-block">
                        <h2 style="margin:0; padding:0; font-size:1.85rem; color:{text_color}; font-weight:700; line-height:1.2;">Ofis Stok İzleme Paneli</h2>
                        <span style="color:{subtext_color}; font-size:0.85rem; margin-top:4px;">📅 <b>Son Güncelleme / Sayım Tarihi:</b> {c_stok}</span>
                    </div>
                </div>
            </div>
            """,
        unsafe_allow_html=True,
    )

  with header_col2:
    st.toggle("🌙 Karanlık Mod", key="dark_mode")

  st.markdown(
      f"<hr style='margin-top:10px; margin-bottom:20px;"
      f" border-color:{'#333333' if is_dark else '#e0e0e0'};'>",
      unsafe_allow_html=True,
  )

  # ==========================================
  # 4. FRAGMENT ALANI
  # ==========================================
  @st.fragment
  def stok_paneli_icerik(data_frame):
    if "clear_ver" not in st.session_state:
      st.session_state.clear_ver = 0
    if "q_grup" not in st.session_state:
      st.session_state.q_grup = "Tümü"
    if "q_marka" not in st.session_state:
      st.session_state.q_marka = "Tümü"
    if "q_stok" not in st.session_state:
      st.session_state.q_stok = False
    if "q_sifir_stok" not in st.session_state:
      st.session_state.q_sifir_stok = False

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
      df_for_marka = data_frame[
          data_frame[c_grup].astype(str) == current_grup
      ]
    else:
      df_for_marka = data_frame
    marka_ops = ["Tümü"] + sorted([
        str(x)
        for x in df_for_marka[c_marka].dropna().unique()
        if str(x).lower() != "nan"
    ])

    if current_marka != "Tümü":
      df_for_grup = data_frame[
          data_frame[c_marka].astype(str) == current_marka
      ]
    else:
      df_for_grup = data_frame
    grup_ops = ["Tümü"] + sorted([
        str(x)
        for x in df_for_grup[c_grup].dropna().unique()
        if str(x).lower() != "nan"
    ])

    if current_marka not in marka_ops:
      st.session_state.q_marka = "Tümü"
    if current_grup not in grup_ops:
      st.session_state.q_grup = "Tümü"

    with col1:
      v_search = st.text_input(
          label="📝 Ürün Ara",
          key=f"search_box_{st.session_state.clear_ver}",
          placeholder="Ürün adı veya kodu yazıp Enter'a basın...",
      )

    with col2:
      v_marka = st.selectbox("🏷️ Marka", marka_ops, key="q_marka")

    with col3:
      v_grup = st.selectbox("📂 Ürün Grubu", grup_ops, key="q_grup")

    with col4:
      st.markdown(
          "<div style='height: 25px;'></div>", unsafe_allow_html=True
      )
      v_stok = st.checkbox("🚫 Tükenenleri Gizle", key="q_stok")
      v_sifir_stok = st.checkbox(
          "⚠️ Sadece Tükenenleri Listele", key="q_sifir_stok"
      )

    with col5:
      st.markdown(
          "<div style='height: 28px;'></div>", unsafe_allow_html=True
      )
      st.button(
          "🧹 Temizle",
          on_click=filtreleri_temizle,
          use_container_width=True,
      )

    f_df = data_frame.copy()
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
    if v_sifir_stok:
      f_df = f_df[f_df[c_stok] == 0]

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
    with k1:
      st.markdown(
          kpi_card(
              "📋 Toplam Çeşit:",
              f"{t_prod:,}".replace(",", ".") + " Adet",
              "#1E88E5",
          ),
          unsafe_allow_html=True,
      )
    with k2:
      st.markdown(
          kpi_card(
              "📦 Toplam Stok:",
              f"{t_stok:,}".replace(",", ".") + " Adet",
              "#4CAF50",
          ),
          unsafe_allow_html=True,
      )
    with k3:
      st.markdown(
          kpi_card(
              "💰 Toplam Maliyet:",
              f"${t_cost:,.0f}".replace(",", "."),
              "#FFC107",
          ),
          unsafe_allow_html=True,
      )

    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

    out_df = f_df[[
        c_kod,
        c_tanim,
        c_marka,
        c_grup,
        c_stok,
        c_fiyat,
        c_maliyet,
    ]].copy()
    out_df.columns = [
        "Ürün Kodu",
        "Açıklama",
        "Marka",
        "Ürün Grubu",
        "Güncel Stok",
        "Birim Maliyet",
        "Toplam Maliyet",
    ]

    out_df["Ürün Kodu"] = out_df["Ürün Kodu"].astype(str)
    out_df = out_df.reset_index(drop=True)
    raw_stok = out_df["Güncel Stok"].copy()

    out_df["Birim Maliyet"] = out_df["Birim Maliyet"].apply(
        lambda v: (
            f"${v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
    )
    out_df["Toplam Maliyet"] = out_df["Toplam Maliyet"].apply(
        lambda v: (
            f"${v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
    )

    out_df["Güncel Stok"] = out_df["Güncel Stok"].apply(
        lambda v: f"{int(v):,}".replace(",", ".")
    )

    def row_style(row):
      is_zero = raw_stok.loc[row.name] == 0
      if is_dark:
        bg = "#2A2F3B" if is_zero else table_bg
        color = "#F5F5F5"
        return [f"background-color: {bg}; color: {color}"] * len(row)
      else:
        if is_zero:
          return [
              "background-color: rgba(255, 75, 75, 0.15); color: #000000"
          ] * len(row)
        return [""] * len(row)

    # 📏 DİNAMİK YÜKSEKLİK HESAPLAMA (Daha Hassas Ayar)
    # Streamlit Tablo Satırı: 35px, Tablo Başlığı: 38px
    row_count = len(out_df)
    calculated_height = (row_count * 35) + 38
    
    if row_count == 0:
        dynamic_height = 100
    elif calculated_height > 540:
        dynamic_height = 540
    else:
        dynamic_height = calculated_height

    st.dataframe(
        out_df.style.apply(row_style, axis=1),
        use_container_width=True,
        hide_index=True,
        height=dynamic_height,
        column_config={
            "Marka": st.column_config.Column(alignment="center"),
            "Ürün Grubu": st.column_config.Column(alignment="center"),
            "Güncel Stok": st.column_config.Column(alignment="center"),
            "Birim Maliyet": st.column_config.Column(alignment="right"),
            "Toplam Maliyet": st.column_config.Column(alignment="right"),
        },
    )

  stok_paneli_icerik(df)

except Exception as e:
  st.error(f"Hata oluştu: {e}")
