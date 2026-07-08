import streamlit as st

def show(jalankan_query):
    st.header("Status Stok Gudang Saat Ini")
    st.write("Cari status ketersediaan sparepart berdasarkan nama barang atau kode part.")
    
    kata_kunci = st.text_input("🔍 Cari berdasarkan Nama Barang atau Kode Part...", placeholder="Contoh: Transistor, Resistor...")
    
    query_stok = """
    SELECT 
        s.code AS 'Kode Part',
        s.name AS 'Nama Barang',
        s.location AS 'Lokasi Penyimpanan',
        s.min_stock AS 'Stok Min',
        COALESCE(SUM(CASE WHEN t.type = 'IN' THEN t.quantity ELSE 0 END), 0) -
        COALESCE(SUM(CASE WHEN t.type = 'OUT' THEN t.quantity ELSE 0 END), 0) AS 'Stok Sekarang'
    FROM spareparts s
    LEFT JOIN stock_transactions t ON s.id = t.sparepart_id
    GROUP BY s.id
    """
    df_stok = jalankan_query(query_stok)
    
    if kata_kunci:
        df_filtered = df_stok[
            df_stok['Kode Part'].str.contains(kata_kunci, case=False, na=False) |
            df_stok['Nama Barang'].str.contains(kata_kunci, case=False, na=False) |
            df_stok['Lokasi Penyimpanan'].fillna('').str.contains(kata_kunci, case=False, na=False)
        ]
    else:
        df_filtered = df_stok

    # Tampilkan kolom dengan urutan: Nama Barang, Kode Part, ...
    cols_preferred = ['Nama Barang', 'Kode Part', 'Lokasi Penyimpanan', 'Stok Min', 'Stok Sekarang']
    existing_cols = [c for c in cols_preferred if c in df_filtered.columns]
    # Tambahkan kolom lain di akhir jika ada
    other_cols = [c for c in df_filtered.columns if c not in existing_cols]
    df_filtered = df_filtered[existing_cols + other_cols]

    if df_filtered.empty:
        st.warning(f"Tidak ada sparepart yang cocok dengan kata kunci '{kata_kunci}'.")
    else:
        def warnai_stok(row):
            stok = row['Stok Sekarang']
            stok_min = row['Stok Min']
            if stok <= 0:
                return ['background-color: #ffcccc; color: black'] * len(row) 
            elif stok < stok_min:
                return ['background-color: #ffe6cc; color: black'] * len(row) 
            return [''] * len(row)
        
        st.dataframe(df_filtered.style.apply(warnai_stok, axis=1), use_container_width=True)
        
        total_item = len(df_filtered)
        habis = len(df_filtered[df_filtered['Stok Sekarang'] <= 0])
        st.caption(f"Menampilkan {total_item} jenis barang. (Ada {habis} barang berstatus HABIS)")