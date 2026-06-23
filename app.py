import streamlit as st
import pandas as pd
import os
import base64
from pathlib import Path

# ... (Sayfa yapılandırması ve CSS kısmınız aynı kalabilir, 
# sadece st.text_input'un render edilme şeklini aşağıda değiştiriyoruz)

@st.fragment
    def stok_paneli_icerik(data_frame):
        # 1. State Yönetimi
        if "q_grup" not in st.session_state: st.session_state.q_grup = "Tümü"
        if "q_marka" not in st.session_state: st.session_state.q_marka = "Tümü"
        if "q_stok" not in st.session_state: st.session_state.q_stok = False
        if "search_text" not in st.session_state: st.session_state.search_text = ""
        
    def filtreleri_temizle():
        st.session_state.search_text = ""
        st.session_state.q_grup = "Tümü"
        st.session_state.q_marka = "Tümü"
        st.session_state.q_stok = False

        # 2. Arayüz ve Hizalama (vertical_alignment="bottom" ile sabit)
        col1, col2, col3, col4, col5 = st.columns([3.2, 2.4, 2.4, 2.2, 1.2], vertical_alignment="bottom")
        
        with col1:
            # HARF HARF CANLI ARAMA: 
            # on_change=None bırakıyoruz ki her tuş vuruşunda fragment tetiklensin
            v_search = st.text_input(
                "📝 Ürün Ara", 
                value=st.session_state.search_text,
                placeholder="Yazmaya başlayın...",
                key="search_text"
            )

        with col2:
            current_marka = st.selectbox("🏷️ Marka", ["Tümü"] + sorted(data_frame[c_marka].dropna().unique().astype(str).tolist()), key="q_marka")
        
        with col3:
            current_grup = st.selectbox("📂 Ürün Grubu", ["Tümü"] + sorted(data_frame[c_grup].dropna().unique().astype(str).tolist()), key="q_grup")
            
        with col4:
            v_stok = st.checkbox("🚫 Tükenenleri Gizle", key="q_stok")

        with col5:
            st.button("🧹 Temizle", on_click=filtreleri_temizle, use_container_width=True)

        # 3. Filtreleme Algoritması (v_search anlık olarak değiştiği için her harfte burası çalışır)
        f_df = data_frame.copy()
        
        # Canlı filtreleme (Arama kutusuna her harf yazıldığında bu blok yeniden hesaplanır)
        if v_search:
            m1 = f_df[c_kod].astype(str).str.contains(v_search, case=False, na=False)
            m2 = f_df[c_tanim].astype(str).str.contains(v_search, case=False, na=False)
            f_df = f_df[m1 | m2]
            
        if current_marka != "Tümü": f_df = f_df[f_df[c_marka].astype(str) == current_marka]
        if current_grup != "Tümü": f_df = f_df[f_df[c_grup].astype(str) == current_grup]
        if v_stok: f_df = f_df[f_df[c_stok] > 0]

        # ... (Geri kalan KPI kartları ve tablo kısmı aynen devam edebilir)
