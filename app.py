import streamlit as st
import pandas as pd
import os
import base64
from pathlib import Path

# --- GÜNCEL CSS (Menü çakışması ve beyaz boşluk sorunu çözüldü) ---
css_style = """
<style>
    /* Ana kapsayıcıyı düzelt */
    .block-container { padding-top: 1rem !important; }
    
    /* Header Container'ı sabitle */
    .sticky-header {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background-color: white;
        z-index: 998;
        padding: 10px 5%;
        border-bottom: 2px solid #eef1f6;
    }
    
    /* İçeriklerin header'ın altında kalmaması için boşluk bırak */
    .main-content { margin-top: 100px; }
    
    .custom-header-container { display: flex; align-items: center; gap: 20px; }
    .custom-logo { height: 45px; object-fit: contain; }
</style>
"""
st.markdown(css_style, unsafe_allow_html=True)

# ... (logo_to_base64 ve load_data fonksiyonlarınız aynı kalsın) ...

# --- PANEL YAPISI ---
logo_data = logo_to_base64("logo.png") or logo_to_base64("logo.jpg")

# Sabit Header HTML'i
header_html = f"""
<div class="sticky-header">
    <div class="custom-header-container">
        <img src="data:image/png;base64,{logo_data}" class="custom-logo">
        <div>
            <h2 style="margin:0; font-size:1.5rem;">Ofis Stok İzleme Paneli</h2>
        </div>
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# İçerik alanı (Header'ın altına düşmesi için div sınıfı)
st.markdown('<div class="main-content">', unsafe_allow_html=True)

try:
    df = load_data()
    # ... (Buraya diğer filtreleme ve tablo kodlarınızı ekleyin) ...
    
    # Tablo
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Hata: {e}")

st.markdown('</div>', unsafe_allow_html=True)
