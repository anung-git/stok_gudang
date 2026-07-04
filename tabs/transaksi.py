import streamlit as st
from datetime import datetime

# 1. Deklarasikan fungsi Pop-up Window menggunakan decorator st.dialog
@st.dialog("Notifikasi Sistem")
def popup_sukses(pesan):
    st.image("https://img.icons8.com/color/96/checked--v1.png", width=80) # Opsional: Menambah visual centang hijau bawaan web gratisan
    st.success(pesan)
    st.write("Data inventaris telah diperbarui secara real-time di database database offline.")
    if st.button("Oke, Tutup"):
        st.rerun()

def show(jalankan_query, eksekusi_sql):
    st.header("Catat Barang Masuk / Keluar")
    
    # 2. Cek memori setelah rerun, jika ada status sukses, panggil Pop-up Window
    if "notif_transaksi" in st.session_state:
        pesan_saved = st.session_state["notif_transaksi"]
        del st.session_state["notif_transaksi"] # Hapus memori segera agar tidak muncul berulang
        popup_sukses(pesan_saved) # Memunculkan jendela pop-up

    df_pilihan = jalankan_query("SELECT id, code, name FROM spareparts")
    
    if df_pilihan.empty:
        st.warning("Belum ada data barang. Silakan tambah master barang terlebih dahulu di Tab ke-3.")
    else:
        df_pilihan['display'] = df_pilihan['code'] + " - " + df_pilihan['name']
        barang_terpilih = st.selectbox("Pilih Sparepart", options=df_pilihan['display'].tolist())
        id_barang = df_pilihan[df_pilihan['display'] == barang_terpilih]['id'].values[0]
        
        jenis_transaksi = st.radio("Jenis Pergerakan Stok", ["Barang Masuk (IN)", "Barang Keluar (OUT)"])
        tipe_db = "IN" if "Masuk" in jenis_transaksi else "OUT"
        
        jumlah = st.number_input("Jumlah (Pcs/Unit)", min_value=1, value=1)
        
        st.markdown("##### 📅 Pengaturan Waktu Transaksi")
        kol_tgl, kol_jam = st.columns(2)
        with kol_tgl:
            tanggal_pilihan = st.date_input("Pilih Tanggal", value=datetime.now().date())
        with kol_jam:
            jam_pilihan = st.time_input("Pilih Jam", value=datetime.now().time())
            
        waktu_gabungan = datetime.combine(tanggal_pilihan, jam_pilihan).strftime('%Y-%m-%d %H:%M:%S')
        
        nama_pic = st.text_input("Nama Teknisi / Admin", placeholder="Contoh: Budi (Teknisi Mesin A)")
        alasan = st.text_area("Keterangan / Tujuan", placeholder="Contoh: Perbaikan kerusakan motor conveyor utama")
        
        tombol_transaksi = st.button("🚀 Proses Transaksi Stok")
        
        if tombol_transaksi:
            if nama_pic:
                sql_insert = """
                INSERT INTO stock_transactions (sparepart_id, type, quantity, pic_name, purpose, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """
                sukses, pesan = eksekusi_sql(sql_insert, (int(id_barang), tipe_db, jumlah, nama_pic, alasan, waktu_gabungan))
                
                if sukses:
                    # 3. Simpan pesan ke memori, lalu trigger rerun
                    st.session_state["notif_transaksi"] = f"Transaksi {tipe_db} sebanyak {jumlah} Pcs untuk barang '{barang_terpilih}' BERHASIL diproses!"
                    st.rerun()
                else:
                    st.error(f"❌ Gagal mencatat transaksi: {pesan}")
            else:
                st.warning("⚠️ Mohon isi nama Teknisi/Admin yang bertanggung jawab.")