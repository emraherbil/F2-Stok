<style>
    /* ... (Diğer gizleme stilleriniz aynı kalsın) ... */

    /* 1. Kolonları dikeyde 'flex-end' yapma, hepsini normal akışa bırak */
    div[data-testid="column"] {
        display: block !important;
    }

    /* 2. Tüm form elemanları için üst boşluğu standardize et (hizalama için) */
    div[data-testid="stTextInput"], 
    div[data-testid="stSelectbox"], 
    div[data-testid="stCheckbox"] {
        margin-top: 10px !important;
    }

    /* 3. ARAMA KUTUSU: En kritik nokta burası. 
       st_keyup iframe'i silinse bile bu yükseklik korunacak. */
    div[data-testid="column"]:first-child div.element-container:has(iframe) {
        min-height: 80px !important; /* Etiket dahil yükseklik */
        margin-top: 10px !important;
    }

    /* 4. Buton hizalama: Diğerleriyle aynı hizaya gelmesi için */
    div[data-testid="column"]:last-child .stButton {
        margin-top: 35px !important;
    }
</style>
