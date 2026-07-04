import streamlit as st
from datetime import datetime

# 1. Deklarasikan fungsi Pop-up Window (Modal Dialog) di bagian atas
@st.dialog("Notifikasi Sistem")
def popup_sukses(pesan):
    st.markdown("### 🚨 Transaksi Dibatalkan!")
    st.success(pesan)
    st.write("Catatan transaksi telah dihapus secara permanen. Kalkulasi stok aktual gudang otomatis menyesuaikan.")
    if st.button("Oke, Tutup"):
        st.rerun()

def show(jalankan_query, eksekusi_sql):
    st.header("📋 Laporan Penggunaan & Mutasi Barang")
    
    # 2. Cek memori setelah rerun untuk memunculkan Pop-up Window
    if "notif_audit" in st.session_state:
        pesan_saved = st.session_state["notif_audit"]
        del st.session_state["notif_audit"] # Hapus memori segera agar tidak berulang
        popup_sukses(pesan_saved)

    kolom1, kolom2 = st.columns(2)
    with kolom1:
        bulan_pilihan = st.selectbox(
            "Pilih Bulan", 
            options=["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                     "Juli", "Agustus", "September", "Oktober", "November", "Desember"],
            index=datetime.now().month - 1
        )
        list_bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                      "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        angka_bulan = str(list_bulan.index(bulan_pilihan) + 1).zfill(2)

    with kolom2:
        tahun_pilihan = st.selectbox(
            "Pilih Tahun", 
            options=[2025, 2026, 2027, 2028, 2029, 2030],
            index=1  # Menunjuk ke tahun 2026 sesuai tahun berjalan
        )
    
    query_audit = """
    SELECT 
        t.id AS 'ID Transaksi',
        t.created_at AS 'Tanggal & Jam',
        s.code AS 'Kode Part',
        s.name AS 'Nama Barang',
        t.type AS 'Jenis (IN/OUT)',
        t.quantity AS 'Jumlah (Pcs)',
        t.pic_name AS 'Teknisi / Penanggung Jawab',
        t.purpose AS 'Keterangan / Tujuan'
    FROM stock_transactions t
    JOIN spareparts s ON t.sparepart_id = s.id
    WHERE strftime('%m', t.created_at) = ? AND strftime('%Y', t.created_at) = ?
    ORDER BY t.created_at ASC
    """
    
    df_audit = jalankan_query(query_audit, (angka_bulan, str(tahun_pilihan)))
    
    if df_audit.empty:
        st.info(f"Tidak ada riwayat transaksi pada bulan {bulan_pilihan} {tahun_pilihan}.")
    else:
        st.write(f"Menampilkan **{len(df_audit)} transaksi** pada bulan {bulan_pilihan} {tahun_pilihan}:")
        st.dataframe(df_audit, use_container_width=True)
        
        csv_data = df_audit.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Data Laporan (CSV)",
            data=csv_data,
            file_name=f"Laporan_Stok_{bulan_pilihan}_{tahun_pilihan}.csv",
            mime="text/csv",
        )
        
        st.markdown("---")
        st.subheader("⚠️ Pembatalan / Hapus Salah Input Transaksi")
        
        list_id_transaksi = df_audit['ID Transaksi'].tolist()
        id_hapus_pilihan = st.selectbox("Pilih ID Transaksi yang Ingin Dihapus", options=list_id_transaksi)
        
        detail_hapus = df_audit[df_audit['ID Transaksi'] == id_hapus_pilihan].iloc[0]
        st.warning(f"Anda memilih menghapus transaksi ID **{id_hapus_pilihan}** ({detail_hapus['Nama Barang']} - {detail_hapus['Jenis (IN/OUT)']} sebanyak {detail_hapus['Jumlah (Pcs)']} Pcs).")
        
        tombol_hapus = st.button("Hapus Transaksi Ini")
        
        if tombol_hapus:
            sql_delete = "DELETE FROM stock_transactions WHERE id = ?"
            sukses, pesan = eksekusi_sql(sql_delete, (int(id_hapus_pilihan),))
            if sukses:
                # 3. Simpan pesan sukses ke memori, lalu jalankan rerun
                st.session_state["notif_audit"] = f"Transaksi ID {id_hapus_pilihan} ({detail_hapus['Nama Barang']}) BERHASIL dihapus dan dibatalkan dari sistem!"
                st.rerun()
            else:
                st.error(f"❌ Gagal menghapus data: {pesan}")