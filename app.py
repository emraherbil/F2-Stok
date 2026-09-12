# 1. Tabloyu Seçilebilir Yapma
event = st.dataframe(
    out_df,
    on_select="rerun",
    selection_mode="single-row",
    use_container_width=True,
    hide_index=True
)

# 2. Seçilen Satır İçin Detay Penceresi Açma
selected_rows = event.selection.rows
if selected_rows:
    selected_index = selected_rows[0]
    row_data = out_df.iloc[selected_index]

    @st.dialog("📦 Ürün Detayı")
    def detay_penceresi(row):
        st.write(f"**Ürün Kodu:** {row['Ürün Kodu']}")
        st.write(f"**Açıklama:** {row['Açıklama']}")
        st.write(f"**Marka:** {row['Marka']}")
        st.write(f"**Güncel Stok:** {row['Güncel Stok']} Adet")
        st.write(f"**Birim Maliyet:** {row['Birim Maliyet']}")

    detay_penceresi(row_data)
