import streamlit as st
import pandas as pd

# Dosya yolunu belirtin (GitHub deponuzdaki veya lokaldeki konumu)
dosya_yolu = "Stok Sayım Arşivi-v3.1-Web.xlsm"

try:
    # 1. Excel dosyasını Pandas DataFrame olarak okuma
    df = pd.read_excel(dosya_yolu)

    # 2. Gösterilmesini istediğiniz sütunları liste olarak tanımlama
    istenen_sutunlar = [
        "Ürün Kodu", 
        "Açıklama", 
        "Güncel Stok", 
        "Rezerve", 
        "Satışa Açık", 
        "Birim Maliyet", 
        "Toplam Maliyet"
    ]

    # 3. DataFrame'i sadece bu sütunları içerecek şekilde filtreleme
    filtrelenmis_df = df[istenen_sutunlar]

    # 4. Web arayüzünde tabloyu gösterme
    st.subheader("Güncel Stok Durumu")
    
    # st.dataframe, kullanıcının sütunları sıralamasına ve tabloyu genişletmesine olanak tanır
    st.dataframe(filtrelenmis_df, use_container_width=True) 

except KeyError as e:
    st.error(f"Sütun bulunamadı hatası: {e}. Lütfen Excel dosyanızdaki sütun başlıkları ile koddaki isimlerin birebir aynı olduğundan (başında/sonunda boşluk olmadığından) emin olun.")
except Exception as e:
    st.error(f"Veri okunurken bir hata oluştu: {e}")
