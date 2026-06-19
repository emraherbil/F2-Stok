# ==========================================
# 2. SAYFA YAPILANDIRMASI VE CSS SİHİRBAZI (GÜNCELLENMİŞ CSS)
# ==========================================

css_style = """
<style>
    /* Streamlit'in varsayılan üst boşluklarını sıfırla */
    .block-container { padding-top: 0rem !important; padding-bottom: 1rem !important; }
    
    /* ÜST PANELİ SABİTLEME (STICKY) VE KESİLMEYİ ÖNLEME */
    div[data-testid="stMainBlockContainer"] > div:first-child {
        position: -webkit-sticky;
        position: sticky;
        top: 0;
        z-index: 998 !important; /* Menülerin (z-index: 999) altında kalmasını sağlar */
        background-color: #ffffff !important;
        padding-top: 15px !important;
        padding-bottom: 10px !important;
        border-bottom: 2px solid #eef1f6 !important;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.03);
        padding-right: 100px !important; /* Sağdaki menülere çarpmasını önlemek için güvenlik payı */
    }
    
    .custom-header-container {
        display: flex;
        align-items: center;
        gap: 20px;
        padding-bottom: 5px;
    }
    .custom-logo {
        height: 50px;
        object-fit: contain;
    }
    .custom-title-block {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .stCheckbox { margin-top: 30px !important; }
    .stButton button { margin-top: 28px !important; height: 42px !important; }
    
    hr { margin: 0.6rem 0 !important; opacity: 0.4; }
</style>
"""
