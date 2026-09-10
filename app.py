import pandas as pd
import streamlit as st

@st.cache_data
def veriyi_getir():
    # Excel dosyasının 'stok' sayfasını openpyxl motoru ile okuyoruz
    dosya_yolu = "Stok Sayım Arşivi-v3.1-Web.xlsm"
    df = pd.read_excel(dosya_yolu, sheet_name="stok", engine="openpyxl")
    return df

def main():
    st.title("Stok Yönetim Paneli")
    
    try:
        df = veriyi_getir()
        
        # Eklediğiniz DQ, DR, DS sütunlarının Excel'deki birinci satırda yer alan TAM başlıklarını kullanın.
        # Örneğin: 'Rezerve', 'Satışa Açık', vb. 
        # Tabloda görünmesini istediğiniz mevcut sütunları da bu listeye dahil etmelisiniz.
        gosterilecek_sutunlar = [
            "Ürün Kodu",          # Mevcut verinizdeki örnek bir sütun
            "Ürün Adı",           # Mevcut verinizdeki örnek bir sütun
            "Rezerve",            # Excel'deki DQ/DR sütununuzun tam başlığı
            "Satışa Açık"         # Excel'deki DR/DS sütununuzun tam başlığı
        ]
        
        # Tabloyu arayüzde tüm genişliği kaplayacak şekilde render ediyoruz
        st.subheader("Ürün Stok Durumu")
        st.dataframe(df[gosterilecek_sutunlar], use_container_width=True)
        
    except Exception as e:
        st.error(f"Dosya okunurken veya tablo oluşturulurken bir hata meydana geldi: {e}")

if __name__ == "__main__":
    main()
